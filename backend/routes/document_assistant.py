from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from auth import get_current_user
from agents.document_email_generator import generate_email

router = APIRouter(
    prefix="/api/document",
    tags=["Document Assistant"]
)


class DocumentRequest(BaseModel):
    college: str
    reason: str
    tone: str
    roll_no: str
    context: str
    student_name: str


@router.post("/generate")
def generate_document(
    data: DocumentRequest,
    user=Depends(get_current_user)
):
    """
    Generate an academic email based on student input using Groq LLM.
    Requires authentication.
    """
    try:
        email = generate_email(
            college=data.college,
            reason=data.reason,
            tone=data.tone,
            roll_no=data.roll_no,
            context=data.context,
            student_name=data.student_name,
        )
        return {"email": email}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
