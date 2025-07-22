import os
import smtplib
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from email.message import EmailMessage
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def send_email(to_email, subject, body):
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email

    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print(f"Email sent to {to_email} at {datetime.now().strftime('%H:%M')}")
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")

def check_and_notify():
    now = datetime.now().strftime('%H:%M')

    try:
        response = supabase.table('profiles').select('*').execute()
        for user in response.data:
            routine = user.get('routine')
            email = user.get('email')

            if not routine or not email:
                continue

            for task in routine:
                task_time = task.get('time')
                message = task.get('message')
                notify = task.get('notify', False)

                if task_time == now and notify:
                    send_email(
                        to_email=email,
                        subject="Reminder Notification",
                        body=message
                    )

    except Exception as e:
        print(f"Error checking reminders: {e}")

# Schedule with APScheduler
scheduler = BlockingScheduler()

scheduler.add_job(check_and_notify, 'interval', minutes=1)
print("Reminder scheduler started. Checking every minute...")

try:
    scheduler.start()
except (KeyboardInterrupt, SystemExit):
    print("Scheduler stopped.")
