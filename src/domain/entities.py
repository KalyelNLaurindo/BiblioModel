from datetime import date
from typing import Optional, List


class DomainError(Exception):
    """
    Exception raised for domain invariant violations. Keep domain isolated from external systems.
    """
    pass


class ReaderAutoSuspendedError(DomainError):
    """
    Exception raised when a reader is auto-suspended due to critical book return delays.
    """
    pass


class BookEntity:
    """
    Represents a physical book. Manages availability states and a FIFO reservation queue.
    """

    def __init__(
        self,
        book_id: str,
        title: str,
        status: str = "Available",
        hold_queue: list[str] = None,
        author: str = "",
        checkout_count: int = 0
    ) -> None:
        self.book_id = book_id
        self.title = title
        self.status = status
        self.hold_queue = hold_queue if hold_queue is not None else []
        self.author = author
        self.checkout_count = checkout_count

    def reserve(self, reader_id: str) -> None:
        """
        Pushes a reader to the FIFO queue. Transitions status to Reserved.
        """
        if reader_id not in self.hold_queue:
            self.hold_queue.append(reader_id)
        self.status = "Reserved"

    def loan_to(self, reader_id: str) -> None:
        """
        Assigns the book to a reader. Enforces FIFO reservations and status constraints.
        """
        if self.status not in ("Available", "Reserved"):
            raise DomainError("Book is not available for loan")

        if self.hold_queue:
            if self.hold_queue[0] != reader_id:
                raise DomainError("Book is reserved for another reader")
            self.hold_queue.pop(0)

        self.status = "Loaned"

    def return_book(self) -> None:
        """
        Handles book return. Retains Reserved status if queue is not empty, else Available.
        """
        if self.hold_queue:
            self.status = "Reserved"
        else:
            self.status = "Available"


class LoanEntity:
    """
    Represents a loan transaction. Serves as a read-only audit log of a borrowing event.
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
        Determines if the loan is late relative to the current date.
        """
        if self.return_date is not None:
            return False
        return current_date > self.due_date


class ReaderEntity:
    """
    Represents a library reader. Controls borrow eligibility based on outstanding fines and late items.
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
        Associates an active loan with the reader.
        """
        self.active_loans.append(loan)

    def return_loan(self, book_id: str, return_date: date) -> None:
        """
        Marks an active loan as returned and removes it from active list.
        """
        for loan in self.active_loans:
            if loan.book_id == book_id and loan.return_date is None:
                loan.return_date = return_date
                self.active_loans.remove(loan)
                break

    def apply_fine(self, amount: float) -> None:
        """
        Increases reader's fine balance.
        """
        self.fine_balance += amount

    def pay_fine(self, amount: float) -> None:
        """
        Reduces reader's fine balance (cannot go below 0).
        """
        self.fine_balance -= amount
        if self.fine_balance < 0.0:
            self.fine_balance = 0.0

    def waive_fine(self) -> None:
        """
        Clears all outstanding fines.
        """
        self.fine_balance = 0.0

    def update_status(self, current_date: date, auto_suspend_overdue_days: int = 0) -> None:
        """
        Suspends the reader if they have unpaid fines or overdue loans beyond policy threshold.
        """
        if auto_suspend_overdue_days > 0:
            has_overdue = any(
                loan.return_date is None and (current_date - loan.due_date).days >= auto_suspend_overdue_days
                for loan in self.active_loans
            )
        else:
            has_overdue = any(loan.is_overdue(current_date) for loan in self.active_loans)
            
        if self.fine_balance > 0.0 or has_overdue:
            self.status = "Suspended"
        else:
            self.status = "Active"

