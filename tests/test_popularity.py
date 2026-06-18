import os
import tempfile
import pytest
from datetime import date, timedelta
from src.domain.entities import BookEntity, ReaderEntity, LoanEntity
from src.infra.adapters import JSONPersistenceAdapter, INIConfigAdapter, LoanHistoryAdapter
from src.app.use_cases import CheckoutUseCase
from src.infra.cli import CLIController
from tests.test_use_cases import FakeLibraryRepository, FakeConfigProvider
from tests.test_loan_history import FakeLoanHistoryRepository

def test_checkout_count_increments() -> None:
    repo = FakeLibraryRepository()
    config = FakeConfigProvider()
    
    book = BookEntity("B1", "TDD Book")
    reader = ReaderEntity("R1", "Alice")
    
    repo.save_book(book)
    repo.save_reader(reader)
    
    checkout_use_case = CheckoutUseCase(repo, config)
    checkout_use_case.execute("R1", "B1", date.today())
    
    assert book.checkout_count == 1
    
    # Return and checkout again
    book.return_book()
    reader.active_loans.clear()
    checkout_use_case.execute("R1", "B1", date.today())
    assert book.checkout_count == 2

def test_cli_popularity_report() -> None:
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp_db:
        db_path = tmp_db.name
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp_hist:
        hist_path = tmp_hist.name

    try:
        repo = JSONPersistenceAdapter(db_path)
        config = INIConfigAdapter()
        history_repo = LoanHistoryAdapter(hist_path)
        
        b1 = BookEntity("B1", "Book One", checkout_count=5)
        b2 = BookEntity("B2", "Book Two", checkout_count=10)
        b3 = BookEntity("B3", "Book Three", checkout_count=0) # underutilized
        
        # B2 has waitlist of 3 readers
        b2.reserve("R1")
        b2.reserve("R2")
        b2.reserve("R3")
        
        repo.save_book(b1)
        repo.save_book(b2)
        repo.save_book(b3)
        
        loan_b1 = LoanEntity("L_B1", "B1", "R1", date.today() - timedelta(days=5), date.today() + timedelta(days=2))
        repo.save_loan(loan_b1)
        
        controller = CLIController(repo, config, history_repo)
        
        # Test basic report (sorted B2, B1, B3)
        res = controller.execute(["popularity-report"])
        assert "Book Two" in res
        assert "Book One" in res
        assert "Book Three" in res
        # B2 should be first
        assert res.index("Book Two") < res.index("Book One")
        # Recommendation should be present for B2 (waitlist >= 3)
        assert "Recomendação: Adquirir" in res
        assert "Book Two" in res
        
        # Test top filter
        res_top = controller.execute(["popularity-report", "--top", "1"])
        assert "Book Two" in res_top
        assert "Book One" not in res_top
        
        # Test with-waitlist filter
        res_waitlist = controller.execute(["popularity-report", "--with-waitlist"])
        assert "Book Two" in res_waitlist
        assert "Book One" not in res_waitlist
        
        # Test underutilized filter (0 checkouts in 90 days)
        # B3 has 0 checkouts overall, so B3 is underutilized
        res_under = controller.execute(["popularity-report", "--underutilized"])
        assert "Book Three" in res_under
        assert "Book One" not in res_under
        
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
