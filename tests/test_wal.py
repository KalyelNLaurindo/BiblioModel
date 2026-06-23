import os
import tempfile
import json
import pytest
from datetime import date
from src.domain.entities import BookEntity, ReaderEntity, LoanEntity, DomainError
from src.infra.adapters import JSONPersistenceAdapter

def test_save_appends_to_journal() -> None:
    # Arrange
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp:
        tmp_path = tmp.name
    journal_path = tmp_path + ".journal"

    try:
        # Initialize adapter in transactional mode or normal mode
        repo = JSONPersistenceAdapter(file_path=tmp_path, journal_path=journal_path)
        
        # Act: save a book
        book = BookEntity("B1", "Structured Logging")
        # Ensure we set transactional mode or simply check normal save
        # Wait, if we are not in transaction, it saves to journal and then to database, then truncates journal!
        # So to test that journal actually contains entries before truncation, we can simulate transactional mode!
        # In transactional mode, saves write to memory and journal, but do not truncate the journal because no checkpoint occurs.
        repo._in_transaction = True
        repo.save_book(book)

        # Assert: check that journal file exists and has the save_book record
        assert os.path.exists(journal_path)
        with open(journal_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            assert len(lines) == 1
            data = json.loads(lines[0])
            assert data["action"] == "save_book"
            assert data["payload"]["id"] == "B1"
            assert data["payload"]["title"] == "Structured Logging"

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        bak_path = tmp_path + ".bak"
        if os.path.exists(bak_path):
            os.remove(bak_path)
        if os.path.exists(journal_path):
            os.remove(journal_path)

def test_checkpoint_truncates_journal() -> None:
    # Arrange
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp:
        tmp_path = tmp.name
    journal_path = tmp_path + ".journal"

    try:
        repo = JSONPersistenceAdapter(file_path=tmp_path, journal_path=journal_path)
        
        # Act: save a book in normal mode (triggers _save_to_disk which truncates log)
        book = BookEntity("B1", "Structured Logging")
        repo.save_book(book)

        # Assert: journal file should be empty (0 size) or truncated
        assert os.path.exists(journal_path)
        assert os.path.getsize(journal_path) == 0

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        bak_path = tmp_path + ".bak"
        if os.path.exists(bak_path):
            os.remove(bak_path)
        if os.path.exists(journal_path):
            os.remove(journal_path)

def test_recovery_replays_journal_on_top_of_bak() -> None:
    # Arrange
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp:
        tmp_path = tmp.name
    bak_path = tmp_path + ".bak"
    journal_path = tmp_path + ".journal"

    try:
        # 1. Create a valid initial state in backup file (.bak)
        repo_init = JSONPersistenceAdapter(file_path=bak_path, journal_path=journal_path)
        book1 = BookEntity("B1", "Initial Book")
        repo_init.save_book(book1)
        # Verify backup contains B1
        assert repo_init.get_book("B1") is not None

        # 2. Simulate pending transactions in journal. We write them directly to the journal file.
        # This simulates a system crash right after writing to WAL but before main file was replaced.
        with open(journal_path, "w", encoding="utf-8") as f:
            # We append a save_book transaction for B2 and a save_reader for R1
            book2_data = {
                "action": "save_book",
                "payload": {
                    "id": "B2",
                    "title": "Unsaved Book",
                    "author": "Author 2",
                    "status": "Available",
                    "hold_queue": [],
                    "checkout_count": 0
                }
            }
            reader_data = {
                "action": "save_reader",
                "payload": {
                    "id": "R1",
                    "name": "Bob",
                    "status": "Regular",
                    "fine_balance": 10.0,
                    "active_loans": [],
                    "reader_type": "Regular"
                }
            }
            f.write(json.dumps(book2_data) + "\n")
            f.write(json.dumps(reader_data) + "\n")

        # 3. Corrupt the primary database file to force recovery from .bak
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write("corrupted primary { invalid json")

        # 4. Act: Instantiate a new adapter on the corrupted primary file.
        # It must load from .bak AND replay the journal.
        repo_recovered = JSONPersistenceAdapter(file_path=tmp_path, journal_path=journal_path)

        # Assert: Book B1 from bak AND Book B2 / Reader R1 from journal should be loaded
        b1 = repo_recovered.get_book("B1")
        assert b1 is not None
        assert b1.title == "Initial Book"

        b2 = repo_recovered.get_book("B2")
        assert b2 is not None
        assert b2.title == "Unsaved Book"

        r1 = repo_recovered.get_reader("R1")
        assert r1 is not None
        assert r1.name == "Bob"
        assert r1.fine_balance == 10.0

        # Assert: the journal file must be truncated (0 size) after successful recovery
        assert os.path.getsize(journal_path) == 0

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        if os.path.exists(bak_path):
            os.remove(bak_path)
        if os.path.exists(journal_path):
            os.remove(journal_path)
