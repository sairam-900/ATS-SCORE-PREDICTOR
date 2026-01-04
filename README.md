ATS RESUME SCORE PREDICTOR

PROJECT OVERVIEW  
The ATS Resume Score Predictor is a web-based application that analyzes a resume (PDF) and predicts how well it matches Applicant Tracking System (ATS) standards. The system provides an ATS score along with strengths, weaknesses, and improvement suggestions to help users optimize their resumes.

PROBLEM STATEMENT  
Many job applicants face resume rejection due to poor ATS compatibility. They do not know whether their resume matches job requirements or follows ATS-friendly formatting. This project solves that problem by automatically evaluating resumes using AI.

SOLUTION DESCRIPTION  
The application allows users to upload a resume in PDF format. The backend extracts text from the resume and sends it to an AI model. The AI analyzes the content and returns an ATS score along with detailed feedback.

USER FLOW  
1. User opens the ATS Resume Score Predictor website  
2. User uploads a resume (PDF format)  
3. Frontend sends the file to the Flask backend  
4. Backend extracts text from the PDF  
5. Extracted text is sent to Google Gemini AI  
6. AI analyzes the resume  
7. ATS score and feedback are returned to the user  

TECHNOLOGIES USED  
Backend is built using Python  
Flask is used for server-side routing and APIs  
Google Gemini AI (gemini-2.5-flash) is used for resume analysis  
PyPDF2 is used for PDF text extraction  
HTML, CSS, and JavaScript are used for frontend UI  
python-dotenv is used for secure environment variable handling  

PROJECT STRUCTURE  
main.py – Flask backend application  
templates/index.html – Resume upload UI  
static/ – CSS and JavaScript files  
.env – Stores API keys securely  
requirements.txt – Python dependencies  
README.md – Project documentation  

INSTALLATION STEPS  
1. Clone the project repository  
2. Install required Python packages using requirements.txt  
3. Create a .env file and add your Google API key  
4. Run the Flask application  
5. Open the local server URL in a browser  

SECURITY HANDLING  
API keys are stored in environment variables  
No sensitive information is hardcoded in the source code  

DEPLOYMENT  
The application can be deployed on Render or similar platforms by configuring environment variables and running the Flask app as the start command.
live deployment link:- https://ats-score-predictor-ten.vercel.app/app

OUTPUT  
The system displays:  
- ATS Score  
- Resume Strengths  
- Resume Weaknesses  
- Improvement Suggestions  

AUTHOR  
Nakka Leela Lakshmi Sai Ram 
