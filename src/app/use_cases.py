import uuid
from typing import Optional, Set
from datetime import date, timedelta
from src.domain.entities import LoanEntity, BookEntity, ReaderEntity, DomainError, ReaderAutoSuspendedError
from src.domain.services import FineCalculator
from src.app.ports import ILibraryRepository, IConfigProvider, ICheckoutUseCase, IReturnUseCase, IReserveUseCase, IWaiveFineUseCase, IGenerateReportUseCase, ILoanHistoryRepository, IUnitOfWork
from src.app.validators import InputValidator
from src.domain.events import EventDispatcher, BookCheckedOutEvent, BookReturnedEvent

class CheckoutUseCase(ICheckoutUseCase):
    """
    Orchestrates domain objects to execute book loans.
    """

    def __init__(self, repository: ILibraryRepository, config_provider: IConfigProvider, dispatcher: Optional[EventDispatcher] = None) -> None:
        if isinstance(repository, IUnitOfWork):
            self.uow = repository
            self.repository = repository.repository
        else:
            self.uow = None
            self.repository = repository
        self.config_provider = config_provider
        self.dispatcher = dispatcher

    def execute(self, reader_id: str, book_id: str, checkout_date: date) -> LoanEntity:
        """
        Executes book loan. Enforces reader status, borrow limits, and book availability invariants.
        """
        reader_id = InputValidator.sanitize_and_validate_reader_id(reader_id)
        book_id = InputValidator.sanitize_and_validate_book_id(book_id)

        if self.uow:
            with self.uow:
                return self._execute_transactional(reader_id, book_id, checkout_date)
        return self._execute_transactional(reader_id, book_id, checkout_date)

    def _execute_transactional(self, reader_id: str, book_id: str, checkout_date: date) -> LoanEntity:
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
        book.checkout_count += 1

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

        if self.dispatcher:
            event = BookCheckedOutEvent(
                loan_id=loan.loan_id,
                book_id=book.book_id,
                reader_id=reader.reader_id,
                checkout_date=checkout_date,
                due_date=due_date
            )
            self.dispatcher.dispatch(event)

        return loan


class ReturnUseCase(IReturnUseCase):
    """
    Orchestrates domain objects to process book returns and calculate late fee penalties.
    """

    def __init__(self, repository: ILibraryRepository, config_provider: IConfigProvider, history_repository: ILoanHistoryRepository = None, dispatcher: Optional[EventDispatcher] = None) -> None:
        if isinstance(repository, IUnitOfWork):
            self.uow = repository
            self.repository = repository.repository
        else:
            self.uow = None
            self.repository = repository
        self.config_provider = config_provider
        self.history_repository = history_repository
        self.dispatcher = dispatcher

    def evaluate_return(
        self,
        book_id: str,
        return_date: date,
        system_delay: bool = False,
        book_donation: bool = False
    ) -> tuple[float, list[dict]]:
        """
        Evaluate candidate rules and potential fine amount without modifying any state.
        Returns (gross_fine, applicable_rules).
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

        history_records = []
        if self.history_repository:
            history_records = self.history_repository.get_history_by_reader(reader.reader_id)

        from src.domain.policy import FinePolicyEngine
        policy_engine = FinePolicyEngine(self.config_provider)
        applicable_rules = policy_engine.evaluate_rules(
            fine_amount=fine,
            reader=reader,
            loan=loan,
            history_records=history_records,
            system_delay=system_delay,
            book_donation=book_donation
        )
        return fine, applicable_rules

    def execute(
        self,
        book_id: str,
        return_date: date,
        system_delay: bool = False,
        book_donation: bool = False,
        approved_rules: Optional[set[str]] = None,
        operator: Optional[str] = None
    ) -> LoanEntity:
        """
        Processes book return, calculates late fee via FineCalculator, updates status, and persists.
        """
        book_id = InputValidator.sanitize_and_validate_book_id(book_id)

        if self.uow:
            with self.uow:
                return self._execute_transactional(book_id, return_date, system_delay, book_donation, approved_rules, operator)
        return self._execute_transactional(book_id, return_date, system_delay, book_donation, approved_rules, operator)

    def _execute_transactional(
        self,
        book_id: str,
        return_date: date,
        system_delay: bool = False,
        book_donation: bool = False,
        approved_rules: Optional[set[str]] = None,
        operator: Optional[str] = None
    ) -> LoanEntity:
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

        history_records = []
        if self.history_repository:
            history_records = self.history_repository.get_history_by_reader(reader.reader_id)

        from src.domain.policy import FinePolicyEngine
        policy_engine = FinePolicyEngine(self.config_provider)
        policy_result = policy_engine.apply(
            fine_amount=fine,
            reader=reader,
            loan=loan,
            history_records=history_records,
            system_delay=system_delay,
            book_donation=book_donation,
            approved_rules=approved_rules
        )
        final_fine = policy_result.final_fine

        if fine > 0.0:
            if final_fine > 0.0:
                reader.apply_fine(final_fine)
            loan.fine_amount = final_fine

        # Determine operator context
        if not operator:
            try:
                import os
                operator = os.getlogin()
            except Exception:
                try:
                    import getpass
                    operator = getpass.getuser()
                except Exception:
                    operator = "unknown_operator"

        reader.return_loan(book_id, return_date)
        book.return_book()

        auto_suspend_days = self.config_provider.get_auto_suspend_overdue_days()
        reader.update_status(return_date, auto_suspend_days)

        delay_days = (return_date - loan.due_date).days
        if delay_days < 0:
            delay_days = 0
        final_status = "RETURNED_LATE" if delay_days > grace_period else "RETURNED_ON_TIME"

        applied_rules_list = list(policy_result.applied_rules) if fine > 0.0 else []

        if self.dispatcher:
            event = BookReturnedEvent(
                loan=loan,
                book_title=book.title,
                return_date=return_date,
                fine_amount=final_fine,
                original_fine=fine,
                applied_rules=applied_rules_list,
                operator=operator,
                final_status=final_status,
                delay_days=delay_days
            )
            self.dispatcher.dispatch(event)
        else:
            # Log waiver/discount audit entry if applied
            if fine > 0.0 and final_fine < fine:
                import logging
                logger = logging.getLogger("bibliomodel")
                applied_str = ", ".join(policy_result.applied_rules)
                logger.info(
                    f"AUDIT: Discount/Waiver applied for Reader '{reader.reader_id}' on Loan '{loan.loan_id}'. "
                    f"Rules: [{applied_str}] | Original Fine: ${fine:.2f} | Final Fine: ${final_fine:.2f} | "
                    f"Operator: {operator}"
                )

            if self.history_repository:
                # Save waiver details in the archive record
                applied_rules_list_val = policy_result.applied_rules if fine > 0.0 else None
                orig_fine_val = fine if fine > 0.0 else None
                opt_val = operator if fine > 0.0 else None
                
                self.history_repository.archive_loan(
                    loan,
                    book.title,
                    final_status,
                    delay_days,
                    applied_rules=applied_rules_list_val,
                    original_fine=orig_fine_val,
                    operator=opt_val
                )

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

