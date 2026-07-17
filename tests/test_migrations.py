import os
import tempfile
import json
import pytest
from datetime import date, datetime
from src.domain.entities import BookEntity, ReaderEntity, LoanEntity, DomainError
from src.infra.adapters import JSONPersistenceAdapter
from src.infra.migrations import SchemaMigrationRegistry

def test_migration_registry_linear_execution() -> None:
    registry = SchemaMigrationRegistry()
    
    # Register two dummy migrations
    @registry.register(0, 1)
    def migrate_0_to_1(data: dict) -> dict:
        data["step1"] = True
        return data

    @registry.register(1, 2)
    def migrate_1_to_2(data: dict) -> dict:
        data["step2"] = True
        return data

    input_data = {"base": 42}
    output_data = registry.migrate(input_data, start_version=0, target_version=2)
    
    assert output_data["base"] == 42
    assert output_data["step1"] is True
    assert output_data["step2"] is True


def test_migration_registry_invalid_path() -> None:
    registry = SchemaMigrationRegistry()
    
    @registry.register(0, 1)
    def migrate_0_to_1(data: dict) -> dict:
        return data

    # No migration registered for 1 -> 3
    with pytest.raises(ValueError, match="No migration path found"):
        registry.migrate({}, start_version=0, target_version=3)


def test_load_legacy_database_v0_migrates_to_v1() -> None:
    # Prepare a legacy v0 database (raw root format)
    legacy_data = {
        "books": {
            "B1": {
                "id": "B1",
                "title": "Legacy Book",
                "status": "Available",
                "hold_queue": [],
                "author": "Author A",
                "checkout_count": 5
            }
        },
        "readers": {},
        "loans": {}
    }

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp:
        tmp_path = tmp.name
        json.dump(legacy_data, tmp, indent=2)

    try:
        # Act: Load legacy database
        repo = JSONPersistenceAdapter(tmp_path)

        # Assert: Memory state hydrated correctly
        book = repo.get_book("B1")
        assert book is not None
        assert book.title == "Legacy Book"
        assert book.checkout_count == 5

        # Assert: File on disk was automatically updated to v1 format with metadata
        with open(tmp_path, "r", encoding="utf-8") as f:
            disk_data = json.load(f)

        assert "metadata" in disk_data
        assert disk_data["metadata"]["schema_version"] == 1
        assert "engine_version" in disk_data["metadata"]
        assert "last_written_at" in disk_data["metadata"]
        assert "data" in disk_data
        assert "books" in disk_data["data"]
        assert disk_data["data"]["books"]["B1"]["title"] == "Legacy Book"
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        bak_path = tmp_path + ".bak"
        if os.path.exists(bak_path):
            os.remove(bak_path)


def test_save_creates_v1_metadata() -> None:
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp:
        tmp_path = tmp.name

    try:
        repo = JSONPersistenceAdapter(tmp_path)
        book = BookEntity("B2", "Modern Book")
        repo.save_book(book)

        with open(tmp_path, "r", encoding="utf-8") as f:
            disk_data = json.load(f)

        assert "metadata" in disk_data
        assert disk_data["metadata"]["schema_version"] == 1
        assert "data" in disk_data
        assert disk_data["data"]["books"]["B2"]["title"] == "Modern Book"
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        bak_path = tmp_path + ".bak"
        if os.path.exists(bak_path):
            os.remove(bak_path)


def test_migration_failure_restores_from_backup() -> None:
    # Legacy data version 0
    legacy_data = {
        "books": {"B1": {"id": "B1", "title": "Legacy", "status": "Available"}},
        "readers": {},
        "loans": {}
    }

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp:
        tmp_path = tmp.name
        json.dump(legacy_data, tmp, indent=2)

    bak_path = tmp_path + ".bak"
    # Create a valid backup file
    with open(bak_path, "w", encoding="utf-8") as f:
        json.dump(legacy_data, f, indent=2)

    # We will temporarily register a broken migration for 0 -> 1 in the global registry
    # to simulate failure.
    from src.infra.migrations import global_migration_registry
    
    def broken_migration(data: dict) -> dict:
        raise RuntimeError("Migration failed catastrophically")

    # Override registry migration path temporarily
    original_migrations = global_migration_registry._migrations.copy()
    global_migration_registry.register(0, 1)(broken_migration)

    try:
        # Act & Assert: Loading the repo should fail during migration, raising DomainError
        with pytest.raises(DomainError, match="Database file is corrupted and recovery failed"):
            JSONPersistenceAdapter(tmp_path)
    finally:
        # Restore registry
        global_migration_registry._migrations = original_migrations
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        if os.path.exists(bak_path):
            os.remove(bak_path)
