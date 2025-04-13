<<<<<<< HEAD
# Resume Analyzer Application

This application is a Flask-based resume analyzer that matches uploaded resumes with job profiles.

## Project Structure

- `/templates` - HTML templates for the web interface
- `/static` - Static assets (CSS, JS, images)
- `/app.py` - Main Flask application
- `/agents` - Backend processing modules

## Setup and Running

1. Install the required dependencies:

   ```
   pip install -r requirements.txt
   ```

2. Run the Flask application:

   ```
   python app.py
   ```

![Screenshot 2025-04-11 191806](https://github.com/user-attachments/assets/e364bd6d-419a-40ee-8195-82620f7e0c66)
![Screenshot 2025-04-11 191749](https://github.com/user-attachments/assets/2a19851a-ccd0-4227-8249-3492f503b28c)

## Youtube Url-> https://www.youtube.com/watch?v=8lrMx5BgGZs

## How to Use

1. Open the application in your browser 
2. Upload a PDF resume file by dragging and dropping or clicking the upload area
3. Click the "Upload & Analyze" button
4. View the analysis results on the results page

## Features

- Modern, responsive UI with drag-and-drop file uploads
- Real-time search and filtering of resume results
- Score visualization with color-coded progress bars
- Mobile-friendly design

## Technical Implementation

- **Frontend**: HTML, CSS (Tailwind CSS), JavaScript
- **Backend**: Flask (Python)
- **Resume Processing**: Custom AI agents in `/agents` directory

## API Endpoints

- `GET /health` - Health check endpoint
- `POST /upload` - Upload resume file
- `GET /results` - Get HTML page with analysis results
- `GET /api/results` - Get JSON data of analysis results


### Local Deployment

For local deployment with proper production settings:

```
pip install -r requirements.txt
gunicorn app:app
```

