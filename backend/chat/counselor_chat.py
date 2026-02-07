"""
Anonymous Counselor Chat
WebSocket-based real-time chat with consent-based identity revelation
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List
from datetime import datetime
import json
import uuid
# ---------------- MODERATION ----------------
from moderation.professionalism_bot import check_message, generate_warning

class CounselorChatManager:
    """
    Manages anonymous chat sessions between students and counselors
    
    Key features:
    - Anonymous by default (session ID only)
    - Consent-based identity revelation
    - Crisis keyword detection
    - Session persistence
    """
    
    def __init__(self):
        # Active WebSocket connections: {session_id: websocket}
        self.active_sessions: Dict[str, WebSocket] = {}
        
        # Counselor connections: {counselor_id: websocket}
        self.active_counselors: Dict[str, WebSocket] = {}
        
        # Session metadata: {session_id: {...}}
        self.session_metadata: Dict[str, dict] = {}
        
        # Message history: {session_id: [messages]}
        self.message_history: Dict[str, List[dict]] = {}
        
        # Crisis keywords for detection
        self.crisis_keywords = [
            'suicide', 'kill myself', 'end it all', 'no reason to live',
            'hurt myself', 'self harm', 'want to die'
        ]
    
    async def connect_student(self, websocket: WebSocket, session_id: str = None) -> str:
        """
        Connect a student to anonymous chat
        Returns session_id
        """
        await websocket.accept()
        
        if session_id is None:
            session_id = f"anon_{uuid.uuid4().hex[:12]}"
        
        self.active_sessions[session_id] = websocket
        self.session_metadata[session_id] = {
            'started_at': datetime.utcnow().isoformat(),
            'is_anonymous': True,
            'student_id': None,
            'assigned_counselor': None
        }
        self.message_history[session_id] = []
        
        # Notify student
        await websocket.send_json({
            'type': 'connection_established',
            'session_id': session_id,
            'message': 'Connected anonymously. A counselor will join shortly.',
            'is_anonymous': True
        })
        
        # Notify available counselors
        await self._notify_counselors_new_session(session_id)
        
        return session_id
    
    async def connect_counselor(self, websocket: WebSocket, counselor_id: str):
        """Connect a counselor to the chat system"""
        await websocket.accept()
        self.active_counselors[counselor_id] = websocket
        
        # Send list of active sessions
        await self._send_active_sessions(counselor_id)
    
    async def handle_student_message(self, session_id: str, message: str):

        websocket = self.active_sessions.get(session_id)
        if not websocket:
            return

        is_allowed, processed_message = check_message(message)

        if not is_allowed:
            await websocket.send_json({
                "type": "moderation_notice",
                "message": generate_warning(message),
                "timestamp": datetime.utcnow().isoformat()
            })
            return

        message = processed_message
        # --------------------------------------------

        crisis_detected = self._detect_crisis(message)

        msg_data = {
            'type': 'student_message',
            'session_id': session_id,
            'message': message,
            'timestamp': datetime.utcnow().isoformat(),
            'crisis_flag': crisis_detected
        }

        self.message_history[session_id].append(msg_data)

        # Echo back to student (CENSORED version)
        await websocket.send_json({
            'type': 'student_message',
            'message': message,
            'timestamp': msg_data['timestamp']
        })

        # Send to counselor if assigned
        metadata = self.session_metadata.get(session_id, {})
        counselor_id = metadata.get('assigned_counselor')

        if counselor_id and counselor_id in self.active_counselors:
            counselor_ws = self.active_counselors[counselor_id]
            await counselor_ws.send_json(msg_data)

            if crisis_detected:
                await counselor_ws.send_json({
                    'type': 'crisis_alert',
                    'session_id': session_id,
                    'message': 'Crisis keywords detected',
                    'requires_immediate_attention': True
                })


    
    async def handle_counselor_message(self, counselor_id: str, session_id: str, message: str):
        """Handle incoming message from counselor"""
        student_ws = self.active_sessions.get(session_id)
        if not student_ws:
            return
        
        # Assign counselor if not already assigned
        if self.session_metadata[session_id].get('assigned_counselor') is None:
            self.session_metadata[session_id]['assigned_counselor'] = counselor_id
        
        # Store message
        msg_data = {
            'type': 'counselor_message',
            'session_id': session_id,
            'message': message,
            'timestamp': datetime.utcnow().isoformat()
        }
        self.message_history[session_id].append(msg_data)
        
        # Send to student
        await student_ws.send_json({
            'type': 'counselor_message',
            'message': message,
            'timestamp': msg_data['timestamp']
        })
    
    async def request_identity_reveal(self, counselor_id: str, session_id: str, reason: str):
        """
        Counselor requests student to reveal identity
        Requires student consent
        """
        student_ws = self.active_sessions.get(session_id)
        if not student_ws:
            return
        
        await student_ws.send_json({
            'type': 'identity_reveal_request',
            'reason': reason,
            'message': 'Your counselor would like to continue support with your identity. This is optional - you can decline.'
        })
    
    async def handle_consent_response(self, session_id: str, consent_given: bool, student_id: str = None):
        """Handle student's response to identity reveal request"""
        metadata = self.session_metadata.get(session_id)
        if not metadata:
            return
        
        if consent_given and student_id:
            metadata['is_anonymous'] = False
            metadata['student_id'] = student_id
            
            # Notify counselor
            counselor_id = metadata.get('assigned_counselor')
            if counselor_id and counselor_id in self.active_counselors:
                counselor_ws = self.active_counselors[counselor_id]
                await counselor_ws.send_json({
                    'type': 'identity_revealed',
                    'session_id': session_id,
                    'student_id': student_id,
                    'message': 'Student has consented to share identity'
                })
        else:
            # Consent declined
            counselor_id = metadata.get('assigned_counselor')
            if counselor_id and counselor_id in self.active_counselors:
                counselor_ws = self.active_counselors[counselor_id]
                await counselor_ws.send_json({
                    'type': 'identity_reveal_declined',
                    'session_id': session_id,
                    'message': 'Student declined to share identity - please continue anonymous support'
                })
    
    def _detect_crisis(self, message: str) -> bool:
        """Detect crisis keywords in message"""
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in self.crisis_keywords)
    
    async def _notify_counselors_new_session(self, session_id: str):
        """Notify all active counselors of new session"""
        for counselor_id, websocket in self.active_counselors.items():
            await websocket.send_json({
                'type': 'new_session',
                'session_id': session_id,
                'message': 'New anonymous student session started'
            })
    
    async def _send_active_sessions(self, counselor_id: str):
        """Send list of active sessions to counselor"""
        counselor_ws = self.active_counselors.get(counselor_id)
        if not counselor_ws:
            return
        
        sessions = []
        for session_id, metadata in self.session_metadata.items():
            if session_id in self.active_sessions:
                sessions.append({
                    'session_id': session_id,
                    'started_at': metadata['started_at'],
                    'is_anonymous': metadata['is_anonymous'],
                    'assigned_counselor': metadata.get('assigned_counselor')
                })
        
        await counselor_ws.send_json({
            'type': 'active_sessions',
            'sessions': sessions
        })
    
    async def disconnect(self, session_id: str = None, counselor_id: str = None):
        """Handle disconnection"""
        if session_id and session_id in self.active_sessions:
            del self.active_sessions[session_id]
            # Keep metadata and history for review
        
        if counselor_id and counselor_id in self.active_counselors:
            del self.active_counselors[counselor_id]


# Global chat manager instance
counselor_chat_manager = CounselorChatManager()