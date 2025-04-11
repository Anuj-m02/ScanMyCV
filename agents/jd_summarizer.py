from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import pandas as pd
import os
import sys

# 👇 Make sure db connection path is correct
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from memory.db import connect

# Load model + tokenizer once
tokenizer = AutoTokenizer.from_pretrained("sshleifer/distilbart-cnn-12-6")
model = AutoModelForSeq2SeqLM.from_pretrained("sshleifer/distilbart-cnn-12-6")

# ✨ Summarization logic
def summarize_text(text):
    inputs = tokenizer.encode(text, return_tensors="pt", max_length=1024, truncation=True)
    summary_ids = model.generate(
        inputs,
        max_length=150,
        min_length=40,
        length_penalty=2.0,
        num_beams=4,
        early_stopping=True
    )
    return tokenizer.decode(summary_ids[0], skip_special_tokens=True)

# ✅ Insert into DB
def insert_into_db(job_title, original_jd, summary):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO job_descriptions (job_title, original_jd, summary)
        VALUES (?, ?, ?)""", (job_title, original_jd, summary))
    conn.commit()
    conn.close()

# 📄 Read CSV, summarize each row
def summarize_from_csv(csv_path):
    df = pd.read_csv(csv_path, encoding='windows-1252')  # adjust if needed

    for idx, row in df.iterrows():
        job_title = str(row['Job Title'])  # adjust key if needed
        original_jd = str(row['Job Description'])  # adjust key if needed
        summary = summarize_text(original_jd)
        insert_into_db(job_title, original_jd, summary)
        print(f"✅ JD {idx + 1}: {job_title} summarized and stored.")

# 🔧 Run directly
if __name__ == "__main__":
    csv_path = "data\job_description.csv"  # adjust if needed
    summarize_from_csv(csv_path)
