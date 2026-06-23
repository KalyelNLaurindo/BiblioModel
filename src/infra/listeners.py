import logging
from datetime import date
from src.domain.events import BookReturnedEvent, EventDispatcher
from src.app.ports import ILoanHistoryRepository

class ArchiveLoanListener:
    """
    Subscribes to BookReturnedEvent and persists the closed transaction record to the history database.
    """
    def __init__(self, history_repository: ILoanHistoryRepository) -> None:
        self.history_repository = history_repository

    def __call__(self, event: BookReturnedEvent) -> None:
        delay_days = (event.return_date - event.loan.due_date).days
        if delay_days < 0:
            delay_days = 0

        # Arbitrary grace period configuration check from ports/config is done inside UseCase,
        # but here we follow the existing return use case logic for final status.
        # Wait, how was final status calculated before?
        # final_status = "RETURNED_LATE" if delay_days > grace_period else "RETURNED_ON_TIME"
        # We can pass the status estimation, but since the event dispatcher needs to behave identically:
        # Wait, does the event contain the delay_days or status?
        # Actually, let's check: can we just calculate:
        # final_status = "RETURNED_LATE" if delay_days > 0 else "RETURNED_ON_TIME"
        # Wait! The original use case had:
        # final_status = "RETURNED_LATE" if delay_days > grace_period else "RETURNED_ON_TIME"
        # To avoid passing grace_period to the listener, we can either:
        # 1. Store final_status directly in BookReturnedEvent!
        # 2. Or pass grace_period.
        # Wait! Storing final_status or delay_days and final_status directly in the BookReturnedEvent is much simpler!
        # Let's check what the original return use case did:
        # delay_days = (return_date - loan.due_date).days
        # if delay_days < 0: delay_days = 0
        # final_status = "RETURNED_LATE" if delay_days > grace_period else "RETURNED_ON_TIME"
        # If we calculate final_status inside the use case and put it into the BookReturnedEvent, that is incredibly safe!
        # Let's update BookReturnedEvent to also have `final_status` and `delay_days`.
        # That means the listener is completely dumb and just delegates to the repository!
        # Yes! That is perfect. Let's do that!
        
        applied_rules_list = event.applied_rules if event.original_fine > 0.0 else None
        orig_fine_val = event.original_fine if event.original_fine > 0.0 else None
        opt_val = event.operator if event.original_fine > 0.0 else None

        # Archive the loan
        self.history_repository.archive_loan(
            loan=event.loan,
            book_title=event.book_title,
            final_status=event.final_status,
            delay_days=event.delay_days,
            applied_rules=applied_rules_list,
            original_fine=orig_fine_val,
            operator=opt_val
        )


class AuditLogListener:
    """
    Subscribes to BookReturnedEvent and emits auditing warnings if discounts or waivers were applied.
    """
    def __call__(self, event: BookReturnedEvent) -> None:
        if event.original_fine > 0.0 and event.fine_amount < event.original_fine:
            logger = logging.getLogger("bibliomodel")
            applied_str = ", ".join(event.applied_rules)
            logger.info(
                f"AUDIT: Discount/Waiver applied for Reader '{event.reader_id}' on Loan '{event.loan_id}'. "
                f"Rules: [{applied_str}] | Original Fine: ${event.original_fine:.2f} | Final Fine: ${event.fine_amount:.2f} | "
                f"Operator: {event.operator}"
            )


def bootstrap_listeners(dispatcher: EventDispatcher, history_repository: ILoanHistoryRepository) -> None:
    """
    Wires up core infrastructure event subscribers to the central event dispatcher.
    """
    archive_listener = ArchiveLoanListener(history_repository)
    audit_listener = AuditLogListener()

    dispatcher.register(BookReturnedEvent, archive_listener)
    dispatcher.register(BookReturnedEvent, audit_listener)
