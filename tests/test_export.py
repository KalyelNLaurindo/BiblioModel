import os
import tempfile
import csv
import pytest
from src.domain.entities import BookEntity, ReaderEntity, LoanEntity, DomainError
from src.infra.adapters import JSONPersistenceAdapter
from src.infra.cli import CLIController
from src.infra.adapters import INIConfigAdapter

def test_export_reports() -> None:
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp:
        db_path = tmp.name

    try:
        repo = JSONPersistenceAdapter(db_path)
        config = INIConfigAdapter()
        
        # Save sample data
        repo.save_book(BookEntity("B1", "Domain-Driven Design", author="Eric Evans"))
        repo.save_reader(ReaderEntity("R1", "Alice Smith"))
        
        controller = CLIController(repo, config)
        
        # Test export books to CSV
        csv_output = os.path.join("reports", "test_books.csv")
        if os.path.exists(csv_output):
            os.remove(csv_output)
            
        res = controller.execute(["export", "--type", "books", "--format", "csv", "--output", csv_output])
        assert "Success" in res
        assert os.path.exists(csv_output)
        
        with open(csv_output, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)
            assert len(rows) == 2
            assert rows[0] == ["Book ID", "Title", "Author", "Status", "Hold Queue"]
            assert rows[1] == ["B1", "Domain-Driven Design", "Eric Evans", "Available", ""]
            
        # Test export books to HTML
        html_output = os.path.join("reports", "test_books.html")
        if os.path.exists(html_output):
            os.remove(html_output)
            
        res = controller.execute(["export", "--type", "books", "--format", "html", "--output", html_output])
        assert "Success" in res
        assert os.path.exists(html_output)
        
        with open(html_output, "r", encoding="utf-8") as f:
            content = f.read()
            assert "<!DOCTYPE html>" in content
            assert "Domain-Driven Design" in content
            assert "Eric Evans" in content
            
        # Clean up exported files
        if os.path.exists(csv_output):
            os.remove(csv_output)
        if os.path.exists(html_output):
            os.remove(html_output)
            
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)
        bak_path = db_path + ".bak"
        if os.path.exists(bak_path):
            os.remove(bak_path)

def test_export_path_traversal_prevention() -> None:
    db_path = "db_temp.json"
    repo = JSONPersistenceAdapter(db_path)
    config = INIConfigAdapter()
    controller = CLIController(repo, config)
    
    # Attempt to export outside workspace should raise/fail
    try:
        # A relative path designed to escape the workspace directory
        res = controller.execute(["export", "--type", "books", "--format", "csv", "--output", "../../outside.csv"])
        assert "Security Error" in res or "Error" in res
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)
        bak_path = db_path + ".bak"
        if os.path.exists(bak_path):
            os.remove(bak_path)
