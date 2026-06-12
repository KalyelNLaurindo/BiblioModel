import re
from src.domain.entities import DomainError

class InputValidator:
    """
    Validates and sanitizes IDs and inputs to prevent traversal attacks and empty fields.
    """
    
    @staticmethod
    def sanitize_and_validate_reader_id(reader_id: str) -> str:
        """
        Sanitizes and checks if reader ID follows 'R' + digits pattern, ensuring no traversal chars.
        """
        if not isinstance(reader_id, str):
            raise DomainError("Invalid reader ID format")
        
        sanitized = reader_id.strip()
        if not sanitized:
            raise DomainError("Invalid reader ID format: cannot be empty")
            
        if ".." in sanitized or "/" in sanitized or "\\" in sanitized:
            raise DomainError("Invalid reader ID format: traversal characters detected")
            
        if not re.match(r"^R\d+$", sanitized):
            raise DomainError("Invalid reader ID format")
            
        return sanitized

    @staticmethod
    def sanitize_and_validate_book_id(book_id: str) -> str:
        """
        Sanitizes and checks if book ID follows 'B' + digits pattern, ensuring no traversal chars.
        """
        if not isinstance(book_id, str):
            raise DomainError("Invalid book ID format")
            
        sanitized = book_id.strip()
        if not sanitized:
            raise DomainError("Invalid book ID format: cannot be empty")
            
        if ".." in sanitized or "/" in sanitized or "\\" in sanitized:
            raise DomainError("Invalid book ID format: traversal characters detected")
            
        if not re.match(r"^B\d+$", sanitized):
            raise DomainError("Invalid book ID format")
            
        return sanitized

    @staticmethod
    def sanitize_and_validate_general(val: str, field_name: str) -> str:
        """
        Sanitizes arbitrary text fields against empty values and directory traversal symbols.
        """
        if not isinstance(val, str):
            raise DomainError(f"Invalid {field_name} format")
            
        sanitized = val.strip()
        if not sanitized:
            raise DomainError(f"Invalid {field_name} format: cannot be empty")
            
        if ".." in sanitized or "/" in sanitized or "\\" in sanitized:
            raise DomainError(f"Invalid {field_name} format: traversal characters detected")
            
        return sanitized
