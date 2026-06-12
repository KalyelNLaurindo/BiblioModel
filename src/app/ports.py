from abc import ABC, abstractmethod

class IConfigProvider(ABC):
    """
    Port defining configuration retrieval methods for the library business rules.
    """

    @abstractmethod
    def get_max_loans(self) -> int:
        """
        Returns the maximum number of books a reader can borrow at the same time.
        """
        pass

    @abstractmethod
    def get_loan_period_days(self) -> int:
        """
        Returns the default loan duration in days.
        """
        pass

    @abstractmethod
    def get_daily_fine_rate(self) -> float:
        """
        Returns the daily fine rate amount for overdue books.
        """
        pass
