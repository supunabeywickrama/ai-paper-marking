import smtplib
from email.message import EmailMessage
import os
from backend.config import settings

async def send_results_email(to_email: str, student_name: str, exam_title: str, total_score: float, pdf_path: str):
    """
    Sends an email with the annotated results PDF attached using SMTP.
    """
    # If SMTP is not configured, we just print and skip
    if not settings.smtp_username or not settings.smtp_password:
        print(f"[Mock Email] To: {to_email}, Subject: Results for {exam_title}, Score: {total_score}")
        return

    msg = EmailMessage()
    msg['Subject'] = f"AI Marked Results: {exam_title}"
    msg['From'] = settings.smtp_username
    msg['To'] = to_email
    
    body = f"Hello {student_name},\n\nYour exam '{exam_title}' has been automatically marked by the AI system.\nYour total score is: {total_score}.\n\nPlease find your annotated answer sheet attached.\n\nBest,\nAI Marking System"
    msg.set_content(body)
    
    if os.path.exists(pdf_path):
        with open(pdf_path, 'rb') as f:
            pdf_data = f.read()
            msg.add_attachment(pdf_data, maintype='application', subtype='pdf', filename=os.path.basename(pdf_path))
            
    try:
        # We use a synchronous SMTP send inside an async function for simplicity, 
        # in a prod environment you'd use aiosmtplib.
        with smtplib.SMTP(settings.smtp_server, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_username, settings.smtp_password)
            server.send_message(msg)
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")
