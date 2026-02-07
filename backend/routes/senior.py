"""
WebSocket Routes for Chat Features
Senior Chat and GovConnect WebSocket endpoints
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from chat.senior_chat import senior_chat_manager
import json

router = APIRouter()


@router.websocket("/ws/senior-chat/student")
async def senior_chat_student_endpoint(
    websocket: WebSocket,
    user_id: str = Query(...)
):
    """
    WebSocket endpoint for students in senior chat
    """
    try:
        # Connect student
        await senior_chat_manager.connect_student(websocket, user_id)
        
        while True:
            # Receive message
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            message_type = message_data.get('type')
            
            if message_type == 'submit_profile':
                # Student submitting course and batch
                course = message_data.get('course')
                batch = message_data.get('batch')
                await senior_chat_manager.submit_student_profile(
                    user_id, course, batch
                )
            
            elif message_type == 'select_senior':
                # Student selecting a senior mentor
                senior_id = message_data.get('senior_id')
                await senior_chat_manager.match_with_senior(
                    user_id, senior_id
                )
            
            elif message_type == 'chat_message':
                # Student sending message
                message = message_data.get('message')
                client_id = message_data.get('client_id')
                await senior_chat_manager.handle_student_message(
                    user_id, message, client_id
                )
    
    except WebSocketDisconnect:
        await senior_chat_manager.disconnect_student(user_id)
    except Exception as e:
        print(f"Senior chat error: {e}")
        await senior_chat_manager.disconnect_student(user_id)


@router.websocket("/ws/senior-chat/senior")
async def senior_chat_senior_endpoint(
    websocket: WebSocket,
    senior_id: str = Query(...)
):
    """
    WebSocket endpoint for senior mentors
    (For future implementation)
    """
    await websocket.accept()
    try:
        await websocket.send_json({
            'type': 'info',
            'message': 'Senior interface coming soon'
        })
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass