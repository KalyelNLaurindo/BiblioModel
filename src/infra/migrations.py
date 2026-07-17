import datetime
from typing import Dict, Callable, Tuple

class SchemaMigrationRegistry:
    def __init__(self) -> None:
        # Key: (from_version, to_version), Value: Callable[[dict], dict]
        self._migrations: Dict[Tuple[int, int], Callable[[dict], dict]] = {}

    def register(self, from_version: int, to_version: int) -> Callable:
        def decorator(func: Callable[[dict], dict]) -> Callable[[dict], dict]:
            self._migrations[(from_version, to_version)] = func
            return func
        return decorator

    def migrate(self, data: dict, start_version: int, target_version: int) -> dict:
        current_version = start_version
        while current_version < target_version:
            next_version = current_version + 1
            step = (current_version, next_version)
            if step in self._migrations:
                data = self._migrations[step](data)
                current_version = next_version
            else:
                raise ValueError(f"No migration path found from version {current_version} to {target_version}")
        return data

global_migration_registry = SchemaMigrationRegistry()

@global_migration_registry.register(0, 1)
def migrate_v0_to_v1(data: dict) -> dict:
    """
    Transforms old flat schema (version 0) to version 1 structured schema.
    """
    # Version 0 formats directly had books, readers, loans
    return {
        "metadata": {
            "schema_version": 1,
            "last_written_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "engine_version": "1.0.0"
        },
        "data": {
            "books": data.get("books", {}),
            "readers": data.get("readers", {}),
            "loans": data.get("loans", {})
        }
    }
