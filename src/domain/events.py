from abc import ABC
from datetime import datetime, date
from typing import Callable, Dict, List, Type, Any, Optional, Set

class DomainEvent(ABC):
    """
    Base abstraction for all domain events.
    Records the date/time when the business event occurred to maintain a clear timeline.
    """
    def __init__(self) -> None:
        self.occurred_on = datetime.utcnow()


class BookCheckedOutEvent(DomainEvent):
    """
    Emitted when a reader borrows a book, establishing a loan transaction contract.
    """
    def __init__(
        self,
        loan_id: str,
        book_id: str,
        reader_id: str,
        checkout_date: date,
        due_date: date
    ) -> None:
        super().__init__()
        self.loan_id = loan_id
        self.book_id = book_id
        self.reader_id = reader_id
        self.checkout_date = checkout_date
        self.due_date = due_date


class BookReturnedEvent(DomainEvent):
    """
    Emitted when a book is returned, triggering potential calculations for late fees
    and updating the active status of the reader.
    """
    def __init__(
        self,
        loan: Any,
        book_title: str,
        return_date: date,
        fine_amount: float,
        original_fine: float,
        applied_rules: List[str],
        operator: str,
        final_status: str,
        delay_days: int
    ) -> None:
        super().__init__()
        self.loan = loan
        self.book_title = book_title
        self.return_date = return_date
        self.fine_amount = fine_amount
        self.original_fine = original_fine
        self.applied_rules = applied_rules
        self.operator = operator
        self.final_status = final_status
        self.delay_days = delay_days

    @property
    def loan_id(self) -> str:
        return self.loan.loan_id

    @property
    def book_id(self) -> str:
        return self.loan.book_id

    @property
    def reader_id(self) -> str:
        return self.loan.reader_id



class EventDispatcher:
    """
    In-memory pub/sub engine that routes domain events to their registered side-effect listeners.
    Ensures that domain state mutations remain decoupled from peripheral side-effects.
    """
    def __init__(self) -> None:
        self._listeners: Dict[Type[DomainEvent], List[Callable[[Any], None]]] = {}

    def register(self, event_type: Type[DomainEvent], listener: Callable[[Any], None]) -> None:
        """
        Subscribes a side-effect callback to receive updates whenever a matching event occurs.
        """
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(listener)

    def dispatch(self, event: DomainEvent) -> None:
        """
        Broadcasts the domain event to all interested subscribers.
        """
        event_type = type(event)
        if event_type in self._listeners:
            for listener in self._listeners[event_type]:
                listener(event)
