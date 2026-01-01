const API_BASE = '/api/v1';

interface RequestOptions {
    method?: string;
    body?: any;
    tenantId: string;
}

async function request<T>(endpoint: string, options: RequestOptions): Promise<T> {
    const response = await fetch(`${API_BASE}${endpoint}`, {
        method: options.method || 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-Tenant-ID': options.tenantId,
        },
        body: options.body ? JSON.stringify(options.body) : undefined,
    });

    if (!response.ok) {
        throw new Error(`API Error: ${response.status}`);
    }

    return response.json();
}

export interface Claim {
    claim_id: string;
    claim_number: string;
    status: string;
    amount: { amount: number; currency: string };
    created_at: string;
}

export interface Decision {
    decision_id: string;
    claim_id: string;
    outcome: string;
    confidence: number;
    reasoning_trace: string;
    risk_level: string;
}

export const claimsService = {
    list: (tenantId: string) =>
        request<Claim[]>('/claims', { tenantId }),

    getById: (tenantId: string, claimId: string) =>
        request<Claim>(`/claims/${claimId}`, { tenantId }),

    submit: (tenantId: string, claimData: any) =>
        request<string>('/claims', { method: 'POST', body: claimData, tenantId }),

    getDecision: (tenantId: string, claimId: string) =>
        request<Decision>(`/claims/${claimId}/decision`, { tenantId }),

    override: (tenantId: string, claimId: string, newOutcome: string) =>
        request<void>(`/claims/${claimId}/override`, {
            method: 'POST',
            body: { outcome: newOutcome },
            tenantId
        }),
};

export const analyticsService = {
    getAutomationRate: (tenantId: string) =>
        request<{ rate: number }>('/analytics/automation-rate', { tenantId }),

    getModelHealth: (tenantId: string) =>
        request<{ drift: number; precision: number; latency: number }>('/analytics/model-health', { tenantId }),
};
