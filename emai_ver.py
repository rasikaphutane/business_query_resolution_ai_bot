# import smtplib
# from email.message import EmailMessage
# import os
# from dotenv import load_dotenv

# load_dotenv()

# SMTP_SERVER = os.getenv("SMTP_SERVER")
# SMTP_PORT = int(os.getenv("SMTP_PORT"))
# SMTP_USERNAME = os.getenv("SMTP_USERNAME")
# SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

# def send_email(to, subject, content):
#     msg = EmailMessage()
#     msg["From"] = SMTP_USERNAME
#     msg["To"] = to
#     msg["Subject"] = subject
#     msg.set_content(content, subtype="html")

#     print(f"Connecting to {SMTP_SERVER}:{SMTP_PORT}")
#     try:
#         with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
#             server.set_debuglevel(1)
#             server.ehlo()
#             server.starttls()
#             server.ehlo()
#             server.login(SMTP_USERNAME, SMTP_PASSWORD)
#             server.send_message(msg)
#         print("✅ Email sent successfully.")
#     except Exception as e:
#         print(f"❌ Email failed: {e}")
#         raise
