import pytest
import sys
from datetime import date, timedelta
from unittest.mock import MagicMock, patch
from src.infra.cli import CLIFormatter, CLIController
from src.infra.shell import InteractiveShell
from src.domain.entities import BookEntity, ReaderEntity, LoanEntity
from src.infra.translation_service import TranslationService
from tests.test_use_cases import FakeLibraryRepository, FakeConfigProvider

def test_cli_formatter_ascii_fallback_badges() -> None:
    # Save original settings
    original_force = CLIFormatter.force_ascii
    
    try:
        # Force ASCII
        CLIFormatter.force_ascii = True
        
        ok_msg = CLIFormatter.format_ok("Success message")
        warn_msg = CLIFormatter.format_warn("Warning message")
        err_msg = CLIFormatter.format_error("Error message")
        hold_msg = CLIFormatter.format_hold("Hold message")
        
        assert "(+) \033[92m[SUCCESS]\033[0m Success message" in ok_msg
        assert "(*)" in warn_msg
        assert "(x)" in err_msg
        assert "(=)" in hold_msg
    finally:
        CLIFormatter.force_ascii = original_force

def test_cli_formatter_ascii_fallback_table() -> None:
    original_force = CLIFormatter.force_ascii
    
    try:
        CLIFormatter.force_ascii = True
        
        headers = ["ID", "Title"]
        rows = [["1", "DDD Book"]]
        table = CLIFormatter.render_table(headers, rows)
        
        # Check that ASCII-only characters are used instead of Unicode box-drawing
        assert "+" in table
        assert "-" in table
        assert "|" in table
        assert "┌" not in table
        assert "─" not in table
        assert "│" not in table
    finally:
        CLIFormatter.force_ascii = original_force

def test_shell_status_line_db_ok_and_no_overdues() -> None:
    repo = FakeLibraryRepository()
    config = FakeConfigProvider()
    controller = CLIController(repo, config)
    shell = InteractiveShell(controller)
    
    # Verify status line content
    status_line = shell._get_status_line()
    assert "Language: EN" in status_line
    assert "DB: OK" in status_line
    assert "Active Overdues: 0" in status_line

def test_shell_status_line_db_error() -> None:
    repo = MagicMock()
    # Force list_books to raise an exception
    repo.list_books.side_effect = Exception("DB Connection Lost")
    
    config = FakeConfigProvider()
    controller = CLIController(repo, config)
    shell = InteractiveShell(controller)
    
    status_line = shell._get_status_line()
    assert "DB: ERROR" in status_line

def test_shell_status_line_with_overdues() -> None:
    repo = FakeLibraryRepository()
    config = FakeConfigProvider()
    
    # Save a book, reader, and overdue loan
    book = BookEntity("B1", "DDD Book")
    reader = ReaderEntity("R1", "Alice")
    # Due yesterday (overdue)
    due_date = date.today() - timedelta(days=1)
    loan = LoanEntity("L1", "B1", "R1", date.today() - timedelta(days=8), due_date)
    
    repo.save_book(book)
    repo.save_reader(reader)
    repo.save_loan(loan)
    
    controller = CLIController(repo, config)
    shell = InteractiveShell(controller)
    
    status_line = shell._get_status_line()
    assert "Active Overdues: 1" in status_line

def test_shell_language_switching_via_prompt() -> None:
    repo = FakeLibraryRepository()
    config = FakeConfigProvider()
    translation_service = TranslationService(config)
    
    controller = CLIController(repo, config, translation_service=translation_service)
    shell = InteractiveShell(controller)
    
    # Simulating user input choosing option "3" (Español)
    with patch("builtins.input", return_value="3"):
        shell._switch_language_prompt()
        
    # Check that language was updated to 'es' in the translation service
    assert translation_service.get_locale() == "es"
