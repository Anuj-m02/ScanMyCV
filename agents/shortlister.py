import sqlite3

def create_connection():
    return sqlite3.connect("memory/database.db")

# 📌 Fetch candidates with match_score >= 0.7
def fetch_shortlisted_candidates(threshold=0.7):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, match_score FROM candidates
        WHERE match_score >= ?
    """, (threshold,))
    candidates = cursor.fetchall()
    conn.close()
    return candidates

# 📌 Insert basic interview placeholder
def insert_interviews(candidates):
    conn = create_connection()
    cursor = conn.cursor()

    for candidate_id, name, score in candidates:
        cursor.execute("""
            INSERT INTO interviews (candidate_id, interview_date, interview_time, interview_format)
            VALUES (?, ?, ?, ?)
        """, (candidate_id, "To be scheduled", "To be scheduled", "To be scheduled"))

        print(f"📩 {name} has been selected for an interview. Regards, HR Team.")

    conn.commit()
    conn.close()

def shortlist_candidates_and_get_status(threshold=0.75):
    candidates = fetch_shortlisted_candidates(threshold)
    if not candidates:
        return "❌ No candidates met the threshold."
    insert_interviews(candidates)
    return "✅ Candidates have been shortlisted."

if __name__ == "__main__":
    shortlist_candidates_and_get_status()
