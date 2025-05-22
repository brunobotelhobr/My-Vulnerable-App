# Vulnerable Application Demo

This is a deliberately vulnerable application, created for educational purposes to demonstrate common web security issues.

⚠️ **WARNING: This application contains intentional vulnerabilities. DO NOT use in production!** ⚠️

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Start the server:
```bash
uvicorn main:app --reload
```

2. Access the application:
- Backend API: http://localhost:8000
- Frontend: http://localhost:8000/index.html

## API Documentation

Full API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Legal Disclaimer

This application is for educational purposes only. The vulnerabilities demonstrated here are dangerous in real environments. Always follow security best practices in production applications.