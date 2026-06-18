import os
import tempfile
from datetime import date, timedelta
from src.domain.entities import BookEntity, ReaderEntity, LoanEntity
from src.infra.adapters import JSONPersistenceAdapter, INIConfigAdapter
from src.infra.cli import CLIController

def test_notify_overdue() -> None:
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp:
        db_path = tmp.name

    try:
        repo = JSONPersistenceAdapter(db_path)
        config = INIConfigAdapter()
        
        # Save sample data
        book = BookEntity("B1", "Domain-Driven Design")
        reader = ReaderEntity("R1", "Alice Smith")
        # Overdue loan: checked out 10 days ago, due 3 days ago
        loan = LoanEntity("L1", "B1", "R1", date.today() - timedelta(days=10), date.today() - timedelta(days=3))
        reader.add_loan(loan)
        
        repo.save_book(book)
        repo.save_reader(reader)
        repo.save_loan(loan)
        
        controller = CLIController(repo, config)
        
        # Clean existing notifications folder
        notif_dir = os.path.join(".", "notifications")
        if os.path.exists(notif_dir):
            for f in os.listdir(notif_dir):
                if f.startswith("email_R1_"):
                    try:
                        os.remove(os.path.join(notif_dir, f))
                    except Exception:
                        pass
                        
        res = controller.execute(["notify-overdue"])
        assert "Success" in res
        
        # Check that file was created
        found_notif = False
        if os.path.exists(notif_dir):
            for f in os.listdir(notif_dir):
                if f.startswith("email_R1_") and f.endswith(".txt"):
                    found_notif = True
                    # Verify content
                    with open(os.path.join(notif_dir, f), "r", encoding="utf-8") as file_handle:
                        content = file_handle.read()
                        assert "Alice Smith" in content
                        assert "Domain-Driven Design" in content
                        assert "Fine" in content or "Multa" in content or "fine" in content
                        assert "Return Instructions" in content or "instruções" in content or "return" in content
                    
                    # Clean up
                    try:
                        os.remove(os.path.join(notif_dir, f))
                    except Exception:
                        pass
        assert found_notif
        
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)
        bak_path = db_path + ".bak"
        if os.path.exists(bak_path):
            os.remove(bak_path)
