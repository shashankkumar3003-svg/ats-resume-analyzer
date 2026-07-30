import { useState } from "react";
import "./App.css";

const API_BASE_URL = "https://ats-resume-analyzer-9gpy.onrender.com";

function App() {
  const [jobDescription, setJobDescription] = useState("");
  const [resume, setResume] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  function handleFileChange(event) {
    const selectedFile = event.target.files?.[0] || null;

    setError("");
    setResult(null);

    if (
      selectedFile &&
      selectedFile.type !== "application/pdf"
    ) {
      setResume(null);
      setError("Please select a PDF file only.");
      event.target.value = "";
      return;
    }

    setResume(selectedFile);
  }

  async function analyzeResume() {
    setError("");
    setResult(null);

    if (!resume) {
      setError("Please select a PDF resume.");
      return;
    }

    if (!jobDescription.trim()) {
      setError("Please enter the job description.");
      return;
    }

    const formData = new FormData();

    formData.append("resume", resume);
    formData.append("job_description", jobDescription);

    try {
      setLoading(true);

      const response = await fetch(
        `${API_BASE_URL}/upload-resume`,
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Unable to analyze the resume."
        );
      }

      setResult(data);
    } catch (requestError) {
      setError(
        requestError.message ||
        "Unable to connect to the backend."
      );
    } finally {
      setLoading(false);
    }
  }

  function downloadReport() {
    window.open(
      `${API_BASE_URL}${result?.report_url || "/download-report"}`,
      "_blank",
      "noopener,noreferrer"
    );
  }

  function resetForm() {
    setResume(null);
    setJobDescription("");
    setResult(null);
    setError("");

    const fileInput = document.getElementById("resume-input");

    if (fileInput) {
      fileInput.value = "";
    }
  }

  function scoreLabel(score) {
    if (score >= 80) return "Strong Match";
    if (score >= 60) return "Good Match";
    if (score >= 40) return "Moderate Match";
    return "Low Match";
  }

  return (
    <main className="app">
      <section className="card">
        <header className="header">
          <p className="eyebrow">FULL-STACK PROJECT</p>
          <h1>ATS Resume Analyzer</h1>
          <p className="subtitle">
            Upload a PDF resume and compare it with a job description.
          </p>
        </header>

        <div className="form-section">
          <label className="label" htmlFor="resume-input">
            Upload Resume
          </label>

          <input
            id="resume-input"
            type="file"
            accept=".pdf,application/pdf"
            onChange={handleFileChange}
          />

          <p className="filename">
            {resume
              ? `Selected file: ${resume.name}`
              : "No file selected"}
          </p>

          <label className="label" htmlFor="job-description">
            Job Description
          </label>

          <textarea
            id="job-description"
            rows="11"
            placeholder="Paste the complete job description here..."
            value={jobDescription}
            onChange={(event) => {
              setJobDescription(event.target.value);
              setResult(null);
              setError("");
            }}
          />

          <div className="button-row">
            <button
              className="primary-button"
              onClick={analyzeResume}
              disabled={loading}
            >
              {loading ? "Analyzing Resume..." : "Analyze Resume"}
            </button>

            <button
              className="secondary-button"
              onClick={resetForm}
              disabled={loading}
            >
              Reset
            </button>
          </div>

          {error && (
            <div className="error" role="alert">
              {error}
            </div>
          )}
        </div>

        {result && (
          <section className="result">
            <div className="score-header">
              <div>
                <p className="score-label">
                  {scoreLabel(result.score)}
                </p>

                <h2>ATS Score: {result.score}%</h2>

                <p>
                  Matched {result.matched_count} out of{" "}
                  {result.total_keywords} detected skills
                </p>
              </div>
            </div>

            <div className="progress-track">
              <div
                className="progress-value"
                style={{ width: `${result.score}%` }}
              />
            </div>

            <div className="result-section">
              <h3>Matched Skills</h3>

              {result.matched_skills.length ? (
                <div className="tags">
                  {result.matched_skills.map((skill) => (
                    <span
                      className="tag matched"
                      key={skill}
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              ) : (
                <p>No matching skills were detected.</p>
              )}
            </div>

            <div className="result-section">
              <h3>Missing Skills</h3>

              {result.missing_skills.length ? (
                <div className="tags">
                  {result.missing_skills.map((skill) => (
                    <span
                      className="tag missing"
                      key={skill}
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              ) : (
                <p>No important detected skills are missing.</p>
              )}
            </div>

            <div className="result-section">
              <h3>Recommendations</h3>

              <ul className="suggestions">
                {result.suggestions.map((suggestion, index) => (
                  <li key={`${suggestion}-${index}`}>
                    {suggestion}
                  </li>
                ))}
              </ul>
            </div>

            <button
              className="download-button"
              onClick={downloadReport}
            >
              Download ATS Report
            </button>

            <p className="disclaimer">
              This is a skill-matching estimate, not an official employer ATS
              score.
            </p>
          </section>
        )}
      </section>
    </main>
  );
}

export default App;
              
