import os
import re
import json
import PyPDF2
from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_cors import CORS
from google import genai
from io import BytesIO
from dotenv import load_dotenv

# =========================
# LOAD ENV VARIABLES
# =========================
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise RuntimeError("GOOGLE_API_KEY is missing in .env file")

# =========================
# FLASK APP
# =========================
app = Flask(__name__)
CORS(app)

# =========================
# GEMINI CLIENT
# =========================
client = genai.Client(api_key=GOOGLE_API_KEY)

# =========================
# PDF TEXT EXTRACTION
# =========================
def extract_text_from_pdf_bytes(pdf_bytes):
    text = ""
    try:
        reader = PyPDF2.PdfReader(BytesIO(pdf_bytes))
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    except Exception as e:
        print(f"PDF extraction error: {e}")
    return text.strip()

# =========================
# RESUME VALIDATION
# =========================
RESUME_KEYWORDS = [
    "education", "experience", "skills", "projects",
    "internship", "certification", "objective", "summary",
    "work experience", "technical skills"
]

def is_probable_resume(text):
    text = text.lower()
    score = sum(1 for k in RESUME_KEYWORDS if k in text)
    return score >= 3

# =========================
# PARSE GEMINI RESPONSE
# =========================
def parse_gemini_response(response_text):
    try:
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            return json.loads(json_match.group())
    except:
        pass
    return None

def get_default_response():
    return {
        "score": 50,
        "role": "Professional",
        "description": "Unable to analyze the resume properly.",
        "skillGap": "Unknown",
        "experienceLevel": "Not Determined",
        "strengths": ["Resume uploaded successfully"],
        "improvements": ["Please upload a clearer and more detailed resume"]
    }

# =========================
# ROUTES
# =========================
@app.route("/")
def home():
    return redirect(url_for("app_page"))

@app.route("/app")
def app_page():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze_resume():

    resume = request.files.get("resume")
    job_description = request.form.get("description", "") or request.form.get("job_description", "")

    if not resume:
        return jsonify({"error": "Resume PDF is required"}), 400

    try:
        resume_text = extract_text_from_pdf_bytes(resume.read())

        # ---------- BASIC TEXT CHECK ----------
        if not resume_text or len(resume_text) < 100:
            return jsonify({
                "error": "❌ Could not extract readable text. Upload a valid resume PDF."
            }), 400

        # ---------- RULE-BASED RESUME CHECK ----------
        if not is_probable_resume(resume_text):
            return jsonify({
                "error": "❌ Uploaded PDF is NOT a resume. Please upload a proper resume."
            }), 400

        # =========================
        # GEMINI PROMPT
        # =========================
        prompt = f"""
First determine whether the following text is a professional resume.

If it is NOT a resume, respond ONLY with:
{{"not_a_resume": true}}

If it IS a resume, then analyze it as instructed.

You are an expert ATS (Applicant Tracking System) Resume Analyzer.

Respond ONLY with a valid JSON object in this exact format:

{{
    "score": <number from 0-100>,
    "role": "<best matching job role>",
    "description": "<2-3 sentence explanation>",
    "skillGap": "<Excellent Match | Minor Gaps | Moderate Gaps | Significant Gaps>",
    "experienceLevel": "<Entry Level | Junior Level | Mid Level | Senior Level | Executive Level>",
    "strengths": [
        "<strength 1>",
        "<strength 2>",
        "<strength 3>",
        "<strength 4>",
        "<strength 5>"
    ],
    "improvements": [
        "<improvement 1>",
        "<improvement 2>",
        "<improvement 3>",
        "<improvement 4>",
        "<improvement 5>"
    ]
}}

JOB DESCRIPTION:
{job_description if job_description else "General employability analysis"}

RESUME CONTENT:
{resume_text}
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        response_text = response.text.strip()
        response_text = re.sub(r'^```json\s*|^```\s*|\s*```$', '', response_text)

        result = parse_gemini_response(response_text)

        if result is None:
            try:
                result = json.loads(response_text)
            except:
                result = get_default_response()

        # ---------- LLM RESUME CONFIRMATION ----------
        if result.get("not_a_resume"):
            return jsonify({
                "error": "❌ This document does not appear to be a resume."
            }), 400

        # ---------- FIELD VALIDATION ----------
        required_fields = [
            "score", "role", "description",
            "skillGap", "experienceLevel",
            "strengths", "improvements"
        ]

        for field in required_fields:
            if field not in result:
                result = get_default_response()
                break

        result["score"] = int(result.get("score", 50))

        if not isinstance(result.get("strengths"), list):
            result["strengths"] = [result["strengths"]]

        if not isinstance(result.get("improvements"), list):
            result["improvements"] = [result["improvements"]]

        return jsonify(result)

    except Exception as e:
        print("Analyze Error:", e)
        return jsonify({"error": "Internal server error"}), 500

@app.route("/health")
def health_check():
    return jsonify({"status": "healthy", "service": "ATS Resume Analyzer"})

# =========================
# RUN SERVER
# =========================
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
