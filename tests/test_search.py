import os
import tempfile
import pytest
from src.domain.entities import BookEntity, ReaderEntity
from src.infra.adapters import JSONPersistenceAdapter

def test_search_books_and_readers() -> None:
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp:
        tmp_path = tmp.name

    try:
        repo = JSONPersistenceAdapter(tmp_path)
        
        # Save books
        repo.save_book(BookEntity("B1", "Domain-Driven Design", author="Eric Evans"))
        repo.save_book(BookEntity("B2", "Design Patterns", author="Gang of Four"))
        repo.save_book(BookEntity("B3", "Clean Architecture", author="Robert C. Martin"))
        
        # Save readers
        repo.save_reader(ReaderEntity("R1", "Alice Smith"))
        repo.save_reader(ReaderEntity("R2", "Bob Jones"))
        repo.save_reader(ReaderEntity("R3", "Charlie Smith"))
        
        # Test exact search
        books = repo.search_books("Design Patterns")
        assert len(books) == 1
        assert books[0].book_id == "B2"
        
        # Test case-insensitive search
        books = repo.search_books("clean architecture")
        assert len(books) == 1
        assert books[0].book_id == "B3"
        
        # Test partial title search
        books = repo.search_books("Design")
        assert len(books) == 2  # Domain-Driven Design, Design Patterns
        ids = {b.book_id for b in books}
        assert ids == {"B1", "B2"}
        
        # Test partial author search
        books = repo.search_books("Evans")
        assert len(books) == 1
        assert books[0].book_id == "B1"
        
        # Test no results
        books = repo.search_books("Nonexistent Book")
        assert len(books) == 0
        
        # Test empty query (should return all books)
        books = repo.search_books("")
        assert len(books) == 3
        
        # Test reader search (case-insensitive, partial name)
        readers = repo.search_readers("smith")
        assert len(readers) == 2  # Alice Smith, Charlie Smith
        names = {r.name for r in readers}
        assert names == {"Alice Smith", "Charlie Smith"}
        
        # Test reader no results
        readers = repo.search_readers("David")
        assert len(readers) == 0
        
        # Test reader empty query (returns all)
        readers = repo.search_readers("")
        assert len(readers) == 3
        
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        bak_path = tmp_path + ".bak"
        if os.path.exists(bak_path):
            os.remove(bak_path)
