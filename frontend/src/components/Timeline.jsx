export default function Timeline({ events }) {
  if (!events || events.length === 0) {
    return (
      <div className="text-center" style={{ padding: '2rem' }}>
        <p className="text-muted">No friction events recorded</p>
      </div>
    );
  }

  const getSeverityBadge = (severity) => {
    if (severity < 0.4) return 'badge-success';
    if (severity < 0.7) return 'badge-warning';
    return 'badge-error';
  };

  const getSeverityLabel = (severity) => {
    if (severity < 0.4) return 'Low';
    if (severity < 0.7) return 'Moderate';
    return 'High';
  };

  return (
    <div className="timeline">
      {events.map((event, index) => (
        <div key={event.id} className="timeline-item" style={{ animationDelay: `${index * 0.1}s` }}>
          <div className="timeline-content">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '0.75rem' }}>
              <div>
                <h4 style={{ marginBottom: '0.35rem', color: '#1D1D1F', fontWeight: '800', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  {event.event_type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                </h4>
                <span className={`badge ${getSeverityBadge(event.severity)}`}>
                  {getSeverityLabel(event.severity)} Severity
                </span>
              </div>
              <span className="text-black font-bold" style={{ fontSize: '0.85rem' }}>
                {new Date(event.timestamp).toLocaleDateString()}
              </span>
            </div>
            <p className="text-foreground font-medium" style={{ marginBottom: 0, lineHeight: '1.6' }}>
              {event.description}
            </p>
          </div>
        </div>
      ))}
    </div>
  );
}