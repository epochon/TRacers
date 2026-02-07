import { useState, useEffect, useRef } from 'react';
import { Send, User, Shield } from 'lucide-react';
import { Button } from './ui/button';

export default function ChatBox({ title, type }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [socket, setSocket] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const messagesEndRef = useRef(null);
  const clientIdRef = useRef(crypto.randomUUID()); // ✅ stable per tab

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(scrollToBottom, [messages]);

  /* -------------------- WEBSOCKET CONNECTION -------------------- */
  useEffect(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    let wsUrl = null;

    /* counselor chat (unchanged) */
    if (type === 'counselor') {
      wsUrl = `${protocol}//${window.location.host}/ws/counselor-chat/student`;
    }

    /* community chat */
    if (type === 'community') {
      const user = JSON.parse(localStorage.getItem('user'));
      const userId = user?.id || 'anonymous';
      wsUrl = `${protocol}//${window.location.host}/ws/community-chat/general?user_id=${encodeURIComponent(
        userId
      )}&is_anonymous=true`;
    }

    if (!wsUrl) return;

    const ws = new WebSocket(wsUrl);
    setSocket(ws);

    ws.onopen = () => setIsConnected(true);

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);

      /* ---- history ---- */
      if (data.type === 'message_history') {
        setMessages(
          data.messages.map((m) => ({
            id: crypto.randomUUID(),
            text: m.message,
            sender: m.client_id === clientIdRef.current ? 'student' : 'other',
            timestamp: m.timestamp,
            clientId: m.client_id
          }))
        );
        return;
      }

      /* ---- community/system ---- */
      if (data.type === 'chat_message' || data.type === 'system') {
        setMessages((prev) => {
          // Replace optimistic message if client_id matches
          if (data.client_id) {
            return prev.map((msg) =>
              msg.clientId === data.client_id
                ? { ...msg, text: data.message }
                : msg
            );
          }

          return [
            ...prev,
            {
              id: crypto.randomUUID(),
              text: data.message,
              sender:
                data.client_id === clientIdRef.current ? 'student' : 'other',
              timestamp: data.timestamp,
              clientId: data.client_id
            }
          ];
        });
      }

      /* ---- counselor reply ---- */
      if (data.type === 'counselor_message') {
        setMessages((prev) => [
          ...prev,
          {
            id: crypto.randomUUID(),
            text: data.message,
            sender: 'counselor',
            timestamp: data.timestamp
          }
        ]);
      }

      /* ---- counselor reply ---- */
      if (data.type === 'counselor_message') {
        setMessages((prev) => [
          ...prev,
          {
            id: crypto.randomUUID(),
            text: data.message,
            sender: 'counselor',
            timestamp: data.timestamp
          }
        ]);
      }

      if (data.type === 'moderation_notice') {
        alert(data.message);
      }
    };

    ws.onclose = () => setIsConnected(false);

    return () => ws.close();
  }, [type]);

  /* -------------------- SEND MESSAGE -------------------- */
  const handleSend = () => {
    if (!input.trim() || !socket || socket.readyState !== WebSocket.OPEN) return;

    const clientMsgId = crypto.randomUUID();

    // optimistic UI
    setMessages((prev) => [
      ...prev,
      {
        id: clientMsgId,
        text: input,
        sender: 'student',
        timestamp: new Date().toISOString(),
        clientId: clientMsgId
      }
    ]);

    socket.send(
      JSON.stringify({
        type: 'chat_message',
        message: input,
        client_id: clientMsgId
      })
    );

    setInput('');
  };

  return (
    <div className="flex flex-col h-full bg-white relative">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center text-muted-foreground p-6 opacity-80">
            {type === 'counselor' ? <Shield className="w-12 h-12 mb-3 text-primary" /> : <User className="w-12 h-12 mb-3 text-primary" />}
            <p className="max-w-[80%] font-medium">
              {type === 'counselor'
                ? 'Start a conversation anonymously. Your identity is protected.'
                : 'Join the community conversation'}
            </p>
          </div>
        )}

        {messages.map((m) => (
          <div
            key={m.id}
            className={`flex ${m.sender === 'student' ? 'justify-end' : 'justify-start'
              }`}
          >
            <div
              className={`max-w-[80%] rounded-2xl px-4 py-3 ${m.sender === 'student'
                ? 'bg-black text-black rounded-tr-none shadow-sm'
                : m.sender === 'system'
                  ? 'bg-red-50 text-red-700 border border-red-100'
                  : 'bg-gray-100 text-foreground rounded-tl-none border border-border/50'
                }`}
            >
              <p className="text-white text-sm font-medium leading-relaxed">{m.text}</p>
              <div className={`text-[10px] mt-1 font-semibold ${m.sender === 'student' ? 'text-gray-300' : 'text-muted-foreground'}`}>
                {new Date(m.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </div>
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      <div className="p-4 bg-gray-50 border-t border-border">
        <textarea
          className="w-full bg-white border-2 border-border rounded-xl p-3 text-sm text-foreground placeholder:text-muted-foreground focus:ring-2 focus:ring-primary focus:border-primary outline-none transition-all resize-none font-medium"
          placeholder="Type your message..."
          rows="2"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              handleSend();
            }
          }}
        />
        <div className="mt-3 flex justify-between items-center">
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <span
              className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-yellow-500'
                }`}
            />
            {isConnected ? 'Secure Connection' : 'Connecting...'}
          </div>
          <Button
            onClick={handleSend}
            disabled={!input.trim() || !isConnected}
            className="rounded-full px-6"
          >
            Send <Send className="w-4 h-4 ml-2" />
          </Button>
        </div>
      </div>
    </div>
  );
}
