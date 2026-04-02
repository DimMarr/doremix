import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class EmailSender:
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = 587
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_FROM = "noreply@doremix.fr"
    TEMPLATE_PATH = os.path.join(
        os.path.dirname(__file__), "templates", "template_confirm.html"
    )

    @staticmethod
    def build_verification_email(username: str, code: str) -> str:
        with open(EmailSender.TEMPLATE_PATH, "r", encoding="utf-8") as f:
            body = f.read()
        body = body.replace("{{ username }}", username)
        body = body.replace("{{ code }}", str(code))
        return body

    @staticmethod
    def send_email(to_email: str, username: str, code: str):
        mail_server = EmailSender.MAIL_SERVER
        mail_username = EmailSender.MAIL_USERNAME
        mail_password = EmailSender.MAIL_PASSWORD

        assert mail_server is not None, "MAIL_SERVER is missing in .env"
        assert mail_username is not None, "MAIL_USERNAME is missing in .env"
        assert mail_password is not None, "MAIL_PASSWORD is missing in .env"

        msg = MIMEMultipart("alternative")
        msg["From"] = EmailSender.MAIL_FROM
        msg["To"] = to_email
        msg["Subject"] = "Active ton compte Doremix 🎵"
        msg.attach(
            MIMEText(EmailSender.build_verification_email(username, code), "html")
        )

        try:
            server = smtplib.SMTP(mail_server, EmailSender.MAIL_PORT)
            server.starttls()
            server.login(mail_username, mail_password)
            server.sendmail(EmailSender.MAIL_FROM, to_email, msg.as_string())
            print(f"Mail envoyé à {to_email}")
        except Exception as e:
            print(f"Erreur mail à {to_email} :", e)
        finally:
            server.quit()
