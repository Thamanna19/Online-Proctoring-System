# Online Proctoring System (Django)

An online exam platform with AI-assisted proctoring. Students take timed multiple-choice exams while the webcam is monitored for suspicious behaviour such as no face or multiple faces in view.

## Features
- Student registration and login; separate staff/admin login
- Course-based student and staff dashboards
- Staff create exams (title, course, duration, schedule) and multiple-choice questions
- Exam confirmation page, timed exam taking, automatic scoring and results
- Webcam face check using OpenCV Haar cascades (no face / multiple faces)
- Suspicious activity logging per student and exam

## Tech Stack
- Python, Django
- OpenCV, NumPy (face detection)
- HTML templates with JavaScript webcam capture, SQLite

## Project Structure
```
secure_exam/
├── exam/          # models, views, forms, templates, face_detect.py
├── secure_exam/   # project settings and URLs
└── manage.py
```

## Getting Started
```bash
cd secure_exam
python -m venv venv
venv\Scripts\activate          # Windows  (source venv/bin/activate on macOS/Linux)
pip install django opencv-python numpy
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
Open http://127.0.0.1:8000/. Allow camera access when starting an exam. A standalone webcam demo is in `exam/face_detect.py` (press `q` to quit).

> Note: the repository currently contains a committed `env/` folder; it should be removed and added to `.gitignore`.