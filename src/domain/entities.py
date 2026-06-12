from datetime import date
from typing import Optional, List


class DomainError(Exception):
    """
    Custom exception raised for violations of domain invariants and rules.
    """
    pass


class BookEntity:
    """
    Represents a physical book in the library system.
    Protects domain invariants around availability, loans, and FIFO reservations.
    """

    def __init__(
        self,
        book_id: str,
        title: str,
        status: str = "Available",
        hold_queue: list[str] = None
    ) -> None:
        self.book_id = book_id
        self.title = title
        self.status = status
        self.hold_queue = hold_queue if hold_queue is not None else []

    def reserve(self, reader_id: str) -> None:
        """
        Adds a reader to the first-in-first-out (FIFO) hold queue for this book.
        Transitions the book status to 'Reserved'.
        """
        if reader_id not in self.hold_queue:
            self.hold_queue.append(reader_id)
        self.status = "Reserved"

    def loan_to(self, reader_id: str) -> None:
        """
        Loans the book to a reader.
        Ensures the book is available and not reserved for another reader.
        """
        # A book can only be loaned if it is 'Available' or 'Reserved'
        if self.status not in ("Available", "Reserved"):
            raise DomainError("Book is not available for loan")

        # If there is a hold queue, the reader must be the first person in line
        if self.hold_queue:
            if self.hold_queue[0] != reader_id:
                raise DomainError("Book is reserved for another reader")
            # Remove the reader from the queue since they are borrowing it
            self.hold_queue.pop(0)

        self.status = "Loaned"

    def return_book(self) -> None:
        """
        Handles the return of a book.
        If there are outstanding reservations, sets the status back to 'Reserved'.
        Otherwise, makes the book 'Available'.
        """
        if self.hold_queue:
            self.status = "Reserved"
        else:
            self.status = "Available"


class LoanEntity:
    """
    Represents a loan transaction of a physical book by a reader.
    """

    def __init__(
        self,
        loan_id: str,
        book_id: str,
        reader_id: str,
        checkout_date: date,
        due_date: date,
        return_date: Optional[date] = None,
        fine_amount: float = 0.0
    ) -> None:
        self.loan_id = loan_id
        self.book_id = book_id
        self.reader_id = reader_id
        self.checkout_date = checkout_date
        self.due_date = due_date
        self.return_date = return_date
        self.fine_amount = fine_amount

    def is_overdue(self, current_date: date) -> bool:
        """
        Checks if the loan is overdue relative to a target date.
        """
        if self.return_date is not None:
            return False
        return current_date > self.due_date


class ReaderEntity:
    """
    Represents a library patron / reader.
    Controls borrower eligibility based on late returns and unpaid fines.
    """

    def __init__(
        self,
        reader_id: str,
        name: str,
        status: str = "Active",
        fine_balance: float = 0.0,
        active_loans: Optional[List[LoanEntity]] = None
    ) -> None:
        self.reader_id = reader_id
        self.name = name
        self.status = status
        self.fine_balance = fine_balance
        self.active_loans = active_loans if active_loans is not None else []

    def add_loan(self, loan: LoanEntity) -> None:
        """
        Adds a new active loan to the reader.
        """
        self.active_loans.append(loan)

    def return_loan(self, book_id: str, return_date: date) -> None:
        """
        Returns a loaned book and removes it from active loans.
        """
        for loan in self.active_loans:
            if loan.book_id == book_id and loan.return_date is None:
                loan.return_date = return_date
                self.active_loans.remove(loan)
                break

    def apply_fine(self, amount: float) -> None:
        """
        Applies a monetary fine to the reader.
        """
        self.fine_balance += amount

    def pay_fine(self, amount: float) -> None:
        """
        Pays off/reduces the reader's fine balance.
        """
        self.fine_balance -= amount
        if self.fine_balance < 0.0:
            self.fine_balance = 0.0

    def update_status(self, current_date: date) -> None:
        """
        Transitions the reader's status to Suspended if they have unpaid fines
        or overdue loans. Restores Active status otherwise.
        """
        has_overdue = any(loan.is_overdue(current_date) for loan in self.active_loans)
        if self.fine_balance > 0.0 or has_overdue:
            self.status = "Suspended"
        else:
            self.status = "Active"

