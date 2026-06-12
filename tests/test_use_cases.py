import pytest
from datetime import date
from src.domain.entities import BookEntity, ReaderEntity, LoanEntity, DomainError
from src.app.ports import ILibraryRepository, IConfigProvider
from src.app.use_cases import CheckoutUseCase
from typing import Dict, Optional

class FakeLibraryRepository(ILibraryRepository):
    def __init__(self) -> None:
        self.books: Dict[str, BookEntity] = {}
        self.readers: Dict[str, ReaderEntity] = {}
        self.loans: Dict[str, LoanEntity] = {}

    def get_book(self, book_id: str) -> Optional[BookEntity]:
        return self.books.get(book_id)

    def save_book(self, book: BookEntity) -> None:
        self.books[book.book_id] = book

    def get_reader(self, reader_id: str) -> Optional[ReaderEntity]:
        return self.readers.get(reader_id)

    def save_reader(self, reader: ReaderEntity) -> None:
        self.readers[reader.reader_id] = reader

    def save_loan(self, loan: LoanEntity) -> None:
        self.loans[loan.loan_id] = loan


class FakeConfigProvider(IConfigProvider):
    def __init__(self, max_loans: int = 3, loan_period_days: int = 7) -> None:
        self._max_loans = max_loans
        self._loan_period_days = loan_period_days

    def get_max_loans(self) -> int:
        return self._max_loans

    def get_loan_period_days(self) -> int:
        return self._loan_period_days

    def get_daily_fine_rate(self) -> float:
        return 2.00

    def get_grace_period_days(self) -> int:
        return 0


def test_checkout_success() -> None:
    # Arrange
    repo = FakeLibraryRepository()
    config = FakeConfigProvider()
    
    book = BookEntity(book_id="B1", title="Domain-Driven Design")
    reader = ReaderEntity(reader_id="R1", name="Alice")
    
    repo.save_book(book)
    repo.save_reader(reader)
    
    use_case = CheckoutUseCase(repository=repo, config_provider=config)
    checkout_date = date(2026, 6, 12)
    
    # Act
    loan = use_case.execute(reader_id="R1", book_id="B1", checkout_date=checkout_date)
    
    # Assert
    assert loan.loan_id is not None
    assert loan.book_id == "B1"
    assert loan.reader_id == "R1"
    assert loan.checkout_date == checkout_date
    assert loan.due_date == date(2026, 6, 19) # 12 + 7 days
    assert loan.return_date is None
    
    # Check that reader and book entities were updated and saved
    saved_book = repo.get_book("B1")
    assert saved_book is not None
    assert saved_book.status == "Loaned"
    
    saved_reader = repo.get_reader("R1")
    assert saved_reader is not None
    assert len(saved_reader.active_loans) == 1
    assert saved_reader.active_loans[0].loan_id == loan.loan_id


def test_checkout_reader_not_found() -> None:
    # Arrange
    repo = FakeLibraryRepository()
    config = FakeConfigProvider()
    
    book = BookEntity(book_id="B1", title="Domain-Driven Design")
    repo.save_book(book)
    
    use_case = CheckoutUseCase(repository=repo, config_provider=config)
    
    # Act & Assert
    with pytest.raises(DomainError, match="Reader not found"):
        use_case.execute(reader_id="R999", book_id="B1", checkout_date=date(2026, 6, 12))


def test_checkout_book_not_found() -> None:
    # Arrange
    repo = FakeLibraryRepository()
    config = FakeConfigProvider()
    
    reader = ReaderEntity(reader_id="R1", name="Alice")
    repo.save_reader(reader)
    
    use_case = CheckoutUseCase(repository=repo, config_provider=config)
    
    # Act & Assert
    with pytest.raises(DomainError, match="Book not found"):
        use_case.execute(reader_id="R1", book_id="B999", checkout_date=date(2026, 6, 12))


def test_checkout_reader_suspended() -> None:
    # Arrange
    repo = FakeLibraryRepository()
    config = FakeConfigProvider()
    
    book = BookEntity(book_id="B1", title="Domain-Driven Design")
    reader = ReaderEntity(reader_id="R1", name="Alice")
    # reader starts active but applying fine and updating status suspends them
    reader.apply_fine(10.00)
    reader.update_status(date(2026, 6, 12))
    
    repo.save_book(book)
    repo.save_reader(reader)
    
    use_case = CheckoutUseCase(repository=repo, config_provider=config)
    
    # Act & Assert
    with pytest.raises(DomainError, match="Reader is suspended"):
        use_case.execute(reader_id="R1", book_id="B1", checkout_date=date(2026, 6, 12))


def test_checkout_reader_limit_reached() -> None:
    # Arrange
    repo = FakeLibraryRepository()
    config = FakeConfigProvider(max_loans=2)
    
    book1 = BookEntity("B1", "DDD")
    book2 = BookEntity("B2", "TDD")
    book3 = BookEntity("B3", "Clean Code")
    reader = ReaderEntity("R1", "Alice")
    
    # reader already has 2 active loans (which is the max)
    loan1 = LoanEntity("L1", "B1", "R1", date(2026, 6, 10), date(2026, 6, 17))
    loan2 = LoanEntity("L2", "B2", "R1", date(2026, 6, 10), date(2026, 6, 17))
    reader.add_loan(loan1)
    reader.add_loan(loan2)
    
    repo.save_book(book1)
    repo.save_book(book2)
    repo.save_book(book3)
    repo.save_reader(reader)
    
    use_case = CheckoutUseCase(repository=repo, config_provider=config)
    
    # Act & Assert
    with pytest.raises(DomainError, match="Reader active loans limit reached"):
        use_case.execute(reader_id="R1", book_id="B3", checkout_date=date(2026, 6, 12))


def test_checkout_book_already_loaned() -> None:
    # Arrange
    repo = FakeLibraryRepository()
    config = FakeConfigProvider()
    
    book = BookEntity("B1", "DDD")
    book.loan_to("R2") # loaned to another reader
    
    reader = ReaderEntity("R1", "Alice")
    
    repo.save_book(book)
    repo.save_reader(reader)
    
    use_case = CheckoutUseCase(repository=repo, config_provider=config)
    
    # Act & Assert
    with pytest.raises(DomainError, match="Book is not available for loan"):
        use_case.execute(reader_id="R1", book_id="B1", checkout_date=date(2026, 6, 12))


def test_checkout_book_reserved_for_other() -> None:
    # Arrange
    repo = FakeLibraryRepository()
    config = FakeConfigProvider()
    
    book = BookEntity("B1", "DDD")
    book.loan_to("R3")
    book.reserve("R2") # reserved for reader R2
    book.return_book() # now in reserved status
    
    reader = ReaderEntity("R1", "Alice")
    
    repo.save_book(book)
    repo.save_reader(reader)
    
    use_case = CheckoutUseCase(repository=repo, config_provider=config)
    
    # Act & Assert
    with pytest.raises(DomainError, match="Book is reserved for another reader"):
        use_case.execute(reader_id="R1", book_id="B1", checkout_date=date(2026, 6, 12))


def test_checkout_book_reserved_for_self() -> None:
    # Arrange
    repo = FakeLibraryRepository()
    config = FakeConfigProvider()
    
    book = BookEntity("B1", "DDD")
    book.loan_to("R3")
    book.reserve("R1") # reserved for R1
    book.return_book() # now in reserved status
    
    reader = ReaderEntity("R1", "Alice")
    
    repo.save_book(book)
    repo.save_reader(reader)
    
    use_case = CheckoutUseCase(repository=repo, config_provider=config)
    
    # Act
    loan = use_case.execute(reader_id="R1", book_id="B1", checkout_date=date(2026, 6, 12))
    
    # Assert
    assert loan is not None
    assert loan.book_id == "B1"
    assert loan.reader_id == "R1"
    assert book.status == "Loaned"
    assert book.hold_queue == []
