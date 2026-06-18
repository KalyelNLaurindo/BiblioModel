from abc import ABC, abstractmethod
from datetime import date
from typing import Optional, List
from src.domain.entities import BookEntity, ReaderEntity, LoanEntity

class IConfigProvider(ABC):
    """
    Interface/Port defining dynamic library business rules configurations.
    """

    @abstractmethod
    def get_max_loans(self) -> int:
        """
        Max concurrent books a reader can borrow.
        """
        pass

    @abstractmethod
    def get_loan_period_days(self) -> int:
        """
        Default duration of a loan.
        """
        pass

    @abstractmethod
    def get_daily_fine_rate(self) -> float:
        """
        Late fee rate per day.
        """
        pass

    @abstractmethod
    def get_grace_period_days(self) -> int:
        """
        Grace period before fines accumulate.
        """
        pass

    @abstractmethod
    def get_auto_suspend_overdue_days(self) -> int:
        """
        Get policy threshold for automatic reader suspension on overdue books.
        """
        pass


class ILibraryRepository(ABC):
    """
    Outbound port defining persistence operations for library entities.
    """

    @abstractmethod
    def get_book(self, book_id: str) -> Optional[BookEntity]:
        """
        Retrieve a book by ID.
        """
        pass

    @abstractmethod
    def save_book(self, book: BookEntity) -> None:
        """
        Save or update book state.
        """
        pass

    @abstractmethod
    def get_reader(self, reader_id: str) -> Optional[ReaderEntity]:
        """
        Retrieve a reader by ID.
        """
        pass

    @abstractmethod
    def save_reader(self, reader: ReaderEntity) -> None:
        """
        Save or update reader state.
        """
        pass

    @abstractmethod
    def save_loan(self, loan: LoanEntity) -> None:
        """
        Save or update loan transaction.
        """
        pass

    @abstractmethod
    def get_active_loan_by_book(self, book_id: str) -> Optional[LoanEntity]:
        """
        Retrieve active loan for book (where return_date is None).
        """
        pass

    @abstractmethod
    def list_books(self) -> List[BookEntity]:
        """
        List all books.
        """
        pass

    @abstractmethod
    def list_readers(self) -> List[ReaderEntity]:
        """
        List all readers.
        """
        pass

    @abstractmethod
    def list_loans(self) -> List[LoanEntity]:
        """
        List all loans.
        """
        pass

    @abstractmethod
    def search_books(self, query: str) -> List[BookEntity]:
        """
        Search books by partial title or author (case-insensitive).
        """
        pass

    @abstractmethod
    def search_readers(self, query: str) -> List[ReaderEntity]:
        """
        Search readers by partial name (case-insensitive).
        """
        pass


class ICheckoutUseCase(ABC):
    """
    Inbound port for the book loan use case.
    """

    @abstractmethod
    def execute(self, reader_id: str, book_id: str, checkout_date: date) -> LoanEntity:
        """
        Execute loan process.
        """
        pass


class IReturnUseCase(ABC):
    """
    Inbound port for the book return use case.
    """

    @abstractmethod
    def execute(self, book_id: str, return_date: date) -> LoanEntity:
        """
        Execute return process.
        """
        pass


class IReserveUseCase(ABC):
    """
    Inbound port for the book reservation use case.
    """

    @abstractmethod
    def execute(self, reader_id: str, book_id: str) -> BookEntity:
        """
        Execute reservation process.
        """
        pass


class IWaiveFineUseCase(ABC):
    """
    Inbound port for waiving reader fines.
    """

    @abstractmethod
    def execute(self, reader_id: str) -> ReaderEntity:
        """
        Execute fine waiving process.
        """
        pass


class IGenerateReportUseCase(ABC):
    """
    Inbound port for status report generation.
    """

    @abstractmethod
    def execute(self) -> dict:
        """
        Compile daily status report statistics.
        """
        pass


class ILoanHistoryRepository(ABC):
    """
    Outbound port defining persistence operations for closed loan histories.
    """

    @abstractmethod
    def archive_loan(self, loan: LoanEntity, book_title: str, final_status: str, delay_days: int) -> None:
        """
        Archive a returned loan into history.
        """
        pass

    @abstractmethod
    def get_history_by_reader(self, reader_id: str) -> List[dict]:
        """
        Retrieve all archived loan history dictionary records for a reader.
        """
        pass




