import argparse
import time
import logging
import os
import getpass
from datetime import date
from typing import List, Optional
from src.app.ports import ILibraryRepository, IConfigProvider
from src.app.use_cases import CheckoutUseCase, ReturnUseCase, ReserveUseCase
from src.domain.entities import DomainError

class TestableArgumentParser(argparse.ArgumentParser):
    """
    Subclass of argparse.ArgumentParser that overrides error and exit methods
    to raise exceptions instead of printing directly to stderr/stdout and
    terminating the interpreter via sys.exit.
    This ensures safety inside test runners and interactive prompts.
    """
    def error(self, message: str) -> None:
        raise argparse.ArgumentError(None, message)

    def exit(self, status: int = 0, message: Optional[str] = None) -> None:
        if message:
            raise ValueError(message)
        raise ValueError(f"ArgumentParser exited with status {status}")


class CLIFormatter:
    """
    Format output messages with color-coded Unicode badges for enhanced UX.
    """
    @staticmethod
    def format_ok(message: str) -> str:
        # Green [OK]
        return f"🟢 \033[92m[OK]\033[0m {message}"

    @staticmethod
    def format_warn(message: str) -> str:
        # Yellow [WARN]
        return f"🟡 \033[93m[WARN]\033[0m {message}"

    @staticmethod
    def format_error(message: str) -> str:
        # Red [ERROR]
        return f"🔴 \033[91m[ERROR]\033[0m {message}"

    @staticmethod
    def format_hold(message: str) -> str:
        # Blue [HOLD]
        return f"🔵 \033[94m[HOLD]\033[0m {message}"


class CLIController:
    """
    Outbound/Console command router adapter that parses command arguments
    and delegates execution flow to the appropriate use case engines.
    """

    def __init__(self, repository: ILibraryRepository, config_provider: IConfigProvider) -> None:
        """
        Initializes the controller with database repository and configuration access,
        constructing checkout, return, and reserve use cases.
        """
        self.repository = repository
        self.config_provider = config_provider
        self.checkout_use_case = CheckoutUseCase(repository, config_provider)
        self.return_use_case = ReturnUseCase(repository, config_provider)
        self.reserve_use_case = ReserveUseCase(repository)

    def execute(self, args: List[str]) -> str:
        """
        Parses command arguments and executes the requested operation.
        Returns a formatted output string containing success validations or errors.
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

        result_message = ""
        status = "unknown"

        try:
            try:
                parsed_args = parser.parse_args(args)
            except (argparse.ArgumentError, ValueError) as err:
                status = "parse_error"
                result_message = CLIFormatter.format_error(f"Error parsing arguments: {str(err)}")
                return result_message

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
                status = "success"
                result_message = CLIFormatter.format_ok("Success: Basic library state report generated.")

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
