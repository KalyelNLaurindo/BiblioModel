import pytest
from datetime import date, timedelta
from src.domain.entities import ReaderEntity, LoanEntity, BookEntity
from src.domain.policy import FinePolicyEngine

class DummyConfigProvider:
    def __init__(self, policy_dict=None):
        self.policy_dict = policy_dict or {}

    def get_fine_policy(self) -> dict:
        return self.policy_dict


def test_policy_engine_pcd_waiver_100_percent():
    # PCD reader gets 100% discount, no approval required
    config = DummyConfigProvider()
    engine = FinePolicyEngine(config)
    
    reader = ReaderEntity(reader_id="R001", name="PCD Reader", reader_type="PCD")
    loan = LoanEntity(loan_id="L001", book_id="B001", reader_id="R001", checkout_date=date(2026, 6, 1), due_date=date(2026, 6, 8))
    
    # 10.0 fine, PCD reader
    result = engine.apply(
        fine_amount=10.0,
        reader=reader,
        loan=loan,
        history_records=[],
        system_delay=False,
        book_donation=False
    )
    
    assert result.original_fine == 10.0
    assert result.final_fine == 0.0
    assert "PCD Waiver" in result.applied_rules
    assert result.discount_amount == 10.0


def test_policy_engine_system_delay_100_percent():
    # System delay gets 100% discount, no approval required
    config = DummyConfigProvider()
    engine = FinePolicyEngine(config)
    
    reader = ReaderEntity(reader_id="R001", name="Regular Reader", reader_type="Regular")
    loan = LoanEntity(loan_id="L001", book_id="B001", reader_id="R001", checkout_date=date(2026, 6, 1), due_date=date(2026, 6, 8))
    
    result = engine.apply(
        fine_amount=20.0,
        reader=reader,
        loan=loan,
        history_records=[],
        system_delay=True,
        book_donation=False
    )
    
    assert result.original_fine == 20.0
    assert result.final_fine == 0.0
    assert "System Delay Waiver" in result.applied_rules


def test_policy_engine_first_offense_requires_approval():
    # First offense gets 25% discount, requires approval
    config = DummyConfigProvider()
    engine = FinePolicyEngine(config)
    
    reader = ReaderEntity(reader_id="R001", name="Regular Reader", reader_type="Regular")
    loan = LoanEntity(loan_id="L001", book_id="B001", reader_id="R001", checkout_date=date(2026, 6, 1), due_date=date(2026, 6, 8))
    
    # Without approval
    result_no_app = engine.apply(
        fine_amount=10.0,
        reader=reader,
        loan=loan,
        history_records=[], # no past history records with fine > 0
        system_delay=False,
        book_donation=False,
        approved_rules=set()
    )
    assert result_no_app.final_fine == 10.0
    assert "First Offense Discount" in result_no_app.requires_approval_rules
    assert "First Offense Discount" not in result_no_app.applied_rules
    
    # With approval
    result_app = engine.apply(
        fine_amount=10.0,
        reader=reader,
        loan=loan,
        history_records=[],
        system_delay=False,
        book_donation=False,
        approved_rules={"First Offense Discount"}
    )
    assert result_app.final_fine == 7.5
    assert "First Offense Discount" in result_app.applied_rules


def test_policy_engine_book_donation_requires_approval():
    # Book donation gets 50% discount, requires approval
    config = DummyConfigProvider()
    engine = FinePolicyEngine(config)
    
    reader = ReaderEntity(reader_id="R001", name="Regular Reader", reader_type="Regular")
    loan = LoanEntity(loan_id="L001", book_id="B001", reader_id="R001", checkout_date=date(2026, 6, 1), due_date=date(2026, 6, 8))
    
    # Without approval
    result_no_app = engine.apply(
        fine_amount=10.0,
        reader=reader,
        loan=loan,
        history_records=[{"fine_amount": 5.0}], # has past fine, so first offense not applicable
        system_delay=False,
        book_donation=True,
        approved_rules=set()
    )
    assert result_no_app.final_fine == 10.0
    assert "Book Donation Discount" in result_no_app.requires_approval_rules
    assert "Book Donation Discount" not in result_no_app.applied_rules
    
    # With approval
    result_app = engine.apply(
        fine_amount=10.0,
        reader=reader,
        loan=loan,
        history_records=[{"fine_amount": 5.0}],
        system_delay=False,
        book_donation=True,
        approved_rules={"Book Donation Discount"}
    )
    assert result_app.final_fine == 5.0
    assert "Book Donation Discount" in result_app.applied_rules


def test_policy_engine_multiple_additive_max_100_percent():
    # First Offense (25%) + Book Donation (50%) = 75%
    config = DummyConfigProvider()
    engine = FinePolicyEngine(config)
    
    reader = ReaderEntity(reader_id="R001", name="Regular Reader", reader_type="Regular")
    loan = LoanEntity(loan_id="L001", book_id="B001", reader_id="R001", checkout_date=date(2026, 6, 1), due_date=date(2026, 6, 8))
    
    result = engine.apply(
        fine_amount=100.0,
        reader=reader,
        loan=loan,
        history_records=[],
        system_delay=False,
        book_donation=True,
        approved_rules={"First Offense Discount", "Book Donation Discount"}
    )
    assert result.final_fine == 25.0 # 75% discount
    
    # If we add system delay (100%), total discount is capped at 100%
    result_all = engine.apply(
        fine_amount=100.0,
        reader=reader,
        loan=loan,
        history_records=[],
        system_delay=True,
        book_donation=True,
        approved_rules={"First Offense Discount", "Book Donation Discount"}
    )
    assert result_all.final_fine == 0.0


def test_policy_engine_config_overrides():
    # Load overrides from config
    config = DummyConfigProvider({
        "first_offense_discount": "40",
        "first_offense_requires_approval": "false",
        "pcd_discount": "80",
        "pcd_requires_approval": "true"
    })
    engine = FinePolicyEngine(config)
    
    reader = ReaderEntity(reader_id="R001", name="PCD Reader", reader_type="PCD")
    loan = LoanEntity(loan_id="L001", book_id="B001", reader_id="R001", checkout_date=date(2026, 6, 1), due_date=date(2026, 6, 8))
    
    # PCD now requires approval, and is 80% discount. First offense does not require approval and is 40%.
    # First offense applies (no past fines).
    # PCD applies.
    # Total with PCD approved: 40% + 80% = 120% capped at 100% -> 0.0 fine
    result = engine.apply(
        fine_amount=10.0,
        reader=reader,
        loan=loan,
        history_records=[],
        system_delay=False,
        book_donation=False,
        approved_rules={"PCD Waiver"}
    )
    assert result.final_fine == 0.0
    assert "PCD Waiver" in result.applied_rules
    assert "First Offense Discount" in result.applied_rules
    
    # PCD without approval: only First Offense applies (40% discount) -> 6.0 fine
    result_no_pcd_app = engine.apply(
        fine_amount=10.0,
        reader=reader,
        loan=loan,
        history_records=[],
        system_delay=False,
        book_donation=False,
        approved_rules=set()
    )
    assert result_no_pcd_app.final_fine == 6.0
    assert "PCD Waiver" not in result_no_pcd_app.applied_rules
    assert "First Offense Discount" in result_no_pcd_app.applied_rules


def test_return_use_case_with_pcd_waiver_100_percent():
    from tests.test_use_cases import FakeLibraryRepository, FakeConfigProvider
    from src.app.use_cases import ReturnUseCase
    from tests.test_loan_history import FakeLoanHistoryRepository
    
    repo = FakeLibraryRepository()
    config = FakeConfigProvider()
    config._daily_fine_rate = 2.0
    config._grace_period_days = 0
    history_repo = FakeLoanHistoryRepository()
    
    book = BookEntity("B1", "Title 1")
    # PCD Reader type
    reader = ReaderEntity("R1", "PCD Reader", reader_type="PCD")
    
    checkout_date = date.today() - timedelta(days=10)
    due_date = checkout_date + timedelta(days=7)
    loan = LoanEntity("L1", "B1", "R1", checkout_date, due_date)
    
    book.loan_to("R1")
    reader.add_loan(loan)
    
    repo.save_book(book)
    repo.save_reader(reader)
    repo.save_loan(loan)
    
    return_use_case = ReturnUseCase(repo, config, history_repo)
    # 3 days late -> 6.0 gross fine, but 0.0 final fine because PCD
    returned_loan = return_use_case.execute("B1", date.today())
    
    assert returned_loan.fine_amount == 0.0
    assert reader.fine_balance == 0.0
    
    assert len(history_repo.history) == 1
    record = history_repo.history[0]
    assert record["fine_amount"] == 0.0
    assert record["original_fine"] == 6.0
    assert "PCD Waiver" in record["applied_rules"]


def test_return_use_case_first_offense_requires_approval_flow():
    from tests.test_use_cases import FakeLibraryRepository, FakeConfigProvider
    from src.app.use_cases import ReturnUseCase
    from tests.test_loan_history import FakeLoanHistoryRepository
    
    # 1. Without operator approval
    repo = FakeLibraryRepository()
    config = FakeConfigProvider()
    config._daily_fine_rate = 2.0
    config._grace_period_days = 0
    history_repo = FakeLoanHistoryRepository()
    
    book = BookEntity("B1", "Title 1")
    reader = ReaderEntity("R1", "Common Reader", reader_type="Regular")
    
    checkout_date = date.today() - timedelta(days=10)
    due_date = checkout_date + timedelta(days=7)
    loan = LoanEntity("L1", "B1", "R1", checkout_date, due_date)
    
    book.loan_to("R1")
    reader.add_loan(loan)
    
    repo.save_book(book)
    repo.save_reader(reader)
    repo.save_loan(loan)
    
    return_use_case = ReturnUseCase(repo, config, history_repo)
    
    # Evaluate return: should return 6.0 gross fine and candidate rules
    gross, applicable = return_use_case.evaluate_return("B1", date.today())
    assert gross == 6.0
    assert len(applicable) == 1
    assert applicable[0]["name"] == "First Offense Discount"
    assert applicable[0]["requires_approval"] is True
    
    # Return book without passing approved_rules -> First Offense Discount is not applied -> 6.0 fine
    returned_loan = return_use_case.execute("B1", date.today(), approved_rules=set())
    assert returned_loan.fine_amount == 6.0
    assert reader.fine_balance == 6.0
    
    # 2. With operator approval
    repo = FakeLibraryRepository()
    reader2 = ReaderEntity("R2", "Common Reader 2", reader_type="Regular")
    loan2 = LoanEntity("L2", "B2", "R2", checkout_date, due_date)
    book2 = BookEntity("B2", "Title 2")
    book2.loan_to("R2")
    reader2.add_loan(loan2)
    repo.save_book(book2)
    repo.save_reader(reader2)
    repo.save_loan(loan2)
    
    return_use_case = ReturnUseCase(repo, config, history_repo)
    # Return book passing First Offense Discount approved -> 25% discount -> 4.5 fine
    returned_loan2 = return_use_case.execute(
        "B2", date.today(),
        approved_rules={"First Offense Discount"},
        operator="SuperLibrarian"
    )
    assert returned_loan2.fine_amount == 4.5
    assert reader2.fine_balance == 4.5
    
    # Audit log validation
    record = history_repo.history[-1]
    assert record["fine_amount"] == 4.5
    assert record["original_fine"] == 6.0
    assert "First Offense Discount" in record["applied_rules"]
    assert record["operator"] == "SuperLibrarian"


def test_cli_return_with_approval_prompt_yes(monkeypatch):
    from tests.test_use_cases import FakeLibraryRepository, FakeConfigProvider
    from tests.test_loan_history import FakeLoanHistoryRepository
    from src.infra.cli import CLIController
    
    repo = FakeLibraryRepository()
    config = FakeConfigProvider()
    config._daily_fine_rate = 2.0
    config._grace_period_days = 0
    history_repo = FakeLoanHistoryRepository()
    
    book = BookEntity("B1", "Title 1")
    reader = ReaderEntity("R1", "Alice", reader_type="Regular")
    
    checkout_date = date.today() - timedelta(days=10)
    due_date = checkout_date + timedelta(days=7)
    loan = LoanEntity("L1", "B1", "R1", checkout_date, due_date)
    
    book.loan_to("R1")
    reader.add_loan(loan)
    
    repo.save_book(book)
    repo.save_reader(reader)
    repo.save_loan(loan)
    
    controller = CLIController(repo, config, history_repo)
    
    # Mock user input to return "s" (yes) for the prompt
    monkeypatch.setattr("builtins.input", lambda _: "s")
    
    res = controller.execute(["return", "--book", "B1"])
    assert "returned" in res
    assert "Late return fine: $4.50" in res  # 6.0 original, 25% discount applied -> 4.5
    
    # Verify the loan has 4.5 fine
    assert repo.get_reader("R1").fine_balance == 4.5


def test_cli_return_with_approval_prompt_no(monkeypatch):
    from tests.test_use_cases import FakeLibraryRepository, FakeConfigProvider
    from tests.test_loan_history import FakeLoanHistoryRepository
    from src.infra.cli import CLIController
    
    repo = FakeLibraryRepository()
    config = FakeConfigProvider()
    config._daily_fine_rate = 2.0
    config._grace_period_days = 0
    history_repo = FakeLoanHistoryRepository()
    
    book = BookEntity("B1", "Title 1")
    reader = ReaderEntity("R1", "Alice", reader_type="Regular")
    
    checkout_date = date.today() - timedelta(days=10)
    due_date = checkout_date + timedelta(days=7)
    loan = LoanEntity("L1", "B1", "R1", checkout_date, due_date)
    
    book.loan_to("R1")
    reader.add_loan(loan)
    
    repo.save_book(book)
    repo.save_reader(reader)
    repo.save_loan(loan)
    
    controller = CLIController(repo, config, history_repo)
    
    # Mock user input to return "n" (no) for the prompt
    monkeypatch.setattr("builtins.input", lambda _: "n")
    
    res = controller.execute(["return", "--book", "B1"])
    assert "returned" in res
    assert "Late return fine: $6.00" in res  # 6.0 original, no discount
    
    # Verify the loan has 6.0 fine
    assert repo.get_reader("R1").fine_balance == 6.0


def test_cli_return_with_system_delay_flag():
    from tests.test_use_cases import FakeLibraryRepository, FakeConfigProvider
    from tests.test_loan_history import FakeLoanHistoryRepository
    from src.infra.cli import CLIController
    
    repo = FakeLibraryRepository()
    config = FakeConfigProvider()
    config._daily_fine_rate = 2.0
    config._grace_period_days = 0
    history_repo = FakeLoanHistoryRepository()
    
    book = BookEntity("B1", "Title 1")
    # Even if they have a history of fines, system delay should waive it
    reader = ReaderEntity("R1", "Alice", reader_type="Regular")
    # pre-populate history with fine > 0 to rule out first offense
    history_repo.archive_loan(
        LoanEntity("L0", "B0", "R1", date.today(), date.today(), date.today(), 10.0),
        "B0", "RETURNED_LATE", 5
    )
    
    checkout_date = date.today() - timedelta(days=10)
    due_date = checkout_date + timedelta(days=7)
    loan = LoanEntity("L1", "B1", "R1", checkout_date, due_date)
    
    book.loan_to("R1")
    reader.add_loan(loan)
    
    repo.save_book(book)
    repo.save_reader(reader)
    repo.save_loan(loan)
    
    controller = CLIController(repo, config, history_repo)
    
    # Run with system-delay flag. Should waive 100% fine, no prompt.
    res = controller.execute(["return", "--book", "B1", "--system-delay"])
    assert "returned" in res
    assert "Late return fine" not in res  # fine is 0
    assert repo.get_reader("R1").fine_balance == 0.0


