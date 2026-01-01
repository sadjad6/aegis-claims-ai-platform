from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time
import json
import logging

logger = logging.getLogger("audit")

class AuditLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        tenant_id = request.headers.get("X-Tenant-ID", "unknown")
        start_time = time.time()
        
        response = await call_next(request)
        
        duration = time.time() - start_time
        
        audit_log = {
            "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            "tenant_id": tenant_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration": f"{duration:.3f}s",
            "client_ip": request.client.host if request.client else "unknown"
        }
        
        # In production, send to CloudWatch or Kinesis
        logger.info(json.dumps(audit_log))
        
        return response
