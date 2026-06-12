from datetime import date


class FineCalculator:
    """
    Domain service for calculating fines on returned books.
    """

    def calculate_fine(
        self,
        due_date: date,
        return_date: date,
        daily_rate: float,
        grace_period_days: int
    ) -> float:
        """
        Calculates the late fee fine based on return date and grace period.
        If the grace period is exceeded, the fine is calculated over the entire
        duration of the delay (no deduction of the grace period days).
        """
        late_days = (return_date - due_date).days
        if late_days <= 0:
            return 0.0

        if late_days <= grace_period_days:
            return 0.0

        return float(late_days * daily_rate)
