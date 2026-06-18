import pytest
from datetime import date, timedelta
from src.domain.entities import BookEntity, ReaderEntity, LoanEntity, ReaderAutoSuspendedError, DomainError
from src.app.use_cases import CheckoutUseCase, ReturnUseCase
from src.infra.cli import CLIController
from tests.test_use_cases import FakeLibraryRepository, FakeConfigProvider

def test_reader_auto_suspension_thresholds() -> None:
    repo = FakeLibraryRepository()
    config = FakeConfigProvider(auto_suspend_overdue_days=14)
    
    # Setup reader and book
    reader = ReaderEntity("R1", "Alice")
    book = BookEntity("B1", "TDD Book")
    repo.save_reader(reader)
    repo.save_book(book)
    
    # Scenario 1: Overdue loan with N-1 days (13 days overdue)
    # due_date is checkout_date + 7. If checkout is today - 20 days, due_date is today - 13 days.
    # overdue days = today - due_date = 13 days.
    checkout_date = date.today() - timedelta(days=20)
    due_date = checkout_date + timedelta(days=7)
    loan = LoanEntity("L1", "B1", "R1", checkout_date, due_date)
    reader.add_loan(loan)
    repo.save_loan(loan)
    
    # update status: should remain active because overdue is N-1 (13) < N (14)
    reader.update_status(date.today(), config.get_auto_suspend_overdue_days())
    assert reader.status == "Active"
    
    # Try another checkout: should succeed
    book2 = BookEntity("B2", "DDD Book")
    repo.save_book(book2)
    checkout_use_case = CheckoutUseCase(repo, config)
    new_loan = checkout_use_case.execute("R1", "B2", date.today())
    assert new_loan is not None
    assert new_loan.book_id == "B2"

def test_reader_auto_suspension_blocks_checkout() -> None:
    repo = FakeLibraryRepository()
    config = FakeConfigProvider(auto_suspend_overdue_days=14)
    
    reader = ReaderEntity("R1", "Alice")
    book = BookEntity("B1", "TDD Book")
    repo.save_reader(reader)
    repo.save_book(book)
    
    # Scenario 2: Overdue loan with N days (14 days overdue)
    checkout_date = date.today() - timedelta(days=21)
    due_date = checkout_date + timedelta(days=7)
    loan = LoanEntity("L1", "B1", "R1", checkout_date, due_date)
    reader.add_loan(loan)
    repo.save_loan(loan)
    
    # update status: should be suspended
    reader.update_status(date.today(), config.get_auto_suspend_overdue_days())
    assert reader.status == "Suspended"
    
    # Try checkout: should raise ReaderAutoSuspendedError
    book2 = BookEntity("B2", "DDD Book")
    repo.save_book(book2)
    checkout_use_case = CheckoutUseCase(repo, config)
    
    with pytest.raises(ReaderAutoSuspendedError, match="Reader has critical overdue loans"):
        checkout_use_case.execute("R1", "B2", date.today())

def test_return_and_waive_restores_active_status() -> None:
    repo = FakeLibraryRepository()
    config = FakeConfigProvider(auto_suspend_overdue_days=14)
    
    reader = ReaderEntity("R1", "Alice")
    book = BookEntity("B1", "TDD Book")
    book.loan_to("R1")
    checkout_date = date.today() - timedelta(days=21)
    due_date = checkout_date + timedelta(days=7)
    loan = LoanEntity("L1", "B1", "R1", checkout_date, due_date)
    reader.add_loan(loan)
    repo.save_loan(loan)
    repo.save_reader(reader)
    repo.save_book(book)
    
    return_use_case = ReturnUseCase(repo, config)
    
    # Return book today -> 14 days late -> fine is applied, reader remains suspended because of fine balance
    return_use_case.execute("B1", date.today())
    
    assert reader.fine_balance > 0.0
    reader.update_status(date.today(), config.get_auto_suspend_overdue_days())
    assert reader.status == "Suspended"
    
    # Pay fine to restore active status
    reader.pay_fine(reader.fine_balance)
    reader.update_status(date.today(), config.get_auto_suspend_overdue_days())
    assert reader.status == "Active"

def test_cli_check_overdue() -> None:
    repo = FakeLibraryRepository()
    config = FakeConfigProvider(auto_suspend_overdue_days=14)
    
    reader = ReaderEntity("R1", "Alice")
    book = BookEntity("B1", "TDD Book")
    book.loan_to("R1")
    # 15 days overdue
    checkout_date = date.today() - timedelta(days=22)
    due_date = checkout_date + timedelta(days=7)
    loan = LoanEntity("L1", "B1", "R1", checkout_date, due_date)
    reader.add_loan(loan)
    repo.save_loan(loan)
    repo.save_reader(reader)
    repo.save_book(book)
    
    controller = CLIController(repo, config)
    res = controller.execute(["check-overdue"])
    assert "Success" in res
    assert "1" in res  # should mention 1 reader suspended
    
    assert reader.status == "Suspended"
