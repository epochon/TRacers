import { useState, useEffect } from 'react';
import { MessageSquare, LogOut } from 'lucide-react';
import { api } from '../api';
import { useAuth } from '../auth';
import RiskCard from '../components/RiskCard';
import IrreversibilityGauge from '../components/IrreversibilityGauge';


export default function CounselorDashboard() {
  const { user, logout } = useAuth();
  const [dashboard, setDashboard] = useState(null);
  const [studentsAtRisk, setStudentsAtRisk] = useState([]);
  const [selectedStudent, setSelectedStudent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [activeSessions, setActiveSessions] = useState([]);
  const [activeChatSession, setActiveChatSession] = useState(null); // Currently selected chat session
  const [chatHistory, setChatHistory] = useState({}); // { session_id: [messages] }
  const [wsConnected, setWsConnected] = useState(false);
  const [socket, setSocket] = useState(null);

  useEffect(() => {
    loadData();
    // Auto-connect to chat on load (optional, or user triggered)
    // connectToChatSystem(); 
    return () => {
      if (socket) socket.close();
    }
  }, []);

  const connectToChatSystem = () => {
    if (!user) return;

    // Connect as current user
    const counselorId = user.username;

    // Use relative path to leverage Vite proxy
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/counselor-chat/counselor/${counselorId}`;

    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log("Connected to Counselor Chat System");
      setWsConnected(true);
      setSocket(ws);
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log("Counselor received:", data);

      if (data.type === 'active_sessions') {
        setActiveSessions(data.sessions);
      } else if (data.type === 'new_session') {
        setActiveSessions(prev => [
          ...prev,
          {
            session_id: data.session_id,
            started_at: new Date().toISOString(),
            unread: true
          }
        ]);
      } else if (data.type === 'student_message') {
        // Update chat history
        setChatHistory(prev => ({
          ...prev,
          [data.session_id]: [
            ...(prev[data.session_id] || []),
            {
              sender: 'student',
              message: data.message,
              timestamp: data.timestamp || new Date().toISOString()
            }
          ]
        }));

        // Allow re-rendering to show unread status if needed
        if (activeChatSession !== data.session_id) {
          // Logic to mark unread could go here
        }
      }
    };

    ws.onclose = () => {
      console.log("Disconnected from Counselor Chat System");
      setWsConnected(false);
    };
  };

  const handleSendMessage = (sessionId, message) => {
    if (!message.trim() || !socket) return;

    // Send to WebSocket
    socket.send(JSON.stringify({
      type: 'message',
      session_id: sessionId,
      message: message
    }));

    // Update local history
    setChatHistory(prev => ({
      ...prev,
      [sessionId]: [
        ...(prev[sessionId] || []),
        {
          sender: 'counselor',
          message: message,
          timestamp: new Date().toISOString()
        }
      ]
    }));
  };

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [dashData, riskData] = await Promise.all([
        api.getCounselorDashboard(),
        api.getStudentsAtRisk()
      ]);

      setDashboard(dashData);
      setStudentsAtRisk(riskData);
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleStudentSelect = async (studentId) => {
    try {
      const details = await api.getStudentDetails(studentId);
      setSelectedStudent(details);
    } catch (error) {
      console.error('Failed to load student details:', error);
    }
  };

  if (loading) {
    return (
      <div className="page-wrapper" style={{ display: 'flex', justifyContent: 'center', padding: '4rem' }}>
        <div className="spinner"></div>
      </div>
    );
  }



  return (
    <div className="min-h-screen bg-white text-foreground">
      {/* Header */}
      <header className="sticky top-0 z-50 border-b border-border bg-white/80 backdrop-blur-xl shadow-sm">
        <div className="container mx-auto px-6 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-xl font-semibold tracking-tight text-foreground">Counselor Dashboard</h1>
            <p className="text-xs text-muted-foreground">Student Support Management</p>
          </div>

          <div className="flex items-center gap-4">
            <div className="text-right hidden md:block">
              <p className="text-sm font-medium text-foreground">{user?.full_name || user?.username}</p>
              <p className="text-xs text-muted-foreground">Counselor Access</p>
            </div>
            <button onClick={logout} className="p-2 hover:bg-secondary rounded-full transition-colors" title="Logout">
              <LogOut className="w-5 h-5" />
            </button>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-6 py-8">

        {/* Tab Navigation */}
        <div className="glass-card p-4 mb-6">
          <div className="flex gap-2">
            <button
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${activeTab === 'overview' ? 'bg-primary text-white shadow-sm' : 'text-muted-foreground hover:bg-secondary'
                }`}
              onClick={() => setActiveTab('overview')}
            >
              Overview
            </button>
            <button
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${activeTab === 'students' ? 'bg-primary text-white shadow-sm' : 'text-muted-foreground hover:bg-secondary'
                }`}
              onClick={() => setActiveTab('students')}
            >
              Students at Risk
            </button>
            <button
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${activeTab === 'sessions' ? 'bg-primary text-white shadow-sm' : 'text-muted-foreground hover:bg-secondary'
                }`}
              onClick={() => setActiveTab('sessions')}
            >
              Anonymous Sessions
            </button>
          </div>
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && dashboard && (
          <div className="fade-in">
            <div className="grid grid-4 mb-xl">
              <div className="card">
                <h4>Total Monitored</h4>
                <div style={{ fontSize: '2.5rem', fontWeight: '700', color: 'var(--primary)', marginTop: '0.5rem' }}>
                  {dashboard.statistics.total_monitored_students}
                </div>
                <p className="text-muted">Students</p>
              </div>

              <div className="card">
                <h4>Need Attention</h4>
                <div style={{ fontSize: '2.5rem', fontWeight: '700', color: 'var(--warning)', marginTop: '0.5rem' }}>
                  {dashboard.statistics.students_needing_attention}
                </div>
                <p className="text-muted">Elevated friction</p>
              </div>

              <div className="card">
                <h4>Soft Outreach</h4>
                <div style={{ fontSize: '2.5rem', fontWeight: '700', color: 'var(--info)', marginTop: '0.5rem' }}>
                  {dashboard.statistics.soft_outreach_recommended}
                </div>
                <p className="text-muted">Recommended</p>
              </div>

              <div className="card">
                <h4>Human Intervention</h4>
                <div style={{ fontSize: '2.5rem', fontWeight: '700', color: 'var(--error)', marginTop: '0.5rem' }}>
                  {dashboard.statistics.human_intervention_recommended}
                </div>
                <p className="text-muted">Recommended</p>
              </div>
            </div>

            <div className="card">
              <div className="alert alert-success">
                <strong>Ethics Note:</strong> {dashboard.ethics_note}
              </div>
            </div>
          </div>
        )}

        {/* Students at Risk Tab */}
        {activeTab === 'students' && (
          <div className="fade-in">
            <div className="card mb-lg">
              <div className="card-header">
                <h3 className="card-title">Students Requiring Attention</h3>
                <span className="badge badge-warning">{studentsAtRisk.length} students</span>
              </div>

              <div className="alert alert-warning" style={{ marginBottom: '2rem' }}>
                <strong>Aggregated View Only:</strong> This shows risk signals based on bureaucratic friction,
                not surveillance. Individual details require justified access.
              </div>
            </div>

            <div className="grid grid-2">
              {studentsAtRisk.map((student) => (
                <RiskCard
                  key={student.student_id}
                  student={student}
                  onSelect={handleStudentSelect}
                />
              ))}
            </div>

            {studentsAtRisk.length === 0 && (
              <div className="card text-center" style={{ padding: '3rem' }}>
                <p className="text-muted">No students currently flagged for attention</p>
              </div>
            )}
          </div>
        )}

        {/* Anonymous Sessions Tab */}
        {activeTab === 'sessions' && (
          <div className="fade-in h-[calc(100vh-200px)] flex gap-6">

            {/* Session List (Left Sidebar) */}
            <div className="w-1/3 card flex flex-col p-0 overflow-hidden">
              <div className="p-4 border-b border-white/10 flex justify-between items-center bg-slate-900/50">
                <h3 className="font-semibold text-lg">Active Sessions</h3>
                <div className="flex items-center gap-2">
                  <div className={`w-2 h-2 rounded-full ${wsConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></div>
                  <span className="text-xs text-muted-foreground">{wsConnected ? 'Live' : 'Offline'}</span>
                </div>
              </div>

              {!wsConnected && (
                <div className="p-6 text-center">
                  <button className="btn btn-primary w-full" onClick={connectToChatSystem}>
                    Connect Now
                  </button>
                </div>
              )}

              <div className="flex-1 overflow-y-auto p-2 space-y-2">
                {wsConnected && activeSessions.length === 0 && (
                  <div className="text-center py-8 text-muted-foreground">
                    <MessageSquare className="w-8 h-8 mx-auto mb-2 opacity-50" />
                    <p className="text-sm">No active sessions</p>
                  </div>
                )}

                {activeSessions.map(session => (
                  <div
                    key={session.session_id}
                    onClick={() => setActiveChatSession(session.session_id)}
                    className={`p-4 rounded-xl cursor-pointer transition-all border ${activeChatSession === session.session_id
                      ? 'bg-primary/20 border-primary/50'
                      : 'bg-white/5 border-transparent hover:bg-white/10'
                      }`}
                  >
                    <div className="flex justify-between items-start mb-1">
                      <span className="font-bold text-sm text-foreground">
                        Anon {session.session_id.substring(5, 9)}
                      </span>
                      {session.unread && activeChatSession !== session.session_id && (
                        <span className="w-2 h-2 bg-red-500 rounded-full animate-bounce"></span>
                      )}
                    </div>
                    <p className="text-xs text-muted-foreground truncate">
                      {chatHistory[session.session_id]?.slice(-1)[0]?.message || "Started new session..."}
                    </p>
                  </div>
                ))}
              </div>
            </div>

            {/* Chat Area (Right Main) */}
            <div className="flex-1 card p-0 overflow-hidden flex flex-col bg-slate-900/80 relative">
              {!activeChatSession ? (
                <div className="flex-1 flex flex-col items-center justify-center text-muted-foreground opacity-50">
                  <MessageSquare className="w-16 h-16 mb-4" />
                  <p className="text-lg">Select a session to start chatting</p>
                </div>
              ) : (
                <>
                  {/* Chat Header */}
                  <div className="p-4 border-b border-border flex justify-between items-center bg-gray-50">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-black flex items-center justify-center text-white text-xs font-bold">
                        ?
                      </div>
                      <div>
                        <h3 className="font-bold text-sm text-black">Anonymous Student</h3>
                        <p className="text-[10px] text-muted-foreground font-medium">ID: {activeChatSession}</p>
                      </div>
                    </div>
                    <button className="btn btn-ghost hover:bg-red-50 hover:text-red-600 btn-sm font-semibold border border-border">
                      End Session
                    </button>
                  </div>

                  {/* Messages */}
                  <div className="flex-1 overflow-y-auto p-4 space-y-4">
                    {(!chatHistory[activeChatSession] || chatHistory[activeChatSession].length === 0) && (
                      <div className="text-center text-xs text-muted-foreground my-4">
                        Session Started. Waiting for student message...
                      </div>
                    )}

                    {chatHistory[activeChatSession]?.map((msg, idx) => (
                      <div key={idx} className={`flex ${msg.sender === 'counselor' ? 'justify-end' : 'justify-start'}`}>
                        <div className={`max-w-[70%] rounded-2xl px-4 py-3 ${msg.sender === 'counselor'
                          ? 'bg-black text-white rounded-tr-none shadow-sm'
                          : 'bg-gray-100 text-black rounded-tl-none border border-border'
                          }`}>
                          <p className="text-sm font-medium leading-relaxed">{msg.message}</p>
                          <div className={`text-[10px] mt-1 font-semibold text-right ${msg.sender === 'counselor' ? 'text-gray-300' : 'text-muted-foreground'}`}>
                            {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Input Area */}
                  <div className="p-4 border-t border-border bg-white">
                    <div className="flex gap-2">
                      <textarea
                        className="flex-1 bg-gray-50 border-2 border-border rounded-xl p-3 text-sm text-black placeholder:text-muted-foreground focus:ring-2 focus:ring-primary focus:border-border outline-none resize-none font-medium"
                        rows="1"
                        placeholder="Type your message..."
                        id="counselor-input"
                        onKeyPress={(e) => {
                          if (e.key === 'Enter' && !e.shiftKey) {
                            e.preventDefault();
                            const input = document.getElementById('counselor-input');
                            handleSendMessage(activeChatSession, input.value);
                            input.value = '';
                          }
                        }}
                      />
                      <button
                        className="bg-black text-white rounded-xl px-6 font-bold text-sm tracking-wide transition-all hover:bg-gray-900 active:scale-95"
                        onClick={() => {
                          const input = document.getElementById('counselor-input');
                          handleSendMessage(activeChatSession, input.value);
                          input.value = '';
                        }}
                      >
                        Send
                      </button>
                    </div>
                  </div>
                </>
              )}
            </div>
          </div>
        )}

        {/* Student Details Modal */}
        {selectedStudent && (
          <div style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0, 0, 0, 0.5)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
            padding: '2rem'
          }}>
            <div className="card" style={{ maxWidth: '800px', width: '100%', maxHeight: '90vh', overflowY: 'auto' }}>
              <div className="card-header">
                <h3 className="card-title">{selectedStudent.student_info.name}</h3>
                <button className="btn btn-ghost" onClick={() => setSelectedStudent(null)}>
                  ✕ Close
                </button>
              </div>

              <div style={{ marginBottom: '1.5rem' }}>
                <h4>Current Assessment</h4>
                <div style={{ marginBottom: '1.5rem', display: 'flex', gap: '1rem' }}>
                  <div style={{ flex: 1 }}>
                    <IrreversibilityGauge
                      distance={selectedStudent.current_assessment.distance_to_irreversibility}
                      headline={selectedStudent.current_assessment.headline}
                    />
                  </div>
                  <div style={{ flex: 1, background: 'var(--bg-secondary)', padding: '1rem', borderRadius: 'var(--radius-md)' }}>
                    <p><strong>Decision:</strong> <span className="badge badge-warning">{selectedStudent.current_assessment.decision}</span></p>
                    <p><strong>Aggregate Risk:</strong> {(selectedStudent.current_assessment.aggregate_risk * 100).toFixed(0)}%</p>
                    <p>{selectedStudent.current_assessment.justification}</p>
                    {selectedStudent.current_assessment.ethics_veto && (
                      <div className="alert alert-error mt-sm">VETOED BY ETHICS AGENT</div>
                    )}
                  </div>
                </div>
              </div>

              <div style={{ marginBottom: '1.5rem' }}>
                <h4>Agent Insights</h4>
                {selectedStudent.agent_insights.map((insight, idx) => (
                  <div key={idx} style={{ background: 'var(--bg-secondary)', padding: '1rem', borderRadius: 'var(--radius-md)', marginBottom: '0.5rem' }}>
                    <strong>{insight.agent}:</strong> {insight.comment}
                    <div style={{ marginTop: '0.5rem' }}>
                      <span className="badge badge-info">Risk: {(insight.risk * 100).toFixed(0)}%</span>
                      <span className="badge badge-success ml-sm">Confidence: {(insight.confidence * 100).toFixed(0)}%</span>
                    </div>
                  </div>
                ))}
              </div>

              <div>
                <h4>Recent Friction Events</h4>
                {selectedStudent.recent_friction_events.map((event, idx) => (
                  <div key={idx} style={{ background: 'var(--bg-secondary)', padding: '1rem', borderRadius: 'var(--radius-md)', marginBottom: '0.5rem' }}>
                    <strong>{event.type}</strong>
                    <p className="text-muted">{event.description}</p>
                    <small className="text-muted">{new Date(event.date).toLocaleDateString()}</small>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}