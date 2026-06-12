import uuid
from datetime import date, timedelta
from src.domain.entities import LoanEntity, BookEntity, ReaderEntity, DomainError
from src.domain.services import FineCalculator
from src.app.ports import ILibraryRepository, IConfigProvider, ICheckoutUseCase, IReturnUseCase, IReserveUseCase, IWaiveFineUseCase, IGenerateReportUseCase
from src.app.validators import InputValidator

class CheckoutUseCase(ICheckoutUseCase):
    """
    Coordinates domain objects to execute book loans.
    Implements ICheckoutUseCase port to enforce book checkout business logic.
    """

    def __init__(self, repository: ILibraryRepository, config_provider: IConfigProvider) -> None:
        """
        Initializes the use case with required repository and configuration provider.
        """
        self.repository = repository
        self.config_provider = config_provider

    def execute(self, reader_id: str, book_id: str, checkout_date: date) -> LoanEntity:
        """
        Executes the book checkout process for a reader on a specific date.
        Validates reader eligibility, loan limits, and book availability.
        Returns the created LoanEntity if successful, or raises DomainError on violation.
        """
        reader_id = InputValidator.sanitize_and_validate_reader_id(reader_id)
        book_id = InputValidator.sanitize_and_validate_book_id(book_id)

        # Retrieve reader and book from the repository
        reader = self.repository.get_reader(reader_id)
        if not reader:
            raise DomainError("Reader not found")

        book = self.repository.get_book(book_id)
        if not book:
            raise DomainError("Book not found")

        # Update reader's status based on overdue loans and fines
        reader.update_status(checkout_date)

        # Validate reader eligibility (cannot borrow if suspended)
        if reader.status == "Suspended":
            raise DomainError("Reader is suspended")

        # Validate reader limit (cannot borrow if maximum allowed loans is reached)
        max_loans = self.config_provider.get_max_loans()
        if len(reader.active_loans) >= max_loans:
            raise DomainError("Reader active loans limit reached")

        # Check book status/reservations and transition book state to "Loaned"
        book.loan_to(reader_id)

        # Create new loan entity with a generated UUID
        loan_id = str(uuid.uuid4())
        loan_days = self.config_provider.get_loan_period_days()
        due_date = checkout_date + timedelta(days=loan_days)

        loan = LoanEntity(
            loan_id=loan_id,
            book_id=book_id,
            reader_id=reader_id,
            checkout_date=checkout_date,
            due_date=due_date
        )

        # Associate loan with the reader
        reader.add_loan(loan)

        # Persist updated states to the repository
        self.repository.save_book(book)
        self.repository.save_reader(reader)
        self.repository.save_loan(loan)

        return loan


class ReturnUseCase(IReturnUseCase):
    """
    Coordinates domain objects to execute book returns and calculate late fines.
    Implements IReturnUseCase port to enforce book return and penalty calculations.
    """

    def __init__(self, repository: ILibraryRepository, config_provider: IConfigProvider) -> None:
        """
        Initializes the use case with required repository and configuration provider.
        """
        self.repository = repository
        self.config_provider = config_provider

    def execute(self, book_id: str, return_date: date) -> LoanEntity:
        """
        Executes the return process for a given book.
        Locates the active loan, calculates any applicable late return fines,
        updates the reader's state (suspending them if fines are accrued),
        updates the book's availability, and saves all changes.
        """
        book_id = InputValidator.sanitize_and_validate_book_id(book_id)

        # Retrieve book from repository
        book = self.repository.get_book(book_id)
        if not book:
            raise DomainError("Book not found")

        # Retrieve active loan for this book (where return_date is None)
        loan = self.repository.get_active_loan_by_book(book_id)
        if not loan:
            raise DomainError("No active loan found for this book")

        # Validate return date (cannot be before checkout date)
        if return_date < loan.checkout_date:
            raise DomainError("Return date cannot be before checkout date")

        # Retrieve reader associated with the active loan
        reader = self.repository.get_reader(loan.reader_id)
        if not reader:
            raise DomainError("Reader not found")

        # Calculate late fine using FineCalculator domain service
        calculator = FineCalculator()
        daily_rate = self.config_provider.get_daily_fine_rate()
        grace_period = self.config_provider.get_grace_period_days()

        fine = calculator.calculate_fine(
            due_date=loan.due_date,
            return_date=return_date,
            daily_rate=daily_rate,
            grace_period_days=grace_period
        )

        # Apply fine to reader and transaction if fine > 0
        if fine > 0.0:
            reader.apply_fine(fine)
            loan.fine_amount = fine

        # Perform return transitions in entities (updates loan fields and book state)
        reader.return_loan(book_id, return_date)
        book.return_book()

        # Update reader's suspension status immediately based on the return transaction
        reader.update_status(return_date)

        # Persist updated states to repository
        self.repository.save_book(book)
        self.repository.save_reader(reader)
        self.repository.save_loan(loan)

        return loan


class ReserveUseCase(IReserveUseCase):
    """
    Coordinates domain objects to execute book reservations.
    Implements IReserveUseCase port.
    """

    def __init__(self, repository: ILibraryRepository) -> None:
        """
        Initializes the use case with required repository.
        """
        self.repository = repository

    def execute(self, reader_id: str, book_id: str) -> BookEntity:
        """
        Executes the reservation of a book for a given reader.
        Ensures book is not available (must be checked out),
        reader doesn't already hold the book, and reader hasn't already reserved it.
        """
        reader_id = InputValidator.sanitize_and_validate_reader_id(reader_id)
        book_id = InputValidator.sanitize_and_validate_book_id(book_id)

        # Retrieve book from repository
        book = self.repository.get_book(book_id)
        if not book:
            raise DomainError("Book not found")

        # Retrieve reader
        reader = self.repository.get_reader(reader_id)
        if not reader:
            raise DomainError("Reader not found")

        # Validate book status (only currently unavailable/loaned/reserved books can be reserved)
        if book.status == "Available":
            raise DomainError("Book is available and can be checked out directly")

        # Verify if the reader is the current active borrower of this book
        active_loan = self.repository.get_active_loan_by_book(book_id)
        if active_loan and active_loan.reader_id == reader_id:
            raise DomainError("Reader cannot reserve a book they currently hold")

        # Verify if reader already reserved this book (redundant reservation hold)
        if reader_id in book.hold_queue:
            raise DomainError("Reader has already reserved this book")

        # Perform reservation on domain model
        book.reserve(reader_id)

        # Save states
        self.repository.save_book(book)

        return book


class WaiveFineUseCase(IWaiveFineUseCase):
    """
    Coordinates domain objects to waive all fines for a reader.
    Implements IWaiveFineUseCase port.
    """

    def __init__(self, repository: ILibraryRepository) -> None:
        self.repository = repository

    def execute(self, reader_id: str) -> ReaderEntity:
        reader_id = InputValidator.sanitize_and_validate_reader_id(reader_id)
        reader = self.repository.get_reader(reader_id)
        if not reader:
            raise DomainError("Reader not found")

        reader.waive_fine()
        reader.update_status(date.today())
        self.repository.save_reader(reader)
        return reader


class GenerateReportUseCase(IGenerateReportUseCase):
    """
    Coordinates retrieval of library status statistics.
    Implements IGenerateReportUseCase port.
    """

    def __init__(self, repository: ILibraryRepository) -> None:
        self.repository = repository

    def execute(self) -> dict:
        books = self.repository.list_books()
        readers = self.repository.list_readers()
        loans = self.repository.list_loans()

        today = date.today()
        
        # Calculate active loans count
        active_loans = [loan for loan in loans if loan.return_date is None]
        total_active_loans = len(active_loans)

        # Calculate overdue books
        overdue_books = [loan for loan in active_loans if loan.is_overdue(today)]
        total_overdue = len(overdue_books)

        # Calculate unpaid fees
        total_unpaid_fees = sum(reader.fine_balance for reader in readers)

        # Queue statistics
        reserved_books = [book for book in books if book.status == "Reserved" or len(book.hold_queue) > 0]
        total_reservations = sum(len(book.hold_queue) for book in books)

        return {
            "total_active_loans": total_active_loans,
            "total_overdue": total_overdue,
            "total_unpaid_fees": total_unpaid_fees,
            "total_reservations": total_reservations,
            "reserved_books_count": len(reserved_books)
        }

