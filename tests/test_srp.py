import os
import tempfile
import csv
import pytest
from datetime import date
from unittest.mock import MagicMock
from src.app.ports import IConfigProvider
from src.infra.exporters import ReportExporter
from src.infra.smtp_adapter import SMTPNotificationService
from src.infra.shell import InteractiveShell

def test_report_exporter_csv() -> None:
    exporter = ReportExporter()
    with tempfile.TemporaryDirectory(dir=".") as tmp_dir:
        output_file = os.path.join(tmp_dir, "test_export.csv")
        headers = ["Col1", "Col2"]
        rows = [["Val1", "Val2"], ["Val3", "Val4"]]
        
        path = exporter.export_report("test", "csv", headers, rows, output_file)
        assert os.path.exists(path)
        
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            data = list(reader)
            assert data[0] == headers
            assert data[1] == rows[0]
            assert data[2] == rows[1]

def test_report_exporter_html() -> None:
    exporter = ReportExporter()
    with tempfile.TemporaryDirectory(dir=".") as tmp_dir:
        output_file = os.path.join(tmp_dir, "test_export.html")
        headers = ["Col1", "Col2"]
        rows = [["Val1", "Val2"]]
        
        path = exporter.export_report("test", "html", headers, rows, output_file)
        assert os.path.exists(path)
        
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            assert "<!DOCTYPE html>" in content
            assert "Val1" in content
            assert "Val2" in content

def test_report_exporter_path_traversal() -> None:
    exporter = ReportExporter()
    with pytest.raises(PermissionError):
        exporter.export_report("test", "csv", ["Col"], [["Val"]], "../../outside_workspace.csv")

def test_smtp_notification_service() -> None:
    config_mock = MagicMock(spec=IConfigProvider)
    service = SMTPNotificationService(config_mock)
    
    today = date.today()
    reader_id = "R_TEST"
    reader_name = "John Doe"
    reader_email = "john@example.com"
    
    overdue_loans = [
        {"title": "Test Book 1", "due_date": "2026-06-20", "fine": 2.0},
        {"title": "Test Book 2", "due_date": "2026-06-21", "fine": 1.0}
    ]
    
    # Ensure notifications directory is clean
    notif_dir = os.path.abspath(os.path.join(".", "notifications"))
    os.makedirs(notif_dir, exist_ok=True)
    target_file = os.path.join(notif_dir, f"email_{reader_id}_{today.isoformat()}.txt")
    if os.path.exists(target_file):
        os.remove(target_file)
        
    try:
        success = service.send_overdue_notification(
            reader_id=reader_id,
            reader_name=reader_name,
            reader_email=reader_email,
            reader_fine_balance=3.0,
            overdue_loans=overdue_loans,
            today=today
        )
        assert success
        assert os.path.exists(target_file)
        
        with open(target_file, "r", encoding="utf-8") as f:
            content = f.read()
            assert "John Doe" in content
            assert "Test Book 1" in content
            assert "Test Book 2" in content
            assert "3.00" in content
    finally:
        if os.path.exists(target_file):
            os.remove(target_file)

def test_interactive_shell_runs_commands(monkeypatch) -> None:
    mock_controller = MagicMock()
    mock_controller.execute.return_value = "Mocked execution success"
    
    shell = InteractiveShell(mock_controller)
    
    # Simulate typing 'list-books' then 'exit'
    inputs = iter(["list-books", "exit"])
    monkeypatch.setattr('builtins.input', lambda prompt: next(inputs))
    
    res = shell.run()
    assert "closed" in res.lower()
    mock_controller.execute.assert_called_once_with(["list-books"])
