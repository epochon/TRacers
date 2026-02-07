"""
Senior Mentorship Chat
Connects first-year students with verified senior mentors based on course/batch
"""

from fastapi import WebSocket
from typing import Dict, List, Optional
from datetime import datetime
import uuid
from moderation.professionalism_bot import check_message, generate_warning


class SeniorChatManager:
    """
    Manages chat sessions between first-year students and senior mentors
    
    Features:
    - Course and batch-based matching
    - Verified senior mentors only
    - One-on-one mentorship sessions
    - Session history and continuity
    """
    
    def __init__(self):
        # Active student connections: {student_id: websocket}
        self.student_connections: Dict[str, WebSocket] = {}
        
        # Active senior connections: {senior_id: websocket}
        self.senior_connections: Dict[str, WebSocket] = {}
        
        # Active chat sessions: {session_id: {...}}
        self.active_sessions: Dict[str, dict] = {}
        
        # Student profiles: {student_id: {course, batch, matched_senior_id}}
        self.student_profiles: Dict[str, dict] = {}
        
        # Message history: {session_id: [messages]}
        self.message_history: Dict[str, List[dict]] = {}
        
        # Demo senior database - in production, this would come from DB
        self.available_seniors = {
            'senior_001': {
                'id': 'senior_001',
                'name': 'Rahul Kumar',
                'course': 'Computer Science',
                'batch': '2022',
                'specializations': ['Algorithms', 'Web Development', 'Placements'],
                'available': True
            },
            'senior_002': {
                'id': 'senior_002',
                'name': 'Priya Sharma',
                'course': 'Computer Science',
                'batch': '2021',
                'specializations': ['Machine Learning', 'Research', 'Higher Studies'],
                'available': True
            },
            'senior_003': {
                'id': 'senior_003',
                'name': 'Arjun Reddy',
                'course': 'Electrical Engineering',
                'batch': '2022',
                'specializations': ['Core Placements', 'Circuit Design', 'Internships'],
                'available': True
            },
            'senior_004': {
                'id': 'senior_004',
                'name': 'Sneha Patel',
                'course': 'Mechanical Engineering',
                'batch': '2021',
                'specializations': ['CAD/CAM', 'Placements', 'Campus Life'],
                'available': True
            },
            'senior_005': {
                'id': 'senior_005',
                'name': 'Vikram Singh',
                'course': 'Computer Science',
                'batch': '2023',
                'specializations': ['Competitive Programming', 'Projects', 'Clubs'],
                'available': True
            }
        }
    
    async def connect_student(
        self,
        websocket: WebSocket,
        student_id: str,
        course: str = None,
        batch: str = None
    ) -> dict:
        """
        Connect a student to senior chat
        Returns matching status and available seniors
        """
        await websocket.accept()
        self.student_connections[student_id] = websocket
        
        # Check if student has existing profile
        if student_id in self.student_profiles:
            profile = self.student_profiles[student_id]
            
            # Check if already matched
            if profile.get('matched_senior_id'):
                session_id = profile.get('session_id')
                if session_id in self.active_sessions:
                    # Resume existing session
                    await self._send_session_history(websocket, session_id)
                    return {
                        'status': 'resumed',
                        'session_id': session_id,
                        'senior': self.available_seniors.get(profile['matched_senior_id'])
                    }
        else:
            # New student - create profile if course/batch provided
            if course and batch:
                self.student_profiles[student_id] = {
                    'student_id': student_id,
                    'course': course,
                    'batch': batch,
                    'matched_senior_id': None,
                    'session_id': None,
                    'created_at': datetime.utcnow().isoformat()
                }
        
        # Send connection confirmation
        await websocket.send_json({
            'type': 'connection_established',
            'message': 'Connected to Senior Mentorship Chat',
            'has_profile': student_id in self.student_profiles
        })
        
        return {'status': 'connected', 'has_profile': student_id in self.student_profiles}
    
    async def submit_student_profile(
        self,
        student_id: str,
        course: str,
        batch: str
    ) -> dict:
        """
        Student submits their course and batch for matching
        Returns list of available seniors
        """
        # Save student profile
        self.student_profiles[student_id] = {
            'student_id': student_id,
            'course': course,
            'batch': batch,
            'matched_senior_id': None,
            'session_id': None,
            'created_at': datetime.utcnow().isoformat()
        }
        
        # Find matching seniors (same course, earlier batch)
        matching_seniors = self._find_matching_seniors(course, batch)
        
        # Send to student
        websocket = self.student_connections.get(student_id)
        if websocket:
            await websocket.send_json({
                'type': 'profile_submitted',
                'matching_seniors': matching_seniors,
                'message': f'Found {len(matching_seniors)} available mentors in {course}'
            })
        
        return {
            'success': True,
            'matching_seniors': matching_seniors
        }
    
    async def match_with_senior(
        self,
        student_id: str,
        senior_id: str
    ) -> dict:
        """
        Match student with selected senior and create chat session
        """
        if student_id not in self.student_profiles:
            return {'success': False, 'error': 'Student profile not found'}
        
        if senior_id not in self.available_seniors:
            return {'success': False, 'error': 'Senior not found'}
        
        # Create new session
        session_id = f"senior_session_{uuid.uuid4().hex[:12]}"
        
        self.active_sessions[session_id] = {
            'session_id': session_id,
            'student_id': student_id,
            'senior_id': senior_id,
            'started_at': datetime.utcnow().isoformat(),
            'status': 'active'
        }
        
        # Update student profile
        self.student_profiles[student_id]['matched_senior_id'] = senior_id
        self.student_profiles[student_id]['session_id'] = session_id
        
        # Initialize message history
        self.message_history[session_id] = []
        
        # Notify student
        student_ws = self.student_connections.get(student_id)
        if student_ws:
            senior_info = self.available_seniors[senior_id]
            await student_ws.send_json({
                'type': 'match_created',
                'session_id': session_id,
                'senior': senior_info,
                'message': f'Connected with {senior_info["name"]} ({senior_info["batch"]} batch)'
            })
        
        # Notify senior if online
        senior_ws = self.senior_connections.get(senior_id)
        if senior_ws:
            await senior_ws.send_json({
                'type': 'new_mentee',
                'session_id': session_id,
                'student_id': student_id,
                'course': self.student_profiles[student_id]['course'],
                'batch': self.student_profiles[student_id]['batch']
            })
        
        return {
            'success': True,
            'session_id': session_id,
            'senior': senior_info
        }
    
    async def handle_student_message(
        self,
        student_id: str,
        message: str,
        client_id: str = None
    ):
        """Handle message from student to senior"""
        profile = self.student_profiles.get(student_id)
        if not profile or not profile.get('session_id'):
            return
        
        session_id = profile['session_id']
        session = self.active_sessions.get(session_id)
        if not session:
            return

        # ------------------ MODERATION (STUDENT ONLY) ------------------

        is_allowed, processed_message = check_message(message)

        if not is_allowed:
            student_ws = self.student_connections.get(student_id)
            if student_ws:
                await student_ws.send_json({
                    "type": "moderation_notice",
                    "message": generate_warning(message)
                })
            return

    # Use censored version
        message = processed_message

        # Create message data
        msg_data = {
            'type': 'student_message',
            'session_id': session_id,
            'sender': 'student',
            'message': message,
            'client_id': client_id,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Store in history
        self.message_history[session_id].append(msg_data)
        
        # Send to senior
        senior_id = session['senior_id']
        senior_ws = self.senior_connections.get(senior_id)
        if senior_ws:
            await senior_ws.send_json(msg_data)
        
        # Echo back to student
        student_ws = self.student_connections.get(student_id)
        if student_ws:
            await student_ws.send_json({
                'type': 'message_sent',
                'message': message,
                'client_id': client_id,
                'timestamp': msg_data['timestamp']
            })
    
    async def handle_senior_message(
        self,
        senior_id: str,
        session_id: str,
        message: str
    ):
        """Handle message from senior to student"""
        session = self.active_sessions.get(session_id)
        if not session or session['senior_id'] != senior_id:
            return
        
        # Create message data
        msg_data = {
            'type': 'senior_message',
            'session_id': session_id,
            'sender': 'senior',
            'message': message,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Store in history
        self.message_history[session_id].append(msg_data)
        
        # Send to student
        student_id = session['student_id']
        student_ws = self.student_connections.get(student_id)
        if student_ws:
            await student_ws.send_json(msg_data)
    
    def _find_matching_seniors(self, course: str, batch: str) -> List[dict]:
        """
        Find seniors matching the student's course and from earlier batches
        """
        matching = []
        student_batch_year = int(batch) if batch.isdigit() else 9999
        
        for senior_id, senior in self.available_seniors.items():
            # Match by course
            if senior['course'].lower() != course.lower():
                continue
            
            # Senior should be from earlier batch
            senior_batch_year = int(senior['batch']) if senior['batch'].isdigit() else 0
            if senior_batch_year >= student_batch_year:
                continue
            
            # Check availability
            if not senior.get('available', True):
                continue
            
            matching.append({
                'id': senior_id,
                'name': senior['name'],
                'batch': senior['batch'],
                'specializations': senior['specializations'],
                'years_ahead': student_batch_year - senior_batch_year
            })
        
        # Sort by years ahead (closer batches first)
        matching.sort(key=lambda x: x['years_ahead'])
        
        return matching
    
    async def _send_session_history(self, websocket: WebSocket, session_id: str):
        """Send recent message history to reconnecting user"""
        history = self.message_history.get(session_id, [])
        await websocket.send_json({
            'type': 'message_history',
            'messages': history[-50:]  # Last 50 messages
        })
    
    async def disconnect_student(self, student_id: str):
        """Handle student disconnection"""
        if student_id in self.student_connections:
            del self.student_connections[student_id]
    
    async def disconnect_senior(self, senior_id: str):
        """Handle senior disconnection"""
        if senior_id in self.senior_connections:
            del self.senior_connections[senior_id]
    
    def get_student_profile(self, student_id: str) -> Optional[dict]:
        """Get student profile if exists"""
        return self.student_profiles.get(student_id)
    
    def get_available_seniors(self, course: str = None) -> List[dict]:
        """Get list of all available seniors, optionally filtered by course"""
        seniors = []
        for senior_id, senior in self.available_seniors.items():
            if course and senior['course'].lower() != course.lower():
                continue
            if senior.get('available', True):
                seniors.append({
                    'id': senior_id,
                    'name': senior['name'],
                    'course': senior['course'],
                    'batch': senior['batch'],
                    'specializations': senior['specializations']
                })
        return seniors


# Global instance
senior_chat_manager = SeniorChatManager()