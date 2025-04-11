from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import os
import shutil
import requests

from agents import resume_extractor, cv_matcher, shortlister, scheduler
from agents.cv_matcher import compute_similarity_and_get_results
from agents.shortlister import shortlist_candidates_and_get_status
from agents.scheduler import schedule_interviews_and_get_status
from agents import email_sender

UPLOAD_FOLDER = "uploaded_resumes"
ALLOWED_EXTENSIONS = {"pdf"}

app = Flask(__name__)
app.secret_key = "your_secret_key"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/health")
def health_check():
    """Health check endpoint for frontend to verify backend is running"""
    return jsonify({"status": "ok", "message": "Backend server is running"})

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        flash("❌ No file part")
        return redirect(url_for("index"))

    file = request.files["file"]
    if file.filename == "":
        flash("❌ No selected file")
        return redirect(url_for("index"))

    if file and allowed_file(file.filename):
        # Clear old resume data and files
        resume_extractor.delete_all_resumes()
        folder = "data\CVs1"
        if os.path.exists(folder):
            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f"⚠️ Failed to delete {file_path}. Reason: {e}")
        else:
            os.makedirs(folder, exist_ok=True)

        # Save uploaded resume to proper location
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(filepath)

        shutil.copy(filepath, os.path.join(folder, file.filename))

        # Process the resume + matching
        resume_extractor.process_resume_folder(folder)
        compute_similarity_and_get_results()
        shortlist_candidates_and_get_status()
        schedule_interviews_and_get_status()

        flash("🎯 Matching complete. View results below.")
        return redirect(url_for("results"))
    else:
        flash("❌ Invalid file format. Please upload a PDF.")
        return redirect(url_for("index"))

@app.route("/results")
def results():
    match_results = compute_similarity_and_get_results()
    shortlist_status = shortlist_candidates_and_get_status()
    interview_status = schedule_interviews_and_get_status()

    # Process the results for better display
    for result in match_results:
        # Add email_sent field for UI if not present
        if 'email_sent' not in result:
            result['email_sent'] = False
        
        # If email is None or empty string, set a default value
        if not result.get('email'):
            result['email'] = ""

    return render_template("results.html",
                           match_results=match_results,
                           shortlist_status=shortlist_status,
                           interview_status=interview_status)

@app.route("/send-email/<candidate_id>", methods=["POST"])
def send_email_to_candidate(candidate_id):
    """Send an email to a specific candidate."""
    try:
        # Get candidate information from the database
        candidate_data = None
        match_results = compute_similarity_and_get_results()
        
        for result in match_results:
            if result["candidate_id"] == candidate_id:
                candidate_data = result
                break
        
        if not candidate_data:
            flash("❌ Candidate not found")
            return redirect(url_for("results"))
        
        # Send the email
        result = email_sender.send_email_to_candidate(
            candidate_id=candidate_data["candidate_id"],
            name=candidate_data["candidate_name"],
            email=candidate_data["email"],
            score=candidate_data["match_score"],
            job_title=candidate_data.get("job_title", "the position")
        )
        
        if result["success"]:
            flash(f"✅ {result['message']}")
        else:
            flash(f"❌ {result['message']}")
        
        return redirect(url_for("results"))
    
    except Exception as e:
        flash(f"❌ Error: {str(e)}")
        return redirect(url_for("results"))

@app.route("/send-all-emails", methods=["POST"])
def send_all_emails():
    """Send emails to all shortlisted candidates."""
    try:
        result = email_sender.send_emails_to_shortlisted(threshold=0.75)
        
        if result["success"]:
            flash(f"✅ {result['message']}")
        else:
            flash(f"❌ {result['message']}")
        
        return redirect(url_for("results"))
    
    except Exception as e:
        flash(f"❌ Error: {str(e)}")
        return redirect(url_for("results"))

# API endpoint for frontend
@app.route("/api/results", methods=["GET"])
def api_results():
    match_results = compute_similarity_and_get_results()
    shortlist_status = shortlist_candidates_and_get_status()
    interview_status = schedule_interviews_and_get_status()
    
    return jsonify({
        "match_results": match_results,
        "shortlist_status": shortlist_status,
        "interview_status": interview_status
    })

if __name__ == "__main__":
    app.run(debug=True)
