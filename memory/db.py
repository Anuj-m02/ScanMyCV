import sqlite3

# 📌 Connect to the database
def connect():
    return sqlite3.connect("memory/database.db")

# 📌 Alias for compatibility with other scripts
create_connection = connect

# 📌 Create all required tables (drops old candidates table if needed)
def create_tables():
    conn = connect()
    cursor = conn.cursor()

    # Drop candidates table to ensure schema is updated
    cursor.execute("DROP TABLE IF EXISTS candidates")

    # Create Job Descriptions Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS job_descriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_title TEXT,
        original_jd TEXT,
        summary TEXT
    )""")

    # Create Candidates Table (with email column)
    cursor.execute("""
    CREATE TABLE candidates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        cv_text TEXT,
        extracted_info TEXT,
        match_score REAL
    )""")

    # Create CV Matches Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cv_matches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cv_path TEXT,
        jd_summary TEXT,
        similarity_score REAL
    )""")

    # Create Interviews Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS interviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        candidate_id INTEGER,
        interview_date TEXT,
        interview_time TEXT,
        interview_format TEXT,
        FOREIGN KEY(candidate_id) REFERENCES candidates(id)
    )""")

    conn.commit()
    conn.close()

# 📌 Clear old resume-related data
def clear_old_resumes():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM candidates")
    cursor.execute("DELETE FROM cv_matches")
    cursor.execute("DELETE FROM interviews")
    conn.commit()
    conn.close()
