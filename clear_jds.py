import sqlite3

conn = sqlite3.connect("memory/database.db")
cursor = conn.cursor()

# Delete all job descriptions
cursor.execute("DELETE FROM job_descriptions")
conn.commit()

print("✅ Cleared all job descriptions.")
conn.close()
