import os
import logging
import smtplib
import configparser
from email.mime.text import MIMEText
from datetime import date
from src.app.ports import INotificationService, IConfigProvider

class SMTPNotificationService(INotificationService):
    """
    Concrete adapter for sending email notifications.
    Generates simulated files in 'notifications/' and optionally sends emails via SMTP.
    """

    def __init__(self, config_provider: IConfigProvider = None) -> None:
        self.config_provider = config_provider
        self.logger = logging.getLogger("bibliomodel")

    def send_overdue_notification(
        self,
        reader_id: str,
        reader_name: str,
        reader_email: str,
        reader_fine_balance: float,
        overdue_loans: list,
        today: date
    ) -> bool:
        """
        Send overdue notification email.
        """
        # Read SMTP config
        has_smtp = False
        smtp_host = ""
        smtp_port = 1025
        smtp_sender = "library@example.com"

        # Check config.ini first as fallback/default
        config_file = "config.ini"
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

        # Build message body
        books_lines = []
        for item in overdue_loans:
            title = item.get("title", "Unknown Book")
            due_date_str = item.get("due_date", "")
            fine = item.get("fine", 0.0)
            books_lines.append(f" - '{title}' (Due: {due_date_str}, Estimated Fine: ${fine:.2f})")

        msg = f"Dear {reader_name},\n\n"
        msg += "This is a notification that you have overdue books in BiblioModel Library:\n"
        msg += "\n".join(books_lines) + "\n\n"
        msg += f"Total Outstanding Fine Balance: ${reader_fine_balance:.2f}\n\n"
        msg += "Return Instructions:\n"
        msg += "Please return these books to the library as soon as possible to avoid further fines and suspension.\n"
        msg += "Fines accumulate daily.\n\n"
        msg += "Best regards,\nBiblioModel Library Management"

        # Setup folder
        notif_dir = os.path.abspath(os.path.join(".", "notifications"))
        os.makedirs(notif_dir, exist_ok=True)

        file_path = os.path.join(notif_dir, f"email_{reader_id}_{today.isoformat()}.txt")
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(msg)
        except Exception as err:
            self.logger.error(f"Failed to write notification file for {reader_id}: {err}")
            return False

        if has_smtp:
            try:
                mime_msg = MIMEText(msg)
                mime_msg["Subject"] = "BiblioModel Overdue Book Notification"
                mime_msg["From"] = smtp_sender
                mime_msg["To"] = reader_email
                with smtplib.SMTP(smtp_host, smtp_port, timeout=2) as server:
                    server.sendmail(smtp_sender, [reader_email], mime_msg.as_string())
            except Exception as smtp_err:
                self.logger.warning(
                    f"SMTP send failed for {reader_id}: {smtp_err} (simulated file generated successfully)"
                )

        return True
