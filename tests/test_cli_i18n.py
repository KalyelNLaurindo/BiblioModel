import pytest
from datetime import date
from tests.test_use_cases import FakeLibraryRepository, FakeConfigProvider
from src.domain.entities import BookEntity, ReaderEntity, LoanEntity
from src.infra.cli import CLIController
from src.infra.translation_service import TranslationService

def test_cli_help_translation_spanish() -> None:
    repo = FakeLibraryRepository()
    config = FakeConfigProvider()
    controller = CLIController(repo, config)
    
    # Spanish help command
    res = controller.execute(["help", "--lang", "es"])
    assert "BIBLIOMODEL CLI" in res
    assert "REGLAS DE NEGOCIO ACTIVAS" in res
    assert "Límite de Préstamos Simultáneos" in res
    assert "Período de Préstamo" in res
    assert "Tasa Diaria de Multa" in res

def test_cli_help_translation_french() -> None:
    repo = FakeLibraryRepository()
    config = FakeConfigProvider()
    controller = CLIController(repo, config)
    
    res = controller.execute(["help", "--lang", "fr"])
    assert "BIBLIOMODEL CLI" in res
    assert "RÈGLES MÉTIER ACTIVES" in res

def test_cli_help_translation_german() -> None:
    repo = FakeLibraryRepository()
    config = FakeConfigProvider()
    controller = CLIController(repo, config)
    
    res = controller.execute(["help", "--lang", "de"])
    assert "BIBLIOMODEL CLI" in res
    assert "AKTIVE GESCHÄFTSREGELN" in res

def test_cli_help_translation_portuguese() -> None:
    repo = FakeLibraryRepository()
    config = FakeConfigProvider()
    controller = CLIController(repo, config)
    
    res = controller.execute(["help", "--lang", "pt"])
    assert "BIBLIOMODEL CLI" in res
    assert "REGRAS DE NEGÓCIO ATIVAS" in res

def test_cli_help_translation_english() -> None:
    repo = FakeLibraryRepository()
    config = FakeConfigProvider()
    controller = CLIController(repo, config)
    
    res = controller.execute(["help", "--lang", "en"])
    assert "BIBLIOMODEL CLI" in res
    assert "ACTIVE BUSINESS RULES" in res

def test_cli_loan_success_translation_spanish() -> None:
    repo = FakeLibraryRepository()
    config = FakeConfigProvider()
    
    book = BookEntity("B1", "DDD Book")
    reader = ReaderEntity("R1", "Alice")
    repo.save_book(book)
    repo.save_reader(reader)
    
    controller = CLIController(repo, config)
    res = controller.execute(["loan", "--reader", "R1", "--book", "B1", "--date", "2026-06-12", "--lang", "es"])
    
    # Éxito: Libro 'B1' prestado al Lector 'R1' hasta 2026-06-19.
    assert "[SUCCESS]" in res
    assert "Éxito: Libro" in res
    assert "prestado al Lector" in res

def test_cli_list_books_translation_spanish() -> None:
    repo = FakeLibraryRepository()
    config = FakeConfigProvider()
    
    book = BookEntity("B1", "DDD Book")
    repo.save_book(book)
    
    controller = CLIController(repo, config)
    res = controller.execute(["list-books", "--lang", "es"])
    
    assert "ID del Libro" in res
    assert "Título" in res
    assert "Estado" in res
    assert "Cola de Espera" in res
    assert "B1" in res
    assert "DDD Book" in res

def test_cli_return_success_translation_spanish() -> None:
    repo = FakeLibraryRepository()
    config = FakeConfigProvider()
    
    book = BookEntity("B1", "DDD Book")
    book.loan_to("R1")
    reader = ReaderEntity("R1", "Alice")
    loan = LoanEntity("L1", "B1", "R1", date(2026, 6, 1), date(2026, 6, 8))
    reader.add_loan(loan)
    
    repo.save_book(book)
    repo.save_reader(reader)
    repo.save_loan(loan)
    
    controller = CLIController(repo, config)
    res = controller.execute(["return", "--book", "B1", "--date", "2026-06-05", "--lang", "es"])
    
    assert "[SUCCESS]" in res
    assert "Éxito: Libro" in res
    assert "devuelto" in res

def test_cli_reserve_success_translation_spanish() -> None:
    repo = FakeLibraryRepository()
    config = FakeConfigProvider()
    
    book = BookEntity("B1", "DDD Book")
    book.loan_to("R2")
    reader = ReaderEntity("R1", "Alice")
    
    repo.save_book(book)
    repo.save_reader(reader)
    
    controller = CLIController(repo, config)
    res = controller.execute(["reserve", "--reader", "R1", "--book", "B1", "--lang", "es"])
    
    assert "[HOLD]" in res
    assert "Éxito: Libro" in res
    assert "reservado para el Lector" in res

def test_cli_waive_success_translation_spanish() -> None:
    repo = FakeLibraryRepository()
    config = FakeConfigProvider()
    
    reader = ReaderEntity("R1", "Alice")
    reader.apply_fine(10.00)
    repo.save_reader(reader)
    
    controller = CLIController(repo, config)
    res = controller.execute([
        "waive",
        "--reader", "R1",
        "--operator", "Director John",
        "--reason", "Patron disputed fine",
        "--lang", "es"
    ])
    
    assert "[SUCCESS]" in res
    assert "Éxito: Multa exonerada para el Lector" in res

def test_cli_loan_success_translation_french() -> None:
    repo = FakeLibraryRepository()
    config = FakeConfigProvider()
    book = BookEntity("B1", "DDD Book")
    reader = ReaderEntity("R1", "Alice")
    repo.save_book(book)
    repo.save_reader(reader)
    
    controller = CLIController(repo, config)
    res = controller.execute(["loan", "--reader", "R1", "--book", "B1", "--date", "2026-06-12", "--lang", "fr"])
    assert "[SUCCESS]" in res
    assert "Succès: Livre" in res
    assert "prêté au Lecteur" in res

def test_cli_loan_success_translation_german() -> None:
    repo = FakeLibraryRepository()
    config = FakeConfigProvider()
    book = BookEntity("B1", "DDD Book")
    reader = ReaderEntity("R1", "Alice")
    repo.save_book(book)
    repo.save_reader(reader)
    
    controller = CLIController(repo, config)
    res = controller.execute(["loan", "--reader", "R1", "--book", "B1", "--date", "2026-06-12", "--lang", "de"])
    assert "[SUCCESS]" in res
    assert "Erfolg: Buch" in res
    assert "ausgeliehen an Leser" in res

def test_cli_loan_success_translation_portuguese() -> None:
    repo = FakeLibraryRepository()
    config = FakeConfigProvider()
    book = BookEntity("B1", "DDD Book")
    reader = ReaderEntity("R1", "Alice")
    repo.save_book(book)
    repo.save_reader(reader)
    
    controller = CLIController(repo, config)
    res = controller.execute(["loan", "--reader", "R1", "--book", "B1", "--date", "2026-06-12", "--lang", "pt"])
    assert "[SUCCESS]" in res
    assert "Sucesso: Livro" in res
    assert "emprestado para o Leitor" in res

def test_cli_list_books_translation_german() -> None:
    repo = FakeLibraryRepository()
    config = FakeConfigProvider()
    book = BookEntity("B1", "DDD Book")
    repo.save_book(book)
    
    controller = CLIController(repo, config)
    res = controller.execute(["list-books", "--lang", "de"])
    assert "Buch ID" in res
    assert "Titel" in res
    assert "Status" in res
    assert "Warteschlange" in res

