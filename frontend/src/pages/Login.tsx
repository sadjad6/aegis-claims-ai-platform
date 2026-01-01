import React, { useState } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Button, Card } from '../components/ui';

const DEMO_TENANTS = [
    { id: 'tenant-acme', name: 'Acme Insurance Co.' },
    { id: 'tenant-shield', name: 'Shield Protect Ltd.' },
    { id: 'tenant-apex', name: 'Apex Coverage Inc.' },
];

const Login: React.FC = () => {
    const { tenantId, login } = useAuth();
    const [selectedTenant, setSelectedTenant] = useState<string | null>(null);

    if (tenantId) {
        return <Navigate to="/dashboard" replace />;
    }

    const handleLogin = () => {
        if (selectedTenant) {
            login(selectedTenant);
        }
    };

    return (
        <div style={{
            minHeight: '100vh',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'radial-gradient(circle at center, rgba(59, 130, 246, 0.1), transparent)',
        }}>
            <Card style={{ width: '400px', textAlign: 'center' }}>
                <h1 className="gradient-text" style={{ marginBottom: '8px' }}>AegisClaims AI</h1>
                <p style={{ color: 'var(--text-secondary)', marginBottom: '32px' }}>
                    Select your organization to continue
                </p>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginBottom: '24px' }}>
                    {DEMO_TENANTS.map(tenant => (
                        <div
                            key={tenant.id}
                            onClick={() => setSelectedTenant(tenant.id)}
                            style={{
                                padding: '16px',
                                border: selectedTenant === tenant.id
                                    ? '2px solid var(--accent-blue)'
                                    : '1px solid var(--border-color)',
                                borderRadius: '8px',
                                cursor: 'pointer',
                                background: selectedTenant === tenant.id ? 'rgba(59, 130, 246, 0.1)' : 'transparent',
                                transition: 'all 0.2s',
                            }}
                        >
                            <div style={{ fontWeight: 600 }}>{tenant.name}</div>
                            <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>{tenant.id}</div>
                        </div>
                    ))}
                </div>

                <Button onClick={handleLogin} fullWidth disabled={!selectedTenant}>
                    Continue to Dashboard
                </Button>

                <p style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '24px' }}>
                    In production, this would integrate with AWS Cognito OIDC
                </p>
            </Card>
        </div>
    );
};

export default Login;
