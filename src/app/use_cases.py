import uuid
from datetime import date, timedelta
from src.domain.entities import LoanEntity, BookEntity, ReaderEntity, DomainError, ReaderAutoSuspendedError
from src.domain.services import FineCalculator
from src.app.ports import ILibraryRepository, IConfigProvider, ICheckoutUseCase, IReturnUseCase, IReserveUseCase, IWaiveFineUseCase, IGenerateReportUseCase, ILoanHistoryRepository
from src.app.validators import InputValidator

class CheckoutUseCase(ICheckoutUseCase):
    """
    Orchestrates domain objects to execute book loans.
    """

    def __init__(self, repository: ILibraryRepository, config_provider: IConfigProvider) -> None:
        self.repository = repository
        self.config_provider = config_provider

    def execute(self, reader_id: str, book_id: str, checkout_date: date) -> LoanEntity:
        """
        Executes book loan. Enforces reader status, borrow limits, and book availability invariants.
        """
        reader_id = InputValidator.sanitize_and_validate_reader_id(reader_id)
        book_id = InputValidator.sanitize_and_validate_book_id(book_id)

        reader = self.repository.get_reader(reader_id)
        if not reader:
            raise DomainError("Reader not found")

        book = self.repository.get_book(book_id)
        if not book:
            raise DomainError("Book not found")

        auto_suspend_days = self.config_provider.get_auto_suspend_overdue_days()
        has_critical_overdue = any(
            loan.return_date is None and (checkout_date - loan.due_date).days >= auto_suspend_days
            for loan in reader.active_loans
        )
        if has_critical_overdue:
            raise ReaderAutoSuspendedError("Reader has critical overdue loans and is auto-suspended")

        reader.update_status(checkout_date, auto_suspend_days)

        if reader.status == "Suspended":
            raise DomainError("Reader is suspended")

        max_loans = self.config_provider.get_max_loans()
        if len(reader.active_loans) >= max_loans:
            raise DomainError("Reader active loans limit reached")

        book.loan_to(reader_id)

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

        reader.add_loan(loan)

        self.repository.save_book(book)
        self.repository.save_reader(reader)
        self.repository.save_loan(loan)

        return loan


class ReturnUseCase(IReturnUseCase):
    """
    Orchestrates domain objects to process book returns and calculate late fee penalties.
    """

    def __init__(self, repository: ILibraryRepository, config_provider: IConfigProvider, history_repository: ILoanHistoryRepository = None) -> None:
        self.repository = repository
        self.config_provider = config_provider
        self.history_repository = history_repository

    def execute(self, book_id: str, return_date: date) -> LoanEntity:
        """
        Processes book return, calculates late fee via FineCalculator, updates status, and persists.
        """
        book_id = InputValidator.sanitize_and_validate_book_id(book_id)

        book = self.repository.get_book(book_id)
        if not book:
            raise DomainError("Book not found")

        loan = self.repository.get_active_loan_by_book(book_id)
        if not loan:
            raise DomainError("No active loan found for this book")

        if return_date < loan.checkout_date:
            raise DomainError("Return date cannot be before checkout date")

        reader = self.repository.get_reader(loan.reader_id)
        if not reader:
            raise DomainError("Reader not found")

        calculator = FineCalculator()
        daily_rate = self.config_provider.get_daily_fine_rate()
        grace_period = self.config_provider.get_grace_period_days()

        fine = calculator.calculate_fine(
            due_date=loan.due_date,
            return_date=return_date,
            daily_rate=daily_rate,
            grace_period_days=grace_period
        )

        if fine > 0.0:
            reader.apply_fine(fine)
            loan.fine_amount = fine

        reader.return_loan(book_id, return_date)
        book.return_book()

        auto_suspend_days = self.config_provider.get_auto_suspend_overdue_days()
        reader.update_status(return_date, auto_suspend_days)

        if self.history_repository:
            delay_days = (return_date - loan.due_date).days
            if delay_days < 0:
                delay_days = 0
            final_status = "RETURNED_LATE" if delay_days > grace_period else "RETURNED_ON_TIME"
            self.history_repository.archive_loan(loan, book.title, final_status, delay_days)

        self.repository.save_book(book)
        self.repository.save_reader(reader)
        self.repository.save_loan(loan)

        return loan


class ReserveUseCase(IReserveUseCase):
    """
    Orchestrates domain objects to execute book reservations.
    """

    def __init__(self, repository: ILibraryRepository) -> None:
        self.repository = repository

    def execute(self, reader_id: str, book_id: str) -> BookEntity:
        """
        Executes reservation. Ensures book is loaned out, and reader has no current borrow/reservation for it.
        """
        reader_id = InputValidator.sanitize_and_validate_reader_id(reader_id)
        book_id = InputValidator.sanitize_and_validate_book_id(book_id)

        book = self.repository.get_book(book_id)
        if not book:
            raise DomainError("Book not found")

        reader = self.repository.get_reader(reader_id)
        if not reader:
            raise DomainError("Reader not found")

        if book.status == "Available":
            raise DomainError("Book is available and can be checked out directly")

        active_loan = self.repository.get_active_loan_by_book(book_id)
        if active_loan and active_loan.reader_id == reader_id:
            raise DomainError("Reader cannot reserve a book they currently hold")

        if reader_id in book.hold_queue:
            raise DomainError("Reader has already reserved this book")

        book.reserve(reader_id)
        self.repository.save_book(book)

        return book


class WaiveFineUseCase(IWaiveFineUseCase):
    """
    Orchestrates waiving all fine balances for a reader.
    """

    def __init__(self, repository: ILibraryRepository) -> None:
        self.repository = repository

    def execute(self, reader_id: str) -> ReaderEntity:
        """
        Perdons all fines, updates eligibility status, and saves.
        """
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
    Compiles daily status report statistics.
    """

    def __init__(self, repository: ILibraryRepository) -> None:
        self.repository = repository

    def execute(self) -> dict:
        """
        Queries repository lists and builds overview of loans, overdues, fees, and reservations.
        """
        books = self.repository.list_books()
        readers = self.repository.list_readers()
        loans = self.repository.list_loans()

        today = date.today()
        
        active_loans = [loan for loan in loans if loan.return_date is None]
        total_active_loans = len(active_loans)

        overdue_books = [loan for loan in active_loans if loan.is_overdue(today)]
        total_overdue = len(overdue_books)

        total_unpaid_fees = sum(reader.fine_balance for reader in readers)

        reserved_books = [book for book in books if book.status == "Reserved" or len(book.hold_queue) > 0]
        total_reservations = sum(len(book.hold_queue) for book in books)

        return {
            "total_active_loans": total_active_loans,
            "total_overdue": total_overdue,
            "total_unpaid_fees": total_unpaid_fees,
            "total_reservations": total_reservations,
            "reserved_books_count": len(reserved_books)
        }

