# Notice Management System

## Project Description
A comprehensive Notice Management System built to streamline communication within an organization. It allows for the easy dissemination of important notices, announcements, and updates.

## Features
- Secure authentication and role-based access.
- Create, view, and manage notices efficiently.
- MongoDB integration for flexible document storage.
- Admin dashboard to oversee notices and users.

## Technology Stack
- **Backend:** Python, Django 3.2
- **Database:** MongoDB (via Djongo)
- **Other:** Python-decouple, Gunicorn, Whitenoise

## Folder Structure
```
NOTICE MANAGEMENT/
│
├── company_notice_system/ # Main Django Project config
├── core/                  # Core App 1
├── core_app/              # Core App 2
├── media/                 # Uploaded media files
├── static/                # Static files (CSS, JS, Images)
├── templates/             # HTML Templates
├── venv/                  # Virtual Environment
├── .env.example           # Example Env Variables
├── manage.py              # Django execution script
└── requirements.txt       # Project Dependencies
```

## Installation Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/darshanpm33/NOTICE-MANAGEMENT.git
   ```
2. Navigate to the project directory:
   ```bash
   cd NOTICE-MANAGEMENT
   ```
3. Set up the virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install setuptools legacy-cgi # If running on Python 3.12+
   ```

## Environment Variables
Create a `.env` file in the root directory based on `.env.example`.
- `SECRET_KEY`: Django secret key for cryptographic signing.
- `DEBUG`: Set to `True` for development, `False` for production.
- `DATABASE_URL`: MongoDB connection string.
- `DATABASE_NAME`: Name of the database to connect to.

## Running Backend
1. Ensure your MongoDB server is running.
2. Apply database migrations:
   ```bash
   python manage.py migrate
   ```
3. Start the development server:
   ```bash
   python manage.py runserver
   ```
The app will be accessible at `http://127.0.0.1:8000/`.

## Screenshots
*(Add screenshots of the dashboard, notice boards, etc., here.)*

## Future Enhancements
- Email and Push notifications integration.
- Frontend overhaul using a modern SPA framework.
- Advanced notice scheduling and expiration features.

## Author
Darshan

## License
This project is proprietary and confidential. All rights reserved.
