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

3. Access the application at http://localhost:5000

## How to Use

1. Open the application in your browser (http://localhost:5000)
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

## Deployment

### Render.com (Free)

1. Create a [Render.com](https://render.com) account
2. Connect your GitHub repository
3. Create a new Web Service, point to your repository
4. Render will automatically detect the `render.yaml` configuration
5. Deploy with the following settings (or they'll be set automatically):
   - Environment: Python
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`

### Railway.app (Free Tier)

1. Create a [Railway.app](https://railway.app) account
2. Connect your GitHub repository
3. Create a new project from the repository
4. Railway will detect the Python application
5. Add the following environment variable: `PORT=8080`
6. Deploy the application

### PythonAnywhere (Free)

1. Create a [PythonAnywhere](https://www.pythonanywhere.com) account
2. Go to the Web tab and create a new web app
3. Choose Manual Configuration and select Python 3.9
4. In the Code section, clone your Git repository
5. Set up a virtual environment and install requirements
6. Configure the WSGI file to point to your Flask app
7. Reload the web app

### Local Deployment

For local deployment with proper production settings:

```
pip install -r requirements.txt
gunicorn app:app
```

Access at http://localhost:8000
=======
# ScanMyCV
Resume Analyzer
>>>>>>> a1e92d6ed2d18ac8432966ab63219ceafb7b29db
