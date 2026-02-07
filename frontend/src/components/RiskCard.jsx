export default function RiskCard({ student, onSelect }) {
  const getRiskColor = (level) => {
    if (level === 'Low') return 'var(--success)';
    if (level === 'Moderate') return 'var(--warning)';
    return 'var(--error)';
  };

  const getRiskBadge = (level) => {
    if (level === 'Low') return 'badge-success';
    if (level === 'Moderate') return 'badge-warning';
    return 'badge-error';
  };

  const getDecisionBadge = (decision) => {
    if (decision === 'WATCH') return 'badge-info';
    if (decision === 'SOFT_OUTREACH') return 'badge-warning';
    if (decision === 'ESCALATE_TO_HUMAN') return 'badge-error';
    return 'badge-success';
  };

  return (
    <div
      className="card"
      style={{
        borderLeft: `4px solid ${getRiskColor(student.risk_level)}`,
        cursor: 'pointer',
        transition: 'all 0.3s ease'
      }}
      onClick={() => onSelect(student.student_id)}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '1rem' }}>
        <div>
          <h4 style={{ marginBottom: '0.5rem' }}>{student.student_name}</h4>
          <span className={`badge ${getRiskBadge(student.risk_level)}`}>
            {student.risk_level} Risk
          </span>
        </div>
        {student.requires_attention && (
          <span style={{ fontSize: '1.5rem', color: 'var(--warning)' }}>⚠️</span>
        )}
      </div>

      <div style={{ marginBottom: '1rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
          <span className="text-foreground font-bold">Aggregate Risk:</span>
          <span style={{ fontWeight: '800', color: getRiskColor(student.risk_level) }}>
            {(student.aggregate_risk * 100).toFixed(0)}%
          </span>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
          <span className="text-foreground font-bold">Friction Events:</span>
          <span style={{ fontWeight: '800', color: '#000000' }}>{student.friction_count}</span>
        </div>
      </div>

      <div style={{ paddingTop: '1rem', borderTop: '1px solid var(--bg-tertiary)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span className={`badge ${getDecisionBadge(student.decision)}`}>
            {student.decision.replace(/_/g, ' ')}
          </span>
          <span className="text-muted" style={{ fontSize: '0.85rem' }}>
            {new Date(student.last_analyzed).toLocaleDateString()}
          </span>
        </div>
      </div>

      <div style={{ marginTop: '1rem', fontSize: '0.85rem', color: 'var(--info)' }}>
        Click for details →
      </div>
    </div>
  );
}