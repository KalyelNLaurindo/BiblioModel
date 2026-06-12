import pytest
from src.domain.entities import BookEntity, DomainError

def test_book_entity_initial_state() -> None:
    # A book should start as Available with an empty hold queue
    book = BookEntity(book_id="B101", title="Test Driven Development")
    assert book.book_id == "B101"
    assert book.title == "Test Driven Development"
    assert book.status == "Available"
    assert book.hold_queue == []

def test_book_entity_loan_success() -> None:
    book = BookEntity(book_id="B101", title="TDD")
    # Loan to a reader when available
    book.loan_to(reader_id="R101")
    assert book.status == "Loaned"

def test_book_entity_loan_failure_already_loaned() -> None:
    book = BookEntity(book_id="B101", title="TDD")
    book.loan_to(reader_id="R101")
    
    # Cannot loan again when already loaned
    with pytest.raises(DomainError, match="Book is not available for loan"):
        book.loan_to(reader_id="R102")

def test_book_entity_reserve_when_loaned() -> None:
    book = BookEntity(book_id="B101", title="TDD")
    book.loan_to(reader_id="R101")
    
    # Reserve the book for another reader
    book.reserve(reader_id="R102")
    assert book.status == "Reserved"
    assert book.hold_queue == ["R102"]

def test_book_entity_multiple_reservations_fifo() -> None:
    book = BookEntity(book_id="B101", title="TDD")
    book.loan_to(reader_id="R101")
    
    # Add multiple readers to the hold queue
    book.reserve(reader_id="R102")
    book.reserve(reader_id="R103")
    assert book.hold_queue == ["R102", "R103"]

def test_book_entity_loan_only_to_first_reserver() -> None:
    book = BookEntity(book_id="B101", title="TDD")
    book.loan_to(reader_id="R101")
    book.reserve(reader_id="R102")
    book.reserve(reader_id="R103")
    
    # Book is returned
    book.return_book()
    assert book.status == "Reserved"
    
    # R103 tries to borrow but they are second in line
    with pytest.raises(DomainError, match="Book is reserved for another reader"):
        book.loan_to(reader_id="R103")
        
    # R102 is first in line and borrows successfully
    book.loan_to(reader_id="R102")
    assert book.status == "Loaned"
    assert book.hold_queue == ["R103"]

def test_book_entity_return_to_available_when_no_reservations() -> None:
    book = BookEntity(book_id="B101", title="TDD")
    book.loan_to(reader_id="R101")
    book.return_book()
    assert book.status == "Available"
    assert book.hold_queue == []


def test_loan_entity_creation_and_overdue() -> None:
    from src.domain.entities import LoanEntity
    from datetime import date

    # Create a normal loan
    loan = LoanEntity(
        loan_id="L301",
        book_id="B202",
        reader_id="R101",
        checkout_date=date(2026, 6, 10),
        due_date=date(2026, 6, 17)
    )
    assert loan.loan_id == "L301"
    assert loan.book_id == "B202"
    assert loan.reader_id == "R101"
    assert loan.checkout_date == date(2026, 6, 10)
    assert loan.due_date == date(2026, 6, 17)
    assert loan.return_date is None
    assert loan.fine_amount == 0.0

    # Test is_overdue
    assert not loan.is_overdue(date(2026, 6, 15))
    assert not loan.is_overdue(date(2026, 6, 17))
    assert loan.is_overdue(date(2026, 6, 18))

    # Test return book removes overdue status
    loan.return_date = date(2026, 6, 16)
    assert not loan.is_overdue(date(2026, 6, 18))


def test_reader_entity_creation_and_loans() -> None:
    from src.domain.entities import ReaderEntity, LoanEntity
    from datetime import date

    reader = ReaderEntity(reader_id="R101", name="Jane Doe")
    assert reader.reader_id == "R101"
    assert reader.name == "Jane Doe"
    assert reader.status == "Active"
    assert reader.fine_balance == 0.0
    assert reader.active_loans == []

    # Add active loan
    loan = LoanEntity("L301", "B202", "R101", date(2026, 6, 10), date(2026, 6, 17))
    reader.add_loan(loan)
    assert len(reader.active_loans) == 1
    assert reader.active_loans[0] == loan

    # Return loan
    reader.return_loan("B202", return_date=date(2026, 6, 16))
    assert len(reader.active_loans) == 0


def test_reader_suspension_due_to_fines() -> None:
    from src.domain.entities import ReaderEntity
    from datetime import date

    reader = ReaderEntity(reader_id="R101", name="Jane Doe")
    
    # Fine accrued
    reader.apply_fine(15.0)
    assert reader.fine_balance == 15.0
    
    # Status updates to Suspended due to unpaid fines
    reader.update_status(date(2026, 6, 12))
    assert reader.status == "Suspended"

    # Paying fine partially keeps it suspended if balance > 0
    reader.pay_fine(5.0)
    assert reader.fine_balance == 10.0
    reader.update_status(date(2026, 6, 12))
    assert reader.status == "Suspended"

    # Paying full fine restores active status
    reader.pay_fine(10.0)
    assert reader.fine_balance == 0.0
    reader.update_status(date(2026, 6, 12))
    assert reader.status == "Active"


def test_reader_suspension_due_to_overdue_loans() -> None:
    from src.domain.entities import ReaderEntity, LoanEntity
    from datetime import date

    reader = ReaderEntity(reader_id="R101", name="Jane Doe")
    loan = LoanEntity("L301", "B202", "R101", date(2026, 6, 1), date(2026, 6, 8))
    reader.add_loan(loan)

    # On June 7th, loan is not overdue
    reader.update_status(date(2026, 6, 7))
    assert reader.status == "Active"

    # On June 9th, loan is overdue, so reader should be Suspended
    reader.update_status(date(2026, 6, 9))
    assert reader.status == "Suspended"

    # Return loan on June 10th
    reader.return_loan("B202", return_date=date(2026, 6, 10))
    # Reader should return to Active if no fines
    reader.update_status(date(2026, 6, 10))
    assert reader.status == "Active"

