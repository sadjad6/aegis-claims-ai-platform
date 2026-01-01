import React from 'react';

interface CardProps {
    children: React.ReactNode;
    className?: string;
    style?: React.CSSProperties;
}

export const Card: React.FC<CardProps> = ({ children, className = '', style }) => (
    <div className={`glass-card ${className}`} style={{ padding: '24px', ...style }}>
        {children}
    </div>
);

interface StatCardProps {
    label: string;
    value: string | number;
    color?: string;
    trend?: string;
}

export const StatCard: React.FC<StatCardProps> = ({ label, value, color, trend }) => (
    <Card>
        <div style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>{label}</div>
        <div style={{ fontSize: '28px', fontWeight: 700, marginTop: '8px', color: color || 'inherit' }}>
            {value}
        </div>
        {trend && (
            <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '4px' }}>
                {trend}
            </div>
        )}
    </Card>
);

interface ButtonProps {
    children: React.ReactNode;
    variant?: 'primary' | 'secondary';
    onClick?: () => void;
    fullWidth?: boolean;
    disabled?: boolean;
}

export const Button: React.FC<ButtonProps> = ({
    children,
    variant = 'primary',
    onClick,
    fullWidth,
    disabled
}) => {
    const baseStyle: React.CSSProperties = {
        width: fullWidth ? '100%' : 'auto',
        padding: '10px 20px',
        borderRadius: '8px',
        fontWeight: 600,
        cursor: disabled ? 'not-allowed' : 'pointer',
        opacity: disabled ? 0.5 : 1,
    };

    const variantStyles: Record<string, React.CSSProperties> = {
        primary: {
            background: 'linear-gradient(135deg, var(--accent-blue), var(--accent-purple))',
            border: 'none',
            color: 'white',
        },
        secondary: {
            background: 'transparent',
            border: '1px solid var(--border-color)',
            color: 'white',
        },
    };

    return (
        <button
            style={{ ...baseStyle, ...variantStyles[variant] }}
            onClick={onClick}
            disabled={disabled}
        >
            {children}
        </button>
    );
};

interface BadgeProps {
    children: React.ReactNode;
    variant?: 'success' | 'warning' | 'danger' | 'neutral';
}

export const Badge: React.FC<BadgeProps> = ({ children, variant = 'neutral' }) => {
    const colorMap: Record<string, string> = {
        success: 'var(--success)',
        warning: 'var(--warning)',
        danger: 'var(--danger)',
        neutral: 'var(--text-secondary)',
    };

    return (
        <span style={{
            padding: '4px 12px',
            borderRadius: '100px',
            fontSize: '12px',
            fontWeight: 600,
            color: colorMap[variant],
            backgroundColor: `${colorMap[variant]}20`,
            border: `1px solid ${colorMap[variant]}40`,
        }}>
            {children}
        </span>
    );
};

interface ConfidenceBarProps {
    value: number;
}

export const ConfidenceBar: React.FC<ConfidenceBarProps> = ({ value }) => (
    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <div style={{ width: '60px', height: '6px', background: 'rgba(255,255,255,0.1)', borderRadius: '3px' }}>
            <div style={{
                width: `${value * 100}%`,
                height: '100%',
                background: value > 0.7 ? 'var(--success)' : value > 0.4 ? 'var(--warning)' : 'var(--danger)',
                borderRadius: '3px'
            }} />
        </div>
        <span style={{ fontSize: '14px' }}>{(value * 100).toFixed(0)}%</span>
    </div>
);
