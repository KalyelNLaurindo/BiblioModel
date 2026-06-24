import os
import tempfile
import json
import pytest
from datetime import date
from src.domain.entities import BookEntity, ReaderEntity, LoanEntity, DomainError
from src.infra.adapters import JSONPersistenceAdapter

def test_save_and_load_lifecycle() -> None:
    # Arrange: use a temporary file path
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp:
        tmp_path = tmp.name

    try:
        # Initialize empty repository
        repo = JSONPersistenceAdapter(tmp_path)
        
        # Create entities
        book = BookEntity("B1", "Domain-Driven Design")
        reader = ReaderEntity("R1", "Alice")
        loan = LoanEntity("L1", "B1", "R1", date(2026, 6, 10), date(2026, 6, 17))
        reader.add_loan(loan)
        
        # Save entities
        repo.save_book(book)
        repo.save_reader(reader)
        repo.save_loan(loan)
        
        # Act: Instantiate another adapter referencing the same file to simulate reload
        new_repo = JSONPersistenceAdapter(tmp_path)
        
        # Assert: verify state restoration
        loaded_book = new_repo.get_book("B1")
        assert loaded_book is not None
        assert loaded_book.title == "Domain-Driven Design"
        assert loaded_book.status == "Available"
        
        loaded_reader = new_repo.get_reader("R1")
        assert loaded_reader is not None
        assert loaded_reader.name == "Alice"
        assert len(loaded_reader.active_loans) == 1
        
        loaded_loan = loaded_reader.active_loans[0]
        assert loaded_loan.loan_id == "L1"
        assert loaded_loan.book_id == "B1"
        assert loaded_loan.reader_id == "R1"
        assert loaded_loan.checkout_date == date(2026, 6, 10)
        assert loaded_loan.due_date == date(2026, 6, 17)
        assert loaded_loan.return_date is None
        assert loaded_loan.fine_amount == 0.0
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        bak_path = tmp_path + ".bak"
        if os.path.exists(bak_path):
            os.remove(bak_path)


def test_atomic_write_rotation() -> None:
    # Arrange
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp:
        tmp_path = tmp.name

    try:
        repo = JSONPersistenceAdapter(tmp_path)
        
        # Save first book
        book1 = BookEntity("B1", "Book 1")
        repo.save_book(book1)
        
        # At this point, tmp_path contains book1. bak doesn't exist or is empty
        bak_path = tmp_path + ".bak"
        assert os.path.exists(tmp_path)
        
        # Save second book -> triggers atomic write and rotates primary to .bak
        book2 = BookEntity("B2", "Book 2")
        repo.save_book(book2)
        
        # Assert: primary contains B1 and B2, bak contains B1 only
        assert os.path.exists(bak_path)
        
        # Load from primary
        repo_primary = JSONPersistenceAdapter(tmp_path)
        assert repo_primary.get_book("B1") is not None
        assert repo_primary.get_book("B2") is not None
        
        # Load from bak
        repo_bak = JSONPersistenceAdapter(bak_path)
        assert repo_bak.get_book("B1") is not None
        assert repo_bak.get_book("B2") is None
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        bak_path = tmp_path + ".bak"
        if os.path.exists(bak_path):
            os.remove(bak_path)


def test_recovery_from_corrupted_json(caplog) -> None:
    # Arrange
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp:
        tmp_path = tmp.name
    bak_path = tmp_path + ".bak"

    try:
        # Create a valid backup file (.bak)
        repo = JSONPersistenceAdapter(bak_path)
        book = BookEntity("B1", "Backup Title")
        repo.save_book(book)
        
        # Create a corrupted primary file (.json) with invalid JSON syntax
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write("invalid json { content")
            
        # Act: Instantiating the adapter should detect the corruption in primary,
        # fallback to read from .bak, and rewrite/heal the primary file.
        healed_repo = JSONPersistenceAdapter(tmp_path)
        
        # Assert
        loaded_book = healed_repo.get_book("B1")
        assert loaded_book is not None
        assert loaded_book.title == "Backup Title"
        
        # Verify that primary file was healed (contains valid JSON now)
        with open(tmp_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            assert "books" in data
            assert "B1" in data["books"]

        # Verify warning logs were produced
        warnings = [record.message for record in caplog.records if record.levelname == "WARNING"]
        assert any("corrupted" in w.lower() for w in warnings)
        assert any("successful" in w.lower() or "restored" in w.lower() for w in warnings)

        # Verify that the backup file is still valid and not replaced by corrupted data
        with open(bak_path, "r", encoding="utf-8") as f:
            bak_data = json.load(f)
            assert "books" in bak_data
            assert "B1" in bak_data["books"]
            assert bak_data["books"]["B1"]["title"] == "Backup Title"
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        if os.path.exists(bak_path):
            os.remove(bak_path)



def test_schema_validation_boot_failure() -> None:
    # Arrange: both primary and backup files are corrupted
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp:
        tmp_path = tmp.name
    bak_path = tmp_path + ".bak"

    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write("{ invalid json")
        with open(bak_path, "w", encoding="utf-8") as f:
            f.write("invalid backup")
            
        # Act & Assert: should raise DomainError due to corrupted database and failed recovery
        with pytest.raises(DomainError, match="Database file is corrupted and recovery failed"):
            JSONPersistenceAdapter(tmp_path)
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        if os.path.exists(bak_path):
            os.remove(bak_path)


def test_recovery_when_primary_empty_but_backup_valid() -> None:
    # Arrange
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp:
        tmp_path = tmp.name
    bak_path = tmp_path + ".bak"

    try:
        # Create a valid backup file (.bak)
        repo = JSONPersistenceAdapter(bak_path)
        book = BookEntity("B1", "Backup Title")
        repo.save_book(book)

        # Create an empty primary file (size 0)
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write("")

        # Act: Instantiating should trigger self-healing recovery from backup
        healed_repo = JSONPersistenceAdapter(tmp_path)

        # Assert
        loaded_book = healed_repo.get_book("B1")
        assert loaded_book is not None
        assert loaded_book.title == "Backup Title"
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        if os.path.exists(bak_path):
            os.remove(bak_path)


def test_persistence_blocked_by_os_permission(monkeypatch) -> None:
    # Arrange
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp:
        tmp_path = tmp.name

    try:
        repo = JSONPersistenceAdapter(tmp_path)
        book = BookEntity("B1", "Title 1")
        
        # Mock os.replace to raise PermissionError
        def mock_replace(src, dst):
            raise PermissionError("Access denied")
        monkeypatch.setattr(os, "replace", mock_replace)

        # Act & Assert: Should raise DomainError on save
        with pytest.raises(DomainError, match="Failed to persist state database to disk"):
            repo.save_book(book)

        # Temp file should be cleaned up
        tmp_file_path = tmp_path + ".tmp"
        assert not os.path.exists(tmp_file_path)
    finally:
        # Restore mock to avoid issues cleaning up
        monkeypatch.undo()
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def test_atomic_write_failure_mid_operation(monkeypatch) -> None:
    # Arrange
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp:
        tmp_path = tmp.name
    bak_path = tmp_path + ".bak"

    try:
        repo = JSONPersistenceAdapter(tmp_path)
        book1 = BookEntity("B1", "Book 1")
        repo.save_book(book1)

        # Ensure primary contains B1 and read its content
        assert os.path.exists(tmp_path)
        with open(tmp_path, "r", encoding="utf-8") as f:
            primary_content_before = f.read()

        # Mock second os.replace to fail, but let the first one (rotation) succeed
        original_replace = os.replace
        calls = []
        def mock_replace(src, dst):
            calls.append((src, dst))
            if dst == tmp_path:
                raise OSError("Disk full / Write failed mid-operation")
            original_replace(src, dst)

        monkeypatch.setattr(os, "replace", mock_replace)

        book2 = BookEntity("B2", "Book 2")
        with pytest.raises(DomainError, match="Failed to persist state database to disk"):
            repo.save_book(book2)

        # The backup file (.bak) should match the primary state before the failure (B1)
        assert os.path.exists(bak_path)
        with open(bak_path, "r", encoding="utf-8") as f:
            bak_content_after = f.read()
        assert primary_content_before == bak_content_after
    finally:
        monkeypatch.undo()
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        if os.path.exists(bak_path):
            os.remove(bak_path)

