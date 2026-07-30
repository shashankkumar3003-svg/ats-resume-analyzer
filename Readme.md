# ATS Resume Analyzer

A full-stack ATS Resume Analyzer built using React and FastAPI.

The application allows users to upload a PDF resume, paste a job description, calculate an ATS-style skill match score, view matched and missing skills, receive resume improvement suggestions, and download a PDF analysis report.

## Features

- Upload PDF resumes
- Extract resume text using PyPDF
- Compare resume skills with a job description
- Calculate ATS match score
- Show matched skills
- Show missing skills
- Generate resume improvement suggestions
- Download ATS analysis report as PDF
- Responsive React user interface
- FastAPI backend with REST API integration

## Tech Stack

### Frontend
- React.js
- JavaScript
- HTML
- CSS
- Vite

### Backend
- Python
- FastAPI
- PyPDF
- ReportLab
- Uvicorn

## Project Structure

```text
ats-resume-analyzer/
├── backend/
│   ├── main.py
│   ├── report.py
│   ├── requirements.txt
│   └── venv/
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
│
└── README.md
