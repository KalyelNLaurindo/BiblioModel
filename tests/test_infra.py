import os
import tempfile
import logging
from src.infra.adapters import INIConfigAdapter

def test_ini_config_adapter_loads_values() -> None:
    # Create a temporary config file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.ini') as tmp:
        tmp.write("[library]\nmax_loans = 5\nloan_period_days = 14\ndaily_fine_rate = 1.50\ngrace_period_days = 3\n")
        tmp_path = tmp.name

    try:
        adapter = INIConfigAdapter(tmp_path)
        assert adapter.get_max_loans() == 5
        assert adapter.get_loan_period_days() == 14
        assert adapter.get_daily_fine_rate() == 1.50
        assert adapter.get_grace_period_days() == 3
    finally:
        os.remove(tmp_path)

def test_ini_config_adapter_fallback_on_missing_file() -> None:
    # Use a non-existent file path
    adapter = INIConfigAdapter("non_existent_file.ini")
    assert adapter.get_max_loans() == 3
    assert adapter.get_loan_period_days() == 7
    assert adapter.get_daily_fine_rate() == 2.00
    assert adapter.get_grace_period_days() == 0

def test_ini_config_adapter_fallback_on_missing_options() -> None:
    # Create a temporary config file with missing options
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.ini') as tmp:
        tmp.write("[library]\nmax_loans = 10\n")
        tmp_path = tmp.name

    try:
        adapter = INIConfigAdapter(tmp_path)
        assert adapter.get_max_loans() == 10
        assert adapter.get_loan_period_days() == 7  # default fallback
        assert adapter.get_daily_fine_rate() == 2.00  # default fallback
        assert adapter.get_grace_period_days() == 0  # default fallback
    finally:
        os.remove(tmp_path)


def test_setup_logger() -> None:
    from src.infra.adapters import setup_logger
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as tmp:
        log_path = tmp.name

    try:
        logger = setup_logger(log_path)
        assert logger.name == "bibliomodel"
        logger.info("Test log message")
        
        # Verify log file has content
        with open(log_path, "r", encoding="utf-8") as f:
            content = f.read()
            assert "Test log message" in content
            assert "[INFO]" in content
    finally:
        # Clean up logger handlers to release file lock
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)
        os.remove(log_path)

