from datetime import date
from typing import List, Set, Dict

class PolicyResult:
    """
    Holds the outcome of evaluating the policy engine on a loan fine.
    """
    def __init__(self, original_fine: float, final_fine: float, applied_rules: List[str], requires_approval_rules: List[str]) -> None:
        self.original_fine = original_fine
        self.final_fine = final_fine
        self.applied_rules = applied_rules
        self.requires_approval_rules = requires_approval_rules
        self.discount_amount = original_fine - final_fine


class FinePolicyEngine:
    """
    Evaluates fine waiver and discount rules defined in config.ini or standard business guidelines.
    """
    def __init__(self, config_provider) -> None:
        self.config_provider = config_provider

    def evaluate_rules(
        self,
        fine_amount: float,
        reader,
        loan,
        history_records: List[dict],
        system_delay: bool = False,
        book_donation: bool = False
    ) -> List[dict]:
        """
        Gathers list of candidate rules applicable to the checkout context.
        """
        # Load from config or use default rules
        policy = self.config_provider.get_fine_policy()
        
        # Helper to get config overrides
        def get_discount(rule_key: str, default_pct: float) -> float:
            val = policy.get(f"{rule_key}_discount")
            if val is not None:
                try:
                    return float(val) / 100.0
                except ValueError:
                    pass
            return default_pct

        def get_requires_approval(rule_key: str, default_val: bool) -> bool:
            val = policy.get(f"{rule_key}_requires_approval")
            if val is not None:
                return val.lower() == "true"
            return default_val

        applicable_rules = []

        # Rule 1: PCD Waiver (100%)
        if getattr(reader, "reader_type", "Regular") == "PCD":
            applicable_rules.append({
                "name": "PCD Waiver",
                "discount": get_discount("pcd", 1.0),
                "requires_approval": get_requires_approval("pcd", False)
            })

        # Rule 2: Institutional System Delay (100%)
        if system_delay:
            applicable_rules.append({
                "name": "System Delay Waiver",
                "discount": get_discount("system_delay", 1.0),
                "requires_approval": get_requires_approval("system_delay", False)
            })

        # Rule 3: Book Donation (50%)
        if book_donation:
            applicable_rules.append({
                "name": "Book Donation Discount",
                "discount": get_discount("book_donation", 0.5),
                "requires_approval": get_requires_approval("book_donation", True)
            })

        # Rule 4: First Offense (25%)
        # Reader has NO other past loans in history with fine_amount > 0
        has_past_fines = any(r.get("fine_amount", 0.0) > 0.0 for r in history_records)
        if not has_past_fines:
            applicable_rules.append({
                "name": "First Offense Discount",
                "discount": get_discount("first_offense", 0.25),
                "requires_approval": get_requires_approval("first_offense", True)
            })

        return applicable_rules

    def calculate_final_fine(self, fine_amount: float, applicable_rules: List[dict], approved_rules: Set[str]) -> PolicyResult:
        """
        Computes final fine value, summing up approved discounts up to 100%.
        """
        total_discount = 0.0
        applied_names = []
        requires_approval_names = []

        for rule in applicable_rules:
            name = rule["name"]
            discount = rule["discount"]
            req_app = rule["requires_approval"]

            if req_app:
                requires_approval_names.append(name)
                if name in approved_rules:
                    total_discount += discount
                    applied_names.append(name)
            else:
                total_discount += discount
                applied_names.append(name)

        if total_discount > 1.0:
            total_discount = 1.0

        final_fine = fine_amount * (1.0 - total_discount)
        return PolicyResult(fine_amount, final_fine, applied_names, requires_approval_names)

    def apply(
        self,
        fine_amount: float,
        reader,
        loan,
        history_records: List[dict] = None,
        system_delay: bool = False,
        book_donation: bool = False,
        approved_rules: Set[str] = None
    ) -> PolicyResult:
        """
        Evaluates applicable rules and calculates the final fine after approved discounts.
        """
        if approved_rules is None:
            approved_rules = set()
        applicable_rules = self.evaluate_rules(
            fine_amount=fine_amount,
            reader=reader,
            loan=loan,
            history_records=history_records or [],
            system_delay=system_delay,
            book_donation=book_donation
        )
        return self.calculate_final_fine(fine_amount, applicable_rules, approved_rules)

