import os
import fitz  # PyMuPDF
import re
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from memory.db import create_connection


# --- Delete existing resumes from DB ---
def delete_all_resumes():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM candidates")
    conn.commit()
    conn.close()

# --- Extract text from a single PDF ---
def extract_text_from_pdf(pdf_path):
    text = ""
    doc = fitz.open(pdf_path)
    for page in doc:
        text += page.get_text()
    return text

# --- Extract email (basic example) ---
def extract_email(text):
    match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    return match.group(0) if match else "N/A"

# --- Extract proper name from resume text ---
def extract_name(text):
    # Try to find name at the beginning of the resume (typically at the top)
    lines = text.strip().split('\n')
    
    # Look for name patterns in the first few lines
    for line in lines[:10]:  # Check first 10 lines
        line = line.strip()
        if line and len(line) > 2 and len(line.split()) <= 4:
            # Skip lines that are likely to be headers/titles
            if not any(keyword in line.lower() for keyword in ['resume', 'cv', 'curriculum', 'vitae']):
                # Check if it looks like a name (first word capitalized, etc.)
                words = line.split()
                if len(words) >= 2 and words[0][0].isupper() and words[1][0].isupper():
                    return line
    
    # Try to find a more common name pattern if the above fails
    name_match = re.search(r'([A-Z][a-z]+(?: [A-Z][a-z]+)+)', ' '.join(lines[:15]))
    if name_match:
        return name_match.group(1)
        
    # If all else fails, extract a potential name using a different pattern
    for line in lines[:15]:
        # Look for lines with 2-3 words, all capitalized first letter
        words = line.strip().split()
        if 2 <= len(words) <= 3 and all(w[0].isupper() for w in words if w):
            return line.strip()
            
    # Return None if no name could be found
    return None

# --- Store into DB ---
def insert_resume(name, email, text):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO candidates (name, email, cv_text, extracted_info, match_score) VALUES (?, ?, ?, ?, ?)",
        (name, email, text, "", 0.0)
    )
    conn.commit()
    conn.close()

# --- Process entire folder ---
def process_resume_folder(folder_path):
    delete_all_resumes()
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(folder_path, filename)
            text = extract_text_from_pdf(pdf_path)
            email = extract_email(text)
            
            # Try to extract real name from resume text
            extracted_name = extract_name(text)
            if extracted_name:
                name = extracted_name
            else:
                # Fall back to filename without extension if extraction fails
                name = filename.replace(".pdf", "")
                
            insert_resume(name, email, text)
            print(f"✅ Processed: {filename}, Name: {name}")

# --- Example run ---
if __name__ == "__main__":
    resume_folder = "data\CVs1"  # change if needed
    process_resume_folder(resume_folder)
