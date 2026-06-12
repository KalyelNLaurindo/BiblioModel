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
