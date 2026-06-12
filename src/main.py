import sys
import logging
from src.infra.adapters import INIConfigAdapter, JSONPersistenceAdapter, setup_logger
from src.infra.cli import CLIController, CLIFormatter
from src.domain.entities import DomainError

def main() -> None:
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
        print(f"🔴 \033[91m[ERROR]\033[0m Falha de permissão ao configurar logs: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"🔴 \033[91m[ERROR]\033[0m Erro ao inicializar logs: {e}")
        sys.exit(1)

    try:
        config = INIConfigAdapter("config.ini")
    except PermissionError as e:
        print(CLIFormatter.format_error(f"Falha de permissão ao ler arquivo de configuração (config.ini): {e}"))
        sys.exit(1)
    except Exception as e:
        print(CLIFormatter.format_error(f"Erro ao ler arquivo de configuração: {e}"))
        sys.exit(1)

    try:
        repo = JSONPersistenceAdapter("db_backup.json")
    except PermissionError as e:
        print(CLIFormatter.format_error(f"Falha de permissão de acesso ao banco de dados (db_backup.json): {e}"))
        sys.exit(1)
    except DomainError as e:
        print(CLIFormatter.format_error(f"Falha crítica de persistência/integridade: {e}"))
        sys.exit(1)
    except Exception as e:
        print(CLIFormatter.format_error(f"Erro ao inicializar o banco de dados: {e}"))
        sys.exit(1)

    controller = CLIController(repo, config)
    args = sys.argv[1:]
    
    try:
        output = controller.execute(args)
        print(output)
    except PermissionError as e:
        print(CLIFormatter.format_error(f"Falha de permissão durante a execução do comando: {e}"))
        sys.exit(1)
    except Exception as e:
        print(CLIFormatter.format_error(f"Erro inesperado na execução: {e}"))
        sys.exit(1)

if __name__ == "__main__":
    main()
