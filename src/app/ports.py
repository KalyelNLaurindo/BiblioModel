from abc import ABC, abstractmethod
from datetime import date
from typing import Optional
from src.domain.entities import BookEntity, ReaderEntity, LoanEntity

class IConfigProvider(ABC):
    """
    Port defining configuration retrieval methods for the library business rules.
    """

    @abstractmethod
    def get_max_loans(self) -> int:
        """
        Returns the maximum number of books a reader can borrow at the same time.
        """
        pass

    @abstractmethod
    def get_loan_period_days(self) -> int:
        """
        Returns the default loan duration in days.
        """
        pass

    @abstractmethod
    def get_daily_fine_rate(self) -> float:
        """
        Returns the daily fine rate amount for overdue books.
        """
        pass

    @abstractmethod
    def get_grace_period_days(self) -> int:
        """
        Returns the grace period in days before fines start accumulating.
        """
        pass


class ILibraryRepository(ABC):
    """
    Outbound port defining database/persistence operations for library entities.
    """

    @abstractmethod
    def get_book(self, book_id: str) -> Optional[BookEntity]:
        """
        Retrieves a book by its unique ID.
        """
        pass

    @abstractmethod
    def save_book(self, book: BookEntity) -> None:
        """
        Saves or updates a book's state in the repository.
        """
        pass

    @abstractmethod
    def get_reader(self, reader_id: str) -> Optional[ReaderEntity]:
        """
        Retrieves a reader by their unique ID.
        """
        pass

    @abstractmethod
    def save_reader(self, reader: ReaderEntity) -> None:
        """
        Saves or updates a reader's state in the repository.
        """
        pass

    @abstractmethod
    def save_loan(self, loan: LoanEntity) -> None:
        """
        Saves or updates a loan transaction in the repository.
        """
        pass

    @abstractmethod
    def get_active_loan_by_book(self, book_id: str) -> Optional[LoanEntity]:
        """
        Retrieves the single active loan associated with the book (where return_date is None).
        """
        pass


class ICheckoutUseCase(ABC):
    """
    Inbound port defining the checkout/loan execution use case.
    """

    @abstractmethod
    def execute(self, reader_id: str, book_id: str, checkout_date: date) -> LoanEntity:
        """
        Executes the book loan process for a given reader.
        """
        pass


class IReturnUseCase(ABC):
    """
    Inbound port defining the book return execution use case.
    """

    @abstractmethod
    def execute(self, book_id: str, return_date: date) -> LoanEntity:
        """
        Executes the book return process.
        """
        pass


class IReserveUseCase(ABC):
    """
    Inbound port defining the book reservation execution use case.
    """

    @abstractmethod
    def execute(self, reader_id: str, book_id: str) -> BookEntity:
        """
        Executes the book reservation process.
        """
        pass



