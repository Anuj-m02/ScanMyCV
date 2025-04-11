import sqlite3
import re
from sentence_transformers import SentenceTransformer, util

# 📌 Connect to the database
def create_connection():
    return sqlite3.connect("memory/database.db")

# 🧼 Cleaning function
def clean_text(text):
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s.,]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

# 🔍 Fetch JDs and CVs from database
def fetch_data():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, summary FROM job_descriptions")
    jds = cursor.fetchall()

    cursor.execute("SELECT id, name, cv_text FROM candidates")
    cvs = cursor.fetchall()

    conn.close()
    return jds, cvs

# 📝 Update match score in candidates table
def update_match_score(candidate_id, score):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE candidates SET match_score = ? WHERE id = ?", (score, candidate_id))
    conn.commit()
    conn.close()

# 💾 Save best match in cv_matches table
def insert_cv_match(cv_path, jd_summary, similarity_score):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO cv_matches (cv_path, jd_summary, similarity_score) VALUES (?, ?, ?)",
        (cv_path, jd_summary, similarity_score)
    )
    conn.commit()
    conn.close()
# 🆕 Save best CV match with JD summary and score
def save_cv_match(cv_path, jd_summary, score):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO cv_matches (cv_path, jd_summary, similarity_score)
        VALUES (?, ?, ?)
    """, (cv_path, jd_summary, score))
    conn.commit()
    conn.close()

# 🔧 Main logic to compare and save
# 🔍 Main logic to compute similarity
def compute_similarity_and_get_results():
    jds, cvs = fetch_data()
    model = SentenceTransformer('all-mpnet-base-v2')
    results = []

    # Get all candidates with their emails
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, match_score FROM candidates")
    candidates_data = cursor.fetchall()
    candidates_dict = {candidate[0]: {"name": candidate[1], "email": candidate[2], "match_score": candidate[3]} for candidate in candidates_data}
    conn.close()

    for cv_id, name, cv_text in cvs:
        clean_cv = clean_text(cv_text)
        cv_emb = model.encode(clean_cv, convert_to_tensor=True)
        best_score = 0.0
        best_jd_summary = ""
        best_jd_id = None

        for jd_id, jd_summary in jds:
            clean_jd = clean_text(jd_summary)
            jd_emb = model.encode(clean_jd, convert_to_tensor=True)
            score = util.pytorch_cos_sim(cv_emb, jd_emb).item()
            if score > best_score:
                best_score = score
                best_jd_summary = jd_summary
                best_jd_id = jd_id

        update_match_score(cv_id, best_score)
        save_cv_match(name, best_jd_summary, best_score)

        # Get email from candidates_dict
        candidate_email = candidates_dict.get(cv_id, {}).get("email", "")

        results.append({
            "candidate_id": f"C{cv_id}",
            "candidate_name": name,
            "email": candidate_email,
            "jd_id": best_jd_id,
            "job_title": best_jd_summary,
            "match_score": round(best_score, 4)
        })

    return results


# 🔁 Alias for main execution
match_resumes = compute_similarity_and_get_results

if __name__ == "__main__":
    compute_similarity_and_get_results()
