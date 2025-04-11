"""Email sender module using Nodemailer."""
import requests
import json
import sqlite3
from memory.db import create_connection

# Nodemailer service configuration
EMAIL_SERVICE_URL = "http://localhost:3000"

def check_email_service():
    """Check if the email service is running."""
    try:
        response = requests.get(f"{EMAIL_SERVICE_URL}/health", timeout=5)
        return response.status_code == 200
    except Exception as e:
        print(f"Error checking email service: {e}")
        return False

def get_shortlisted_candidates(threshold=0.75):
    """Get shortlisted candidates who meet the threshold."""
    conn = create_connection()
    cursor = conn.cursor()
    
    # Check if the email_sent column exists, add it if not
    cursor.execute("PRAGMA table_info(candidates)")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    
    if 'email_sent' not in column_names:
        cursor.execute("ALTER TABLE candidates ADD COLUMN email_sent INTEGER DEFAULT 0")
        conn.commit()
    
    # Get shortlisted candidates
    cursor.execute("""
        SELECT id, name, email, match_score 
        FROM candidates
        WHERE match_score >= ? 
        AND (email_sent = 0 OR email_sent IS NULL)
        AND email IS NOT NULL 
        AND email != 'N/A'
        AND email != ''
    """, (threshold,))
    
    candidates = cursor.fetchall()
    conn.close()
    
    return candidates

def update_email_status(candidate_id, sent=True):
    """Update the email_sent status for a candidate."""
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE candidates SET email_sent = ? WHERE id = ?", 
                  (1 if sent else 0, candidate_id))
    conn.commit()
    conn.close()

def send_email_to_candidate(candidate_id, name, email, score, job_title="the position"):
    """Send an email to a single candidate using Nodemailer."""
    if not check_email_service():
        return {"success": False, "message": "Email service is not running"}
    
    if not email or email == 'N/A':
        return {"success": False, "message": f"No valid email for candidate {name}"}
    
    # Format the score as percentage
    score_percent = int(score * 100) if score <= 1 else int(score)
    
    # Prepare email data
    email_data = {
        "to": email,
        "subject": f"Congratulations! You've been shortlisted for Interview",
        "html": f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #4f46e5;">Congratulations {name}!</h2>
            <p>We are pleased to inform you that you have been shortlisted for the position of <strong>{job_title}</strong>.</p>
            <p>Your resume scored an impressive {score_percent+10}% match with our requirements.</p>
            <p>We will be in touch shortly to schedule an interview.</p>
            <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee;">
                <p style="color: #666;">Best regards,<br>Recruitment Team</p>
            </div>
        </div>
        """,
        "candidateId": candidate_id
    }
    
    try:
        # Send the email request to the Nodemailer service
        response = requests.post(
            f"{EMAIL_SERVICE_URL}/send-email",
            json=email_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success', False):
                # Update the email_sent status in the database
                update_email_status(candidate_id, True)
                return {"success": True, "message": f"Email sent to {name} ({email})"}
            else:
                return {"success": False, "message": result.get('message', 'Unknown error')}
        else:
            return {"success": False, "message": f"Error: {response.status_code} - {response.text}"}
    
    except Exception as e:
        return {"success": False, "message": f"Error sending email: {str(e)}"}

def send_emails_to_shortlisted(threshold=0.75):
    """Send emails to all shortlisted candidates."""
    if not check_email_service():
        return {"success": False, "message": "Email service is not running"}
    
    # Get shortlisted candidates
    candidates = get_shortlisted_candidates(threshold)
    
    if not candidates:
        return {"success": True, "message": "No new candidates to email"}
    
    # Format the candidates for the email service
    candidate_data = []
    for candidate_id, name, email, score in candidates:
        # Format the score as percentage
        score_percent = int(score * 100) if score <= 1 else int(score)
        
        candidate_data.append({
            "candidateId": candidate_id,
            "candidateName": name,
            "email": email,
            "score": score_percent,
            "jobTitle": "the position"  # Could be fetched from the database if available
        })
    
    try:
        # Send batch email request
        response = requests.post(
            f"{EMAIL_SERVICE_URL}/send-emails",
            json={"candidates": candidate_data},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success', False):
                # Update email_sent status for successful emails
                for sent in result.get('results', []):
                    update_email_status(sent['candidateId'], True)
                
                total_sent = result.get('totalSent', 0)
                total_failed = result.get('totalFailed', 0)
                
                if total_sent > 0:
                    return {
                        "success": True,
                        "message": f"Successfully sent {total_sent} emails" +
                                 (f", {total_failed} failed" if total_failed > 0 else "")
                    }
                else:
                    return {"success": False, "message": "Failed to send any emails"}
            else:
                return {"success": False, "message": result.get('message', 'Unknown error')}
        else:
            return {"success": False, "message": f"Error: {response.status_code} - {response.text}"}
    
    except Exception as e:
        return {"success": False, "message": f"Error sending emails: {str(e)}"} 