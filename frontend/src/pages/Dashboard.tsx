import React from 'react'

const Dashboard: React.FC = () => {
    const claims = [
        { id: '1', number: 'CLM-8239', status: 'DECIDED', outcome: 'APPROVED', confidence: 0.94, description: 'Motor accident - front fender damage' },
        { id: '2', number: 'CLM-7412', status: 'DECIDED', outcome: 'DENIED', confidence: 0.88, description: 'Property damage - flood (excluded)' },
        { id: '3', number: 'CLM-9011', status: 'UNDER_REVIEW', outcome: 'PENDING', confidence: 0.45, description: 'Multiple vehicle collision' },
    ]

    return (
        <div>
            <header style={{ marginBottom: '40px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                    <h1 style={{ margin: 0 }}>Claims Dashboard</h1>
                    <p style={{ color: 'var(--text-secondary)', marginTop: '8px' }}>Manage and monitor AI-driven claim decisions.</p>
                </div>
                <button className="btn-primary">+ Submit New Claim</button>
            </header>

            <div className="stats-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '20px', marginBottom: '40px' }}>
                <div className="glass-card" style={{ padding: '20px' }}>
                    <div style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>Total Claims</div>
                    <div style={{ fontSize: '28px', fontWeight: 700, marginTop: '8px' }}>1,284</div>
                </div>
                <div className="glass-card" style={{ padding: '20px' }}>
                    <div style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>Automation Rate</div>
                    <div style={{ fontSize: '28px', fontWeight: 700, marginTop: '8px', color: 'var(--success)' }}>92.4%</div>
                </div>
                <div className="glass-card" style={{ padding: '20px' }}>
                    <div style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>Avg. Confidence</div>
                    <div style={{ fontSize: '28px', fontWeight: 700, marginTop: '8px' }}>0.89</div>
                </div>
                <div className="glass-card" style={{ padding: '20px' }}>
                    <div style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>Pending Overrides</div>
                    <div style={{ fontSize: '28px', fontWeight: 700, marginTop: '8px', color: 'var(--warning)' }}>12</div>
                </div>
            </div>

            <div className="glass-card" style={{ overflow: 'hidden' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                    <thead>
                        <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                            <th style={{ padding: '20px', color: 'var(--text-secondary)' }}>Claim Number</th>
                            <th style={{ padding: '20px', color: 'var(--text-secondary)' }}>Description</th>
                            <th style={{ padding: '20px', color: 'var(--text-secondary)' }}>Status</th>
                            <th style={{ padding: '20px', color: 'var(--text-secondary)' }}>Outcome</th>
                            <th style={{ padding: '20px', color: 'var(--text-secondary)' }}>Confidence</th>
                        </tr>
                    </thead>
                    <tbody>
                        {claims.map(claim => (
                            <tr key={claim.id} style={{ borderBottom: '1px solid var(--border-color)', cursor: 'pointer' }}>
                                <td style={{ padding: '20px', fontWeight: 600 }}>{claim.number}</td>
                                <td style={{ padding: '20px', color: 'var(--text-secondary)' }}>{claim.description}</td>
                                <td style={{ padding: '20px' }}>
                                    <span style={{
                                        padding: '4px 10px',
                                        borderRadius: '100px',
                                        fontSize: '12px',
                                        backgroundColor: 'rgba(255, 255, 255, 0.05)',
                                        border: '1px solid var(--border-color)'
                                    }}>{claim.status}</span>
                                </td>
                                <td style={{ padding: '20px' }}>
                                    <span style={{
                                        color: claim.outcome === 'APPROVED' ? 'var(--success)' : claim.outcome === 'DENIED' ? 'var(--danger)' : 'var(--warning)',
                                        fontWeight: 600
                                    }}>{claim.outcome}</span>
                                </td>
                                <td style={{ padding: '20px' }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                        <div style={{ width: '60px', height: '6px', background: 'rgba(255,255,255,0.1)', borderRadius: '3px' }}>
                                            <div style={{ width: `${claim.confidence * 100}%`, height: '100%', background: 'var(--accent-blue)', borderRadius: '3px' }}></div>
                                        </div>
                                        <span style={{ fontSize: '14px' }}>{(claim.confidence * 100).toFixed(0)}%</span>
                                    </div>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    )
}

export default Dashboard
