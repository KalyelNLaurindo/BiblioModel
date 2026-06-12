import re
from src.domain.entities import DomainError

class InputValidator:
    """
    Utility class for sanitizing and validating system inputs to prevent
    malicious strings, directory traversal, empty fields, and malformed IDs.
    """
    
    @staticmethod
    def sanitize_and_validate_reader_id(reader_id: str) -> str:
        if not isinstance(reader_id, str):
            raise DomainError("Invalid reader ID format")
        
        sanitized = reader_id.strip()
        if not sanitized:
            raise DomainError("Invalid reader ID format: cannot be empty")
            
        # Check for directory traversal
        if ".." in sanitized or "/" in sanitized or "\\" in sanitized:
            raise DomainError("Invalid reader ID format: traversal characters detected")
            
        # Check pattern: R followed by digits
        if not re.match(r"^R\d+$", sanitized):
            raise DomainError("Invalid reader ID format")
            
        return sanitized

    @staticmethod
    def sanitize_and_validate_book_id(book_id: str) -> str:
        if not isinstance(book_id, str):
            raise DomainError("Invalid book ID format")
            
        sanitized = book_id.strip()
        if not sanitized:
            raise DomainError("Invalid book ID format: cannot be empty")
            
        # Check for directory traversal
        if ".." in sanitized or "/" in sanitized or "\\" in sanitized:
            raise DomainError("Invalid book ID format: traversal characters detected")
            
        # Check pattern: B followed by digits
        if not re.match(r"^B\d+$", sanitized):
            raise DomainError("Invalid book ID format")
            
        return sanitized

    @staticmethod
    def sanitize_and_validate_general(val: str, field_name: str) -> str:
        if not isinstance(val, str):
            raise DomainError(f"Invalid {field_name} format")
            
        sanitized = val.strip()
        if not sanitized:
            raise DomainError(f"Invalid {field_name} format: cannot be empty")
            
        # Check for directory traversal / escape attempts
        if ".." in sanitized or "/" in sanitized or "\\" in sanitized:
            raise DomainError(f"Invalid {field_name} format: traversal characters detected")
            
        return sanitized
