"""
TRACES+ Main Application
Trajectory-Aware Collective System for Student Retention

A responsible multi-agent AI system that:
- Detects silent dropout risk from bureaucratic friction
- Preserves human dignity through explicit restraint
- Enables safe, consent-based support
- Knows when NOT to act
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Optional
import uvicorn


# Import database and models
from database import Base, engine, get_db
from models import User, StudentEvent
from auth import (
    get_password_hash, 
    authenticate_user, 
    create_access_token,
    get_current_user
)

# Import routes
from routes import student, counselor, admin, senior

# Import chat managers
from chat.counselor_chat import counselor_chat_manager
from chat.first_year_chat import community_chat_manager

# Import agents
from agents.coordinator import CoordinatorAgent

# Pydantic models for requests
from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str
    email: str
    full_name: str
    role: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    username: str
    role: str


# Initialize FastAPI app
app = FastAPI(
    title="TRACES+",
    description="Trajectory-Aware Collective System for Student Retention",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup event to preload ML models
@app.on_event("startup")
async def startup_event():
    import asyncio
    
    def load_models():
        print("Pre-loading ML Models in background thread...")
        try:
            # Import here to avoid circular dependencies
            from routes.student import get_coordinator_singleton
            
            # Initialize singleton to load models into memory
            _ = get_coordinator_singleton()
            print("ML Models loaded successfully in background!")
        except Exception as e:
            print(f"Warning: Could not pre-load ML models: {e}")

    # Run in background without awaiting completion to unblock server startup
    # Use create_task to ensure the coroutine runs
    asyncio.create_task(asyncio.to_thread(load_models))
    print("Server starting up immediately (Models loading in background)...")

# Create database tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(student.router)
app.include_router(counselor.router)
app.include_router(admin.router)
app.include_router(senior.router)
# Include calendar router
from routes import calendar, document_assistant
app.include_router(calendar.router)
app.include_router(document_assistant.router)

# Root endpoint
@app.get("/")
async def root():
    """API root with system information"""
    return {
        "name": "TRACES+",
        "version": "1.0.0",
        "description": "Responsible multi-agent system for student support",
        "core_principles": [
            "No student punishment or labeling",
            "No automated disciplinary actions",
            "Explicit uncertainty modeling",
            "Ethical restraint and refusal",
            "Human-in-the-loop escalation",
            "Privacy-first, consent-based"
        ],
        "status": "operational"
    }


# Authentication endpoints
@app.post("/api/auth/register", response_model=TokenResponse)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if username exists
    existing_user = db.query(User).filter(User.username == request.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Validate role
    if request.role not in ['student', 'counselor', 'admin']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role"
        )
    
    # Create user
    hashed_password = get_password_hash(request.password)
    user = User(
        username=request.username,
        password=hashed_password,
        email=request.email,
        full_name=request.full_name,
        role=request.role
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Generate token
    access_token = create_access_token(data={"sub": user.username})
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        username=user.username,
        role=user.role
    )


@app.post("/api/auth/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Login user"""
    user = authenticate_user(db, request.username, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generate token
    access_token = create_access_token(data={"sub": user.username})
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        username=user.username,
        role=user.role
    )


@app.get("/api/auth/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role
    }


# Agent analysis endpoint
@app.post("/api/analyze-student/{student_id}")
async def analyze_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Run multi-agent analysis on student
    Available to counselors and admins for testing
    """
    # Get student events
    events = db.query(StudentEvent).filter(
        StudentEvent.student_id == student_id
    ).all()
    
    # Run Irreversibility Arbiter analysis (replaces Coordinator)
    from agents.irreversibility_arbiter import IrreversibilityArbiter
    arbiter = IrreversibilityArbiter()
    result = arbiter.analyze_student(events)
    
    # Store results in database
    from models import AgentOutput, CoordinatorDecision
    
    # Store agent outputs
    for agent_output in result['agent_outputs']:
        # Map disparate scores to 'risk_score' for DB compatibility
        score = agent_output.get('risk') or agent_output.get('capacity_score') or agent_output.get('inertia_score') or 0.0
        
        output = AgentOutput(
            student_id=student_id,
            agent_name=agent_output['agent'],
            risk_score=float(score),
            confidence=agent_output.get('confidence', 0.5),
            comment=agent_output.get('comment') or agent_output.get('reasoning') or '',
            analysis_data=str(agent_output)
        )
        db.add(output)
    
    # Store decision with new metrics
    decision = CoordinatorDecision(
        student_id=student_id,
        decision=result['decision'],
        justification=result['justification'],
        ethics_veto=result['ethics_veto'],
        aggregate_risk=result['aggregate_risk'],
        uncertainty_level=result['uncertainty_level'],
        meta_data=result.get('extra_metrics', {})
    )
    db.add(decision)
    
    db.commit()
    
    return result


# WebSocket endpoints for chat
@app.websocket("/ws/counselor-chat/student")
async def websocket_counselor_chat_student(websocket: WebSocket, session_id: Optional[str] = None):
    """
    WebSocket endpoint for student anonymous chat with counselor
    """
    session_id = await counselor_chat_manager.connect_student(websocket, session_id)
    
    try:
        while True:
            data = await websocket.receive_json()
            
            if data.get('type') == 'message':
                await counselor_chat_manager.handle_student_message(
                    session_id, 
                    data['message']
                )
            elif data.get('type') == 'consent_response':
                await counselor_chat_manager.handle_consent_response(
                    session_id,
                    data.get('consent_given', False),
                    data.get('student_id')
                )
    
    except WebSocketDisconnect:
        await counselor_chat_manager.disconnect(session_id=session_id)


@app.websocket("/ws/counselor-chat/counselor/{counselor_id}")
async def websocket_counselor_chat_counselor(websocket: WebSocket, counselor_id: str):
    """
    WebSocket endpoint for counselor side of anonymous chat
    """
    await counselor_chat_manager.connect_counselor(websocket, counselor_id)
    
    try:
        while True:
            data = await websocket.receive_json()
            
            if data.get('type') == 'message':
                await counselor_chat_manager.handle_counselor_message(
                    counselor_id,
                    data['session_id'],
                    data['message']
                )
            elif data.get('type') == 'request_identity':
                await counselor_chat_manager.request_identity_reveal(
                    counselor_id,
                    data['session_id'],
                    data.get('reason', '')
                )
    
    except WebSocketDisconnect:
        await counselor_chat_manager.disconnect(counselor_id=counselor_id)


from fastapi import WebSocket, WebSocketDisconnect
from typing import Optional

@app.websocket("/ws/community-chat/{room_id}")
async def websocket_community_chat(websocket: WebSocket, room_id: str):
    params = websocket.query_params
    user_id = params.get("user_id")
    is_anonymous = params.get("is_anonymous") == "true"
    display_name = params.get("display_name")

    if not user_id:
        await websocket.close(code=1008)
        return

    print("[WS CONNECT]", room_id, user_id)

    success = await community_chat_manager.join_room(
        websocket=websocket,
        room_id=room_id,
        user_id=user_id,
        is_anonymous=is_anonymous,
        display_name=display_name
    )

    if not success:
        await websocket.close()
        return

    try:
        while True:
            data = await websocket.receive_json()
            print("[WS DATA]", data)

            if data.get("type") in ("message", "chat_message"):
                await community_chat_manager.handle_message(
                    room_id=room_id,
                    user_id=user_id,
                    message=data.get("message", ""),
                    is_anonymous=is_anonymous,
                    display_name=display_name,
                    client_id=data.get("client_id")  # ✅ pass through
                )

    except WebSocketDisconnect:
        print("[WS DISCONNECT]", user_id)
        await community_chat_manager.leave_room(room_id, user_id)


@app.get("/api/community-chat/rooms")
async def get_community_rooms():
    """Get list of available community chat rooms"""
    return {
        "rooms": community_chat_manager.get_room_list()
    }


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# Initialize demo data (for testing)
@app.post("/api/dev/init-demo-data")
async def init_demo_data(db: Session = Depends(get_db)):
    """
    Initialize demo data for testing
    Creates sample users and events
    """
    from utils.risk_utils import generate_sample_events
    
    # Create demo users if they don't exist
    demo_users = [
        {
            "username": "student1",
            "password": "demo123",
            "email": "student1@traces.edu",
            "full_name": "Student User",
            "role": "student"
        },
        {
            "username": "student2",
            "password": "demo123",
            "email": "student2@traces.edu",
            "full_name": "Generic Student",
            "role": "student"
        },
        {
            "username": "counselor1",
            "password": "demo123",
            "email": "counselor1@traces.edu",
            "full_name": "Verified Counselor",
            "role": "counselor"
        },
        {
            "username": "admin1",
            "password": "demo123",
            "email": "admin1@traces.edu",
            "full_name": "Admin User",
            "role": "admin"
        }
    ]
    
    created_users = []
    for user_data in demo_users:
        existing = db.query(User).filter(User.username == user_data['username']).first()
        if not existing:
            user = User(
                username=user_data['username'],
                password=get_password_hash(user_data['password']),
                email=user_data['email'],
                full_name=user_data['full_name'],
                role=user_data['role']
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            created_users.append(user)
    
    # Generate sample events for students
    if created_users:
        for user in created_users:
            if user.role == "student":
                # Generate different scenarios
                if "student1" in user.username:
                    generate_sample_events(db, user.id, scenario="moderate")
                elif "student2" in user.username:
                    generate_sample_events(db, user.id, scenario="high")
    
    return {
        "message": "Demo data initialized",
        "users_created": len(created_users),
        "note": "Login credentials: username/demo123"
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)