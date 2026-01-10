# 10. Best Practices

This chapter covers essential best practices for building production-ready AI agents.

---

## Error Handling

### Robust Tool Execution

```python
class RobustToolExecutor:
    def __init__(self, max_retries: int = 3, timeout: int = 30):
        self.max_retries = max_retries
        self.timeout = timeout
    
    async def execute(self, tool: Callable, params: dict) -> dict:
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                result = await asyncio.wait_for(
                    tool(**params),
                    timeout=self.timeout
                )
                return {"success": True, "result": result}
            
            except asyncio.TimeoutError:
                last_error = "Timeout"
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
            
            except Exception as e:
                last_error = str(e)
                if self._is_retryable(e):
                    await asyncio.sleep(2 ** attempt)
                else:
                    break
        
        return {
            "success": False,
            "error": last_error,
            "attempts": attempt + 1
        }
    
    def _is_retryable(self, error: Exception) -> bool:
        retryable = (ConnectionError, TimeoutError)
        return isinstance(error, retryable)
```

### Graceful Degradation

```python
class DegradableAgent:
    def __init__(self, primary_llm, fallback_llm, tools):
        self.primary = primary_llm
        self.fallback = fallback_llm
        self.tools = tools
    
    async def run(self, query: str) -> str:
        try:
            return await self._run_with_llm(self.primary, query)
        except Exception as e:
            logger.warning(f"Primary LLM failed: {e}, using fallback")
            
            try:
                return await self._run_with_llm(self.fallback, query)
            except Exception as e:
                logger.error(f"Fallback LLM also failed: {e}")
                return self._rule_based_fallback(query)
    
    def _rule_based_fallback(self, query: str) -> str:
        """Last resort: simple rule-based response."""
        return "I'm having trouble processing your request. Please try again later or contact support."
```

---

## Monitoring and Observability

### Agent Metrics

```python
from prometheus_client import Counter, Histogram, Gauge
import time

# Define metrics
agent_requests = Counter(
    'agent_requests_total', 
    'Total agent requests',
    ['agent_name', 'status']
)

agent_latency = Histogram(
    'agent_latency_seconds', 
    'Agent response latency',
    ['agent_name']
)

agent_steps = Histogram(
    'agent_steps', 
    'Number of steps per agent run',
    ['agent_name']
)

tool_usage = Counter(
    'agent_tool_usage_total', 
    'Tool invocations',
    ['agent_name', 'tool_name', 'status']
)

class MonitoredAgent:
    def __init__(self, agent, name: str):
        self.agent = agent
        self.name = name
    
    async def run(self, query: str) -> str:
        start_time = time.time()
        
        try:
            result = await self.agent.run(query)
            agent_requests.labels(self.name, "success").inc()
            return result
        
        except Exception as e:
            agent_requests.labels(self.name, "error").inc()
            raise
        
        finally:
            duration = time.time() - start_time
            agent_latency.labels(self.name).observe(duration)
```

### Structured Logging

```python
import structlog

logger = structlog.get_logger()

class LoggedAgent:
    def __init__(self, agent):
        self.agent = agent
    
    async def run(self, query: str, request_id: str) -> str:
        log = logger.bind(request_id=request_id, query=query)
        
        log.info("agent_started")
        
        try:
            result = await self.agent.run(query)
            
            log.info("agent_completed", 
                     steps=self.agent.step_count,
                     tools_used=self.agent.tools_used)
            
            return result
        
        except Exception as e:
            log.error("agent_failed", error=str(e))
            raise
```

---

## Human-in-the-Loop (HITL)

### When to Escalate

| Condition | Action |
|-----------|--------|
| Confidence < 0.7 | Request review |
| High-value decision | Require approval |
| Sensitive data | Require approval |
| Unusual pattern | Flag for review |
| Tool failure | Escalate if critical |

### HITL Implementation

```python
class HITLController:
    def __init__(self, notification_service, review_queue):
        self.notifier = notification_service
        self.queue = review_queue
    
    async def check_escalation(self, 
                                action: dict, 
                                context: dict) -> dict:
        rules = [
            self._check_confidence(context),
            self._check_value_threshold(action),
            self._check_sensitivity(action),
        ]
        
        for rule in rules:
            if rule["escalate"]:
                return await self._escalate(action, context, rule["reason"])
        
        return {"proceed": True}
    
    async def _escalate(self, action: dict, context: dict, reason: str):
        # Create review request
        review_item = {
            "action": action,
            "context": context,
            "reason": reason,
            "created_at": datetime.utcnow()
        }
        
        # Add to queue and notify
        await self.queue.add(review_item)
        await self.notifier.send_alert(
            f"Agent action requires review: {reason}"
        )
        
        return {"proceed": False, "awaiting_review": True}
```

---

## Safety Considerations

### Input Validation

```python
class SafeAgent:
    def __init__(self, agent, guardrails):
        self.agent = agent
        self.guardrails = guardrails
    
    async def run(self, query: str) -> str:
        # Pre-processing guardrails
        sanitized = self.guardrails.sanitize_input(query)
        
        if self.guardrails.is_harmful(sanitized):
            return "I cannot process this request."
        
        # Run agent
        response = await self.agent.run(sanitized)
        
        # Post-processing guardrails
        if self.guardrails.is_harmful_output(response):
            return "I cannot provide this response."
        
        return response

class Guardrails:
    def __init__(self):
        self.harmful_patterns = [...]
        self.pii_patterns = [...]
    
    def sanitize_input(self, text: str) -> str:
        # Remove potential prompt injections
        text = re.sub(r"ignore previous instructions", "", text, flags=re.I)
        return text
    
    def is_harmful(self, text: str) -> bool:
        return any(p.search(text) for p in self.harmful_patterns)
```

### Rate Limiting

```python
from functools import wraps
import time

class RateLimiter:
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window = window_seconds
        self.requests = {}
    
    def check(self, user_id: str) -> bool:
        now = time.time()
        
        # Clean old entries
        self.requests = {
            k: v for k, v in self.requests.items()
            if now - v[-1] < self.window
        }
        
        # Check limit
        user_requests = self.requests.get(user_id, [])
        user_requests = [t for t in user_requests if now - t < self.window]
        
        if len(user_requests) >= self.max_requests:
            return False
        
        user_requests.append(now)
        self.requests[user_id] = user_requests
        return True
```

---

## Production Deployment

### Deployment Checklist

- [ ] **Monitoring**: Metrics, logs, and alerts configured
- [ ] **Rate Limiting**: Protect against abuse
- [ ] **Timeouts**: All external calls have timeouts
- [ ] **Fallbacks**: Graceful degradation implemented
- [ ] **HITL**: Escalation paths defined
- [ ] **Security**: Input validation and output filtering
- [ ] **Cost Controls**: Token/API call limits
- [ ] **Testing**: Benchmark suite, regression tests

### Configuration Management

```python
from pydantic_settings import BaseSettings

class AgentConfig(BaseSettings):
    # LLM Settings
    llm_model: str = "gpt-4"
    llm_temperature: float = 0.0
    max_tokens: int = 4096
    
    # Agent Behavior
    max_steps: int = 10
    confidence_threshold: float = 0.7
    enable_hitl: bool = True
    
    # Safety
    rate_limit_requests: int = 100
    rate_limit_window: int = 3600
    
    # Observability
    log_level: str = "INFO"
    enable_tracing: bool = True
    
    class Config:
        env_prefix = "AGENT_"
```

### Health Checks

```python
from fastapi import FastAPI, Response

app = FastAPI()

@app.get("/health")
async def health_check():
    checks = {
        "llm": await check_llm_connection(),
        "database": await check_database_connection(),
        "vector_store": await check_vector_store(),
    }
    
    all_healthy = all(checks.values())
    
    return Response(
        content=json.dumps({"status": "healthy" if all_healthy else "unhealthy", "checks": checks}),
        status_code=200 if all_healthy else 503,
        media_type="application/json"
    )
```

---

## Summary

Building production-ready AI agents requires attention to:

1. **Reliability**: Robust error handling and fallbacks
2. **Observability**: Comprehensive monitoring and logging
3. **Safety**: Input validation, output filtering, guardrails
4. **Human Oversight**: HITL for critical decisions
5. **Operations**: Health checks, rate limiting, configuration management

---

**Previous**: [← Implementation Patterns](./09-implementation-patterns.md) | **Back to**: [Index →](./README.md)
