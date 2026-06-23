import shlex
import sys
from datetime import date
from src.infra.cli import CLIFormatter

class InteractiveShell:
    """
    Encapsulates the interactive console / shell loop logic.
    """

    def __init__(self, controller) -> None:
        self.controller = controller

    def _print_text(self, text: str) -> None:
        if not CLIFormatter.should_color():
            print(CLIFormatter.strip_ansi(text))
        else:
            print(text)

    def _get_status_line(self) -> str:
        lang_str = "EN"
        translation = getattr(self.controller, "translation_service", None)
        if translation:
            lang_str = translation.get_locale().upper()
        
        try:
            self.controller.repository.list_books()
            db_status = "OK"
        except Exception:
            db_status = "ERROR"
            
        overdue_count = 0
        try:
            today = date.today()
            loans = self.controller.repository.list_loans()
            for loan in loans:
                if not loan.return_date and loan.due_date < today:
                    overdue_count += 1
        except Exception:
            pass
            
        return f"\033[90m[Language: {lang_str} | DB: {db_status} | Active Overdues: {overdue_count}]\033[0m"

    def _switch_language_prompt(self) -> None:
        translation = getattr(self.controller, "translation_service", None)
        self._print_text("\nSelect language / Selecione o idioma / Seleccione el idioma / Choisir la langue / Sprache wählen:")
        self._print_text("  [1] English (EN)")
        self._print_text("  [2] Português (PT)")
        self._print_text("  [3] Español (ES)")
        self._print_text("  [4] Français (FR)")
        self._print_text("  [5] Deutsch (DE)")
        
        try:
            choice = input("Choice [1-5]: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
            
        lang_map = {
            "1": "en",
            "2": "pt",
            "3": "es",
            "4": "fr",
            "5": "de"
        }
        
        if choice in lang_map:
            new_lang = lang_map[choice]
            if translation:
                try:
                    translation.set_locale(new_lang)
                    self._print_text(CLIFormatter.format_ok(f"Language switched to {new_lang.upper()}!"))
                except Exception as e:
                    self._print_text(CLIFormatter.format_error(f"Error setting language: {e}"))
        else:
            self._print_text(CLIFormatter.format_error("Invalid choice / Opção inválida"))

    def run(self) -> str:
        """
        Runs the interactive loop reading commands from stdin and writing to stdout.
        """
        translation = getattr(self.controller, "translation_service", None)
        self._print_text(CLIFormatter.get_welcome_banner(translation))

        default_tip = (
            "💡 \033[96m[TIP]\033[0m Type \033[92m'help'\033[0m (without slashes) to view active rules & full command docs.\n\n"
            "Recommended Commands:\n"
            "  • \033[92mlist-books\033[0m          - Render all books & hold queues\n"
            "  • \033[92mlist-readers\033[0m        - Render all readers & fine balances\n"
            "  • \033[92mpopularity-report\033[0m   - Show book rankings & waitlists\n"
            "  • \033[92mreport\033[0m              - Generate daily handover status report\n"
            "  • \033[93mexit\033[0m / \033[93mquit\033[0m         - Close the interactive console\n"
        )
        tip = default_tip
        if translation:
            tip_translated = translation.translate("shell_tip")
            if tip_translated != "shell_tip":
                tip = tip_translated.replace("\\n", "\n").replace("\\033", "\033")

        self._print_text(tip)

        while True:
            # Refresh translation references in loop in case language changes
            translation = getattr(self.controller, "translation_service", None)
            goodbye_msg = "Goodbye!"
            already_in_shell_msg = "Already in shell mode."
            shell_closed_msg = "Interactive shell closed."
            shortcuts_msg = "[L] Switch Language | [Q] Quit"

            if translation:
                translated_goodbye = translation.translate("goodbye")
                if translated_goodbye != "goodbye":
                    goodbye_msg = translated_goodbye
                translated_already = translation.translate("already_in_shell")
                if translated_already != "already_in_shell":
                    already_in_shell_msg = translated_already
                translated_closed = translation.translate("shell_closed")
                if translated_closed != "shell_closed":
                    shell_closed_msg = translated_closed
                translated_shortcuts = translation.translate("shell_shortcuts")
                if translated_shortcuts != "shell_shortcuts":
                    shortcuts_msg = translated_shortcuts

            try:
                # Print persistent status line and shortcuts
                self._print_text(self._get_status_line())
                self._print_text(shortcuts_msg)

                line = input("bibliomodel> ")
                if not line.strip():
                    continue

                try:
                    cmd_args = shlex.split(line)
                except ValueError as shlex_err:
                    self._print_text(CLIFormatter.format_error(f"Command line split error: {shlex_err}"))
                    continue

                if not cmd_args:
                    continue

                # Support Q/q shortcut
                if cmd_args[0] in ("exit", "quit", "q", "Q"):
                    self._print_text(goodbye_msg)
                    break

                # Support L/l shortcut or "lang" / "switch-language"
                if cmd_args[0] in ("l", "L", "lang"):
                    self._switch_language_prompt()
                    continue

                if cmd_args[0] == "shell":
                    self._print_text(CLIFormatter.format_error(already_in_shell_msg))
                    continue

                res = self.controller.execute(cmd_args)
                self._print_text(res)
            except (KeyboardInterrupt, EOFError):
                self._print_text(f"\n{goodbye_msg}")
                break
            except Exception as loop_err:
                self._print_text(CLIFormatter.format_error(f"Shell loop error: {loop_err}"))

        return shell_closed_msg
