import os
import tempfile
import logging
from src.infra.adapters import INIConfigAdapter

def test_ini_config_adapter_loads_values() -> None:
    # Create a temporary config file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.ini') as tmp:
        tmp.write("[library]\nmax_loans = 5\nloan_period_days = 14\ndaily_fine_rate = 1.50\ngrace_period_days = 3\n")
        tmp_path = tmp.name

    try:
        adapter = INIConfigAdapter(tmp_path)
        assert adapter.get_max_loans() == 5
        assert adapter.get_loan_period_days() == 14
        assert adapter.get_daily_fine_rate() == 1.50
        assert adapter.get_grace_period_days() == 3
    finally:
        os.remove(tmp_path)

def test_ini_config_adapter_fallback_on_missing_file() -> None:
    # Use a non-existent file path
    adapter = INIConfigAdapter("non_existent_file.ini")
    assert adapter.get_max_loans() == 3
    assert adapter.get_loan_period_days() == 7
    assert adapter.get_daily_fine_rate() == 2.00
    assert adapter.get_grace_period_days() == 0

def test_ini_config_adapter_fallback_on_missing_options() -> None:
    # Create a temporary config file with missing options
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.ini') as tmp:
        tmp.write("[library]\nmax_loans = 10\n")
        tmp_path = tmp.name

    try:
        adapter = INIConfigAdapter(tmp_path)
        assert adapter.get_max_loans() == 10
        assert adapter.get_loan_period_days() == 7  # default fallback
        assert adapter.get_daily_fine_rate() == 2.00  # default fallback
        assert adapter.get_grace_period_days() == 0  # default fallback
    finally:
        os.remove(tmp_path)


def test_setup_logger() -> None:
    from src.infra.adapters import setup_logger
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as tmp:
        log_path = tmp.name

    try:
        logger = setup_logger(log_path)
        assert logger.name == "bibliomodel"
        logger.info("Test log message")
        
        # Verify log file has content
        with open(log_path, "r", encoding="utf-8") as f:
            content = f.read()
            assert "Test log message" in content
            assert "[INFO]" in content
    finally:
        # Clean up logger handlers to release file lock
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)
        os.remove(log_path)


from tests.test_use_cases import FakeLibraryRepository, FakeConfigProvider
from src.domain.entities import BookEntity, ReaderEntity, LoanEntity
from datetime import date

def test_cli_controller_loan_success() -> None:
    from src.infra.cli import CLIController
    repo = FakeLibraryRepository()
    config = FakeConfigProvider()
    
    book = BookEntity("B1", "DDD Book")
    reader = ReaderEntity("R1", "Alice")
    repo.save_book(book)
    repo.save_reader(reader)
    
    controller = CLIController(repo, config)
    
    # Run loan command with explicit date
    res = controller.execute(["loan", "--reader", "R1", "--book", "B1", "--date", "2026-06-12"])
    assert "[OK]" in res
    assert "loaned" in res
    assert "R1" in res
    assert "B1" in res
    
    # Verify states
    assert book.status == "Loaned"
    assert len(reader.active_loans) == 1

def test_cli_controller_loan_missing_args() -> None:
    from src.infra.cli import CLIController
    repo = FakeLibraryRepository()
    config = FakeConfigProvider()
    controller = CLIController(repo, config)
    
    res = controller.execute(["loan", "--reader", "R1"])
    assert "[ERROR]" in res
    assert "parsing" in res.lower()

def test_cli_controller_loan_invalid_date() -> None:
    from src.infra.cli import CLIController
    repo = FakeLibraryRepository()
    config = FakeConfigProvider()
    book = BookEntity("B1", "DDD Book")
    reader = ReaderEntity("R1", "Alice")
    repo.save_book(book)
    repo.save_reader(reader)
    
    controller = CLIController(repo, config)
    res = controller.execute(["loan", "--reader", "R1", "--book", "B1", "--date", "invalid-date"])
    assert "[ERROR]" in res
    assert "date format" in res.lower()

def test_cli_controller_loan_domain_error() -> None:
    from src.infra.cli import CLIController
    repo = FakeLibraryRepository()
    config = FakeConfigProvider()
    controller = CLIController(repo, config)
    
    # Reader not found
    res = controller.execute(["loan", "--reader", "R999", "--book", "B1"])
    assert "[ERROR]" in res
    assert "reader not found" in res.lower()

def test_cli_controller_return_success_and_fines() -> None:
    from src.infra.cli import CLIController
    repo = FakeLibraryRepository()
    config = FakeConfigProvider()
    
    book = BookEntity("B1", "DDD Book")
    book.loan_to("R1")
    reader = ReaderEntity("R1", "Alice")
    loan = LoanEntity("L1", "B1", "R1", date(2026, 6, 1), date(2026, 6, 8))
    reader.add_loan(loan)
    
    repo.save_book(book)
    repo.save_reader(reader)
    repo.save_loan(loan)
    
    controller = CLIController(repo, config)
    
    # Return 3 days late (due on 8th, returned on 11th) -> $6 fine -> warning badge
    res = controller.execute(["return", "--book", "B1", "--date", "2026-06-11"])
    assert "[WARN]" in res
    assert "returned" in res
    assert "fine: $6.00" in res
    
    assert book.status == "Available"
    assert reader.fine_balance == 6.00

def test_cli_controller_reserve_success() -> None:
    from src.infra.cli import CLIController
    repo = FakeLibraryRepository()
    config = FakeConfigProvider()
    
    book = BookEntity("B1", "DDD Book")
    book.loan_to("R2") # book must be loaned to be reserved
    reader = ReaderEntity("R1", "Alice")
    
    repo.save_book(book)
    repo.save_reader(reader)
    
    controller = CLIController(repo, config)
    res = controller.execute(["reserve", "--reader", "R1", "--book", "B1"])
    assert "[HOLD]" in res
    assert "reserved" in res
    
    assert book.status == "Reserved"
    assert book.hold_queue == ["R1"]

def test_cli_controller_report_success() -> None:
    from src.infra.cli import CLIController
    repo = FakeLibraryRepository()
    config = FakeConfigProvider()
    controller = CLIController(repo, config)
    res = controller.execute(["report"])
    assert "[OK]" in res

def test_cli_controller_telemetry_logging(caplog) -> None:
    from src.infra.cli import CLIController
    repo = FakeLibraryRepository()
    config = FakeConfigProvider()
    
    book = BookEntity("B1", "DDD Book")
    reader = ReaderEntity("R1", "Alice")
    repo.save_book(book)
    repo.save_reader(reader)
    
    controller = CLIController(repo, config)
    
    caplog.clear()
    res = controller.execute(["loan", "--reader", "R1", "--book", "B1"])
        
    # Check that execution time and operator were logged under INFO level
    # Check that execution time and operator were logged under INFO level
    info_logs = [record.message for record in caplog.records if record.levelname == "INFO"]
    assert any("resolved in" in log or "execution" in log.lower() for log in info_logs)
    assert any("operator" in log.lower() for log in info_logs)


def test_cli_controller_waive_success(caplog) -> None:
    from src.infra.cli import CLIController
    repo = FakeLibraryRepository()
    config = FakeConfigProvider()
    
    reader = ReaderEntity("R1", "Alice")
    reader.apply_fine(10.00)
    reader.update_status(date.today())
    repo.save_reader(reader)
    
    controller = CLIController(repo, config)
    
    caplog.clear()
    res = controller.execute([
        "waive",
        "--reader", "R1",
        "--operator", "Director John",
        "--reason", "Patron disputed fine"
    ])
    
    assert "[OK]" in res
    assert "R1" in res
    assert reader.fine_balance == 0.0
    assert reader.status == "Active"
    
    # Check that audit log is recorded
    audit_logs = [record.message for record in caplog.records]
    assert any("Director John" in log for log in audit_logs)
    assert any("R1" in log for log in audit_logs)
    assert any("Patron disputed fine" in log for log in audit_logs)
    assert any("waived" in log.lower() or "waive" in log.lower() for log in audit_logs)

def test_cli_controller_waive_missing_params() -> None:
    from src.infra.cli import CLIController
    repo = FakeLibraryRepository()
    config = FakeConfigProvider()
    
    reader = ReaderEntity("R1", "Alice")
    reader.apply_fine(10.00)
    repo.save_reader(reader)
    
    controller = CLIController(repo, config)
    
    # Missing reason
    res1 = controller.execute(["waive", "--reader", "R1", "--operator", "Director John"])
    assert "[ERROR]" in res1
    assert "reason" in res1.lower()
    assert reader.fine_balance == 10.00
    
    # Missing operator
    res2 = controller.execute(["waive", "--reader", "R1", "--reason", "some reason"])
    assert "[ERROR]" in res2
    assert "operator" in res2.lower()
    assert reader.fine_balance == 10.00

def test_cli_controller_report_export() -> None:
    from src.infra.cli import CLIController
    repo = FakeLibraryRepository()
    config = FakeConfigProvider()
    
    # Setup library state
    book1 = BookEntity("B1", "Book One")
    book2 = BookEntity("B2", "Book Two")
    book1.loan_to("R1")
    book2.loan_to("R2")
    # reserve book 1 for R3 and R4
    book1.reserve("R3")
    book1.reserve("R4")
    
    reader1 = ReaderEntity("R1", "Alice")
    reader2 = ReaderEntity("R2", "Bob")
    
    loan1 = LoanEntity("L1", "B1", "R1", date(2026, 6, 1), date(2026, 6, 8)) # Overdue
    loan2 = LoanEntity("L2", "B2", "R2", date(2026, 6, 10), date(2026, 6, 17)) # Active
    
    reader1.add_loan(loan1)
    reader2.add_loan(loan2)
    
    # Bob has fine
    reader2.apply_fine(15.00)
    
    repo.save_book(book1)
    repo.save_book(book2)
    repo.save_reader(reader1)
    repo.save_reader(reader2)
    repo.save_loan(loan1)
    repo.save_loan(loan2)
    
    controller = CLIController(repo, config)
    
    report_file = "daily_handover_report.txt"
    if os.path.exists(report_file):
        os.remove(report_file)
        
    try:
        res = controller.execute(["report"])
        assert "[OK]" in res
        assert os.path.exists(report_file)
        
        with open(report_file, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Check that metrics are present in the report
        assert "Active Loans" in content or "Loans" in content
        assert "Overdue" in content
        assert "Fees" in content or "Fine" in content or "Unpaid" in content
        assert "Queue" in content or "Reserve" in content
    finally:
        if os.path.exists(report_file):
            os.remove(report_file)


def test_cli_formatter_render_table() -> None:
    from src.infra.cli import CLIFormatter
    headers = ["ID", "Name"]
    rows = [["1", "Alice"], ["2", "Bob"]]
    table = CLIFormatter.render_table(headers, rows)
    
    # Check box drawing characters are present
    assert "┌" in table
    assert "┐" in table
    assert "┬" in table
    assert "│" in table
    assert "├" in table
    assert "┼" in table
    assert "┤" in table
    assert "└" in table
    assert "┘" in table
    assert "┴" in table
    
    # Check data is inside
    assert "Alice" in table
    assert "Bob" in table

def test_cli_formatter_long_string_truncation() -> None:
    from src.infra.cli import CLIFormatter
    headers = ["Description"]
    rows = [["This is a very long description that must be truncated"]]
    table = CLIFormatter.render_table(headers, rows, max_col_width=15)
    
    assert "..." in table
    # Check column length limit: col width is 15. Pad is 2 (spaces on both sides) -> cell max length is 17.
    # We check that none of the lines exceed a reasonable terminal limit.
    for line in table.split("\n"):
        assert len(line) <= 25 # line is │ cell │ -> width is 15 + 2 + 2 = 19.

def test_cli_formatter_welcome_banner() -> None:
    from src.infra.cli import CLIFormatter
    banner = CLIFormatter.get_welcome_banner()
    assert "╔" in banner
    assert "═" in banner
    assert "╗" in banner
    assert "║" in banner
    assert "╚" in banner
    assert "╝" in banner
    assert "BIBLIOMODEL" in banner

def test_cli_list_commands() -> None:
    from src.infra.cli import CLIController
    repo = FakeLibraryRepository()
    config = FakeConfigProvider()
    
    book = BookEntity("B1", "DDD Book")
    reader = ReaderEntity("R1", "Alice")
    loan = LoanEntity("L1", "B1", "R1", date(2026, 6, 10), date(2026, 6, 17))
    reader.add_loan(loan)
    
    repo.save_book(book)
    repo.save_reader(reader)
    repo.save_loan(loan)
    
    controller = CLIController(repo, config)
    
    res_books = controller.execute(["list-books"])
    assert "B1" in res_books
    assert "DDD Book" in res_books
    assert "┌" in res_books
    
    res_readers = controller.execute(["list-readers"])
    assert "R1" in res_readers
    assert "Alice" in res_readers
    assert "┌" in res_readers
    
    res_loans = controller.execute(["list-loans"])
    assert "L1" in res_loans
    assert "B1" in res_loans
    assert "R1" in res_loans
    assert "┌" in res_loans






