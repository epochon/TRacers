"""
First-Year Community Chat
Topic-based chat rooms with optional anonymity and moderation
"""

from fastapi import WebSocket
from typing import Dict, List
from datetime import datetime
import uuid


class CommunityChatManager:
    """
    Manages community chat rooms for first-year students
    """

    def __init__(self):
        self.rooms: Dict[str, dict] = {}
        self.connections: Dict[str, Dict[str, WebSocket]] = {}
        self.message_history: Dict[str, List[dict]] = {}

        self._initialize_default_rooms()

    def _initialize_default_rooms(self):
        default_rooms = [
            {
                'id': 'general',
                'name': 'General Discussion',
                'description': 'General first-year student topics',
                'allow_anonymous': True
            },
            {
                'id': 'academic',
                'name': 'Academic Support',
                'description': 'Study tips, course selection, academic challenges',
                'allow_anonymous': True
            },
            {
                'id': 'campus_life',
                'name': 'Campus Life',
                'description': 'Events, clubs, campus resources',
                'allow_anonymous': False
            },
            {
                'id': 'wellness',
                'name': 'Wellness & Balance',
                'description': 'Mental health, stress management, self-care',
                'allow_anonymous': True
            }
        ]

        for room in default_rooms:
            self.rooms[room['id']] = {
                **room,
                'created_at': datetime.utcnow().isoformat(),
                'active_users': set(),
                'message_count': 0,
                'user_names': {}   # ✅ FIX 3: persistent identities
            }
            self.message_history[room['id']] = []

    async def join_room(
        self,
        websocket: WebSocket,
        room_id: str,
        user_id: str,
        is_anonymous: bool = False,
        display_name: str = None
    ) -> bool:

        if room_id not in self.rooms:
            return False

        room = self.rooms[room_id]

        if is_anonymous and not room['allow_anonymous']:
            await websocket.send_json({
                'type': 'error',
                'message': 'This room requires identified participation'
            })
            return False

        await websocket.accept()

        # store connection
        self.connections.setdefault(user_id, {})
        self.connections[user_id][room_id] = websocket
        room['active_users'].add(user_id)

        # ✅ FIX: ALWAYS define final_display_name
        if is_anonymous:
            final_display_name = f"Anonymous{uuid.uuid4().hex[:4]}"
        elif display_name:
            final_display_name = display_name
        else:
            final_display_name = f"User{user_id}"

        room['user_names'][user_id] = final_display_name

        # notify others
        await self._broadcast_to_room(
            room_id,
            {
                'type': 'user_joined',
                'display_name': final_display_name,
                'timestamp': datetime.utcnow().isoformat()
            },
            exclude_user=user_id
        )

        await self._send_recent_history(websocket, room_id)
        return True


    async def handle_message(
        self,
        room_id: str,
        user_id: str,
        message: str,
        is_anonymous: bool = False,
        display_name: str = None,
        client_id: str = None
    ):


        if room_id not in self.rooms:
            return

        from moderation.professionalism_bot import check_message, generate_warning

        # Moderate message
        is_appropriate, moderated_message = check_message(message)

        # ✅ FIX 4: server-side moderation log
        print("[MODERATION]", {
            "room": room_id,
            "user": user_id,
            "message": message,
            "allowed": is_appropriate
        })

        room = self.rooms[room_id]
        final_display_name = room['user_names'].get(user_id, "User")

        # ❌ BLOCKED MESSAGE FLOW
        if not is_appropriate:
            # private warning to sender
            user_ws = self.connections.get(user_id, {}).get(room_id)
            if user_ws:
                await user_ws.send_json({
                    'type': 'moderation_notice',
                    'message': generate_warning(message),
                    'timestamp': datetime.utcnow().isoformat()
                })

            # ✅ FIX 5: visible system message
            await self._broadcast_to_room(room_id, {
                'type': 'system',
                'message': '⚠️ A message was removed for violating community guidelines.',
                'timestamp': datetime.utcnow().isoformat()
            })
            return

        # ✅ NORMAL MESSAGE FLOW (FIX 2)
        msg_data = {
            'type': 'chat_message',
            'room_id': room_id,
            'user_id': None if is_anonymous else user_id,
            'display_name': final_display_name,
            'message': moderated_message,
            'client_id': client_id,  # ✅ SAFE NOW
            'is_anonymous': is_anonymous,
            'timestamp': datetime.utcnow().isoformat()
        }




        self.message_history[room_id].append(msg_data)
        room['message_count'] += 1

        await self._broadcast_to_room(room_id, msg_data)

    async def leave_room(self, room_id: str, user_id: str):
        if room_id not in self.rooms:
            return

        room = self.rooms[room_id]
        room['active_users'].discard(user_id)
        room['user_names'].pop(user_id, None)

        if user_id in self.connections:
            self.connections[user_id].pop(room_id, None)
            if not self.connections[user_id]:
                del self.connections[user_id]

        await self._broadcast_to_room(room_id, {
            'type': 'user_left',
            'timestamp': datetime.utcnow().isoformat()
        })

    async def _broadcast_to_room(self, room_id: str, message: dict, exclude_user: str = None):
        room = self.rooms.get(room_id)
        if not room:
            return

        for uid in list(room['active_users']):
            if exclude_user and uid == exclude_user:
                continue
            ws = self.connections.get(uid, {}).get(room_id)
            if ws:
                try:
                    await ws.send_json(message)
                except:
                    await self.leave_room(room_id, uid)

    async def _send_recent_history(self, websocket: WebSocket, room_id: str, limit: int = 50):
        history = self.message_history.get(room_id, [])
        await websocket.send_json({
            'type': 'message_history',
            'messages': history[-limit:]
        })


# Global instance
community_chat_manager = CommunityChatManager()
