import os
import json
from dotenv import load_dotenv
from groq import Groq

# Correct import for file structure
from utils.email_templates import EMAIL_TEMPLATES

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    # Use fallback key if not found in environment (for simplified testing if user forgot .env)
    # Ideally should raise or use config
    print("WARNING: GROQ_API_KEY not found in env. Ensure it is set.")

# Initialize Groq client safely
try:
    client = Groq(api_key=GROQ_API_KEY)
except Exception as e:
    print(f"Error initializing Groq client: {e}")
    client = None

MODEL_NAME = "llama-3.1-8b-instant"

# Dynamic path resolution to find the guidelines file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GUIDELINES_PATH = os.path.join(BASE_DIR, "utils", "college_guidelines.json")

try:
    with open(GUIDELINES_PATH, "r") as f:
        COLLEGE_GUIDELINES = json.load(f)
except FileNotFoundError:
    print(f"Warning: Guidelines file not found at {GUIDELINES_PATH}. Using default empty policy.")
    COLLEGE_GUIDELINES = {"DEFAULT": {"attendance_policy": "N/A", "medical_leave_policy": "N/A", "internship_policy": "N/A"}}


def normalize(text: str) -> str:
    return text.lower().replace(" ", "").replace("_", "").replace("-", "")


def get_college_policy(college: str):
    """Find specific college policy or return default."""
    if not college:
        return COLLEGE_GUIDELINES.get("DEFAULT")
        
    normalized_college = normalize(college)
    for name, policy in COLLEGE_GUIDELINES.items():
        if name != "DEFAULT" and normalize(name) in normalized_college:
            return policy
            
    return COLLEGE_GUIDELINES.get("DEFAULT")


def select_template(reason: str):
    """Select email template based on keywords in reason."""
    if not reason:
         return EMAIL_TEMPLATES["general"]
         
    r = reason.lower()
    if any(w in r for w in ["medical", "doctor", "hospital", "sick", "illness"]):
        return EMAIL_TEMPLATES.get("medical", EMAIL_TEMPLATES["general"])
    if any(w in r for w in ["internship", "training", "project", "noc"]):
        return EMAIL_TEMPLATES.get("internship", EMAIL_TEMPLATES["general"])
    if "attendance" in r or "absent" in r:
        return EMAIL_TEMPLATES.get("attendance", EMAIL_TEMPLATES["general"])
        
    return EMAIL_TEMPLATES["general"]


def build_prompt(template, policy, tone, context, reason):
    """Construct the LLM prompt."""
    body_base = template.get("body", "")
    body = body_base.replace("{{CONTEXT}}", context).replace("{{REASON}}", reason)

    return f"""
You are an academic administrative email writer.

Task: Write ONLY the body of an email. 
DO NOT include a Subject line.
DO NOT include a closing or sign-off (like "Sincerely" or "[Your Name]").

Details:
Tone: {tone}
Context: {context}

Policies to reference (if relevant types):
- Attendance: {policy.get('attendance_policy', 'N/A')}
- Medical: {policy.get('medical_leave_policy', 'N/A')}
- Internship: {policy.get('internship_policy', 'N/A')}

Draft Body:
{body}
"""


def generate_email(
    *,
    college: str,
    reason: str,
    tone: str,
    student_name: str,
    roll_no: str,
    context: str
) -> str:
    """Generate email using Groq API."""
    if not client:
        return "Error: AI Service Unavailable (API Key missing)."
        
    policy = get_college_policy(college)
    template = select_template(reason)
    prompt = build_prompt(template, policy, tone, context, reason)

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a precise email assistant. You return ONLY the email body text."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=400,
            temperature=0.6,
        )

        email_content = response.choices[0].message.content.strip()
        
        # Cleanup: Remove potential subject lines if LLM ignored instructions
        lines = email_content.split('\n')
        cleaned_lines = [l for l in lines if not l.lower().startswith('subject:')]
        email_content = '\n'.join(cleaned_lines).strip()
        
        # Cleanup: Remove placeholders like [Your Name]
        email_content = email_content.replace("[Your Name]", "").replace("[Student Name]", "").strip()
        
        # Structure the final output
        final_email = f"Subject: {template.get('subject', 'Request').replace('{{REASON}}', reason).replace('{{CONTEXT}}', context)}\n\n"
        final_email += email_content
        final_email += f"\n\nYours sincerely,\n{student_name}\nRoll No: {roll_no}"
        
        return final_email
        
    except Exception as e:
        print(f"Groq API Error: {e}")
        return f"Error generating email: {str(e)}"
