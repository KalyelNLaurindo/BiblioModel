import os
import tempfile
import pytest
from datetime import date
from src.domain.entities import BookEntity, ReaderEntity, LoanEntity, DomainError
from src.infra.adapters import JSONPersistenceAdapter, JSONUnitOfWorkAdapter
from src.app.use_cases import CheckoutUseCase, ReturnUseCase
from tests.test_persistence import test_save_and_load_lifecycle # placeholder / reference

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

def test_uow_commit_saves_to_disk() -> None:
    # Arrange: use a temporary file path
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp:
        tmp_path = tmp.name

    try:
        repo = JSONPersistenceAdapter(tmp_path)
        # Create UoW
        uow = JSONUnitOfWorkAdapter(repo)

        # Act: make modifications within transaction context
        with uow:
            book = BookEntity("B1", "Atomic Book")
            uow.repository.save_book(book)

            # Assert: at this point, it should not have written to disk yet
            fresh_repo = JSONPersistenceAdapter(tmp_path)
            assert fresh_repo.get_book("B1") is None

        # Assert: after leaving block (successful exit), commit is triggered automatically
        fresh_repo = JSONPersistenceAdapter(tmp_path)
        loaded_book = fresh_repo.get_book("B1")
        assert loaded_book is not None
        assert loaded_book.title == "Atomic Book"

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        bak_path = tmp_path + ".bak"
        if os.path.exists(bak_path):
            os.remove(bak_path)

def test_uow_rollback_on_exception() -> None:
    # Arrange: use a temporary file path
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp:
        tmp_path = tmp.name

    try:
        repo = JSONPersistenceAdapter(tmp_path)
        # Save a book first
        book_orig = BookEntity("B1", "Original Title")
        repo.save_book(book_orig)

        uow = JSONUnitOfWorkAdapter(repo)

        # Act: raise exception inside block
        with pytest.raises(ValueError, match="Simulated Error"):
            with uow:
                book_mod = BookEntity("B1", "Modified Title")
                uow.repository.save_book(book_mod)
                raise ValueError("Simulated Error")

        # Assert: the file must contain the original title, not the modified one
        fresh_repo = JSONPersistenceAdapter(tmp_path)
        loaded_book = fresh_repo.get_book("B1")
        assert loaded_book is not None
        assert loaded_book.title == "Original Title"

        # Assert: repository memory cache is also rolled back
        assert repo.get_book("B1").title == "Original Title"

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        bak_path = tmp_path + ".bak"
        if os.path.exists(bak_path):
            os.remove(bak_path)

def test_checkout_use_case_with_uow_success() -> None:
    # Arrange
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp:
        tmp_path = tmp.name

    try:
        repo = JSONPersistenceAdapter(tmp_path)
        
        # Populate initial entities
        book = BookEntity("B1", "Design Patterns")
        reader = ReaderEntity("R1", "Bob")
        repo.save_book(book)
        repo.save_reader(reader)

        uow = JSONUnitOfWorkAdapter(repo)
        config = DummyConfigProvider()
        
        # Instantiate use case under test
        use_case = CheckoutUseCase(uow, config)
        
        # Act
        loan = use_case.execute("R1", "B1", date(2026, 6, 23))
        
        # Assert: check in-memory state
        assert loan.book_id == "B1"
        assert loan.reader_id == "R1"
        
        # Assert: verify it was successfully persisted on disk
        fresh_repo = JSONPersistenceAdapter(tmp_path)
        assert fresh_repo.get_active_loan_by_book("B1") is not None
        
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        bak_path = tmp_path + ".bak"
        if os.path.exists(bak_path):
            os.remove(bak_path)

def test_checkout_use_case_with_uow_rollback_on_failure() -> None:
    # Arrange
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp:
        tmp_path = tmp.name

    try:
        repo = JSONPersistenceAdapter(tmp_path)
        
        # Populate initial entities (but Reader R1 is missing)
        book = BookEntity("B1", "Design Patterns")
        repo.save_book(book)

        uow = JSONUnitOfWorkAdapter(repo)
        config = DummyConfigProvider()
        use_case = CheckoutUseCase(uow, config)
        
        # Act & Assert: Checkout fails due to missing reader
        with pytest.raises(DomainError, match="Reader not found"):
            use_case.execute("R999", "B1", date(2026, 6, 23))
        
        # Assert: check that book is still available (status not modified in disk)
        fresh_repo = JSONPersistenceAdapter(tmp_path)
        loaded_book = fresh_repo.get_book("B1")
        assert loaded_book.status == "Available"
        
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        bak_path = tmp_path + ".bak"
        if os.path.exists(bak_path):
            os.remove(bak_path)

def test_return_use_case_with_uow_success() -> None:
    # Arrange
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp:
        tmp_path = tmp.name

    try:
        repo = JSONPersistenceAdapter(tmp_path)
        
        # Populate initial entities
        book = BookEntity("B1", "Refactoring", status="Loaned")
        reader = ReaderEntity("R1", "Alice")
        loan = LoanEntity("L1", "B1", "R1", date(2026, 6, 10), date(2026, 6, 17))
        reader.add_loan(loan)
        
        repo.save_book(book)
        repo.save_reader(reader)
        repo.save_loan(loan)

        uow = JSONUnitOfWorkAdapter(repo)
        config = DummyConfigProvider()
        use_case = ReturnUseCase(uow, config)
        
        # Act
        returned_loan = use_case.execute("B1", date(2026, 6, 15))
        
        # Assert
        assert returned_loan.return_date == date(2026, 6, 15)
        
        # Assert: verify it was successfully persisted on disk
        fresh_repo = JSONPersistenceAdapter(tmp_path)
        assert fresh_repo.get_active_loan_by_book("B1") is None
        assert fresh_repo.get_book("B1").status == "Available"
        
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        bak_path = tmp_path + ".bak"
        if os.path.exists(bak_path):
            os.remove(bak_path)

