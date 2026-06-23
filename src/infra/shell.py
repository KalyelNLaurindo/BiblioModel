import shlex
from src.infra.cli import CLIFormatter

class InteractiveShell:
    """
    Encapsulates the interactive console / shell loop logic.
    """

    def __init__(self, controller) -> None:
        self.controller = controller

    def run(self) -> str:
        """
        Runs the interactive loop reading commands from stdin and writing to stdout.
        """
        print(CLIFormatter.get_welcome_banner())
        tip = (
            "💡 \033[96m[TIP]\033[0m Type \033[92m'help'\033[0m (without slashes) to view active rules & full command docs.\n\n"
            "Recommended Commands:\n"
            "  • \033[92mlist-books\033[0m          - Render all books & hold queues\n"
            "  • \033[92mlist-readers\033[0m        - Render all readers & fine balances\n"
            "  • \033[92mpopularity-report\033[0m   - Show book rankings & waitlists\n"
            "  • \033[92mreport\033[0m              - Generate daily handover status report\n"
            "  • \033[93mexit\033[0m / \033[93mquit\033[0m         - Close the interactive console\n"
        )
        print(tip)

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

                res = self.controller.execute(cmd_args)
                print(res)
            except (KeyboardInterrupt, EOFError):
                print("\nGoodbye!")
                break
            except Exception as loop_err:
                print(CLIFormatter.format_error(f"Shell loop error: {loop_err}"))

        return "Interactive shell closed."
