import pytest
import os
import re
from unittest.mock import patch
from src.infra.cli import CLIFormatter, CLIController
from src.domain.entities import BookEntity
from tests.test_use_cases import FakeLibraryRepository, FakeConfigProvider

def has_ansi_escapes(text: str) -> bool:
    ansi_escape = re.compile(r'\x1b\[[0-9;]*m|\033\[[0-9;]*m')
    return bool(ansi_escape.search(text))

def test_cli_no_color_flag_removes_ansi_styles() -> None:
    repo = FakeLibraryRepository()
    config = FakeConfigProvider()
    controller = CLIController(repo, config)
    
    # Run help with --no-color
    res = controller.execute(["help", "--no-color"])
    assert not has_ansi_escapes(res)

def test_cli_no_color_env_var_removes_ansi_styles(monkeypatch) -> None:
    monkeypatch.setenv("NO_COLOR", "1")
    repo = FakeLibraryRepository()
    config = FakeConfigProvider()
    controller = CLIController(repo, config)
    
    # Run help (without parameter, relying on env var)
    res = controller.execute(["help"])
    assert not has_ansi_escapes(res)

def test_cli_formatter_strip_ansi() -> None:
    styled_text = "\033[92mSuccess\033[0m Text \x1b[91mError\x1b[0m"
    stripped = CLIFormatter.strip_ansi(styled_text)
    assert stripped == "Success Text Error"
    assert not has_ansi_escapes(stripped)

def test_cli_formatter_badges_no_color() -> None:
    original_no_color = CLIFormatter.no_color
    try:
        CLIFormatter.no_color = True
        
        ok_msg = CLIFormatter.format_ok("Done")
        assert not has_ansi_escapes(ok_msg)
        assert "🟢 [SUCCESS] Done" in ok_msg or "(+) [SUCCESS] Done" in ok_msg
    finally:
        CLIFormatter.no_color = original_no_color

def test_cli_linear_output_format() -> None:
    repo = FakeLibraryRepository()
    config = FakeConfigProvider()
    
    book = BookEntity("B1", "DDD Bounded Contexts")
    repo.save_book(book)
    
    controller = CLIController(repo, config)
    res = controller.execute(["list-books", "--linear"])
    
    # Linear layout output should contain property lines
    assert "Book ID: B1" in res
    assert "Title: DDD Bounded Contexts" in res
    assert "Status: Available" in res
    assert "Hold Queue: None" in res
    
    # Should not contain standard table borders
    assert "┌" not in res
    assert "├" not in res
    assert "+" not in res
