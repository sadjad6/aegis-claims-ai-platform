import React from 'react'
import { BrowserRouter, Routes, Route, Navigate, Link, useLocation } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import ClaimDetail from './pages/ClaimDetail'
import AIOps from './pages/AIOps'

const SidebarLink: React.FC<{ to: string, children: React.ReactNode }> = ({ to, children }) => {
    const location = useLocation();
    const isActive = location.pathname === to;
    return (
        <Link to={to} style={{
            display: 'block',
            color: isActive ? 'var(--accent-blue)' : 'var(--text-secondary)',
            fontWeight: isActive ? 600 : 400,
            textDecoration: 'none',
            marginTop: '20px'
        }}>
            {children}
        </Link>
    );
};

const App: React.FC = () => {
    return (
        <BrowserRouter>
            <div className="app-container" style={{ display: 'flex', minHeight: '100vh' }}>
                <div style={{ width: '260px', borderRight: '1px solid var(--border-color)', padding: '40px 20px' }}>
                    <h2 className="gradient-text" style={{ fontSize: '24px', margin: 0 }}>AegisClaims AI</h2>
                    <nav style={{ marginTop: '60px' }}>
                        <SidebarLink to="/dashboard">Claims Dashboard</SidebarLink>
                        <SidebarLink to="/ai-ops">AI Operations</SidebarLink>
                        <SidebarLink to="/settings">Settings</SidebarLink>
                    </nav>
                </div>

                <main style={{ flex: 1, padding: '60px', background: 'radial-gradient(circle at top right, rgba(59, 130, 246, 0.05), transparent)' }}>
                    <Routes>
                        <Route path="/dashboard" element={<Dashboard />} />
                        <Route path="/claims/:id" element={<ClaimDetail />} />
                        <Route path="/ai-ops" element={<AIOps />} />
                        <Route path="/" element={<Navigate to="/dashboard" replace />} />
                    </Routes>
                </main>
            </div>
        </BrowserRouter>
    )
}

export default App
