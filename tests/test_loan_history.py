import os
import tempfile
import pytest
from datetime import date, timedelta
from src.domain.entities import BookEntity, ReaderEntity, LoanEntity
from src.infra.adapters import JSONPersistenceAdapter, LoanHistoryAdapter, INIConfigAdapter
from src.app.use_cases import ReturnUseCase
from src.infra.cli import CLIController
from tests.test_use_cases import FakeLibraryRepository, FakeConfigProvider

class FakeLoanHistoryRepository:
    def __init__(self) -> None:
        self.history = []

    def archive_loan(
        self,
        loan: LoanEntity,
        book_title: str,
        final_status: str,
        delay_days: int,
        applied_rules: list = None,
        original_fine: float = None,
        operator: str = None
    ) -> None:
        record = {
            "loan_id": loan.loan_id,
            "book_id": loan.book_id,
            "book_title": book_title,
            "reader_id": loan.reader_id,
            "checkout_date": loan.checkout_date.isoformat(),
            "due_date": loan.due_date.isoformat(),
            "return_date": loan.return_date.isoformat() if loan.return_date else date.today().isoformat(),
            "delay_days": delay_days,
            "fine_amount": loan.fine_amount,
            "final_status": final_status
        }
        if applied_rules is not None:
            record["applied_rules"] = applied_rules
        if original_fine is not None:
            record["original_fine"] = original_fine
        if operator is not None:
            record["operator"] = operator
        self.history.append(record)

    def get_history_by_reader(self, reader_id: str):
        return [r for r in self.history if r["reader_id"] == reader_id]

def test_return_archives_loan_history() -> None:
    repo = FakeLibraryRepository()
    config = FakeConfigProvider()
    history_repo = FakeLoanHistoryRepository()
    
    book = BookEntity("B1", "TDD Book")
    book.loan_to("R1")
    reader = ReaderEntity("R1", "Alice")
    # 5 days overdue
    checkout_date = date.today() - timedelta(days=12)
    due_date = checkout_date + timedelta(days=7)
    loan = LoanEntity("L1", "B1", "R1", checkout_date, due_date)
    reader.add_loan(loan)
    
    repo.save_book(book)
    repo.save_reader(reader)
    repo.save_loan(loan)
    
    return_use_case = ReturnUseCase(repo, config, history_repo)
    return_use_case.execute("B1", date.today())
    
    assert len(history_repo.history) == 1
    record = history_repo.history[0]
    assert record["loan_id"] == "L1"
    assert record["book_title"] == "TDD Book"
    assert record["final_status"] == "RETURNED_LATE"
    assert record["delay_days"] == 5
    assert record["fine_amount"] == 10.0

def test_cli_reader_history() -> None:
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp_db:
        db_path = tmp_db.name
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp_hist:
        hist_path = tmp_hist.name

    try:
        repo = JSONPersistenceAdapter(db_path)
        config = INIConfigAdapter()
        history_repo = LoanHistoryAdapter(hist_path)
        
        book1 = BookEntity("B1", "Book One")
        book2 = BookEntity("B2", "Book Two")
        reader = ReaderEntity("R1", "Alice")
        
        # Active loan
        loan1 = LoanEntity("L1", "B1", "R1", date.today() - timedelta(days=2), date.today() + timedelta(days=5))
        reader.add_loan(loan1)
        
        repo.save_book(book1)
        repo.save_book(book2)
        repo.save_reader(reader)
        repo.save_loan(loan1)
        
        # Past/returned loan (archived directly in history)
        loan2 = LoanEntity("L2", "B2", "R1", date.today() - timedelta(days=10), date.today() - timedelta(days=3))
        loan2.return_date = date.today() - timedelta(days=4)
        loan2.fine_amount = 2.0
        history_repo.archive_loan(loan2, "Book Two", "RETURNED_LATE", 3)
        
        controller = CLIController(repo, config, history_repo)
        
        # Test full history display
        res = controller.execute(["reader-history", "--reader-id", "R1"])
        assert "Book One" in res
        assert "Book Two" in res
        assert "ACTIVE" in res
        assert "RETURNED_LATE" in res
        
        # Test last-n filter
        res_limit = controller.execute(["reader-history", "--reader-id", "R1", "--last-n", "1"])
        assert "Book One" in res_limit  # Book One is more recent (checkout today-2 vs today-10)
        assert "Book Two" not in res_limit
        
        # Test overdue-only filter
        res_overdue = controller.execute(["reader-history", "--reader-id", "R1", "--overdue-only"])
        assert "Book Two" in res_overdue  # Book Two has $2.00 fine
        assert "Book One" not in res_overdue  # Book One is on time
        
        # Test export
        export_file = "test_history_export.txt"
        if os.path.exists(export_file):
            os.remove(export_file)
            
        res_export = controller.execute(["reader-history", "--reader-id", "R1", "--export", export_file])
        assert "Success" in res_export
        assert os.path.exists(export_file)
        
        with open(export_file, "r", encoding="utf-8") as f:
            content = f.read()
            assert "Book One" in content
            assert "Book Two" in content
            assert "ACTIVE" in content
            
        # Clean export file
        if os.path.exists(export_file):
            os.remove(export_file)
            
        # Test path traversal prevention on export
        res_traversal = controller.execute(["reader-history", "--reader-id", "R1", "--export", "../../secret_history.txt"])
        assert "Security Error" in res_traversal
        
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)
        bak_path = db_path + ".bak"
        if os.path.exists(bak_path):
            os.remove(bak_path)
        if os.path.exists(hist_path):
            os.remove(hist_path)
        bak_hist = hist_path + ".bak"
        if os.path.exists(bak_hist):
            os.remove(bak_hist)
