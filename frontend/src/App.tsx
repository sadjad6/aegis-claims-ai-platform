import React from 'react'
import { BrowserRouter, Routes, Route, Navigate, Link, useLocation } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import ClaimDetail from './pages/ClaimDetail'
import AIOps from './pages/AIOps'
import Login from './pages/Login'
import ProtectedRoute from './auth/ProtectedRoute'
import { useAuth } from './context/AuthContext'

const SidebarLink: React.FC<{ to: string, children: React.ReactNode }> = ({ to, children }) => {
    const location = useLocation();
    const isActive = location.pathname === to || location.pathname.startsWith(to + '/');
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

const AppLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const { user, logout } = useAuth();

    return (
        <div className="app-container" style={{ display: 'flex', minHeight: '100vh' }}>
            <div style={{ width: '260px', borderRight: '1px solid var(--border-color)', padding: '40px 20px', display: 'flex', flexDirection: 'column' }}>
                <h2 className="gradient-text" style={{ fontSize: '24px', margin: 0 }}>AegisClaims AI</h2>
                <nav style={{ marginTop: '60px', flex: 1 }}>
                    <SidebarLink to="/dashboard">Claims Dashboard</SidebarLink>
                    <SidebarLink to="/ai-ops">AI Operations</SidebarLink>
                    <SidebarLink to="/settings">Settings</SidebarLink>
                </nav>

                {user && (
                    <div style={{ borderTop: '1px solid var(--border-color)', paddingTop: '20px' }}>
                        <div style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>{user.name}</div>
                        <div style={{ fontSize: '12px', color: 'var(--text-secondary)', opacity: 0.7 }}>{user.role}</div>
                        <button
                            onClick={logout}
                            style={{
                                marginTop: '12px',
                                background: 'transparent',
                                border: 'none',
                                color: 'var(--danger)',
                                cursor: 'pointer',
                                fontSize: '12px'
                            }}
                        >
                            Logout
                        </button>
                    </div>
                )}
            </div>

            <main style={{ flex: 1, padding: '60px', background: 'radial-gradient(circle at top right, rgba(59, 130, 246, 0.05), transparent)' }}>
                {children}
            </main>
        </div>
    );
};

const App: React.FC = () => {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/login" element={<Login />} />

                <Route element={<ProtectedRoute />}>
                    <Route path="/dashboard" element={<AppLayout><Dashboard /></AppLayout>} />
                    <Route path="/claims/:id" element={<AppLayout><ClaimDetail /></AppLayout>} />
                    <Route path="/ai-ops" element={<AppLayout><AIOps /></AppLayout>} />
                    <Route path="/settings" element={<AppLayout><div>Settings Page</div></AppLayout>} />
                </Route>

                <Route path="/" element={<Navigate to="/dashboard" replace />} />
            </Routes>
        </BrowserRouter>
    )
}

export default App
