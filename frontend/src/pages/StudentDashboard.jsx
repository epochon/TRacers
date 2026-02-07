import { useState, useEffect } from 'react';
import { api } from '../api';
import Timeline from '../components/Timeline';
import ChatBox from '../components/ChatBox';
import SeniorChatBox from '../components/SeniorChatBox';
import AgentPanel from '../components/AgentPanel';
import CalendarSync from '../components/CalendarSync';
import DocumentAssistant from '../components/DocumentAssistant';
import GovConnectLanding from '../components/GovConnectLanding';
import IrreversibilityGauge from '../components/IrreversibilityGauge';
import { LayoutDashboard, Clock, MessageSquare, Activity, FileText, TrendingUp, Shield, Users, LogOut, Calendar, UserCheck, Building2 } from 'lucide-react';
import { Button } from "../components/ui/button";
import { useAuth } from '../auth';


const TabButton = ({ active, onClick, icon: Icon, label }) => (
  <button
    onClick={onClick}
    className={`flex items-center gap-3 px-5 py-3.5 rounded-xl transition-all duration-200 font-semibold text-sm ${active
      ? 'bg-black text-white shadow-md'
      : 'text-muted-foreground hover:text-foreground hover:bg-gray-100'
      }`}
  >
    <Icon className="w-5 h-5" />
    {label}
  </button>
);

const StatCard = ({ title, value, label, icon: Icon, trend }) => (
  <div className="glass-card p-8 apple-hover">
    <div className="flex justify-between items-start mb-6">
      <div className="p-4 rounded-2xl bg-blue-50 text-primary">
        <Icon className="w-7 h-7" />
      </div>
      {trend && (
        <span className="text-xs font-bold px-3 py-1.5 rounded-full bg-green-50 text-green-700 border border-green-100">
          {trend}
        </span>
      )}
    </div>
    <div className="space-y-2">
      <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">{title}</h3>
      <div className="text-4xl font-bold text-foreground">{value}</div>
      <p className="text-sm text-muted-foreground">{label}</p>
    </div>
  </div>
);

export default function StudentDashboard() {
  const { logout } = useAuth();
  const [dashboard, setDashboard] = useState(null);
  const [timeline, setTimeline] = useState(null);
  const [resources, setResources] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [dashData, timelineData, resourcesData] = await Promise.all([
        api.getStudentDashboard(),
        api.getStudentTimeline(),
        api.getSupportResources()
      ]);

      setDashboard(dashData);
      setTimeline(timelineData);
      setResources(resourcesData);
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-white">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-black"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 text-foreground">
      {/* Header */}
      <header className="sticky top-0 z-50 border-b border-border bg-white/95 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-8 py-5 flex justify-between items-center">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-2xl bg-black flex items-center justify-center shadow-md">
              <span className="font-bold text-white text-xl">T</span>
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-foreground">Student Portal</h1>
              <p className="text-sm text-muted-foreground">TRACERS System</p>
            </div>
          </div>

          <div className="flex items-center gap-6">
            <div className="hidden md:block text-right">
              <p className="text-sm font-bold text-foreground">{dashboard?.student_name}</p>
              <p className="text-xs text-muted-foreground">ID: {dashboard?.student_id}</p>
            </div>
            <Button variant="ghost" size="icon" onClick={logout} title="Logout" className="hover:bg-gray-100 rounded-xl">
              <LogOut className="w-5 h-5" />
            </Button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-8 py-10">
        <div className="flex flex-col lg:flex-row gap-8">
          {/* Sidebar Navigation */}
          <aside className="w-full lg:w-72 flex-shrink-0 space-y-3">
            <TabButton
              active={activeTab === 'overview'}
              onClick={() => setActiveTab('overview')}
              icon={LayoutDashboard}
              label="Overview"
            />
            <TabButton
              active={activeTab === 'timeline'}
              onClick={() => setActiveTab('timeline')}
              icon={Clock}
              label="My Timeline"
            />
            <TabButton
              active={activeTab === 'support'}
              onClick={() => setActiveTab('support')}
              icon={MessageSquare}
              label="Get Support"
            />
            <TabButton
              active={activeTab === 'calendar'}
              onClick={() => setActiveTab('calendar')}
              icon={Calendar}
              label="Calendar Sync"
            />
            <TabButton
              active={activeTab === 'document'}
              onClick={() => setActiveTab('document')}
              icon={FileText}
              label="Document Assistant"
            />
            <TabButton
              active={activeTab === 'insights'}
              onClick={() => setActiveTab('insights')}
              icon={Activity}
              label="System Insights"
            />
            <TabButton
              active={activeTab === 'senior'}
              onClick={() => setActiveTab('senior')}
              icon={UserCheck}
              label="Senior Chat"
            />
            <TabButton
              active={activeTab === 'gov'}
              onClick={() => setActiveTab('gov')}
              icon={Building2}
              label="GovConnect"
            />
          </aside>

          {/* Main Content Area */}
          <div className="flex-1 space-y-8">

            {activeTab === 'overview' && (
              <div className="space-y-8">
                {/* Stats Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  <StatCard
                    title="Friction Events"
                    value={dashboard.total_friction_events}
                    label="Total administrative hurdles"
                    icon={FileText}
                    trend={dashboard.recent_friction_events > 0 ? `+${dashboard.recent_friction_events} new` : null}
                  />
                  <StatCard
                    title="System Status"
                    value="Monitoring"
                    label="Active protection active"
                    icon={Shield}
                  />
                  <div className="glass-card p-8 md:col-span-1 lg:col-span-1 bg-blue-50 border-blue-100">
                    <h3 className="text-sm font-bold text-muted-foreground uppercase tracking-wide mb-6">Irreversibility Risk</h3>
                    <IrreversibilityGauge
                      distance={dashboard.distance_to_irreversibility}
                      headline={dashboard.headline}
                    />
                  </div>
                </div>

                {/* Trajectory Card */}
                <div className="glass-card p-10">
                  <div className="flex items-center gap-4 mb-8">
                    <div className="p-3 rounded-2xl bg-blue-50 text-primary">
                      <TrendingUp className="w-6 h-6" />
                    </div>
                    <h3 className="text-2xl font-bold text-foreground">Your Trajectory Analysis</h3>
                  </div>

                  <p className="text-lg leading-relaxed text-foreground mb-8">
                    {dashboard.trajectory_summary}
                  </p>

                  {dashboard.support_available && (
                    <div className="flex items-start gap-5 p-6 rounded-2xl bg-blue-50 border-2 border-blue-100 text-blue-900">
                      <Shield className="w-6 h-6 shrink-0 mt-1" />
                      <div>
                        <h4 className="font-bold text-lg mb-2">Support Available</h4>
                        <p className="text-base leading-relaxed">
                          Based on your friction trajectory, you may benefit from connecting with a counselor.
                          This is entirely optional and under your control.
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {activeTab === 'timeline' && timeline && (
              <div className="glass-card p-10">
                <div className="flex justify-between items-center mb-10">
                  <div>
                    <h2 className="text-3xl font-bold mb-3 text-foreground">Bureaucratic Timeline</h2>
                    <p className="text-base text-muted-foreground">Tracking administrative friction, not your potential.</p>
                  </div>
                  <div className="px-5 py-2.5 rounded-full bg-gray-100 border border-border text-sm font-bold text-foreground">
                    {timeline.total_events} Events Recorded
                  </div>
                </div>
                <Timeline events={timeline.events} />
              </div>
            )}

            {activeTab === 'support' && resources && (
              <div className="grid md:grid-cols-2 gap-8">
                <div className="glass-card p-8">
                  <div className="flex items-center gap-4 mb-8">
                    <div className="p-3 rounded-2xl bg-green-50 text-green-700">
                      <Shield className="w-6 h-6" />
                    </div>
                    <div>
                      <h3 className="font-bold text-xl text-foreground">Anonymous Counselor</h3>
                      <p className="text-sm text-muted-foreground">Private, confidential support</p>
                    </div>
                  </div>

                  <div className="mb-8 h-[400px] rounded-2xl overflow-hidden border-2 border-border">
                    <ChatBox title="Chat with Counselor" type="counselor" />
                  </div>

                  <div className="text-sm text-muted-foreground space-y-2 pl-4 border-l-2 border-green-200">
                    <p className="font-medium">✓ Completely anonymous</p>
                    <p className="font-medium">✓ Consent-based identity reveal</p>
                    <p className="font-medium">✓ No forced intervention</p>
                  </div>
                </div>

                <div className="glass-card p-8">
                  <div className="flex items-center gap-4 mb-8">
                    <div className="p-3 rounded-2xl bg-blue-50 text-primary">
                      <Users className="w-6 h-6" />
                    </div>
                    <div>
                      <h3 className="font-bold text-xl text-foreground">Community Hub</h3>
                      <p className="text-sm text-muted-foreground">Peer-to-peer connection</p>
                    </div>
                  </div>

                  <div className="mb-8 h-[400px] rounded-2xl overflow-hidden border-2 border-border">
                    <ChatBox title="First-Year Community" type="community" />
                  </div>

                  <div className="text-sm text-muted-foreground">
                    Active Rooms: <span className="text-primary font-bold">General, Academic Support, Campus Life</span>
                  </div>
                </div>
              </div>

            )}

            {activeTab === 'calendar' && (
              <CalendarSync />
            )}

            {activeTab === 'document' && (
              <div className="glass-card p-0 animate-fade-in-up overflow-hidden h-[600px]">
                <DocumentAssistant />
              </div>
            )}

            {activeTab === 'insights' && (
              <div className="glass-card p-10">
                <div className="flex items-center gap-4 mb-8">
                  <div className="p-3 rounded-2xl bg-blue-50 text-primary">
                    <Activity className="w-6 h-6" />
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold text-foreground">System Perception</h2>
                    <p className="text-base text-muted-foreground">How the Multi-Agent System interprets your context to prevent dropout.</p>
                  </div>
                </div>
                <AgentPanel />
              </div>
            )}

            {activeTab === 'senior' && (
              <div className="glass-card p-0 animate-fade-in-up overflow-hidden" style={{ height: '600px' }}>
                <SeniorChatBox />
              </div>
            )}

            {activeTab === 'gov' && (
              <div className="glass-card p-0 animate-fade-in-up overflow-hidden" style={{ minHeight: '600px' }}>
                <GovConnectLanding />
              </div>
            )}

          </div>
        </div>
      </main>
    </div>
  );
}