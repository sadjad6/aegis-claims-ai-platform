import React, { createContext, useContext, useState, useEffect } from 'react';

interface User {
    id: string;
    name: string;
    role: 'ADMIN' | 'ADJUSTER' | 'OPS';
    tenantId: string;
}

interface AuthContextType {
    user: User | null;
    tenantId: string | null;
    login: (tenantId: string) => void;
    logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [user, setUser] = useState<User | null>(null);
    const [tenantId, setTenantId] = useState<string | null>(localStorage.getItem('tenant_id'));

    useEffect(() => {
        if (tenantId) {
            // In real app, verify with Cognito/Auth0
            setUser({
                id: 'user-1',
                name: 'Jane Adjuster',
                role: 'ADJUSTER',
                tenantId: tenantId
            });
        }
    }, [tenantId]);

    const login = (id: string) => {
        setTenantId(id);
        localStorage.setItem('tenant_id', id);
    };

    const logout = () => {
        setTenantId(null);
        setUser(null);
        localStorage.removeItem('tenant_id');
    };

    return (
        <AuthContext.Provider value={{ user, tenantId, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) throw new Error('useAuth must be used within AuthProvider');
    return context;
};
