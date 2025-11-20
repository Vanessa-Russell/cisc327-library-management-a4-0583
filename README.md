# Library Management System – End-to-End Testing & Docker Deployment (Assignment 4)

## Overview

This project extends the Flask-based Library Management System built in previous assignments for CISC 327 (Software Quality Assurance).

Assignment 4 introduces:

- **Browser-based End-to-End (E2E) Testing using Playwright**
- **Complete Docker containerization of the application**
- **Deployment to Docker Hub**
- **Updated run instructions and project layout**

These additions build upon the backend service logic, HTML templates, routes, and database system established earlier.

---

## Project Structure (Updated for A4)

```
cisc327-library-management-a4-0583/
│
├── app/
│   ├── __main__.py              # Application entry point (used by python -m app and Docker)
│   ├── __init__.py
│   ├── database.py
│   ├── services/
│   │   ├── library_service.py
│   │   ├── borrow_service.py
│   │   └── payment_service.py
│   ├── routes/
│   │   ├── catalog_routes.py
│   │   ├── borrowing_routes.py
│   │   ├── api_routes.py
│   │   └── search_routes.py
│   ├── templates/
│   └── library.db
│
├── tests/
│   ├── test_e2e.py              # Browser-based Playwright test (A4 requirement)
│   ├── test_add_book.py
│   ├── test_borrow_book.py
│   ├── test_return_book.py
│   ├── test_search_books.py
│   └── other unit tests…
│
├── Dockerfile
├── requirements.txt
├── student_instructions.md
└── README.md
```

---

## End-to-End Testing (Playwright)

Assignment 4 requires using a real browser to execute a full workflow:

1. Launch the web application  
2. Navigate to **Add Book**  
3. Submit a new book  
4. Verify it appears in the catalog  
5. Navigate to **Return Book**  
6. Submit a return request (dummy behavior allowed)  
7. Validate success or “Not implemented” message  

### **E2E Test File**
`tests/test_e2e.py`

### **Run the E2E Test**

Start the Flask server:

```bash
python -m app
```

Run the test:

```bash
pytest tests/test_e2e.py -v
```

Playwright launches Chromium automatically during the test.

---

## Docker Containerization

Assignment 4 requires the entire application to be containerized with:

- A `Dockerfile` using an official Python image  
- Installed dependencies from `requirements.txt`
- Playwright + Chromium included  
- App served using `flask run` on **port 5000**

### **Dockerfile**
Located at the root of the project.

### Build the Docker Image

```bash
docker build -t library-app .
```

### Run the Docker Container

```bash
docker run -p 5000:5000 library-app
```

Visit:

```
http://localhost:5000
```

---

## Docker Hub Deployment

Assignment 4 requires pushing the Docker image to Docker Hub.

### Tag the Image

```bash
docker tag library-app yourdockerhubusername/library-app:v1
```

### Push to Docker Hub

```bash
docker push yourdockerhubusername/library-app:v1
```

### Remove the Local Image

```bash
docker rmi yourdockerhubusername/library-app:v1
```

### Pull the Image Again

```bash
docker pull yourdockerhubusername/library-app:v1
```

### Run Pulled Image

```bash
docker run -p 5000:5000 yourdockerhubusername/library-app:v1
```

Screenshots of these steps must appear in the Assignment 4 PDF submission.

---

## Database Schema

### **Books Table**
- `id` (INTEGER PRIMARY KEY)
- `title` (TEXT NOT NULL)
- `author` (TEXT NOT NULL)
- `isbn` (TEXT UNIQUE NOT NULL)
- `total_copies` (INTEGER NOT NULL)
- `available_copies` (INTEGER NOT NULL)

### **Borrow Records Table**
- `id` (INTEGER PRIMARY KEY)
- `patron_id` (TEXT NOT NULL)
- `book_id` (INTEGER)
- `borrow_date` (TEXT NOT NULL)
- `due_date` (TEXT NOT NULL)
- `return_date` (TEXT NULL)

---

## Assignment Instructions

Refer to `student_instructions.md` for full marking criteria and instructions.

---

## Resources for Students

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Playwright for Python](https://playwright.dev/python/)
- [Pytest Guide](https://realpython.com/pytest-python-testing/)
- [Docker Documentation](https://docs.docker.com/)

---

# **cisc327-library-management-a4-0583**
