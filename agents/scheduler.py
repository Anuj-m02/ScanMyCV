import sqlite3
import smtplib
from email.message import EmailMessage

# 📌 Connect to DB
def create_connection():
    return sqlite3.connect("memory/database.db")

# 📌 Fetch unscheduled interviews and emails
def fetch_unscheduled_interviews():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT interviews.id, candidates.name, candidates.email
        FROM interviews
        JOIN candidates ON interviews.candidate_id = candidates.id
        WHERE interview_date = 'To be scheduled'
    """)
    data = cursor.fetchall()
    conn.close()
    return data

# 📧 Send email
def send_email(to_email, name):
    msg = EmailMessage()
    msg['Subject'] = "Interview Shortlist Notification"
    msg['From'] = "youremail@gmail.com"
    msg['To'] = to_email
    msg.set_content(f"""
Dear {name},

Congratulations! You have been shortlisted for an interview.

Regards,  
HR Team
""")

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login("youremail@gmail.com", "yourapppassword")
            smtp.send_message(msg)
            print(f"📤 Email sent to {name} at {to_email}")
    except Exception as e:
        print(f"❌ Failed to send email to {to_email}: {e}")

# 🗓️ Schedule interviews and notify
def schedule_interviews_and_get_status():
    interviews = fetch_unscheduled_interviews()
    if not interviews:
        return "✅ All interviews already scheduled."
    conn = create_connection()
    cursor = conn.cursor()
    for interview_id, name, email in interviews:
        date = "2025-04-15"
        time = "10:00 AM"
        fmt = "Online"
        cursor.execute("""
            UPDATE interviews
            SET interview_date = ?, interview_time = ?, interview_format = ?
            WHERE id = ?
        """, (date, time, fmt, interview_id))
        send_email(email, name)
    conn.commit()
    conn.close()
    return f"✅ {len(interviews)} interviews scheduled and emails sent."

if __name__ == "__main__":
    schedule_interviews_and_get_status()
