import { useState, useEffect, useRef } from 'react';
import { Send, User, GraduationCap, BookOpen, Users as UsersIcon, ChevronRight } from 'lucide-react';
import { Button } from './ui/button';

export default function SeniorChatBox() {
  const [step, setStep] = useState('profile'); // 'profile', 'selection', 'chat'
  const [course, setCourse] = useState('');
  const [batch, setBatch] = useState('');
  const [matchingSeniors, setMatchingSeniors] = useState([]);
  const [selectedSenior, setSelectedSenior] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [socket, setSocket] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(scrollToBottom, [messages]);

  // Course options
  const courses = [
    'Computer Science',
    'Electrical Engineering',
    'Mechanical Engineering',
    'Civil Engineering',
    'Electronics Engineering',
    'Chemical Engineering'
  ];

  // Batch options
  const currentYear = new Date().getFullYear();
  const batches = [
    currentYear.toString(),
    (currentYear - 1).toString(),
    (currentYear - 2).toString(),
    (currentYear - 3).toString()
  ];

  /* -------------------- WEBSOCKET CONNECTION -------------------- */
  useEffect(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const user = JSON.parse(localStorage.getItem('user'));
    const userId = user?.id || 'anonymous';

    // Connect to WebSocket
    const wsUrl = `${protocol}//${window.location.host}/ws/senior-chat/student?user_id=${encodeURIComponent(userId)}`;

    const ws = new WebSocket(wsUrl);
    setSocket(ws);

    ws.onopen = () => {
      console.log('Connected to senior chat');
      setIsConnected(true);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('Received:', data);

        if (data.type === 'connection_established' && data.has_profile) {
          setStep('selection');
        }

        if (data.type === 'profile_submitted') {
          setMatchingSeniors(data.matching_seniors || []);
          setStep('selection');
        }

        if (data.type === 'match_created') {
          setSelectedSenior(data.senior);
          setStep('chat');
        }

        if (data.type === 'message_history') {
          setMessages(
            data.messages.map((m) => ({
              id: crypto.randomUUID(),
              text: m.message,
              sender: m.sender,
              timestamp: m.timestamp
            }))
          );
        }

        if (data.type === 'senior_message') {
          setMessages((prev) => [
            ...prev,
            {
              id: crypto.randomUUID(),
              text: data.message,
              sender: 'senior',
              timestamp: data.timestamp || new Date().toISOString()
            }
          ]);
        }
      } catch (e) {
        console.error("Error processing message:", e);
      }
    };

    ws.onclose = () => {
      console.log('Disconnected from senior chat');
      setIsConnected(false);
    };

    return () => ws.close();
  }, []);

  const handleSubmitProfile = () => {
    if (!course || !batch || !socket || socket.readyState !== WebSocket.OPEN) {
      return;
    }

    socket.send(
      JSON.stringify({
        type: 'submit_profile',
        course: course,
        batch: batch
      })
    );
  };

  const handleSelectSenior = (senior) => {
    if (!socket || socket.readyState !== WebSocket.OPEN) return;

    socket.send(
      JSON.stringify({
        type: 'select_senior',
        senior_id: senior.id
      })
    );
  };

  const handleSend = () => {
    if (!input.trim() || !socket || socket.readyState !== WebSocket.OPEN) return;

    const clientMsgId = crypto.randomUUID();

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

  /* -------------------- PROFILE STEP -------------------- */
  if (step === 'profile') {
    return (
      <div className="flex flex-col h-full bg-white rounded-2xl overflow-hidden shadow-2xl border border-gray-100 ring-1 ring-black/5">
        <div className="flex flex-col items-center justify-center flex-1 p-8 space-y-8 animate-fade-in">
          <div className="p-5 rounded-full bg-black text-white shadow-lg">
            <GraduationCap className="w-12 h-12" />
          </div>

          <div className="text-center space-y-3">
            <h3 className="text-2xl font-bold text-black tracking-tight">Connect with Senior Mentors</h3>
            <p className="text-gray-500 max-w-sm text-sm leading-relaxed">
              Get guidance from experienced seniors in your course. Share your details to find the best matches.
            </p>
          </div>

          <div className="w-full max-w-sm space-y-5">
            <div className="space-y-2">
              <label className="text-xs font-bold text-gray-900 uppercase tracking-wider ml-1">Your Course</label>
              <div className="relative">
                <select
                  value={course}
                  onChange={(e) => setCourse(e.target.value)}
                  className="w-full appearance-none bg-gray-50 border border-gray-200 rounded-xl px-4 py-3.5 text-gray-900 focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent transition-all hover:bg-gray-100 font-medium"
                >
                  <option value="" className="text-gray-500">Select your course</option>
                  {courses.map((c) => (
                    <option key={c} value={c} className="text-gray-900">
                      {c}
                    </option>
                  ))}
                </select>
                <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-gray-400">
                  <ChevronRight className="w-4 h-4 rotate-90" />
                </div>
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-xs font-bold text-gray-900 uppercase tracking-wider ml-1">Your Batch</label>
              <div className="relative">
                <select
                  value={batch}
                  onChange={(e) => setBatch(e.target.value)}
                  className="w-full appearance-none bg-gray-50 border border-gray-200 rounded-xl px-4 py-3.5 text-gray-900 focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent transition-all hover:bg-gray-100 font-medium"
                >
                  <option value="" className="text-gray-500">Select your batch year</option>
                  {batches.map((b) => (
                    <option key={b} value={b} className="text-gray-900">
                      {b}
                    </option>
                  ))}
                </select>
                <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-gray-400">
                  <ChevronRight className="w-4 h-4 rotate-90" />
                </div>
              </div>
            </div>

            <Button
              onClick={handleSubmitProfile}
              disabled={!course || !batch || !isConnected}
              className="w-full rounded-xl py-6 bg-black text-white hover:bg-gray-800 disabled:bg-gray-200 disabled:text-gray-400 font-bold shadow-lg transition-all hover:scale-[1.02] active:scale-[0.98]"
            >
              Find Senior Mentors
            </Button>

            <div className="flex items-center justify-center gap-2 text-[10px] font-bold text-gray-400 uppercase tracking-widest pt-2">
              <span
                className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-yellow-500'}`}
              />
              {isConnected ? 'System Connected' : 'Connecting...'}
            </div>
          </div>
        </div>
      </div>
    );
  }

  /* -------------------- SELECTION STEP -------------------- */
  if (step === 'selection') {
    return (
      <div className="flex flex-col h-full bg-white rounded-2xl overflow-hidden shadow-2xl border border-gray-100 ring-1 ring-black/5">
        <div className="p-6 border-b border-gray-100 bg-white">
          <h3 className="text-lg font-bold text-black flex items-center gap-2">
            <UsersIcon className="w-5 h-5 text-black" />
            Available Mentors
          </h3>
          <p className="text-sm text-gray-500 mt-1">
            {matchingSeniors.length} matches found in {course}
          </p>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-3 custom-scrollbar bg-gray-50/50">
          {matchingSeniors.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-64 text-center p-6 border border-dashed border-gray-200 rounded-xl bg-white mx-2">
              <div className="p-4 rounded-full bg-gray-100 mb-4">
                <UsersIcon className="w-8 h-8 text-gray-400" />
              </div>
              <p className="text-gray-900 font-bold">No mentors online</p>
              <p className="text-xs text-gray-500 mt-1 max-w-[200px]">
                Try checking back later or change your course selection.
              </p>
            </div>
          ) : (
            matchingSeniors.map((senior) => (
              <div
                key={senior.id}
                className="group relative p-4 rounded-xl bg-white border border-gray-200 shadow-sm hover:shadow-md hover:border-black/10 transition-all duration-200 cursor-pointer"
                onClick={() => handleSelectSenior(senior)}
              >
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-full bg-gray-100 flex items-center justify-center border border-gray-200">
                    <User className="w-6 h-6 text-gray-600 group-hover:text-black transition-colors" />
                  </div>

                  <div className="flex-1">
                    <h4 className="font-bold text-gray-900 group-hover:text-black">{senior.name}</h4>
                    <p className="text-xs text-gray-500 mt-0.5 font-medium">
                      Batch {senior.batch} • <span className="text-green-600">{senior.years_ahead} Year{senior.years_ahead !== 1 ? 's' : ''} Senior</span>
                    </p>
                  </div>

                  <div className="opacity-0 group-hover:opacity-100 transition-opacity -translate-x-2 group-hover:translate-x-0 duration-200">
                    <div className="p-2 rounded-full bg-black text-white shadow-lg">
                      <Send className="w-4 h-4" />
                    </div>
                  </div>
                </div>

                {senior.specializations && senior.specializations.length > 0 && (
                  <div className="mt-3 flex flex-wrap gap-2 pl-16">
                    {senior.specializations.slice(0, 3).map((spec) => (
                      <span
                        key={spec}
                        className="text-[10px] px-2.5 py-1 rounded-full bg-gray-100 text-gray-600 font-medium"
                      >
                        {spec}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))
          )}
        </div>

        <div className="p-4 border-t border-gray-100 bg-white">
          <Button
            onClick={() => setStep('profile')}
            variant="ghost"
            className="w-full text-gray-500 hover:text-black hover:bg-gray-100 h-12 rounded-xl border border-gray-200 hover:border-gray-300"
          >
            Change Preference
          </Button>
        </div>
      </div>
    );
  }

  /* -------------------- CHAT STEP -------------------- */
  return (
    <div className="flex flex-col h-full bg-white rounded-2xl overflow-hidden shadow-2xl border border-gray-100 ring-1 ring-black/5">
      {/* Chat Header */}
      <div className="p-4 border-b border-gray-100 bg-white flex items-center justify-between z-10">
        <div className="flex items-center gap-3">
          <div className="relative">
            <div className="w-10 h-10 rounded-full bg-black text-white flex items-center justify-center shadow-lg">
              <span className="text-sm font-bold">
                {selectedSenior?.name?.charAt(0) || 'S'}
              </span>
            </div>
            <div className="absolute bottom-0 right-0 w-3 h-3 rounded-full bg-green-500 border-2 border-white" />
          </div>
          <div>
            <h4 className="font-bold text-gray-900 text-sm">{selectedSenior?.name}</h4>
            <p className="text-[10px] text-gray-500 font-bold uppercase tracking-wider">
              Verified Senior Mentor
            </p>
          </div>
        </div>

        <Button
          onClick={() => {
            setStep('selection');
            setMessages([]);
          }}
          variant="ghost"
          size="sm"
          className="text-gray-400 hover:text-red-500 hover:bg-red-50"
        >
          Exit
        </Button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-6 custom-scrollbar scroll-smooth bg-gray-50/50">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center space-y-4 opacity-0 animate-fade-in fill-mode-forwards" style={{ animationDelay: '0.2s' }}>
            <div className="w-20 h-20 rounded-full bg-white border border-gray-200 flex items-center justify-center mb-2 shadow-sm">
              <Send className="w-8 h-8 text-gray-300" />
            </div>
            <div className="space-y-1">
              <p className="text-gray-900 font-bold">Start the conversation</p>
              <p className="text-sm text-gray-500 max-w-[200px] mx-auto">
                Say hello! Ask about their experience in {course}.
              </p>
            </div>
          </div>
        )}

        {messages.map((m) => (
          <div
            key={m.id}
            className={`flex ${m.sender === 'student' ? 'justify-end' : 'justify-start'
              } animate-fade-in-up`}
          >
            <div
              className={`max-w-[85%] p-4 shadow-sm ${m.sender === 'student'
                  ? 'bg-black text-white rounded-2xl rounded-tr-sm'
                  : 'bg-white text-gray-800 border border-gray-200 rounded-2xl rounded-tl-sm'
                }`}
            >
              <p className="text-sm leading-relaxed font-medium">{m.text}</p>
              <div className={`text-[10px] mt-2 font-bold ${m.sender === 'student' ? 'text-gray-400' : 'text-gray-400'
                }`}>
                {new Date(m.timestamp).toLocaleTimeString([], {
                  hour: '2-digit',
                  minute: '2-digit'
                })}
              </div>
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 bg-white border-t border-gray-100">
        <div className="relative flex items-end gap-2">
          <textarea
            className="w-full bg-gray-50 border border-gray-200 rounded-2xl pl-4 pr-12 py-4 text-sm text-gray-900 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent transition-all resize-none custom-scrollbar font-medium"
            placeholder="Type your message..."
            rows="1"
            value={input}
            onChange={(e) => {
              setInput(e.target.value);
              e.target.style.height = 'auto';
              e.target.style.height = Math.min(e.target.scrollHeight, 100) + 'px';
            }}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
          />
          <Button
            onClick={handleSend}
            disabled={!input.trim() || !isConnected}
            className="absolute right-2 bottom-2 h-9 w-9 p-0 rounded-full bg-black hover:bg-gray-800 text-white shadow-md disabled:opacity-0 transition-all duration-200"
          >
            <Send className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}