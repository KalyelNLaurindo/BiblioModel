import os
import json
import logging
import configparser
from datetime import date
from typing import Optional, Dict, List
from src.app.ports import IConfigProvider, ILibraryRepository, ILoanHistoryRepository
from src.domain.entities import BookEntity, ReaderEntity, LoanEntity, DomainError

DEFAULT_MAX_LOANS = 3
DEFAULT_LOAN_PERIOD_DAYS = 7
DEFAULT_DAILY_FINE_RATE = 2.00
DEFAULT_GRACE_PERIOD_DAYS = 0
DEFAULT_AUTO_SUSPEND_OVERDUE_DAYS = 14

class INIConfigAdapter(IConfigProvider):
    """
    Adapter loading configurations from local config.ini. Fallback values are used if fields are missing/corrupted.
    """

    def __init__(self, file_path: str = "config.ini") -> None:
        self._file_path = file_path
        self._config = configparser.ConfigParser()
        self._load_config()

    def _load_config(self) -> None:
        if os.path.exists(self._file_path):
            try:
                self._config.read(self._file_path)
            except Exception:
                self._config = configparser.ConfigParser()
        else:
            self._config = configparser.ConfigParser()

    def get_max_loans(self) -> int:
        try:
            return self._config.getint("library", "max_loans", fallback=DEFAULT_MAX_LOANS)
        except ValueError:
            return DEFAULT_MAX_LOANS

    def get_loan_period_days(self) -> int:
        try:
            return self._config.getint("library", "loan_period_days", fallback=DEFAULT_LOAN_PERIOD_DAYS)
        except ValueError:
            return DEFAULT_LOAN_PERIOD_DAYS

    def get_daily_fine_rate(self) -> float:
        try:
            return self._config.getfloat("library", "daily_fine_rate", fallback=DEFAULT_DAILY_FINE_RATE)
        except ValueError:
            return DEFAULT_DAILY_FINE_RATE

    def get_grace_period_days(self) -> int:
        try:
            return self._config.getint("library", "grace_period_days", fallback=DEFAULT_GRACE_PERIOD_DAYS)
        except ValueError:
            return DEFAULT_GRACE_PERIOD_DAYS

    def get_auto_suspend_overdue_days(self) -> int:
        try:
            return self._config.getint("policy", "auto_suspend_overdue_days", fallback=DEFAULT_AUTO_SUSPEND_OVERDUE_DAYS)
        except ValueError:
            return DEFAULT_AUTO_SUSPEND_OVERDUE_DAYS


class JSONPersistenceAdapter(ILibraryRepository):
    """
    Persists entities in a local JSON database using atomic write switches and recovery files (.bak).
    """

    def __init__(self, file_path: str = "db_backup.json") -> None:
        self._file_path = file_path
        self._books: Dict[str, BookEntity] = {}
        self._readers: Dict[str, ReaderEntity] = {}
        self._loans: Dict[str, LoanEntity] = {}
        self._load_data()

    def clear_cache(self) -> None:
        """
        Clears memory entities and reloads from disk (mainly for testing lifecycle).
        """
        self._books.clear()
        self._readers.clear()
        self._loans.clear()
        self._load_data()

    def _initialize_empty(self) -> None:
        self._books = {}
        self._readers = {}
        self._loans = {}

    def _parse_and_validate(self, path: str) -> None:
        """
        Loads JSON database structure and hydrates objects. Validates schema format.
        """
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, dict):
            raise ValueError("Root element is not a dictionary")
        for key in ("books", "readers", "loans"):
            if key not in data or not isinstance(data[key], dict):
                raise ValueError(f"Missing or invalid section: '{key}'")

        books_data = data["books"]
        readers_data = data["readers"]
        loans_data = data["loans"]

        loaded_books: Dict[str, BookEntity] = {}
        loaded_readers: Dict[str, ReaderEntity] = {}
        loaded_loans: Dict[str, LoanEntity] = {}

        for bid, binfo in books_data.items():
            if not isinstance(binfo, dict) or "id" not in binfo or "title" not in binfo or "status" not in binfo:
                raise ValueError(f"Invalid book schema for book: {bid}")
            loaded_books[bid] = BookEntity(
                book_id=binfo["id"],
                title=binfo["title"],
                status=binfo["status"],
                hold_queue=binfo.get("hold_queue", []),
                author=binfo.get("author", "")
            )

        for lid, linfo in loans_data.items():
            if not isinstance(linfo, dict) or "id" not in linfo or "book_id" not in linfo or "reader_id" not in linfo or "checkout_date" not in linfo or "due_date" not in linfo:
                raise ValueError(f"Invalid loan schema for loan: {lid}")
            
            checkout_date = date.fromisoformat(linfo["checkout_date"])
            due_date = date.fromisoformat(linfo["due_date"])
            return_date = None
            if linfo.get("return_date") is not None:
                return_date = date.fromisoformat(linfo["return_date"])

            loaded_loans[lid] = LoanEntity(
                loan_id=linfo["id"],
                book_id=linfo["book_id"],
                reader_id=linfo["reader_id"],
                checkout_date=checkout_date,
                due_date=due_date,
                return_date=return_date,
                fine_amount=linfo.get("fine_applied", 0.0)
            )

        for rid, rinfo in readers_data.items():
            if not isinstance(rinfo, dict) or "id" not in rinfo or "name" not in rinfo or "status" not in rinfo:
                raise ValueError(f"Invalid reader schema for reader: {rid}")

            active_loan_ids = rinfo.get("active_loans", [])
            active_loans_list = []
            for lid in active_loan_ids:
                if lid in loaded_loans:
                    active_loans_list.append(loaded_loans[lid])

            loaded_readers[rid] = ReaderEntity(
                reader_id=rinfo["id"],
                name=rinfo["name"],
                status=rinfo["status"],
                fine_balance=rinfo.get("fine_balance", 0.0),
                active_loans=active_loans_list
            )

        self._books = loaded_books
        self._loans = loaded_loans
        self._readers = loaded_readers

    def _load_data(self) -> None:
        """
        Loads data from file path, falling back to backup self-healing logic if corrupted.
        """
        try:
            if os.path.exists(self._file_path) and os.path.getsize(self._file_path) > 0:
                self._parse_and_validate(self._file_path)
            else:
                self._initialize_empty()
        except Exception as e:
            bak_path = self._file_path + ".bak"
            if os.path.exists(bak_path) and os.path.getsize(bak_path) > 0:
                logger = logging.getLogger("bibliomodel")
                logger.warning(
                    f"Primary database '{self._file_path}' is corrupted: {e}. "
                    f"Attempting self-healing recovery from backup '{bak_path}'..."
                )
                try:
                    self._parse_and_validate(bak_path)
                    self._recovery_save_to_disk()
                    logger.warning("Self-healing successful. Primary database restored.")
                    return
                except Exception as rec_err:
                    logger.error(f"Self-healing recovery failed: {rec_err}")
            raise DomainError(f"Database file is corrupted and recovery failed: {e}")

    def _serialize_state(self) -> dict:
        books_data = {}
        for bid, book in self._books.items():
            books_data[bid] = {
                "id": book.book_id,
                "title": book.title,
                "author": book.author,
                "status": book.status,
                "hold_queue": book.hold_queue
            }

        loans_data = {}
        for lid, loan in self._loans.items():
            loans_data[lid] = {
                "id": loan.loan_id,
                "book_id": loan.book_id,
                "reader_id": loan.reader_id,
                "checkout_date": loan.checkout_date.isoformat(),
                "due_date": loan.due_date.isoformat(),
                "return_date": loan.return_date.isoformat() if loan.return_date else None,
                "fine_applied": loan.fine_amount
            }

        readers_data = {}
        for rid, reader in self._readers.items():
            active_loan_ids = [loan.loan_id for loan in reader.active_loans]
            readers_data[rid] = {
                "id": reader.reader_id,
                "name": reader.name,
                "status": reader.status,
                "fine_balance": reader.fine_balance,
                "active_loans": active_loan_ids
            }

        return {
            "books": books_data,
            "readers": readers_data,
            "loans": loans_data
        }

    def _save_to_disk(self) -> None:
        """
        Saves states to disk atomically by writing to an intermediate .tmp and swapping.
        """
        serialized = self._serialize_state()
        tmp_path = self._file_path + ".tmp"
        bak_path = self._file_path + ".bak"

        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(serialized, f, indent=2)

            if os.path.exists(self._file_path):
                os.replace(self._file_path, bak_path)

            os.replace(tmp_path, self._file_path)
        except Exception as e:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass
            raise DomainError(f"Failed to persist state database to disk: {e}")

    def _recovery_save_to_disk(self) -> None:
        """
        Swaps backup to primary atomically during self-healing (avoids touching backup file).
        """
        serialized = self._serialize_state()
        tmp_path = self._file_path + ".tmp"

        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(serialized, f, indent=2)

            os.replace(tmp_path, self._file_path)
        except Exception as e:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass
            raise DomainError(f"Recovery state write failed: {e}")

    def get_book(self, book_id: str) -> Optional[BookEntity]:
        return self._books.get(book_id)

    def save_book(self, book: BookEntity) -> None:
        self._books[book.book_id] = book
        self._save_to_disk()

    def get_reader(self, reader_id: str) -> Optional[ReaderEntity]:
        return self._readers.get(reader_id)

    def save_reader(self, reader: ReaderEntity) -> None:
        self._readers[reader.reader_id] = reader
        self._save_to_disk()

    def get_active_loan_by_book(self, book_id: str) -> Optional[LoanEntity]:
        for loan in self._loans.values():
            if loan.book_id == book_id and loan.return_date is None:
                return loan
        return None

    def save_loan(self, loan: LoanEntity) -> None:
        self._loans[loan.loan_id] = loan
        self._save_to_disk()

    def list_books(self) -> List[BookEntity]:
        return list(self._books.values())

    def list_readers(self) -> List[ReaderEntity]:
        return list(self._readers.values())

    def list_loans(self) -> List[LoanEntity]:
        return list(self._loans.values())

    def search_books(self, query: str) -> List[BookEntity]:
        q = query.lower().strip()
        results = []
        for book in self._books.values():
            title_match = q in book.title.lower()
            author_match = q in getattr(book, "author", "").lower()
            if title_match or author_match:
                results.append(book)
        return results

    def search_readers(self, query: str) -> List[ReaderEntity]:
        q = query.lower().strip()
        results = []
        for reader in self._readers.values():
            if q in reader.name.lower():
                results.append(reader)
        return results


class LoanHistoryAdapter(ILoanHistoryRepository):
    """
    Persists returned loan history in a separate JSON database file atomically.
    """
    def __init__(self, file_path: str = "loan_history.json") -> None:
        self._file_path = file_path
        self._history: List[dict] = []
        self._load_data()

    def _load_data(self) -> None:
        if os.path.exists(self._file_path) and os.path.getsize(self._file_path) > 0:
            try:
                with open(self._file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self._history = data
                    else:
                        self._history = []
            except Exception:
                self._history = []
        else:
            self._history = []

    def _save_data(self) -> None:
        tmp_path = self._file_path + ".tmp"
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(self._history, f, indent=2)
            os.replace(tmp_path, self._file_path)
        except Exception as e:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass
            raise DomainError(f"Failed to persist loan history to disk: {e}")

    def archive_loan(self, loan: LoanEntity, book_title: str, final_status: str, delay_days: int) -> None:
        record = {
            "loan_id": loan.loan_id,
            "book_id": loan.book_id,
            "book_title": book_title,
            "reader_id": loan.reader_id,
            "checkout_date": loan.checkout_date.isoformat(),
            "due_date": loan.due_date.isoformat(),
            "return_date": loan.return_date.isoformat() if loan.return_date else date.today().isoformat(),
            "delay_days": delay_days,
            "fine_amount": loan.fine_amount,
            "final_status": final_status
        }
        self._history = [r for r in self._history if r["loan_id"] != loan.loan_id]
        self._history.append(record)
        self._save_data()

    def get_history_by_reader(self, reader_id: str) -> List[dict]:
        return [r for r in self._history if r["reader_id"] == reader_id]


def setup_logger(log_file: str = "bibliomodel.log") -> logging.Logger:
    """
    Initializes system logger, forwarding metrics and operations to files and stdout stream.
    """
    logger = logging.getLogger("bibliomodel")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        try:
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            print(f"Warning: Could not configure file logger: {e}")

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger
