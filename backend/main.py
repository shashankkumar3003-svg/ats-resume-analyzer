import os
import re
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pypdf import PdfReader

from report import generate_report


app = FastAPI(
    title="ATS Resume Analyzer API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


BASE_DIR = Path(__file__).resolve().parent
REPORT_PATH = BASE_DIR / "ATS_Report.pdf"


SKILL_PATTERNS = {
    "Python": [r"\bpython\b"],
    "Java": [r"\bjava\b"],
    "JavaScript": [r"\bjavascript\b", r"\bjava\s*script\b"],
    "React": [r"\breact(?:\.js|js)?\b"],
    "Node.js": [r"\bnode(?:\.js|js)?\b"],
    "Express.js": [r"\bexpress(?:\.js|js)?\b"],
    "FastAPI": [r"\bfastapi\b"],
    "Flask": [r"\bflask\b"],
    "Django": [r"\bdjango\b"],
    "HTML": [r"\bhtml5?\b"],
    "CSS": [r"\bcss3?\b"],
    "SQL": [r"\bsql\b"],
    "MySQL": [r"\bmysql\b"],
    "MongoDB": [r"\bmongodb\b", r"\bmongo\s*db\b"],
    "Git": [r"\bgit\b"],
    "GitHub": [r"\bgithub\b"],
    "REST API": [
        r"\brest\s+apis?\b",
        r"\brestful\s+apis?\b"
    ],
    "Problem Solving": [r"\bproblem[\s-]+solving\b"],
    "Communication": [
        r"\bcommunication\b",
        r"\bcommunication\s+skills?\b"
    ],
    "Data Structures": [r"\bdata\s+structures?\b"],
    "Algorithms": [r"\balgorithms?\b"],
    "Object-Oriented Programming": [
        r"\bobject[\s-]+oriented\s+programming\b",
        r"\boop\b"
    ],
    "Machine Learning": [
        r"\bmachine\s+learning\b",
        r"\bml\b"
    ],
    "Deep Learning": [r"\bdeep\s+learning\b"],
    "Docker": [r"\bdocker\b"],
    "AWS": [
        r"\baws\b",
        r"\bamazon\s+web\s+services\b"
    ],
    "Linux": [r"\blinux\b"],
    "Postman": [r"\bpostman\b"],
    "Firebase": [r"\bfirebase\b"],
    "C++": [r"(?<![\w+])c\+\+(?![\w+])"],
    "C#": [r"(?<![\w#])c#(?![\w#])"],
    "C": [r"(?<![a-zA-Z0-9+#])c(?![a-zA-Z0-9+#])"],
}


def extract_skills(text: str) -> set[str]:
    text = text.lower()
    detected_skills = set()

    for skill, patterns in SKILL_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text, flags=re.IGNORECASE):
                detected_skills.add(skill)
                break

    return detected_skills


def create_suggestions(
    score: int,
    missing_skills: list[str]
) -> list[str]:
    suggestions = []

    if score >= 80:
        suggestions.append(
            "Your resume has a strong match with the job description."
        )
    elif score >= 60:
        suggestions.append(
            "Your resume has a good match. Strengthen the missing skill areas "
            "and add measurable project achievements."
        )
    elif score >= 40:
        suggestions.append(
            "Your resume has a moderate match. Tailor your skills and project "
            "descriptions more closely to the role."
        )
    else:
        suggestions.append(
            "Your resume has a low match. Review the job requirements and "
            "highlight more relevant skills and projects."
        )

    for skill in missing_skills[:8]:
        suggestions.append(
            f"Add evidence of {skill} only if you genuinely have experience "
            "with it, preferably through a project or internship."
        )

    suggestions.append(
        "Use action verbs and measurable results in your project descriptions."
    )

    suggestions.append(
        "Keep the resume ATS-friendly by using simple headings and avoiding "
        "complex graphics or tables."
    )

    return suggestions


@app.get("/")
def home():
    return {
        "message": "ATS Resume Analyzer API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.get("/download-report")
def download_report():
    if not REPORT_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail="Report not found. Analyze a resume first."
        )

    return FileResponse(
        path=str(REPORT_PATH),
        media_type="application/pdf",
        filename="ATS_Report.pdf"
    )


@app.post("/upload-resume")
async def upload_resume(
    resume: UploadFile = File(...),
    job_description: str = Form(...)
):
    if not resume.filename:
        raise HTTPException(
            status_code=400,
            detail="Please upload a resume."
        )

    if not resume.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF resumes are supported."
        )

    if not job_description.strip():
        raise HTTPException(
            status_code=400,
            detail="Please enter a job description."
        )

    try:
        reader = PdfReader(resume.file)
        resume_text_parts = []

        for page in reader.pages:
            page_text = page.extract_text() or ""
            resume_text_parts.append(page_text)

        resume_text = "\n".join(resume_text_parts)

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail="Unable to read this PDF."
        ) from exc

    if not resume_text.strip():
        raise HTTPException(
            status_code=400,
            detail=(
                "No readable text was found. Scanned/image-only PDFs "
                "are not currently supported."
            )
        )

    resume_skills = extract_skills(resume_text)
    job_skills = extract_skills(job_description)

    if not job_skills:
        raise HTTPException(
            status_code=400,
            detail=(
                "No supported technical skills were detected in the job "
                "description. Please paste a more detailed job description."
            )
        )

    matched_skills = sorted(job_skills.intersection(resume_skills))
    missing_skills = sorted(job_skills - resume_skills)

    score = round(
        (len(matched_skills) / len(job_skills)) * 100
    )

    suggestions = create_suggestions(
        score=score,
        missing_skills=missing_skills
    )

    generate_report(
        output_path=REPORT_PATH,
        filename=resume.filename,
        score=score,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        suggestions=suggestions,
    )

    return {
        "filename": resume.filename,
        "score": score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "total_keywords": len(job_skills),
        "matched_count": len(matched_skills),
        "suggestions": suggestions,
        "report_url": "/download-report"
    }