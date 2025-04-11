import sqlite3

def view_table(table_name):
    conn = sqlite3.connect("memory/database.db")
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()

    print(f"📋 Contents of {table_name}:")
    for row in rows:
        print(row)

    conn.close()

# Example usage:
view_table("candidates")
view_table("job_descriptions")
view_table("cv_matches")
