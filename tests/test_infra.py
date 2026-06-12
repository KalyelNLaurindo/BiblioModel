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
    assert "Success" in res
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
    assert "Error parsing arguments" in res

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
    assert "Error" in res or "invalid" in res or "Business Rule" in res or "System Error" in res

def test_cli_controller_loan_domain_error() -> None:
    from src.infra.cli import CLIController
    repo = FakeLibraryRepository()
    config = FakeConfigProvider()
    controller = CLIController(repo, config)
    
    # Reader not found
    res = controller.execute(["loan", "--reader", "R999", "--book", "B1"])
    assert "Business Rule Error" in res
    assert "Reader not found" in res

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
    
    # Return 3 days late (due on 8th, returned on 11th) -> $6 fine
    res = controller.execute(["return", "--book", "B1", "--date", "2026-06-11"])
    assert "Success" in res
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
    assert "Success" in res
    assert "reserved" in res
    
    assert book.status == "Reserved"
    assert book.hold_queue == ["R1"]

def test_cli_controller_report_success() -> None:
    from src.infra.cli import CLIController
    repo = FakeLibraryRepository()
    config = FakeConfigProvider()
    controller = CLIController(repo, config)
    res = controller.execute(["report"])
    assert "Success" in res


