import sys
import logging
from src.infra.adapters import INIConfigAdapter, JSONPersistenceAdapter, LoanHistoryAdapter, setup_logger
from src.infra.cli import CLIController, CLIFormatter
from src.domain.entities import DomainError
from src.app.ports import IConfigProvider, ILibraryRepository, ILoanHistoryRepository
from src.domain.events import EventDispatcher
from src.infra.listeners import bootstrap_listeners
from src.app.use_cases import CheckoutUseCase, ReturnUseCase, ReserveUseCase, WaiveFineUseCase, GenerateReportUseCase
from src.infra.di import DIContainer

def main() -> None:
    """
    Bootstrap entrypoint. Configures UTF-8 terminal encoding, setups logger, config provider, persistence, and executes CLIController.
    """
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
    try:
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

    try:
        setup_logger()
    except PermissionError as e:
        print(f"🔴 \033[91m[ERROR]\033[0m Permission failure configuring logs: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"🔴 \033[91m[ERROR]\033[0m Error initializing logs: {e}")
        sys.exit(1)

    try:
        config = INIConfigAdapter("config.ini")
    except PermissionError as e:
        print(CLIFormatter.format_error(f"Permission failure reading configuration file (config.ini): {e}"))
        sys.exit(1)
    except Exception as e:
        print(CLIFormatter.format_error(f"Error reading configuration file: {e}"))
        sys.exit(1)

    try:
        repo = JSONPersistenceAdapter("db_backup.json")
    except PermissionError as e:
        print(CLIFormatter.format_error(f"Permission failure accessing database (db_backup.json): {e}"))
        sys.exit(1)
    except DomainError as e:
        print(CLIFormatter.format_error(f"Critical persistence/integrity failure: {e}"))
        sys.exit(1)
    except Exception as e:
        print(CLIFormatter.format_error(f"Error initializing database: {e}"))
        sys.exit(1)

    # Bootstrap the Dependency Injection (DI) Container
    container = DIContainer()
    
    # Register Core Infrastructure Adapters
    container.register(IConfigProvider, config)
    container.register(ILibraryRepository, repo)
    
    try:
        history_repo = LoanHistoryAdapter("loan_history.json")
    except Exception as e:
        print(CLIFormatter.format_error(f"Error initializing loan history database: {e}"))
        sys.exit(1)
    container.register(ILoanHistoryRepository, history_repo)
    
    # Register Pub/Sub Event System
    container.register(EventDispatcher, EventDispatcher)
    
    # Bootstrap and wire up domain event listeners
    dispatcher = container.resolve(EventDispatcher)
    bootstrap_listeners(dispatcher, history_repo)
    
    # Register Application Use Cases
    container.register(CheckoutUseCase, CheckoutUseCase)
    container.register(ReturnUseCase, ReturnUseCase)
    container.register(ReserveUseCase, ReserveUseCase)
    container.register(WaiveFineUseCase, WaiveFineUseCase)
    container.register(GenerateReportUseCase, GenerateReportUseCase)
    
    # Register CLI router
    container.register(CLIController, CLIController)

    # Resolve root controller from the container
    try:
        controller = container.resolve(CLIController)
    except Exception as e:
        print(CLIFormatter.format_error(f"Error resolving application dependencies: {e}"))
        sys.exit(1)

    args = sys.argv[1:]
    
    try:
        output = controller.execute(args)
        print(output)
    except PermissionError as e:
        print(CLIFormatter.format_error(f"Permission failure during command execution: {e}"))
        sys.exit(1)
    except Exception as e:
        print(CLIFormatter.format_error(f"Unexpected error during execution: {e}"))
        sys.exit(1)

if __name__ == "__main__":
    main()
