# AegisClaims AI - API Reference

Complete REST API documentation for the AegisClaims AI platform.

---

## Base URL

```
Development: http://localhost:8000/api/v1
Production:  https://api.aegisclaims.example.com/api/v1
```

## Authentication

All API requests require the following headers:

| Header | Required | Description |
|--------|----------|-------------|
| `X-Tenant-ID` | Yes | Tenant identifier for multi-tenancy |
| `Authorization` | Yes* | Bearer token from Cognito |

*Some endpoints may allow anonymous access in development mode.

---

## Endpoints

### Claims

#### List Claims
```http
GET /claims
```

**Headers:**
```
X-Tenant-ID: tenant-acme
Authorization: Bearer <token>
```

**Response:**
```json
[
  {
    "claim_id": "550e8400-e29b-41d4-a716-446655440000",
    "claim_number": "CLM-8239",
    "status": "DECIDED",
    "amount": {
      "amount": 2450.00,
      "currency": "USD"
    },
    "created_at": "2025-12-28T10:30:00Z"
  }
]
```

---

#### Get Claim by ID
```http
GET /claims/{claim_id}
```

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `claim_id` | string (UUID) | Unique claim identifier |

**Response:**
```json
{
  "claim_id": "550e8400-e29b-41d4-a716-446655440000",
  "claim_number": "CLM-8239",
  "tenant_id": "tenant-acme",
  "policy_id": "pol-001",
  "incident_date": "2025-12-28T10:30:00Z",
  "description": "Front fender damage from parking lot incident",
  "status": "DECIDED",
  "amount": {
    "amount": 2450.00,
    "currency": "USD"
  },
  "documents": ["s3://bucket/tenant-acme/doc1.pdf"],
  "created_at": "2025-12-28T11:00:00Z",
  "updated_at": "2025-12-28T11:05:00Z"
}
```

---

#### Submit New Claim
```http
POST /claims
```

**Request Body:**
```json
{
  "policy_number": "POL-XP-900",
  "incident_date": "2025-12-28T10:30:00Z",
  "description": "Motor accident - front fender damage",
  "amount": {
    "amount": 2450.00,
    "currency": "USD"
  },
  "metadata": {
    "location": "Main St & 5th Ave",
    "witnesses": 2
  }
}
```

**Response:**
```json
{
  "claim_id": "550e8400-e29b-41d4-a716-446655440000",
  "claim_number": "CLM-8239",
  "status": "SUBMITTED"
}
```

---

#### Get Claim Decision
```http
GET /claims/{claim_id}/decision
```

**Response:**
```json
{
  "decision_id": "dec-001",
  "claim_id": "550e8400-e29b-41d4-a716-446655440000",
  "outcome": "APPROVED",
  "confidence": 0.94,
  "reasoning_trace": "Coverage verified under comprehensive policy. Fraud score low (0.02). Damage consistent with reported incident.",
  "risk_level": "LOW",
  "decided_by": "AI_AGENT",
  "decided_at": "2025-12-28T11:05:00Z"
}
```

---

#### Override Decision (Human-in-the-Loop)
```http
POST /claims/{claim_id}/override
```

**Request Body:**
```json
{
  "outcome": "DENIED",
  "reason": "Additional investigation required - inconsistent photos"
}
```

**Response:**
```json
{
  "success": true,
  "new_outcome": "DENIED",
  "overridden_by": "user-123"
}
```

---

### Policies

#### Get Policy by Number
```http
GET /policies/{policy_number}
```

**Response:**
```json
{
  "policy_id": "pol-001",
  "policy_number": "POL-XP-900",
  "tenant_id": "tenant-acme",
  "holder_name": "John Doe",
  "coverage_details": {
    "type": "comprehensive",
    "collision": true,
    "liability": true,
    "uninsured_motorist": true
  },
  "limit": {
    "amount": 50000.00,
    "currency": "USD"
  },
  "deductible": {
    "amount": 500.00,
    "currency": "USD"
  },
  "is_active": true
}
```

---

### Analytics

#### Get Automation Rate
```http
GET /analytics/automation-rate
```

**Response:**
```json
{
  "rate": 0.924,
  "period": "30d",
  "total_claims": 1284,
  "auto_decided": 1186
}
```

---

#### Get Model Health
```http
GET /analytics/model-health
```

**Response:**
```json
{
  "fraud_model": {
    "precision": 0.982,
    "recall": 0.945,
    "drift_score": 0.02
  },
  "coverage_llm": {
    "avg_confidence": 0.89,
    "prompt_drift": 0.04,
    "avg_latency_ms": 1800
  }
}
```

---

### Documents

#### Upload Document
```http
POST /documents/upload
Content-Type: multipart/form-data
```

**Form Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `file` | file | PDF, image, or email file |
| `claim_id` | string | Associated claim ID |

**Response:**
```json
{
  "document_key": "tenant-acme/claims/CLM-8239/invoice.pdf",
  "url": "https://s3.amazonaws.com/...",
  "extracted_data": {
    "damage_type": "Collision",
    "estimated_cost": 2450.00,
    "vendor_name": "AutoFix Shop"
  }
}
```

---

## Error Responses

All errors follow this format:

```json
{
  "error": {
    "code": "CLAIM_NOT_FOUND",
    "message": "Claim with ID xyz not found",
    "details": {}
  }
}
```

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `TENANT_NOT_FOUND` | 400 | Invalid or missing tenant ID |
| `CLAIM_NOT_FOUND` | 404 | Claim does not exist |
| `POLICY_NOT_FOUND` | 404 | Policy does not exist |
| `UNAUTHORIZED` | 401 | Missing or invalid auth token |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `VALIDATION_ERROR` | 422 | Invalid request body |
| `INTERNAL_ERROR` | 500 | Server error |

---

## Rate Limits

| Tier | Requests/min | Burst |
|------|--------------|-------|
| Standard | 100 | 200 |
| Premium | 500 | 1000 |
| Enterprise | Unlimited | - |

---

## SDKs

*Coming soon: Python and TypeScript SDKs*
