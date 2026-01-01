import React from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, CheckCircle, XCircle, AlertCircle, Info } from 'lucide-react'

const ClaimDetail: React.FC = () => {
    const { id } = useParams()

    // Mock data for a decided claim
    const claim = {
        id: '1',
        number: 'CLM-8239',
        status: 'DECIDED',
        outcome: 'APPROVED',
        confidence: 0.94,
        description: 'Motor accident - front fender damage and headlight shattered. Incident occurred at intersection of Main St and 5th.',
        incidentDate: '2025-12-28',
        amount: '2,450.00 USD',
        policy: {
            number: 'POL-XP-900',
            holder: 'John Doe',
            coverage: 'Comprehensive Plus',
            deductible: '500.00 USD'
        },
        decision: {
            reasoning: "The claim falls under standard comprehensive coverage for collision damage. Damage reported matches the incident description. Third-party evidence (CCTV) confirms the incident details. Fraud score is extremely low (0.02). Coverage limits allow for the full repair cost minus the deductible.",
            trace: [
                { agent: "Intake Agent", action: "Data validation complete.", status: "SUCCESS" },
                { agent: "Document Agent", action: "OCR processed repair invoice. Extracted $2,450.00.", status: "SUCCESS" },
                { agent: "Fraud Agent", action: "ML model score: 0.02. No anomalies detected.", status: "SUCCESS" },
                { agent: "Coverage Agent", action: "LLM verified Policy POL-XP-900. Collision coverage active.", status: "SUCCESS" },
                { agent: "Decision Agent", action: "Final decision: APPROVED. Confidence 94%.", status: "SUCCESS" }
            ]
        }
    }

    return (
        <div>
            <Link to="/dashboard" style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-secondary)', textDecoration: 'none', marginBottom: '24px' }}>
                <ArrowLeft size={16} /> Back to Dashboard
            </Link>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '40px' }}>
                <div>
                    <h1 style={{ margin: 0 }}>Claim {claim.number}</h1>
                    <div style={{ marginTop: '12px', display: 'flex', gap: '16px' }}>
                        <span style={{ color: 'var(--text-secondary)' }}>ID: {claim.id}</span>
                        <span style={{ color: 'var(--text-secondary)' }}>Date: {claim.incidentDate}</span>
                    </div>
                </div>
                <div style={{ textAlign: 'right' }}>
                    <div style={{
                        color: claim.outcome === 'APPROVED' ? 'var(--success)' : 'var(--danger)',
                        fontSize: '24px',
                        fontWeight: 700
                    }}>
                        {claim.outcome}
                    </div>
                    <div style={{ color: 'var(--text-secondary)', marginTop: '4px' }}>AI Confidence: {(claim.confidence * 100).toFixed(0)}%</div>
                </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '32px' }}>
                <div className="left-col">
                    <section className="glass-card" style={{ padding: '32px', marginBottom: '32px' }}>
                        <h3>Claim Reasoning</h3>
                        <p style={{ lineHeight: 1.6, color: 'var(--text-secondary)', fontSize: '16px' }}>{claim.decision.reasoning}</p>

                        <h4 style={{ marginTop: '32px' }}>Agent Execution Trace</h4>
                        <div style={{ marginTop: '16px' }}>
                            {claim.decision.trace.map((step, i) => (
                                <div key={i} style={{ display: 'flex', gap: '16px', padding: '16px 0', borderBottom: i === claim.decision.trace.length - 1 ? 'none' : '1px solid var(--border-color)' }}>
                                    <div style={{ color: 'var(--success)' }}><CheckCircle size={20} /></div>
                                    <div>
                                        <div style={{ fontWeight: 600, fontSize: '14px' }}>{step.agent}</div>
                                        <div style={{ color: 'var(--text-secondary)', fontSize: '14px', marginTop: '4px' }}>{step.action}</div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </section>

                    <section className="glass-card" style={{ padding: '32px' }}>
                        <h3>Claim Details</h3>
                        <div style={{ marginTop: '24px', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
                            <div>
                                <div style={{ color: 'var(--text-secondary)', fontSize: '12px', textTransform: 'uppercase' }}>Amount</div>
                                <div style={{ fontSize: '18px', fontWeight: 600, marginTop: '4px' }}>{claim.amount}</div>
                            </div>
                            <div>
                                <div style={{ color: 'var(--text-secondary)', fontSize: '12px', textTransform: 'uppercase' }}>Policy</div>
                                <div style={{ fontSize: '18px', fontWeight: 600, marginTop: '4px' }}>{claim.policy.number}</div>
                            </div>
                            <div style={{ gridColumn: 'span 2' }}>
                                <div style={{ color: 'var(--text-secondary)', fontSize: '12px', textTransform: 'uppercase' }}>Description</div>
                                <div style={{ fontSize: '15px', lineHeight: 1.5, marginTop: '4px' }}>{claim.description}</div>
                            </div>
                        </div>
                    </section>
                </div>

                <div className="right-col">
                    <div className="glass-card" style={{ padding: '24px', marginBottom: '24px' }}>
                        <h3>Actions</h3>
                        <button className="btn-primary" style={{ width: '100%', marginBottom: '12px' }}>Confirm AI Decision</button>
                        <button style={{
                            width: '100%',
                            background: 'transparent',
                            border: '1px solid var(--border-color)',
                            color: 'white',
                            padding: '10px',
                            borderRadius: '8px',
                            fontWeight: 600,
                            cursor: 'pointer'
                        }}>Override Decision</button>
                    </div>

                    <div className="glass-card" style={{ padding: '24px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
                            <AlertCircle size={18} color="var(--accent-blue)" />
                            <h3 style={{ margin: 0 }}>Policy Check</h3>
                        </div>
                        <div style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>
                            <div style={{ marginBottom: '12px' }}>Holder: {claim.policy.holder}</div>
                            <div style={{ marginBottom: '12px' }}>Coverage: {claim.policy.coverage}</div>
                            <div style={{ marginBottom: '12px' }}>Deductible: {claim.policy.deductible}</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default ClaimDetail
