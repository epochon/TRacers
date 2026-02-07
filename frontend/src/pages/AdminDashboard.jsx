import { useState, useEffect } from 'react';
import {
  LogOut,
  LayoutDashboard,
  Lightbulb,
  Activity,
  ShieldCheck,
  TrendingUp,
  AlertCircle,
  BarChart3,
  Users,
  Shield,
  Clock,
  ChevronRight,
  Database
} from 'lucide-react';
import { api } from '../api';
import { useAuth } from '../auth';
import { Button } from "../components/ui/button";

const SidebarItem = ({ active, onClick, icon: Icon, label }) => (
  <button
    onClick={onClick}
    className={`w-full flex items-center gap-3 px-5 py-3.5 rounded-xl transition-all duration-200 font-semibold text-sm ${active
      ? 'bg-black text-white shadow-md'
      : 'text-muted-foreground hover:text-foreground hover:bg-gray-100'
      }`}
  >
    <Icon className="w-5 h-5" />
    {label}
  </button>
);

const StatCard = ({ title, value, label, icon: Icon, color = "blue" }) => {
  const colorClasses = {
    blue: "bg-blue-50 text-blue-600",
    purple: "bg-purple-50 text-purple-600",
    amber: "bg-amber-50 text-amber-600",
    emerald: "bg-emerald-50 text-emerald-600",
  };

  return (
    <div className="glass-card p-6 apple-hover">
      <div className="flex justify-between items-start mb-4">
        <div className={`p-3 rounded-2xl ${colorClasses[color] || colorClasses.blue}`}>
          <Icon className="w-6 h-6" />
        </div>
      </div>
      <div className="space-y-1">
        <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-widest">{title}</h3>
        <div className="text-3xl font-bold text-foreground">{value}</div>
        <p className="text-sm text-muted-foreground">{label}</p>
      </div>
    </div>
  );
};

export default function AdminDashboard() {
  const { user, logout } = useAuth();
  const [dashboard, setDashboard] = useState(null);
  const [insights, setInsights] = useState([]);
  const [patterns, setPatterns] = useState(null);
  const [safeguards, setSafeguards] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [dashData, insightsData, patternsData, safeguardsData] = await Promise.all([
        api.getAdminDashboard(),
        api.getSystemInsights(),
        api.getFrictionPatterns(),
        api.getEthicalSafeguards()
      ]);

      setDashboard(dashData);
      setInsights(insightsData);
      setPatterns(patternsData);
      setSafeguards(safeguardsData);
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateInsights = async () => {
    try {
      const result = await api.generateInsights();
      await loadData();
      alert(`Generated ${result.insights.length} new insights`);
    } catch (error) {
      console.error('Failed to generate insights:', error);
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
              <h1 className="text-2xl font-bold tracking-tight text-foreground">Admin Portal</h1>
              <p className="text-sm text-muted-foreground">Systems Overview & Institutional Analytics</p>
            </div>
          </div>

          <div className="flex items-center gap-6">
            <div className="hidden md:block text-right">
              <p className="text-sm font-bold text-foreground">{user?.full_name || user?.username}</p>
              <p className="text-xs text-muted-foreground">Administrator</p>
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
            <SidebarItem
              active={activeTab === 'overview'}
              onClick={() => setActiveTab('overview')}
              icon={LayoutDashboard}
              label="System Overview"
            />
            <SidebarItem
              active={activeTab === 'insights'}
              onClick={() => setActiveTab('insights')}
              icon={Lightbulb}
              label="System Insights"
            />
            <SidebarItem
              active={activeTab === 'patterns'}
              onClick={() => setActiveTab('patterns')}
              icon={Activity}
              label="Friction Patterns"
            />
            <SidebarItem
              active={activeTab === 'safeguards'}
              onClick={() => setActiveTab('safeguards')}
              icon={ShieldCheck}
              label="Ethical Safeguards"
            />
          </aside>

          {/* Main Content Area */}
          <div className="flex-1 min-w-0">
            {/* Overview Tab */}
            {activeTab === 'overview' && dashboard && (
              <div className="space-y-8 animate-in fade-in duration-500">
                <div className="flex items-start gap-4 p-5 rounded-2xl bg-emerald-50 border border-emerald-100 text-emerald-900">
                  <Shield className="w-6 h-6 shrink-0 mt-0.5" />
                  <div>
                    <h4 className="font-bold text-sm mb-1 uppercase tracking-wider">Privacy & Ethics Compliance</h4>
                    <p className="text-sm opacity-90">{dashboard.privacy_note}</p>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <StatCard
                    title="Total Friction Events"
                    value={dashboard.system_statistics.total_friction_events}
                    label="Lifetime recorded events"
                    icon={Database}
                    color="blue"
                  />
                  <StatCard
                    title="Recent Activity"
                    value={dashboard.system_statistics.recent_friction_events}
                    label="Events in last 30 days"
                    icon={TrendingUp}
                    color="purple"
                  />
                  <StatCard
                    title="Primary Friction"
                    value={dashboard.system_statistics.most_common_friction}
                    label="Most occurring barrier"
                    icon={AlertCircle}
                    color="amber"
                  />
                </div>

                <div className="glass-card p-8">
                  <div className="flex items-center gap-3 mb-8">
                    <BarChart3 className="w-6 h-6 text-primary" />
                    <h3 className="text-xl font-bold">Event Type Distribution</h3>
                  </div>
                  <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                    {Object.entries(dashboard.system_statistics.event_type_distribution).map(([type, count]) => (
                      <div key={type} className="p-4 rounded-xl bg-gray-50 border border-gray-100 apple-hover">
                        <div className="text-2xl font-bold text-primary mb-1">{count}</div>
                        <div className="text-xs font-semibold text-muted-foreground uppercase tracking-tight">
                          {type.replace(/_/g, ' ')}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="glass-card p-8">
                  <div className="flex items-center justify-between mb-8">
                    <div className="flex items-center gap-3">
                      <Lightbulb className="w-6 h-6 text-amber-500" />
                      <h3 className="text-xl font-bold">Recent System Insights</h3>
                    </div>
                    <Button variant="outline" size="sm" onClick={() => setActiveTab('insights')} className="rounded-xl">
                      View All <ChevronRight className="w-4 h-4 ml-1" />
                    </Button>
                  </div>
                  <div className="space-y-4">
                    {dashboard.recent_insights.map((insight, idx) => (
                      <div key={idx} className="flex items-start gap-4 p-5 rounded-2xl bg-amber-50 border border-amber-100">
                        <div className="p-2 rounded-lg bg-white shadow-sm flex-shrink-0">
                          <AlertCircle className="w-5 h-5 text-amber-600" />
                        </div>
                        <div className="flex-1">
                          <div className="flex justify-between items-start mb-2">
                            <h4 className="font-bold text-amber-900">{insight.type.replace(/_/g, ' ').toUpperCase()}</h4>
                            <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-red-100 text-red-700">
                              Severity: {(insight.severity * 100).toFixed(0)}%
                            </span>
                          </div>
                          <p className="text-sm text-amber-800 mb-3">{insight.description}</p>
                          <div className="flex items-center gap-2">
                            <Users className="w-4 h-4 text-amber-600" />
                            <span className="text-xs font-semibold text-amber-700">
                              Affects {insight.affected_count} students (anonymized)
                            </span>
                          </div>
                        </div>
                      </div>
                    ))}
                    {dashboard.recent_insights.length === 0 && (
                      <div className="text-center py-10 text-muted-foreground">
                        No recent insights available.
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Insights Tab */}
            {activeTab === 'insights' && (
              <div className="space-y-8 animate-in fade-in duration-500">
                <div className="flex justify-between items-center">
                  <div>
                    <h2 className="text-3xl font-bold mb-2">Institutional Blind Spots</h2>
                    <p className="text-muted-foreground">Identifying systemic process issues across the institution.</p>
                  </div>
                  <Button onClick={handleGenerateInsights} className="rounded-xl shadow-lg">
                    Generate Fresh Insights
                  </Button>
                </div>

                <div className="p-6 rounded-2xl bg-blue-50 border border-blue-100 text-blue-900 flex items-start gap-4">
                  <ShieldCheck className="w-6 h-6 shrink-0 mt-1" />
                  <p className="text-sm font-medium leading-relaxed">
                    These insights are generated by our multi-agent system to identify institutional barriers.
                    They focus on aggregate patterns to maintain student privacy while highlighting process failures.
                  </p>
                </div>

                <div className="space-y-6">
                  {insights.map((insight) => (
                    <div key={insight.id} className="glass-card p-8 apple-hover">
                      <div className="flex justify-between items-start mb-4">
                        <div className="flex gap-2">
                          <span className="px-3 py-1 rounded-full bg-amber-100 text-amber-700 text-xs font-bold uppercase tracking-wider">
                            {insight.insight_type}
                          </span>
                          <span className="px-3 py-1 rounded-full bg-red-100 text-red-700 text-xs font-bold uppercase tracking-wider">
                            Severity: {(insight.severity * 100).toFixed(0)}%
                          </span>
                        </div>
                        <span className="text-xs font-bold text-muted-foreground">{new Date(insight.timestamp).toLocaleDateString()}</span>
                      </div>
                      <h4 className="text-xl font-bold mb-3">{insight.description}</h4>
                      <div className="flex items-center gap-2 text-muted-foreground">
                        <Users className="w-5 h-5" />
                        <span className="text-sm font-medium">Affects {insight.affected_count} students (anonymized)</span>
                      </div>
                    </div>
                  ))}

                  {insights.length === 0 && (
                    <div className="glass-card p-20 text-center">
                      <Lightbulb className="w-12 h-12 text-muted-foreground mx-auto mb-4 opacity-20" />
                      <p className="text-muted-foreground font-semibold mb-6">No insights generated yet</p>
                      <Button onClick={handleGenerateInsights}>Run Analysis Now</Button>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Friction Patterns Tab */}
            {activeTab === 'patterns' && patterns && (
              <div className="space-y-8 animate-in fade-in duration-500">
                <div>
                  <h2 className="text-3xl font-bold mb-2">Friction Pattern Analysis</h2>
                  <p className="text-muted-foreground">Time-period: {patterns.time_period}</p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <StatCard
                    title="Total Events"
                    value={patterns.total_events}
                    label="In current period"
                    icon={Activity}
                    color="blue"
                  />
                  <StatCard
                    title="Weekly Average"
                    value={patterns.events_per_week_avg}
                    label="Stability metric"
                    icon={Clock}
                    color="purple"
                  />
                  <StatCard
                    title="Peak Intensity"
                    value={patterns.peak_friction_weeks.length}
                    label="Critical weeks identified"
                    icon={TrendingUp}
                    color="amber"
                  />
                </div>

                <div className="p-6 rounded-2xl bg-blue-50 border border-blue-100 text-blue-900">
                  <h4 className="font-bold mb-2 uppercase tracking-tight text-sm">System Interpretation</h4>
                  <p className="text-base leading-relaxed opacity-90">{patterns.interpretation}</p>
                </div>

                <div className="glass-card p-8">
                  <h3 className="text-xl font-bold mb-6">Common Event Combinations</h3>
                  <p className="text-sm text-muted-foreground mb-8">Events that frequently occur together, suggesting underlying systemic linkages.</p>
                  <div className="space-y-3">
                    {patterns.common_event_combinations.map((combo, idx) => (
                      <div key={idx} className="flex justify-between items-center p-4 rounded-xl bg-gray-50 border border-gray-100 apple-hover">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-lg bg-white shadow-sm flex items-center justify-center font-bold text-primary">
                            {idx + 1}
                          </div>
                          <span className="font-bold text-foreground">{combo.pair}</span>
                        </div>
                        <span className="px-4 py-1.5 rounded-full bg-primary/10 text-primary text-sm font-bold">
                          {combo.count} occurrences
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Ethical Safeguards Tab */}
            {activeTab === 'safeguards' && safeguards && (
              <div className="space-y-8 animate-in fade-in duration-500">
                <div>
                  <h2 className="text-3xl font-bold mb-2">Ethical Governance</h2>
                  <p className="text-muted-foreground">Monitoring system restraint and student privacy safeguards.</p>
                </div>

                <div className="p-8 rounded-2xl bg-emerald-50 border-2 border-emerald-100 text-emerald-900">
                  <div className="flex items-center gap-4 mb-4">
                    <ShieldCheck className="w-10 h-10 text-emerald-600" />
                    <h3 className="text-2xl font-bold italic">"{safeguards.philosophy}"</h3>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {safeguards.active_safeguards.map((safeguard, idx) => (
                    <div key={idx} className="glass-card p-6 apple-hover">
                      <div className="flex justify-between items-start mb-4">
                        <h4 className="font-bold text-lg">{safeguard.safeguard}</h4>
                        <span className="px-2 py-1 rounded-md bg-emerald-100 text-emerald-700 text-xs font-bold">
                          {safeguard.status}
                        </span>
                      </div>
                      <p className="text-sm text-muted-foreground leading-relaxed">{safeguard.description}</p>
                    </div>
                  ))}
                </div>

                <div className="glass-card p-8">
                  <h3 className="text-xl font-bold mb-6">Restraint Metrics</h3>
                  <p className="text-sm text-muted-foreground mb-8">Verification of the system's commitment to non-interventionist principles.</p>
                  <div className="grid grid-cols-1 gap-4">
                    {Object.entries(safeguards.restraint_metrics).map(([key, value], idx) => (
                      <div key={idx} className="p-5 rounded-2xl bg-gray-50 border border-gray-100">
                        <div className="text-xs font-bold text-primary uppercase tracking-widest mb-2">
                          {key.replace(/_/g, ' ')}
                        </div>
                        <p className="text-foreground font-medium leading-relaxed">{value}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
