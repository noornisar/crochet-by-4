from django.core.management.base import BaseCommand
from store.services.email_service import send_test_email


class Command(BaseCommand):
    help = "Test Gmail SMTP email configuration by sending a test email to the specified recipient."

    def add_arguments(self, parser):
        parser.add_argument(
            "recipient",
            type=str,
            help="The email address to send the test email to (e.g. customer@example.com)",
        )

    def handle(self, *args, **options):
        recipient = options["recipient"].strip()
        self.stdout.write(f"Attempting to send test email to: {recipient} ...")

        success, error = send_test_email(recipient)

        if success:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully sent test email to {recipient}!\n"
                    f"Subject: Test Email - Crochet Store\n"
                    f"Message: This is a test email from my Crochet Store Django website. SMTP configuration is working correctly."
                )
            )
        else:
            self.stderr.write(
                self.style.ERROR(
                    f"Failed to send test email to {recipient}.\n"
                    f"Error Details: {error}\n"
                    f"Please verify your EMAIL_HOST, EMAIL_PORT, EMAIL_USE_TLS, EMAIL_HOST_USER, and EMAIL_HOST_PASSWORD."
                )
            )
