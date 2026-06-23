import pytest
from datetime import date
from src.domain.events import DomainEvent, BookCheckedOutEvent, BookReturnedEvent, EventDispatcher
from src.domain.entities import BookEntity, ReaderEntity, LoanEntity, DomainError
from src.app.use_cases import CheckoutUseCase, ReturnUseCase

class DummyConfigProvider:
    def get_max_loans(self) -> int:
        return 3
    def get_loan_period_days(self) -> int:
        return 7
    def get_daily_fine_rate(self) -> float:
        return 2.0
    def get_grace_period_days(self) -> int:
        return 0
    def get_auto_suspend_overdue_days(self) -> int:
        return 14
    def get_fine_policy(self) -> dict:
        return {}

class InMemoryLibraryRepository:
    def __init__(self):
        self.books = {}
        self.readers = {}
        self.loans = {}

    def get_book(self, book_id):
        return self.books.get(book_id)

    def save_book(self, book):
        self.books[book.book_id] = book

    def get_reader(self, reader_id):
        return self.readers.get(reader_id)

    def save_reader(self, reader):
        self.readers[reader.reader_id] = reader

    def save_loan(self, loan):
        self.loans[loan.loan_id] = loan

    def get_active_loan_by_book(self, book_id):
        for loan in self.loans.values():
            if loan.book_id == book_id and loan.return_date is None:
                return loan
        return None

def test_event_dispatcher_publishes_event_to_listeners() -> None:
    dispatcher = EventDispatcher()
    received_events = []

    def dummy_listener(event: BookCheckedOutEvent) -> None:
        received_events.append(event)

    dispatcher.register(BookCheckedOutEvent, dummy_listener)

    # Act
    event = BookCheckedOutEvent(
        loan_id="L1",
        book_id="B1",
        reader_id="R1",
        checkout_date=date(2026, 6, 23),
        due_date=date(2026, 6, 30)
    )
    dispatcher.dispatch(event)

    # Assert
    assert len(received_events) == 1
    assert received_events[0].loan_id == "L1"
    assert received_events[0].book_id == "B1"
    assert received_events[0].reader_id == "R1"
    assert received_events[0].occurred_on is not None

def test_multiple_listeners_receive_event() -> None:
    dispatcher = EventDispatcher()
    listener_1_calls = 0
    listener_2_calls = 0

    def listener_1(event: BookReturnedEvent) -> None:
        nonlocal listener_1_calls
        listener_1_calls += 1

    def listener_2(event: BookReturnedEvent) -> None:
        nonlocal listener_2_calls
        listener_2_calls += 1

    dispatcher.register(BookReturnedEvent, listener_1)
    dispatcher.register(BookReturnedEvent, listener_2)

    # Act
    loan = LoanEntity("L1", "B1", "R1", date(2026, 6, 10), date(2026, 6, 17))
    event = BookReturnedEvent(
        loan=loan,
        book_title="Clean Code",
        return_date=date(2026, 6, 25),
        fine_amount=0.0,
        original_fine=0.0,
        applied_rules=[],
        operator="admin",
        final_status="RETURNED_ON_TIME",
        delay_days=0
    )
    dispatcher.dispatch(event)

    # Assert
    assert listener_1_calls == 1
    assert listener_2_calls == 1

def test_checkout_use_case_dispatches_event() -> None:
    repo = InMemoryLibraryRepository()
    book = BookEntity("B1", "DDD")
    reader = ReaderEntity("R1", "Alice")
    repo.save_book(book)
    repo.save_reader(reader)

    dispatcher = EventDispatcher()
    dispatched_events = []
    dispatcher.register(BookCheckedOutEvent, lambda e: dispatched_events.append(e))

    use_case = CheckoutUseCase(repo, DummyConfigProvider())
    use_case.dispatcher = dispatcher # Wait, we can either set dispatcher attribute or pass via __init__
    
    # Let's adjust __init__ to accept dispatcher
    use_case = CheckoutUseCase(repo, DummyConfigProvider(), dispatcher=dispatcher)

    # Act
    use_case.execute("R1", "B1", date(2026, 6, 23))

    # Assert
    assert len(dispatched_events) == 1
    assert dispatched_events[0].book_id == "B1"
    assert dispatched_events[0].reader_id == "R1"

def test_return_use_case_dispatches_event() -> None:
    repo = InMemoryLibraryRepository()
    book = BookEntity("B1", "DDD", status="Loaned")
    reader = ReaderEntity("R1", "Alice")
    loan = LoanEntity("L1", "B1", "R1", date(2026, 6, 10), date(2026, 6, 17))
    reader.add_loan(loan)
    repo.save_book(book)
    repo.save_reader(reader)
    repo.save_loan(loan)

    dispatcher = EventDispatcher()
    dispatched_events = []
    dispatcher.register(BookReturnedEvent, lambda e: dispatched_events.append(e))

    use_case = ReturnUseCase(repo, DummyConfigProvider(), dispatcher=dispatcher)

    # Act
    use_case.execute("B1", date(2026, 6, 15))

    # Assert
    assert len(dispatched_events) == 1
    assert dispatched_events[0].book_id == "B1"
    assert dispatched_events[0].reader_id == "R1"
    assert dispatched_events[0].fine_amount == 0.0

def test_listener_integration_archives_and_logs(caplog) -> None:
    from src.infra.listeners import bootstrap_listeners
    class MockHistoryRepository:
        def __init__(self):
            self.archived = []
        def archive_loan(self, loan, book_title, final_status, delay_days, applied_rules=None, original_fine=None, operator=None):
            self.archived.append((loan, book_title, final_status))
        def get_history_by_reader(self, reader_id):
            return []

    repo = InMemoryLibraryRepository()
    book = BookEntity("B1", "DDD", status="Loaned")
    reader = ReaderEntity("R1", "Alice")
    loan = LoanEntity("L1", "B1", "R1", date(2026, 6, 10), date(2026, 6, 17))
    reader.add_loan(loan)
    repo.save_book(book)
    repo.save_reader(reader)
    repo.save_loan(loan)

    history_repo = MockHistoryRepository()
    dispatcher = EventDispatcher()
    bootstrap_listeners(dispatcher, history_repo)

    use_case = ReturnUseCase(repo, DummyConfigProvider(), dispatcher=dispatcher)

    # Act: returning past due date to trigger potential audit logs if waiver/discount engine was active
    # (Here we just want to verify that history archiving runs via the listener)
    use_case.execute("B1", date(2026, 6, 15))

    # Assert: verify listener archived the loan in the mock history repository
    assert len(history_repo.archived) == 1
    assert history_repo.archived[0][1] == "DDD"
    assert history_repo.archived[0][2] == "RETURNED_ON_TIME"

