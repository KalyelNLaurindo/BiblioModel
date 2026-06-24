import argparse
import time
import logging
import os
import getpass
from datetime import date
from typing import List, Optional
from src.app.ports import ILibraryRepository, IConfigProvider, ILoanHistoryRepository, INotificationService, IReportExporter, ITranslationService
from src.app.use_cases import CheckoutUseCase, ReturnUseCase, ReserveUseCase, WaiveFineUseCase, GenerateReportUseCase
from src.domain.entities import DomainError
from src.app.validators import InputValidator
from src.domain.events import EventDispatcher
from src.infra.listeners import bootstrap_listeners

class TestableArgumentParser(argparse.ArgumentParser):
    """
    Argparse subclass raising errors instead of using sys.exit, allowing safe test runs.
    """
    def error(self, message: str) -> None:
        raise argparse.ArgumentError(None, message)

    def exit(self, status: int = 0, message: Optional[str] = None) -> None:
        if message:
            raise ValueError(message)
        raise ValueError(f"ArgumentParser exited with status {status}")


class CLIFormatter:
    """
    Formats CLI messages with status badges and draws ASCII tables.
    """
    force_ascii: bool = False
    no_color: bool = False
    force_linear: bool = False
    _supports_unicode: Optional[bool] = None

    @classmethod
    def strip_ansi(cls, text: str) -> str:
        import re
        ansi_escape = re.compile(r'\x1b\[[0-9;]*m|\033\[[0-9;]*m')
        return ansi_escape.sub('', text)

    @classmethod
    def should_color(cls) -> bool:
        if cls.no_color:
            return False
        if "NO_COLOR" in os.environ:
            return False
        return True

    @classmethod
    def supports_unicode(cls) -> bool:
        if cls.force_ascii:
            return False
        if cls._supports_unicode is not None:
            return cls._supports_unicode
        if "PYTEST_CURRENT_TEST" in os.environ:
            cls._supports_unicode = True
            return True
        try:
            if sys.stdout and sys.stdout.encoding:
                encoding = sys.stdout.encoding.lower()
                if "utf" in encoding or "65001" in encoding:
                    cls._supports_unicode = True
                    return True
        except Exception:
            pass
        cls._supports_unicode = False
        return False

    @classmethod
    def format_ok(cls, message: str) -> str:
        if cls.supports_unicode():
            if cls.should_color():
                return f"🟢 \033[92m[SUCCESS]\033[0m {message}"
            return f"🟢 [SUCCESS] {message}"
        else:
            if cls.should_color():
                return f"(+) \033[92m[SUCCESS]\033[0m {message}"
            return f"(+) [SUCCESS] {message}"

    @classmethod
    def format_warn(cls, message: str) -> str:
        if cls.supports_unicode():
            if cls.should_color():
                return f"🟡 \033[93m[WARN]\033[0m {message}"
            return f"🟡 [WARN] {message}"
        else:
            if cls.should_color():
                return f"(*) \033[93m[WARN]\033[0m {message}"
            return f"(*) [WARN] {message}"

    @classmethod
    def format_error(cls, message: str) -> str:
        if cls.supports_unicode():
            if cls.should_color():
                return f"🔴 \033[91m[ERROR]\033[0m {message}"
            return f"🔴 [ERROR] {message}"
        else:
            if cls.should_color():
                return f"(x) \033[91m[ERROR]\033[0m {message}"
            return f"(x) [ERROR] {message}"

    @classmethod
    def format_hold(cls, message: str) -> str:
        if cls.supports_unicode():
            if cls.should_color():
                return f"🔵 \033[94m[HOLD]\033[0m {message}"
            return f"🔵 [HOLD] {message}"
        else:
            if cls.should_color():
                return f"(=) \033[94m[HOLD]\033[0m {message}"
            return f"(=) [HOLD] {message}"

    @classmethod
    def render_table(cls, headers: List[str], rows: List[List[str]], max_col_width: int = 35) -> str:
        """
        Formats data rows into a single ASCII box table, truncating long fields.
        """
        if cls.force_linear:
            lines = []
            for row in rows:
                item_lines = []
                for h, cell in zip(headers, row):
                    item_lines.append(f"{h}: {cell}")
                lines.append("\n".join(item_lines))
            return ("\n" + "-" * 40 + "\n").join(lines)
        sanitized_headers = []
        for h in headers:
            s_h = str(h)
            if len(s_h) > max_col_width:
                s_h = s_h[:max_col_width - 3] + "..."
            sanitized_headers.append(s_h)

        sanitized_rows = []
        for row in rows:
            sanitized_row = []
            for cell in row:
                s_cell = str(cell)
                if len(s_cell) > max_col_width:
                    s_cell = s_cell[:max_col_width - 3] + "..."
                sanitized_row.append(s_cell)
            sanitized_rows.append(sanitized_row)

        col_widths = [len(h) for h in sanitized_headers]
        for row in sanitized_rows:
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    col_widths[i] = max(col_widths[i], len(cell))
                else:
                    col_widths.append(len(cell))

        if cls.supports_unicode():
            t_top, t_mid, t_bot = "┌", "┬", "┐"
            t_horiz, t_vert = "─", "│"
            t_cross_mid = "┼"
            t_left_mid, t_right_mid = "├", "┤"
            t_bot_left, t_bot_mid, t_bot_right = "└", "┴", "┘"
        else:
            t_top, t_mid, t_bot = "+", "+", "+"
            t_horiz, t_vert = "-", "|"
            t_cross_mid = "+"
            t_left_mid, t_right_mid = "+", "+"
            t_bot_left, t_bot_mid, t_bot_right = "+", "+", "+"

        top_border = t_top + t_mid.join(t_horiz * (w + 2) for w in col_widths) + t_bot + "\n"
        
        header_row = t_vert + t_vert.join(f" {h.ljust(w)} " for h, w in zip(sanitized_headers, col_widths)) + t_vert
        
        header_sep = "\n" + t_left_mid + t_cross_mid.join(t_horiz * (w + 2) for w in col_widths) + t_right_mid
        
        row_strings = []
        for row in sanitized_rows:
            padded_row = row + [""] * (len(col_widths) - len(row))
            row_str = t_vert + t_vert.join(f" {cell.ljust(w)} " for cell, w in zip(padded_row, col_widths)) + t_vert
            row_strings.append(row_str)

        row_sep = "\n" + t_left_mid + t_cross_mid.join(t_horiz * (w + 2) for w in col_widths) + t_right_mid + "\n"
        rows_section = row_sep.join(row_strings)
        
        bottom_sep = "\n" + t_bot_left + t_bot_mid.join(t_horiz * (w + 2) for w in col_widths) + t_bot_right

        table_str = top_border + header_row + header_sep
        if rows_section:
            table_str += "\n" + rows_section
        table_str += bottom_sep
        return table_str

    @staticmethod
    def get_welcome_banner(translation_service=None) -> str:
        """
        CLI welcome banner.
        """
        title = "BIBLIOMODEL CLI"
        subtitle = "Library Loan Tracking & Business Rules"
        if translation_service:
            title = translation_service.translate("welcome_title")
            subtitle = translation_service.translate("welcome_subtitle")
            
        title_padded = f"║{title.center(64)}║\n"
        subtitle_padded = f"║{subtitle.center(64)}║\n"
        banner = (
            "╔════════════════════════════════════════════════════════════════╗\n"
            f"{title_padded}"
            f"{subtitle_padded}"
            "╚════════════════════════════════════════════════════════════════╝"
        )
        return banner


class CLIHelpSystem:
    """
    Generates library rules help text and usage examples.
    """
    @staticmethod
    def render_help(config_provider: IConfigProvider, translation_service=None) -> str:
        banner = CLIFormatter.get_welcome_banner(translation_service)
        try:
            max_loans = config_provider.get_max_loans()
            loan_days = config_provider.get_loan_period_days()
            fine_rate = config_provider.get_daily_fine_rate()
            grace_days = config_provider.get_grace_period_days()
        except Exception:
            max_loans = 3
            loan_days = 7
            fine_rate = 2.00
            grace_days = 0

        # Translate labels
        title_rules = "ACTIVE BUSINESS RULES"
        lbl_limit = "Simultaneous Loan Limit"
        lbl_period = "Loan Period"
        lbl_fine = "Daily Fine Rate"
        lbl_grace = "Grace Period"
        lbl_days = "days"
        if translation_service:
            title_rules = translation_service.translate("active_business_rules")
            lbl_limit = translation_service.translate("rule_limit")
            lbl_period = translation_service.translate("rule_period")
            lbl_fine = translation_service.translate("rule_fine")
            lbl_grace = translation_service.translate("rule_grace")
            lbl_days = translation_service.translate("days")

        rules_str = (
            "┌────────────────────────────────────────────────────────────────┐\n"
            f"│{title_rules.center(64)}│\n"
            "├────────────────────────────────────────────────────────────────┤\n"
            f"│  • {lbl_limit}: {max_loans:<35} │\n"
            f"│  • {lbl_period}: {str(loan_days) + ' ' + lbl_days:<47} │\n"
            f"│  • {lbl_fine}: ${fine_rate:<42.2f} │\n"
            f"│  • {lbl_grace}: {str(grace_days) + ' ' + lbl_days:<46} │\n"
            "└────────────────────────────────────────────────────────────────┘"
        )

        # Build Commands section
        commands_headers = ["Command", "Required / Optional Parameters", "Description"]
        commands_rows = [
            ["loan", "--book <id> --reader <id> [--date YYYY-MM-DD]", "Registers a book loan."],
            ["return", "--book <id> [--date YYYY-MM-DD]", "Registers a book return."],
            ["reserve", "--book <id> --reader <id>", "Reserves an unavailable book (FIFO Queue)."],
            ["report", "None", "Exports and displays the daily system status report."],
            ["waive", "--reader <id> --operator <name> --reason <reason>", "Performs an audited waive of fines."],
            ["list-books", "None", "Lists all books and reservation queues."],
            ["list-readers", "None", "Lists registered readers and balances."],
            ["list-loans", "None", "Lists the complete loan history."],
            ["shell", "None", "Starts the interactive multi-command console."],
            ["help", "None", "Displays this help panel and documentation."]
        ]
        commands_table = CLIFormatter.render_table(commands_headers, commands_rows, max_col_width=45)

        examples_str = (
            "USAGE EXAMPLES:\n"
            "  • Check Out Book:         bibliomodel loan --book B001 --reader R101\n"
            "  • Return Book:            bibliomodel return --book B001 --date 2026-06-15\n"
            "  • Place Reservation:      bibliomodel reserve --book B001 --reader R102\n"
            "  • Waive Reader Fine:      bibliomodel waive --reader R101 --operator \"Director\" --reason \"Dispute accepted\""
        )

        help_output = (
            f"{banner}\n\n"
            f"{rules_str}\n\n"
            f"AVAILABLE COMMANDS TABLE:\n{commands_table}\n\n"
            f"{examples_str}"
        )
        return help_output


class CLIController:
    """
    Parses command arguments and routes execution to target use cases.
    """

    def __init__(
        self,
        repository: ILibraryRepository,
        config_provider: IConfigProvider,
        history_repository: ILoanHistoryRepository = None,
        event_dispatcher: EventDispatcher = None,
        checkout_use_case: CheckoutUseCase = None,
        return_use_case: ReturnUseCase = None,
        reserve_use_case: ReserveUseCase = None,
        waive_fine_use_case: WaiveFineUseCase = None,
        generate_report_use_case: GenerateReportUseCase = None,
        notification_service: INotificationService = None,
        report_exporter: IReportExporter = None,
        translation_service: ITranslationService = None
    ) -> None:
        """
        Initializes use case controllers.
        """
        self.repository = repository
        self.config_provider = config_provider
        
        if history_repository is None:
            from src.infra.adapters import LoanHistoryAdapter
            self.history_repository = LoanHistoryAdapter("loan_history.json")
        else:
            self.history_repository = history_repository

        if event_dispatcher is None:
            self.event_dispatcher = EventDispatcher()
            bootstrap_listeners(self.event_dispatcher, self.history_repository)
        else:
            self.event_dispatcher = event_dispatcher

        self.checkout_use_case = checkout_use_case or CheckoutUseCase(repository, config_provider, dispatcher=self.event_dispatcher)
        self.return_use_case = return_use_case or ReturnUseCase(repository, config_provider, self.history_repository, dispatcher=self.event_dispatcher)
        self.reserve_use_case = reserve_use_case or ReserveUseCase(repository)
        self.waive_fine_use_case = waive_fine_use_case or WaiveFineUseCase(repository)
        self.generate_report_use_case = generate_report_use_case or GenerateReportUseCase(repository)

        if notification_service is None:
            from src.infra.smtp_adapter import SMTPNotificationService
            self.notification_service = SMTPNotificationService(config_provider)
        else:
            self.notification_service = notification_service

        if report_exporter is None:
            from src.infra.exporters import ReportExporter
            self.report_exporter = ReportExporter()
        else:
            self.report_exporter = report_exporter

        if translation_service is None:
            from src.infra.translation_service import TranslationService
            self.translation_service = TranslationService(config_provider)
        else:
            self.translation_service = translation_service



    def execute(self, args: List[str]) -> str:
        """
        Dispatches command list to use cases and logs execution telemetry.
        """
        start_time = time.perf_counter()
        
        # Intercept --no-color and --linear globally
        cleaned_args = list(args)
        no_color_val = False
        if "--no-color" in cleaned_args:
            no_color_val = True
            cleaned_args.remove("--no-color")
        CLIFormatter.no_color = no_color_val

        is_linear = False
        if "--linear" in cleaned_args:
            is_linear = True
            cleaned_args.remove("--linear")
        CLIFormatter.force_linear = is_linear

        # Extract --lang flag if present
        lang_val = None
        if "--lang" in cleaned_args:
            try:
                idx = cleaned_args.index("--lang")
                lang_val = cleaned_args[idx + 1]
                del cleaned_args[idx:idx+2]
            except Exception:
                pass

        if lang_val:
            try:
                self.translation_service.set_locale(lang_val)
            except ValueError:
                pass

        # Determine operator context
        try:
            operator = os.getlogin()
        except Exception:
            try:
                operator = getpass.getuser()
            except Exception:
                operator = "unknown_operator"

        logger = logging.getLogger("bibliomodel")

        # Default empty arguments to shell command
        if not cleaned_args:
            cleaned_args = ["shell"]

        # Intercept help, -h, --help
        if "-h" in cleaned_args or "--help" in cleaned_args or "help" in cleaned_args:
            help_output = CLIHelpSystem.render_help(self.config_provider, self.translation_service)
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            logger.info(
                f"Operator: {operator} | Command: {args} | "
                f"Status: success | Execution resolved in {elapsed_ms:.2f}ms"
            )
            return help_output

        
        parser = TestableArgumentParser(
            description="BiblioModel CLI Library Loan Tracking System",
            prog="bibliomodel"
        )
        
        subparsers = parser.add_subparsers(dest="command", required=True)

        # 1. loan command
        loan_parser = subparsers.add_parser("loan")
        loan_parser.add_argument("--reader", required=True, help="ID of the borrowing reader")
        loan_parser.add_argument("--book", required=True, help="ID of the book being checked out")
        loan_parser.add_argument("--date", help="Loan date in ISO format (YYYY-MM-DD), defaults to today")

        # 2. return command
        return_parser = subparsers.add_parser("return")
        return_parser.add_argument("--book", required=True, help="ID of the book being returned")
        return_parser.add_argument("--date", help="Return date in ISO format (YYYY-MM-DD), defaults to today")
        return_parser.add_argument("--system-delay", action="store_true", help="Flag to indicate institutional system delay")
        return_parser.add_argument("--book-donation", action="store_true", help="Flag to indicate book donation for fine discount")

        # 3. reserve command
        reserve_parser = subparsers.add_parser("reserve")
        reserve_parser.add_argument("--reader", required=True, help="ID of the reserving reader")
        reserve_parser.add_argument("--book", required=True, help="ID of the book being reserved")

        # 4. report command
        subparsers.add_parser("report")

        # 5. waive command
        waive_parser = subparsers.add_parser("waive")
        waive_parser.add_argument("--reader", required=True, help="ID of the reader whose fine is waived")
        waive_parser.add_argument("--operator", help="Name of the operator waiving the fine")
        waive_parser.add_argument("--reason", help="Reason for waiving the fine")

        # 6. list-books command
        subparsers.add_parser("list-books")

        # 7. list-readers command
        subparsers.add_parser("list-readers")

        # 8. list-loans command
        subparsers.add_parser("list-loans")

        # 9. shell command
        subparsers.add_parser("shell")

        # 10. help command
        subparsers.add_parser("help")

        # 11. search-books command
        search_books_parser = subparsers.add_parser("search-books")
        search_books_parser.add_argument("query", nargs="?", default="", help="Query to search books by title or author")

        # 12. search-readers command
        search_readers_parser = subparsers.add_parser("search-readers")
        search_readers_parser.add_argument("query", nargs="?", default="", help="Query to search readers by name")

        # 13. export command
        export_parser = subparsers.add_parser("export")
        export_parser.add_argument("--type", required=True, choices=["books", "readers", "loans"], help="Type of report to export")
        export_parser.add_argument("--format", required=True, choices=["csv", "html"], help="Format of the report")
        export_parser.add_argument("--output", help="Optional output path")

        # 14. notify-overdue command
        subparsers.add_parser("notify-overdue")

        # 15. check-overdue command
        subparsers.add_parser("check-overdue")

        # 16. reader-history command
        reader_history_parser = subparsers.add_parser("reader-history")
        reader_history_parser.add_argument("--reader-id", required=True, help="ID of the reader to query history for")
        reader_history_parser.add_argument("--last-n", type=int, help="Optional limit of history records to display")
        reader_history_parser.add_argument("--overdue-only", action="store_true", help="Only show overdue loans")
        reader_history_parser.add_argument("--export", help="Optional output path to export txt history")

        # 17. popularity-report command
        popularity_report_parser = subparsers.add_parser("popularity-report")
        popularity_report_parser.add_argument("--top", type=int, help="Limit ranking to top N books")
        popularity_report_parser.add_argument("--with-waitlist", action="store_true", help="Only show books with a waitlist")
        popularity_report_parser.add_argument("--underutilized", action="store_true", help="Only show underutilized books (0 checkouts in 90 days)")

        result_message = ""
        status = "unknown"


        try:
            try:
                parsed_args = parser.parse_args(cleaned_args)
            except (argparse.ArgumentError, ValueError) as err:
                status = "parse_error"
                result_message = CLIFormatter.format_error(f"Error parsing arguments: {str(err)}")
                return result_message

            # Apply input validations
            if hasattr(parsed_args, "reader") and parsed_args.reader is not None:
                parsed_args.reader = InputValidator.sanitize_and_validate_reader_id(parsed_args.reader)
            if hasattr(parsed_args, "reader_id") and parsed_args.reader_id is not None:
                parsed_args.reader_id = InputValidator.sanitize_and_validate_reader_id(parsed_args.reader_id)
            if hasattr(parsed_args, "book") and parsed_args.book is not None:
                parsed_args.book = InputValidator.sanitize_and_validate_book_id(parsed_args.book)
            if hasattr(parsed_args, "operator") and parsed_args.operator is not None:
                parsed_args.operator = InputValidator.sanitize_and_validate_general(parsed_args.operator, "operator")
            if hasattr(parsed_args, "reason") and parsed_args.reason is not None:
                parsed_args.reason = InputValidator.sanitize_and_validate_general(parsed_args.reason, "reason")

            if parsed_args.command == "loan":
                loan_date = date.today()
                if parsed_args.date:
                    try:
                        loan_date = date.fromisoformat(parsed_args.date)
                    except ValueError:
                        status = "parse_error"
                        result_message = CLIFormatter.format_error(
                            f"Error parsing arguments: Invalid date format: '{parsed_args.date}'. Expected YYYY-MM-DD."
                        )
                        return result_message
                
                loan = self.checkout_use_case.execute(
                    reader_id=parsed_args.reader,
                    book_id=parsed_args.book,
                    checkout_date=loan_date
                )
                status = "success"
                success_msg = self.translation_service.translate(
                    "loan_success",
                    book=parsed_args.book,
                    reader=parsed_args.reader,
                    due_date=loan.due_date.isoformat()
                )
                result_message = CLIFormatter.format_ok(success_msg)

            elif parsed_args.command == "return":
                return_date = date.today()
                if parsed_args.date:
                    try:
                        return_date = date.fromisoformat(parsed_args.date)
                    except ValueError:
                        status = "parse_error"
                        err_msg = self.translation_service.translate(
                            "error_parsing_arguments",
                            message=f"Invalid date format: '{parsed_args.date}'. Expected YYYY-MM-DD."
                        )
                        result_message = CLIFormatter.format_error(err_msg)
                        return result_message
                
                try:
                    gross_fine, applicable_rules = self.return_use_case.evaluate_return(
                        book_id=parsed_args.book,
                        return_date=return_date,
                        system_delay=parsed_args.system_delay,
                        book_donation=parsed_args.book_donation
                    )
                except DomainError as err:
                    status = "validation_error"
                    result_message = CLIFormatter.format_error(str(err))
                    return result_message

                approved_rules = set()
                if gross_fine > 0.0:
                    for rule in applicable_rules:
                        if rule.get("requires_approval", False):
                            rule_name = rule["name"]
                            discount_pct = int(rule["discount"] * 100)
                            prompt_msg = f"Rule '{rule_name}' ({discount_pct}% discount) requires operator approval. Apply? (s/n): "
                            try:
                                ans = input(prompt_msg).strip().lower()
                                if ans in ('s', 'sim', 'y', 'yes'):
                                    approved_rules.add(rule_name)
                            except (EOFError, IOError):
                                pass

                loan = self.return_use_case.execute(
                    book_id=parsed_args.book,
                    return_date=return_date,
                    system_delay=parsed_args.system_delay,
                    book_donation=parsed_args.book_donation,
                    approved_rules=approved_rules,
                    operator=operator
                )
                
                status = "success"
                msg = self.translation_service.translate("return_success", book=parsed_args.book)
                if loan.fine_amount > 0:
                    fine_msg = self.translation_service.translate("return_fine_message", fine=loan.fine_amount)
                    msg += fine_msg
                    result_message = CLIFormatter.format_warn(msg)
                else:
                    result_message = CLIFormatter.format_ok(msg)


            elif parsed_args.command == "reserve":
                self.reserve_use_case.execute(
                    reader_id=parsed_args.reader,
                    book_id=parsed_args.book
                )
                status = "success"
                success_msg = self.translation_service.translate(
                    "reserve_success",
                    book=parsed_args.book,
                    reader=parsed_args.reader
                )
                result_message = CLIFormatter.format_hold(success_msg)

            elif parsed_args.command == "report":
                report_data = self.generate_report_use_case.execute()
                report_content = (
                    "========================================\n"
                    "       DAILY LIBRARY STATUS REPORT      \n"
                    "========================================\n"
                    f"Date: {date.today().isoformat()}\n"
                    "----------------------------------------\n"
                    f"Total Active Loans: {report_data['total_active_loans']}\n"
                    f"Overdue Loans:      {report_data['total_overdue']}\n"
                    f"Total Unpaid Fees:  ${report_data['total_unpaid_fees']:.2f}\n"
                    f"Reserved Books Count: {report_data['reserved_books_count']}\n"
                    f"Total Hold Queue Size: {report_data['total_reservations']}\n"
                    "========================================\n"
                )
                
                # Generate visual table representation
                report_headers = ["Metric", "Value"]
                report_rows = [
                    ["Total Active Loans", str(report_data['total_active_loans'])],
                    ["Overdue Loans", str(report_data['total_overdue'])],
                    ["Total Unpaid Fees", f"${report_data['total_unpaid_fees']:.2f}"],
                    ["Reserved Books Count", str(report_data['reserved_books_count'])],
                    ["Total Hold Queue Size", str(report_data['total_reservations'])]
                ]
                report_table = CLIFormatter.render_table(report_headers, report_rows)
                
                report_file = "daily_handover_report.txt"
                try:
                    with open(report_file, "w", encoding="utf-8") as f:
                        f.write(report_content)
                    status = "success"
                    success_msg = self.translation_service.translate("report_success", report_file=report_file)
                    result_message = CLIFormatter.format_ok(
                        f"{success_msg}\n{report_table}"
                    )
                except Exception as write_err:
                    status = "system_error"
                    result_message = CLIFormatter.format_error(f"Failed to write report file: {write_err}")

            elif parsed_args.command == "waive":
                if not parsed_args.operator or not parsed_args.reason:
                    status = "validation_error"
                    err_msg = self.translation_service.translate("waive_params_required")
                    result_message = CLIFormatter.format_error(err_msg)
                    return result_message

                self.waive_fine_use_case.execute(parsed_args.reader)
                status = "success"
                # Log audit trail to the log file (required to be logged in bibliomodel.log)
                logger.warning(
                    f"AUDIT: Operator '{parsed_args.operator}' waived fine for Reader '{parsed_args.reader}' "
                    f"due to: '{parsed_args.reason}'"
                )
                success_msg = self.translation_service.translate("waive_success", reader=parsed_args.reader)
                result_message = CLIFormatter.format_ok(success_msg)

            elif parsed_args.command == "list-books":
                books = self.repository.list_books()
                headers = [
                    self.translation_service.translate("col_book_id"),
                    self.translation_service.translate("col_title"),
                    self.translation_service.translate("col_status"),
                    self.translation_service.translate("col_hold_queue")
                ]
                rows = []
                for b in books:
                    rows.append([
                        b.book_id,
                        b.title,
                        b.status,
                        ", ".join(b.hold_queue) if b.hold_queue else "None"
                    ])
                table = CLIFormatter.render_table(headers, rows)
                status = "success"
                result_message = table

            elif parsed_args.command == "list-readers":
                readers = self.repository.list_readers()
                headers = [
                    self.translation_service.translate("col_reader_id"),
                    self.translation_service.translate("col_name"),
                    self.translation_service.translate("col_status"),
                    self.translation_service.translate("col_fine_balance"),
                    self.translation_service.translate("col_active_loans")
                ]
                rows = []
                for r in readers:
                    active_loan_ids = [loan.loan_id for loan in r.active_loans]
                    rows.append([
                        r.reader_id,
                        r.name,
                        r.status,
                        f"${r.fine_balance:.2f}",
                        ", ".join(active_loan_ids) if active_loan_ids else "None"
                    ])
                table = CLIFormatter.render_table(headers, rows)
                status = "success"
                result_message = table

            elif parsed_args.command == "list-loans":
                loans = self.repository.list_loans()
                headers = [
                    self.translation_service.translate("col_loan_id"),
                    self.translation_service.translate("col_book_id"),
                    self.translation_service.translate("col_reader_id"),
                    self.translation_service.translate("col_checkout_date"),
                    self.translation_service.translate("col_due_date"),
                    self.translation_service.translate("col_return_date"),
                    self.translation_service.translate("col_fine")
                ]
                rows = []
                for l in loans:
                    rows.append([
                        l.loan_id,
                        l.book_id,
                        l.reader_id,
                        l.checkout_date.isoformat(),
                        l.due_date.isoformat(),
                        l.return_date.isoformat() if l.return_date else "Active",
                        f"${l.fine_amount:.2f}"
                    ])
                table = CLIFormatter.render_table(headers, rows)
                status = "success"
                result_message = table

            elif parsed_args.command == "shell":
                from src.infra.shell import InteractiveShell
                shell = InteractiveShell(self)
                result_message = shell.run()
                status = "success"

            elif parsed_args.command == "search-books":
                query = parsed_args.query
                books = self.repository.search_books(query)
                headers = [
                    self.translation_service.translate("col_book_id"),
                    self.translation_service.translate("col_title"),
                    self.translation_service.translate("col_author"),
                    self.translation_service.translate("col_status"),
                    self.translation_service.translate("col_hold_queue")
                ]
                rows = []
                for b in books:
                    rows.append([
                        b.book_id,
                        b.title,
                        getattr(b, "author", ""),
                        b.status,
                        ", ".join(b.hold_queue) if b.hold_queue else "None"
                    ])
                table = CLIFormatter.render_table(headers, rows)
                status = "success"
                result_message = table

            elif parsed_args.command == "search-readers":
                query = parsed_args.query
                readers = self.repository.search_readers(query)
                headers = [
                    self.translation_service.translate("col_reader_id"),
                    self.translation_service.translate("col_name"),
                    self.translation_service.translate("col_status"),
                    self.translation_service.translate("col_fine_balance"),
                    self.translation_service.translate("col_active_loans")
                ]
                rows = []
                for r in readers:
                    active_loan_ids = [loan.loan_id for loan in r.active_loans]
                    rows.append([
                        r.reader_id,
                        r.name,
                        r.status,
                        f"${r.fine_balance:.2f}",
                        ", ".join(active_loan_ids) if active_loan_ids else "None"
                    ])
                table = CLIFormatter.render_table(headers, rows)
                status = "success"
                result_message = table

            elif parsed_args.command == "export":
                if parsed_args.type == "books":
                    headers = ["Book ID", "Title", "Author", "Status", "Hold Queue"]
                    rows = [[b.book_id, b.title, getattr(b, "author", ""), b.status, ", ".join(b.hold_queue)] for b in self.repository.list_books()]
                elif parsed_args.type == "readers":
                    headers = ["Reader ID", "Name", "Status", "Fine Balance", "Active Loans"]
                    rows = [[r.reader_id, r.name, r.status, f"${r.fine_balance:.2f}", ", ".join(l.loan_id for l in r.active_loans)] for r in self.repository.list_readers()]
                else: # loans
                    headers = ["Loan ID", "Book ID", "Reader ID", "Checkout Date", "Due Date", "Return Date", "Fine"]
                    rows = [[l.loan_id, l.book_id, l.reader_id, l.checkout_date.isoformat(), l.due_date.isoformat(), l.return_date.isoformat() if l.return_date else "Active", f"${l.fine_amount:.2f}"] for l in self.repository.list_loans()]

                try:
                    exported_path = self.report_exporter.export_report(
                        report_type=parsed_args.type,
                        format_type=parsed_args.format,
                        headers=headers,
                        rows=rows,
                        output_path=parsed_args.output
                    )
                    status = "success"
                    success_msg = self.translation_service.translate("export_success", output_path=exported_path)
                    result_message = CLIFormatter.format_ok(success_msg)
                except PermissionError as perm_err:
                    status = "validation_error"
                    result_message = CLIFormatter.format_error(str(perm_err))
                except Exception as exp_err:
                    status = "system_error"
                    result_message = CLIFormatter.format_error(f"System Error: {str(exp_err)}")

            elif parsed_args.command == "notify-overdue":
                loans = self.repository.list_loans()
                today = date.today()
                overdue_loans = [l for l in loans if l.is_overdue(today)]
                
                # Group by reader
                reader_overdues = {}
                for l in overdue_loans:
                    reader_overdues.setdefault(l.reader_id, []).append(l)
                
                if not reader_overdues:
                    status = "success"
                    success_msg = self.translation_service.translate("no_overdue_loans_found")
                    result_message = CLIFormatter.format_ok(success_msg)
                    return result_message

                from src.domain.services import FineCalculator
                calc = FineCalculator()
                daily_rate = self.config_provider.get_daily_fine_rate()
                grace_period = self.config_provider.get_grace_period_days()

                success_count = 0
                for r_id, r_loans in reader_overdues.items():
                    reader = self.repository.get_reader(r_id)
                    if not reader:
                        continue
                    
                    # Prepare the data needed by INotificationService
                    total_fine = 0.0
                    loans_data = []
                    for l in r_loans:
                        book = self.repository.get_book(l.book_id)
                        title = book.title if book else "Unknown Book"
                        fine = calc.calculate_fine(l.due_date, today, daily_rate, grace_period)
                        total_fine += fine
                        loans_data.append({
                            "title": title,
                            "due_date": l.due_date.isoformat(),
                            "fine": fine
                        })
                    
                    reader_email = f"{r_id.lower()}@example.com"
                    sent = self.notification_service.send_overdue_notification(
                        reader_id=r_id,
                        reader_name=reader.name,
                        reader_email=reader_email,
                        reader_fine_balance=reader.fine_balance + total_fine,
                        overdue_loans=loans_data,
                        today=today
                    )
                    if sent:
                        success_count += 1

                status = "success"
                success_msg = self.translation_service.translate("notify_overdue_success", success_count=success_count)
                result_message = CLIFormatter.format_ok(success_msg)

            elif parsed_args.command == "check-overdue":
                readers = self.repository.list_readers()
                today = date.today()
                auto_suspend_days = self.config_provider.get_auto_suspend_overdue_days()
                
                suspended_count = 0
                for reader in readers:
                    old_status = reader.status
                    reader.update_status(today, auto_suspend_days)
                    if old_status != "Suspended" and reader.status == "Suspended":
                        suspended_count += 1
                        self.repository.save_reader(reader)
                        
                status = "success"
                success_msg = self.translation_service.translate("check_overdue_success", suspended_count=suspended_count)
                result_message = CLIFormatter.format_ok(success_msg)

            elif parsed_args.command == "reader-history":
                r_id = parsed_args.reader_id
                reader = self.repository.get_reader(r_id)
                if not reader:
                    raise DomainError("Reader not found")

                today = date.today()
                
                # 1. Fetch active loans
                active_records = []
                from src.domain.services import FineCalculator
                calc = FineCalculator()
                daily_rate = self.config_provider.get_daily_fine_rate()
                grace_period = self.config_provider.get_grace_period_days()

                for loan in reader.active_loans:
                    book = self.repository.get_book(loan.book_id)
                    title = book.title if book else "Unknown Book"
                    
                    delay = (today - loan.due_date).days
                    if delay < 0:
                        delay = 0
                    fine = calc.calculate_fine(loan.due_date, today, daily_rate, grace_period)
                    
                    active_records.append({
                        "loan_id": loan.loan_id,
                        "book_id": loan.book_id,
                        "book_title": title,
                        "reader_id": loan.reader_id,
                        "checkout_date": loan.checkout_date.isoformat(),
                        "due_date": loan.due_date.isoformat(),
                        "return_date": "Active",
                        "delay_days": delay,
                        "fine_amount": fine,
                        "final_status": "ACTIVE"
                    })

                # 2. Fetch past history
                past_records = self.history_repository.get_history_by_reader(r_id)

                # Merge
                all_records = active_records + past_records

                # Sort by checkout_date descending
                all_records.sort(key=lambda x: x["checkout_date"], reverse=True)

                # Filter overdue only
                if parsed_args.overdue_only:
                    all_records = [r for r in all_records if r["fine_amount"] > 0]

                # Limit by last_n
                if parsed_args.last_n is not None and parsed_args.last_n > 0:
                    all_records = all_records[:parsed_args.last_n]

                headers = [
                    self.translation_service.translate("col_title"),
                    self.translation_service.translate("col_checkout_date"),
                    self.translation_service.translate("col_return_date"),
                    self.translation_service.translate("col_delay"),
                    self.translation_service.translate("col_fine"),
                    self.translation_service.translate("col_status")
                ]
                rows = []
                for r in all_records:
                    rows.append([
                        r["book_title"],
                        r["checkout_date"],
                        r["return_date"],
                        str(r["delay_days"]),
                        f"${r['fine_amount']:.2f}",
                        r["final_status"]
                    ])

                table = CLIFormatter.render_table(headers, rows)

                if parsed_args.export:
                    # Prevent Path Traversal
                    workspace_dir = os.path.abspath(".")
                    target_path = os.path.abspath(parsed_args.export)
                    if not target_path.startswith(workspace_dir):
                        status = "validation_error"
                        result_message = CLIFormatter.format_error("Security Error: Export path must be within the project workspace.")
                        return result_message

                    dir_name = os.path.dirname(target_path)
                    if dir_name:
                        os.makedirs(dir_name, exist_ok=True)

                    # Create fixed-width format text
                    lines = []
                    lines.append(f"LOAN HISTORY REPORT - READER {r_id} ({reader.name})")
                    lines.append(f"Generated on: {today.isoformat()}")
                    lines.append("-" * 95)
                    header_line = f"{'Book Title':<30} | {'Checkout':<12} | {'Return':<12} | {'Delay':<8} | {'Fine':<10} | {'Status':<15}"
                    lines.append(header_line)
                    lines.append("-" * 95)
                    for row in rows:
                        row_line = f"{row[0][:30]:<30} | {row[1]:<12} | {row[2]:<12} | {row[3]:<8} | {row[4]:<10} | {row[5]:<15}"
                        lines.append(row_line)
                    lines.append("-" * 95)
                    
                    with open(target_path, "w", encoding="utf-8") as f:
                        f.write("\n".join(lines))
                    
                    status = "success"
                    result_message = CLIFormatter.format_ok(f"Success: History exported to {parsed_args.export}\n{table}")
                else:
                    status = "success"
                    result_message = table

            elif parsed_args.command == "popularity-report":
                books = self.repository.list_books()
                today = date.today()
                loans = self.repository.list_loans()
                
                history_records = []
                if hasattr(self, "history_repository") and self.history_repository:
                    history_records = getattr(self.history_repository, "_history", [])
                
                book_records = []
                for book in books:
                    waitlist_size = len(book.hold_queue)
                    
                    has_recent_active = any(
                        l.book_id == book.book_id and (today - l.checkout_date).days <= 90
                        for l in loans
                    )
                    
                    has_recent_past = False
                    for r in history_records:
                        if r["book_id"] == book.book_id:
                            try:
                                chk_dt = date.fromisoformat(r["checkout_date"])
                                if (today - chk_dt).days <= 90:
                                    has_recent_past = True
                                    break
                            except Exception:
                                pass
                                
                    has_recent_checkout = has_recent_active or has_recent_past
                    
                    book_records.append({
                        "book": book,
                        "checkout_count": getattr(book, "checkout_count", 0),
                        "waitlist_size": waitlist_size,
                        "has_recent_checkout": has_recent_checkout
                    })

                book_records.sort(key=lambda x: (x["checkout_count"], x["waitlist_size"]), reverse=True)

                if parsed_args.with_waitlist:
                    book_records = [r for r in book_records if r["waitlist_size"] > 0]

                if parsed_args.underutilized:
                    book_records = [r for r in book_records if not r["has_recent_checkout"]]

                if parsed_args.top is not None and parsed_args.top > 0:
                    book_records = book_records[:parsed_args.top]

                headers = [
                    self.translation_service.translate("col_rank"),
                    self.translation_service.translate("col_book_id"),
                    self.translation_service.translate("col_title"),
                    self.translation_service.translate("col_checkout_count"),
                    self.translation_service.translate("col_waitlist_size"),
                    self.translation_service.translate("col_status")
                ]
                rows = []
                for i, r in enumerate(book_records):
                    rows.append([
                        str(i + 1),
                        r["book"].book_id,
                        r["book"].title,
                        str(r["checkout_count"]),
                        str(r["waitlist_size"]),
                        r["book"].status
                    ])

                table = CLIFormatter.render_table(headers, rows)

                recommendations = []
                for r in book_records[:3]:
                    if r["waitlist_size"] >= 3:
                        import math
                        copies = math.ceil(r["waitlist_size"] / 3)
                        recommendations.append(
                            f"Recomendação: Adquirir {copies} cópias adicionais de '{r['book'].title}'"
                        )

                result_message = table
                if recommendations:
                    result_message += "\n\nRECOMENDAÇÕES DE AQUISIÇÃO:\n" + "\n".join(recommendations)

                status = "success"



            else:
                status = "unknown_command"
                result_message = CLIFormatter.format_error("Unknown command")

        except DomainError as de:
            status = "domain_error"
            result_message = CLIFormatter.format_error(f"Business Rule Error: {str(de)}")
        except Exception as e:
            status = "system_error"
            result_message = CLIFormatter.format_error(f"System Error: {str(e)}")
        finally:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            logger.info(
                f"Operator: {operator} | Command: {args} | "
                f"Status: {status} | Execution resolved in {elapsed_ms:.2f}ms"
            )

        return result_message
