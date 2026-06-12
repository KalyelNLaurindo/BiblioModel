import sys
import logging
from src.infra.adapters import INIConfigAdapter, JSONPersistenceAdapter, setup_logger
from src.infra.cli import CLIController, CLIFormatter
from src.domain.entities import DomainError

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

    controller = CLIController(repo, config)
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
