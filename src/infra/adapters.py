import os
import logging
import configparser
from src.app.ports import IConfigProvider

# Default configuration values
DEFAULT_MAX_LOANS = 3
DEFAULT_LOAN_PERIOD_DAYS = 7
DEFAULT_DAILY_FINE_RATE = 2.00
DEFAULT_GRACE_PERIOD_DAYS = 0

class INIConfigAdapter(IConfigProvider):
    """
    Concrete adapter for loading library configurations from an INI file using configparser.
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
                # Fall back to empty config (using defaults) in case of parsing error
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



def setup_logger(log_file: str = "bibliomodel.log") -> logging.Logger:
    """
    Initializes and configures the system logger.
    Logs are written to both the console and a local file.
    """
    logger = logging.getLogger("bibliomodel")
    logger.setLevel(logging.INFO)

    # Avoid duplicate handlers if setup is called multiple times
    if not logger.handlers:
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # File Handler
        try:
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            # Fallback to sys.stderr if log file cannot be written
            print(f"Warning: Could not configure file logger: {e}")

        # Console Handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger
