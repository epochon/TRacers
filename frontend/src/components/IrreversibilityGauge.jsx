import React from 'react';

export default function IrreversibilityGauge({ distance, headline }) {
    // Check if distance is valid number
    const val = typeof distance === 'number' ? distance : 0;
    // Assuming distance is normalized 0-1 or 0-100. Let's assume 0-1 based on typical variable naming "distance".
    // If it's a "distance to irreversibility", 0 means irreversible (bad), 1 means safe (good).
    const percentage = Math.min(100, Math.max(0, val * 100));

    const getColor = (p) => {
        if (p < 30) return '#ef4444'; // Red
        if (p < 70) return '#f59e0b'; // Orange
        return '#22c55e'; // Green
    };

    return (
        <div className="irreversibility-gauge" style={{
            padding: '1.5rem',
            background: 'white',
            border: '2px solid #000000',
            borderRadius: '16px',
            boxShadow: '0 10px 30px -10px rgba(0,0,0,0.1)'
        }}>
            <h4 style={{
                margin: '0 0 1rem 0',
                color: '#000000',
                fontWeight: '900',
                textTransform: 'uppercase',
                letterSpacing: '0.1em',
                fontSize: '0.75rem'
            }}>
                {headline || "Friction Trajectory Model"}
            </h4>

            <div style={{
                width: '100%',
                height: '24px',
                background: '#F3F4F6',
                borderRadius: '12px',
                overflow: 'hidden',
                border: '1px solid #E5E7EB',
                position: 'relative'
            }}>
                <div style={{
                    width: `${percentage}%`,
                    height: '100%',
                    background: `linear-gradient(90deg, ${getColor(percentage)}, #ffffff33)`,
                    transition: 'width 1.5s cubic-bezier(0.34, 1.56, 0.64, 1)',
                    boxShadow: `0 0 20px ${getColor(percentage)}44`
                }} />
                {percentage < 30 && (
                    <div className="absolute inset-0 animate-pulse bg-red-500/10 pointer-events-none" />
                )}
            </div>

            <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                marginTop: '0.75rem',
                fontSize: '0.7rem',
                color: '#000000',
                fontWeight: '900',
                textTransform: 'uppercase',
                letterSpacing: '0.05em'
            }}>
                <span>Irreversible</span>
                <span>Safe</span>
            </div>

            <div style={{
                textAlign: 'center',
                marginTop: '1rem',
                fontSize: '2.5rem',
                fontWeight: '900',
                color: getColor(percentage),
                fontFamily: 'monospace',
                letterSpacing: '-0.05em'
            }}>
                {val.toFixed(2)}
            </div>
        </div>
    );
}
