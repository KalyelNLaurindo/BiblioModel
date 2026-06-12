from datetime import date


class FineCalculator:
    """
    Stateless domain service for calculating late return fines based on rules.
    """

    def calculate_fine(
        self,
        due_date: date,
        return_date: date,
        daily_rate: float,
        grace_period_days: int
    ) -> float:
        """
        Calculates fines. If grace period is exceeded, fine is calculated from due date (no grace deduction).
        """
        late_days = (return_date - due_date).days
        if late_days <= 0:
            return 0.0

        if late_days <= grace_period_days:
            return 0.0

        return float(late_days * daily_rate)
