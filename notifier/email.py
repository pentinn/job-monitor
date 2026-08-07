import smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from config import (
    EMAIL_FROM,
    EMAIL_PASSWORD,
    EMAIL_TO
)


def send_email(jobs):
    """
    Send email notification for new jobs
    """

    if not jobs:
        return


    subject = (
        f"🚨 {len(jobs)} New Software Engineering Job(s) Found"
    )


    body = """
New matching jobs were found:

"""


    for job in jobs:

        body += f"""
--------------------------------

Company:
{job['company']}

Title:
{job['title']}

Location:
{job['location']}

Remote:
{job['remote']}

Posted:
{job['posted']}

Apply:
{job['url']}

"""


    message = MIMEMultipart()

    message["From"] = EMAIL_FROM
    message["To"] = EMAIL_TO
    message["Subject"] = subject


    message.attach(
        MIMEText(
            body,
            "plain"
        )
    )


    with smtplib.SMTP_SSL(
        "smtp.gmail.com",
        465
    ) as server:

        server.login(
            EMAIL_FROM,
            EMAIL_PASSWORD
        )

        server.send_message(
            message
        )


    print("Email sent successfully!")