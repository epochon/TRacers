import { useState, useEffect } from 'react';
import { api } from '../api';

export default function AgentPanel() {
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAnalysis();
  }, []);

  const loadAnalysis = async () => {
    try {
      // In the new backend, getAgentAnalysis might fetch from models or a dedicated endpoint
      // Assuming api.getAgentAnalysis() hits /api/analyze-student/{id} or gets stored analysis
      // For demo, we might need to trigger analysis first
      const data = await api.getAgentAnalysis();
      setAnalysis(data);
    } catch (error) {
      console.error('Failed to load analysis:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', padding: '2rem' }}>
        <div className="spinner"></div>
      </div>
    );
  }

  // Handle both old and new schema
  const outputs = analysis?.agent_outputs || analysis?.analysis || [];

  if (outputs.length === 0) {
    return (
      <div className="text-center" style={{ padding: '2rem' }}>
        <p className="text-muted">Waiting to initialize collective debate...</p>
      </div>
    );
  }

  return (
    <div>
      <div style={{ marginBottom: '1.5rem', display: 'flex', justifyContent: 'space-between' }}>
        <span className="text-muted">
          COLLECTIVE INTELLIGENCE DEBATE
        </span>
        <span className="badge badge-info">{outputs.length} AGENTS ACTIVE</span>
      </div>

      <div className="debate-container">
        {outputs.map((agent, idx) => (
          <div
            key={idx}
            className={`debate-bubble ${agent.agent || agent.agent_name}`}
            style={{ animation: `slideInUp ${0.3 + idx * 0.1}s ease` }}
          >
            <span className="agent-name">
              {agent.agent || agent.agent_name}
            </span>

            <p style={{ margin: 0, color: 'var(--text-primary)' }}>
              {agent.reasoning || agent.comment || 'No assessment provided.'}
            </p>

            <div style={{ marginTop: '0.5rem', display: 'flex', gap: '0.5rem', fontSize: '0.75rem' }}>
              {agent.risk !== undefined && (
                <span className="badge badge-warning">RISK: {agent.risk}</span>
              )}
              {agent.capacity_score !== undefined && (
                <span className="badge badge-success">CAPACITY: {agent.capacity_score}</span>
              )}
              {agent.inertia_score !== undefined && (
                <span className="badge badge-error">INERTIA: {agent.inertia_score}</span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}