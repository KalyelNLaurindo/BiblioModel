import uuid
from datetime import date, timedelta
from src.domain.entities import LoanEntity, DomainError
from src.app.ports import ILibraryRepository, IConfigProvider, ICheckoutUseCase

class CheckoutUseCase(ICheckoutUseCase):
    """
    Coordinates domain objects to execute book loans.
    """

    def __init__(self, repository: ILibraryRepository, config_provider: IConfigProvider) -> None:
        self.repository = repository
        self.config_provider = config_provider

    def execute(self, reader_id: str, book_id: str, checkout_date: date) -> LoanEntity:
        # Retrieve reader and book from the repository
        reader = self.repository.get_reader(reader_id)
        if not reader:
            raise DomainError("Reader not found")

        book = self.repository.get_book(book_id)
        if not book:
            raise DomainError("Book not found")

        # Update reader's status based on overdue loans and fines
        reader.update_status(checkout_date)

        # Validate reader eligibility
        if reader.status == "Suspended":
            raise DomainError("Reader is suspended")

        # Validate reader limit
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

        # Persist updated states
        self.repository.save_book(book)
        self.repository.save_reader(reader)
        self.repository.save_loan(loan)

        return loan
