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
