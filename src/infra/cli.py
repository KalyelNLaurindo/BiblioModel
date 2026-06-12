import argparse
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

        try:
            parsed_args = parser.parse_args(args)
        except (argparse.ArgumentError, ValueError) as err:
            return f"Error parsing arguments: {str(err)}"

        try:
            if parsed_args.command == "loan":
                loan_date = date.today()
                if parsed_args.date:
                    try:
                        loan_date = date.fromisoformat(parsed_args.date)
                    except ValueError:
                        return f"Error parsing arguments: Invalid date format: '{parsed_args.date}'. Expected YYYY-MM-DD."
                
                loan = self.checkout_use_case.execute(
                    reader_id=parsed_args.reader,
                    book_id=parsed_args.book,
                    checkout_date=loan_date
                )
                return f"Success: Book '{parsed_args.book}' loaned to Reader '{parsed_args.reader}' until {loan.due_date.isoformat()}."

            elif parsed_args.command == "return":
                return_date = date.today()
                if parsed_args.date:
                    try:
                        return_date = date.fromisoformat(parsed_args.date)
                    except ValueError:
                        return f"Error parsing arguments: Invalid date format: '{parsed_args.date}'. Expected YYYY-MM-DD."
                
                loan = self.return_use_case.execute(
                    book_id=parsed_args.book,
                    return_date=return_date
                )
                
                msg = f"Success: Book '{parsed_args.book}' returned."
                if loan.fine_amount > 0:
                    msg += f" Late return fine: ${loan.fine_amount:.2f}."
                return msg

            elif parsed_args.command == "reserve":
                self.reserve_use_case.execute(
                    reader_id=parsed_args.reader,
                    book_id=parsed_args.book
                )
                return f"Success: Book '{parsed_args.book}' reserved for Reader '{parsed_args.reader}'."

            elif parsed_args.command == "report":
                # Basic placeholder report implementation, to be expanded in TSK-13
                return "Success: Basic library state report generated."

            else:
                return "Unknown command"

        except DomainError as de:
            return f"Business Rule Error: {str(de)}"
        except Exception as e:
            return f"System Error: {str(e)}"
