import argparse
import time
import logging
import os
import getpass
from datetime import date
from typing import List, Optional
from src.app.ports import ILibraryRepository, IConfigProvider
from src.app.use_cases import CheckoutUseCase, ReturnUseCase, ReserveUseCase, WaiveFineUseCase, GenerateReportUseCase
from src.domain.entities import DomainError
from src.app.validators import InputValidator

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
    @staticmethod
    def format_ok(message: str) -> str:
        return f"🟢 \033[92m[OK]\033[0m {message}"

    @staticmethod
    def format_warn(message: str) -> str:
        return f"🟡 \033[93m[WARN]\033[0m {message}"

    @staticmethod
    def format_error(message: str) -> str:
        return f"🔴 \033[91m[ERROR]\033[0m {message}"

    @staticmethod
    def format_hold(message: str) -> str:
        return f"🔵 \033[94m[HOLD]\033[0m {message}"

    @staticmethod
    def render_table(headers: List[str], rows: List[List[str]], max_col_width: int = 35) -> str:
        """
        Formats data rows into a single ASCII box table, truncating long fields.
        """
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

        top_border = "┌" + "┬".join("─" * (w + 2) for w in col_widths) + "┐\n"
        
        header_row = "│" + "│".join(f" {h.ljust(w)} " for h, w in zip(sanitized_headers, col_widths)) + "│"
        
        header_sep = "\n├" + "┼".join("─" * (w + 2) for w in col_widths) + "┤"
        
        row_strings = []
        for row in sanitized_rows:
            padded_row = row + [""] * (len(col_widths) - len(row))
            row_str = "│" + "│".join(f" {cell.ljust(w)} " for cell, w in zip(padded_row, col_widths)) + "│"
            row_strings.append(row_str)

        row_sep = "\n├" + "┼".join("─" * (w + 2) for w in col_widths) + "┤\n"
        rows_section = row_sep.join(row_strings)
        
        bottom_sep = "\n└" + "┴".join("─" * (w + 2) for w in col_widths) + "┘"

        table_str = top_border + header_row + header_sep
        if rows_section:
            table_str += "\n" + rows_section
        table_str += bottom_sep
        return table_str

    @staticmethod
    def get_welcome_banner() -> str:
        """
        CLI welcome banner.
        """
        banner = (
            "╔════════════════════════════════════════════════════════════════╗\n"
            "║                       BIBLIOMODEL CLI                          ║\n"
            "║            Library Loan Tracking & Business Rules              ║\n"
            "╚════════════════════════════════════════════════════════════════╝"
        )
        return banner


class CLIHelpSystem:
    """
    Generates library rules help text and usage examples.
    """
    @staticmethod
    def render_help(config_provider: IConfigProvider) -> str:
        banner = CLIFormatter.get_welcome_banner()
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

        # Build Rules section
        rules_str = (
            "┌────────────────────────────────────────────────────────────────┐\n"
            "│                     ACTIVE BUSINESS RULES                      │\n"
            "├────────────────────────────────────────────────────────────────┤\n"
            f"│  • Simultaneous Loan Limit: {max_loans:<35} │\n"
            f"│  • Loan Period: {str(loan_days) + ' days':<47} │\n"
            f"│  • Daily Fine Rate: ${fine_rate:<42.2f} │\n"
            f"│  • Grace Period: {str(grace_days) + ' days':<46} │\n"
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

    def __init__(self, repository: ILibraryRepository, config_provider: IConfigProvider) -> None:
        """
        Initializes use case controllers.
        """
        self.repository = repository
        self.config_provider = config_provider
        self.checkout_use_case = CheckoutUseCase(repository, config_provider)
        self.return_use_case = ReturnUseCase(repository, config_provider)
        self.reserve_use_case = ReserveUseCase(repository)
        self.waive_fine_use_case = WaiveFineUseCase(repository)
        self.generate_report_use_case = GenerateReportUseCase(repository)


    def execute(self, args: List[str]) -> str:
        """
        Dispatches command list to use cases and logs execution telemetry.
        """
        start_time = time.perf_counter()
        
        # Determine operator context
        try:
            operator = os.getlogin()
        except Exception:
            try:
                operator = getpass.getuser()
            except Exception:
                operator = "unknown_operator"

        logger = logging.getLogger("bibliomodel")

        # Intercept help, -h, --help
        if not args or "-h" in args or "--help" in args or "help" in args:
            help_output = CLIHelpSystem.render_help(self.config_provider)
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

        result_message = ""
        status = "unknown"


        try:
            try:
                parsed_args = parser.parse_args(args)
            except (argparse.ArgumentError, ValueError) as err:
                status = "parse_error"
                result_message = CLIFormatter.format_error(f"Error parsing arguments: {str(err)}")
                return result_message

            # Apply input validations
            if hasattr(parsed_args, "reader") and parsed_args.reader is not None:
                parsed_args.reader = InputValidator.sanitize_and_validate_reader_id(parsed_args.reader)
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
                result_message = CLIFormatter.format_ok(
                    f"Success: Book '{parsed_args.book}' loaned to Reader '{parsed_args.reader}' until {loan.due_date.isoformat()}."
                )

            elif parsed_args.command == "return":
                return_date = date.today()
                if parsed_args.date:
                    try:
                        return_date = date.fromisoformat(parsed_args.date)
                    except ValueError:
                        status = "parse_error"
                        result_message = CLIFormatter.format_error(
                            f"Error parsing arguments: Invalid date format: '{parsed_args.date}'. Expected YYYY-MM-DD."
                        )
                        return result_message
                
                loan = self.return_use_case.execute(
                    book_id=parsed_args.book,
                    return_date=return_date
                )
                
                status = "success"
                msg = f"Success: Book '{parsed_args.book}' returned."
                if loan.fine_amount > 0:
                    msg += f" Late return fine: ${loan.fine_amount:.2f}."
                    result_message = CLIFormatter.format_warn(msg)
                else:
                    result_message = CLIFormatter.format_ok(msg)

            elif parsed_args.command == "reserve":
                self.reserve_use_case.execute(
                    reader_id=parsed_args.reader,
                    book_id=parsed_args.book
                )
                status = "success"
                result_message = CLIFormatter.format_hold(
                    f"Success: Book '{parsed_args.book}' reserved for Reader '{parsed_args.reader}'."
                )

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
                    result_message = CLIFormatter.format_ok(
                        f"Success: {report_file} generated.\n{report_table}"
                    )
                except Exception as write_err:
                    status = "system_error"
                    result_message = CLIFormatter.format_error(f"Failed to write report file: {write_err}")

            elif parsed_args.command == "waive":
                if not parsed_args.operator or not parsed_args.reason:
                    status = "validation_error"
                    result_message = CLIFormatter.format_error("Operator name and reason parameters are required to waive fines.")
                    return result_message

                self.waive_fine_use_case.execute(parsed_args.reader)
                status = "success"
                # Log audit trail to the log file (required to be logged in bibliomodel.log)
                logger.warning(
                    f"AUDIT: Operator '{parsed_args.operator}' waived fine for Reader '{parsed_args.reader}' "
                    f"due to: '{parsed_args.reason}'"
                )
                result_message = CLIFormatter.format_ok(f"Success: Fine waived for Reader '{parsed_args.reader}'.")

            elif parsed_args.command == "list-books":
                books = self.repository.list_books()
                headers = ["Book ID", "Title", "Status", "Hold Queue"]
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
                headers = ["Reader ID", "Name", "Status", "Fine Balance", "Active Loans"]
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
                headers = ["Loan ID", "Book ID", "Reader ID", "Checkout Date", "Due Date", "Return Date", "Fine"]
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
                print(CLIFormatter.get_welcome_banner())
                print("Type 'exit' or 'quit' to exit the shell.")
                import shlex
                while True:
                    try:
                        line = input("bibliomodel> ")
                        if not line.strip():
                            continue
                        
                        try:
                            cmd_args = shlex.split(line)
                        except ValueError as shlex_err:
                            print(CLIFormatter.format_error(f"Command line split error: {shlex_err}"))
                            continue
                        
                        if not cmd_args:
                            continue
                        
                        if cmd_args[0] in ("exit", "quit"):
                            print("Goodbye!")
                            break
                        
                        if cmd_args[0] == "shell":
                            print(CLIFormatter.format_error("Already in shell mode."))
                            continue
                        
                        res = self.execute(cmd_args)
                        print(res)
                    except (KeyboardInterrupt, EOFError):
                        print("\nGoodbye!")
                        break
                    except Exception as loop_err:
                        print(CLIFormatter.format_error(f"Shell loop error: {loop_err}"))
                status = "success"
                result_message = "Interactive shell closed."

            elif parsed_args.command == "search-books":
                query = parsed_args.query
                books = self.repository.search_books(query)
                headers = ["Book ID", "Title", "Author", "Status", "Hold Queue"]
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
                headers = ["Reader ID", "Name", "Status", "Fine Balance", "Active Loans"]
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
                output_path = parsed_args.output
                if not output_path:
                    output_path = os.path.join("reports", f"export_{parsed_args.type}_{date.today().isoformat()}.{parsed_args.format}")

                # Prevent Path Traversal
                workspace_dir = os.path.abspath(".")
                target_path = os.path.abspath(output_path)
                if not target_path.startswith(workspace_dir):
                    status = "validation_error"
                    result_message = CLIFormatter.format_error("Security Error: Output path must be within the project workspace.")
                    return result_message

                # Create directory if it doesn't exist
                dir_name = os.path.dirname(target_path)
                if dir_name:
                    os.makedirs(dir_name, exist_ok=True)

                if parsed_args.type == "books":
                    headers = ["Book ID", "Title", "Author", "Status", "Hold Queue"]
                    rows = [[b.book_id, b.title, getattr(b, "author", ""), b.status, ", ".join(b.hold_queue)] for b in self.repository.list_books()]
                elif parsed_args.type == "readers":
                    headers = ["Reader ID", "Name", "Status", "Fine Balance", "Active Loans"]
                    rows = [[r.reader_id, r.name, r.status, f"${r.fine_balance:.2f}", ", ".join(l.loan_id for l in r.active_loans)] for r in self.repository.list_readers()]
                else: # loans
                    headers = ["Loan ID", "Book ID", "Reader ID", "Checkout Date", "Due Date", "Return Date", "Fine"]
                    rows = [[l.loan_id, l.book_id, l.reader_id, l.checkout_date.isoformat(), l.due_date.isoformat(), l.return_date.isoformat() if l.return_date else "Active", f"${l.fine_amount:.2f}"] for l in self.repository.list_loans()]

                if parsed_args.format == "csv":
                    import csv
                    with open(target_path, "w", newline="", encoding="utf-8") as f:
                        writer = csv.writer(f)
                        writer.writerow(headers)
                        writer.writerows(rows)
                else: # html
                    rows_html = ""
                    for row in rows:
                        cols_html = "".join(f"<td style='padding: 8px; border: 1px solid #ddd;'>{cell}</td>" for cell in row)
                        rows_html += f"<tr>{cols_html}</tr>"
                    headers_html = "".join(f"<th style='padding: 8px; border: 1px solid #ddd; background-color: #f4f4f4; text-align: left;'>{h}</th>" for h in headers)
                    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Library Report - {parsed_args.type.capitalize()}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; color: #333; }}
        table {{ border-collapse: collapse; width: 100%; margin-top: 15px; }}
        h1 {{ color: #2c3e50; }}
    </style>
</head>
<body>
    <h1>Library Report: {parsed_args.type.capitalize()}</h1>
    <p>Generated on: {date.today().isoformat()}</p>
    <table>
        <thead>
            <tr>{headers_html}</tr>
        </thead>
        <tbody>
            {rows_html}
        </tbody>
    </table>
</body>
</html>"""
                    with open(target_path, "w", encoding="utf-8") as f:
                        f.write(html_content)

                status = "success"
                result_message = CLIFormatter.format_ok(f"Success: Report exported to {output_path}")

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
                    result_message = CLIFormatter.format_ok("No overdue loans found.")
                    return result_message
                
                # Setup folder
                notif_dir = os.path.abspath(os.path.join(".", "notifications"))
                os.makedirs(notif_dir, exist_ok=True)
                
                # Import FineCalculator to calculate fines for notification details
                from src.domain.services import FineCalculator
                calc = FineCalculator()
                daily_rate = self.config_provider.get_daily_fine_rate()
                grace_period = self.config_provider.get_grace_period_days()
                
                # Check for SMTP config
                import configparser
                config_file = "config.ini"
                has_smtp = False
                smtp_host = ""
                smtp_port = 1025
                smtp_sender = "library@example.com"
                if os.path.exists(config_file):
                    try:
                        parser_ini = configparser.ConfigParser()
                        parser_ini.read(config_file)
                        if parser_ini.has_section("smtp"):
                            smtp_host = parser_ini.get("smtp", "host", fallback="")
                            smtp_port = parser_ini.getint("smtp", "port", fallback=1025)
                            smtp_sender = parser_ini.get("smtp", "sender", fallback="library@example.com")
                            if smtp_host:
                                has_smtp = True
                    except Exception:
                        pass
                
                success_count = 0
                for r_id, r_loans in reader_overdues.items():
                    reader = self.repository.get_reader(r_id)
                    if not reader:
                        continue # robustness: skip if reader not found
                    
                    # Compute expected fine
                    total_fine = 0.0
                    books_lines = []
                    for l in r_loans:
                        book = self.repository.get_book(l.book_id)
                        title = book.title if book else "Unknown Book"
                        fine = calc.calculate_fine(l.due_date, today, daily_rate, grace_period)
                        total_fine += fine
                        books_lines.append(f" - '{title}' (Due: {l.due_date.isoformat()}, Estimated Fine: ${fine:.2f})")
                    
                    msg = f"Dear {reader.name},\n\n"
                    msg += "This is a notification that you have overdue books in BiblioModel Library:\n"
                    msg += "\n".join(books_lines) + "\n\n"
                    msg += f"Total Outstanding Fine Balance: ${reader.fine_balance + total_fine:.2f}\n\n"
                    msg += "Return Instructions:\n"
                    msg += "Please return these books to the library as soon as possible to avoid further fines and suspension.\n"
                    msg += "Fines accumulate daily.\n\n"
                    msg += "Best regards,\nBiblioModel Library Management"
                    
                    # Save file
                    file_path = os.path.join(notif_dir, f"email_{r_id}_{today.isoformat()}.txt")
                    file_written = False
                    try:
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(msg)
                        file_written = True
                    except Exception as err:
                        logger.error(f"Failed to write notification file for {r_id}: {err}")
                    
                    if file_written:
                        success_count += 1
                        if has_smtp:
                            try:
                                import smtplib
                                from email.mime.text import MIMEText
                                reader_email = f"{r_id.lower()}@example.com"
                                mime_msg = MIMEText(msg)
                                mime_msg["Subject"] = "BiblioModel Overdue Book Notification"
                                mime_msg["From"] = smtp_sender
                                mime_msg["To"] = reader_email
                                with smtplib.SMTP(smtp_host, smtp_port, timeout=2) as server:
                                    server.sendmail(smtp_sender, [reader_email], mime_msg.as_string())
                            except Exception as smtp_err:
                                logger.warning(f"SMTP send failed for {r_id}: {smtp_err} (simulated file generated successfully)")
                
                status = "success"
                result_message = CLIFormatter.format_ok(f"Success: Simulated notifications sent to {success_count} readers.")



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
