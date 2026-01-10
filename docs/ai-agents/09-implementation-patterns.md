# 9. Implementation Patterns

This chapter provides complete, working code examples for building AI agents.

---

## Pattern 1: Simple ReAct Agent

A minimal agent that reasons and acts using tools.

```python
import json
import re
from typing import Callable

class SimpleReActAgent:
    """A minimal ReAct agent implementation."""
    
    def __init__(self, llm_client, tools: dict, max_steps: int = 10):
        self.llm = llm_client
        self.tools = tools
        self.max_steps = max_steps
        self.history = []
    
    def run(self, query: str) -> str:
        """Execute the agent loop."""
        
        system_prompt = self._build_system_prompt()
        self.history = [{"role": "user", "content": query}]
        
        for step in range(self.max_steps):
            # Get LLM response
            response = self.llm.chat(
                system=system_prompt,
                messages=self.history
            )
            
            # Parse the response
            thought, action, action_input = self._parse_response(response)
            
            print(f"Step {step + 1}")
            print(f"  Thought: {thought}")
            print(f"  Action: {action}")
            
            # Check for final answer
            if action.upper() == "FINISH":
                return action_input
            
            # Execute tool
            if action in self.tools:
                try:
                    observation = self.tools[action](action_input)
                except Exception as e:
                    observation = f"Error: {str(e)}"
            else:
                observation = f"Unknown tool: {action}"
            
            print(f"  Observation: {observation}")
            
            # Add to history
            self.history.append({
                "role": "assistant", 
                "content": response
            })
            self.history.append({
                "role": "user", 
                "content": f"Observation: {observation}"
            })
        
        return "Max steps reached without conclusion."
    
    def _build_system_prompt(self) -> str:
        tool_descriptions = "\n".join([
            f"- {name}: {func.__doc__ or 'No description'}"
            for name, func in self.tools.items()
        ])
        
        return f"""You are a helpful AI agent that can use tools to answer questions.

Available Tools:
{tool_descriptions}
- FINISH: Use when you have the final answer

Always respond in this exact format:
Thought: [your reasoning about what to do next]
Action: [the tool name or FINISH]
Action Input: [the input for the tool or the final answer]

Remember: Only use one action per response."""
    
    def _parse_response(self, response: str) -> tuple:
        thought = re.search(r"Thought:\s*(.+?)(?=Action:|$)", response, re.DOTALL)
        action = re.search(r"Action:\s*(\w+)", response)
        action_input = re.search(r"Action Input:\s*(.+?)$", response, re.DOTALL)
        
        return (
            thought.group(1).strip() if thought else "",
            action.group(1).strip() if action else "FINISH",
            action_input.group(1).strip() if action_input else ""
        )


# Example usage
def get_claim(claim_id: str) -> dict:
    """Retrieve claim details by ID."""
    # Simulated database lookup
    claims = {
        "CLM-001": {"type": "water_damage", "amount": 5000, "status": "pending"},
        "CLM-002": {"type": "theft", "amount": 15000, "status": "under_review"}
    }
    return claims.get(claim_id, {"error": "Claim not found"})

def check_coverage(policy_id: str, claim_type: str) -> dict:
    """Check if a claim type is covered by a policy."""
    # Simulated policy check
    return {"covered": True, "limit": 10000, "deductible": 500}

# Create and run agent
tools = {
    "get_claim": get_claim,
    "check_coverage": check_coverage
}

agent = SimpleReActAgent(llm_client, tools)
result = agent.run("Is claim CLM-001 covered under policy POL-123?")
```

---

## Pattern 2: Tool-Calling Agent with Structured Output

Uses function calling for reliable tool invocation.

```python
from pydantic import BaseModel
from typing import Optional, List

class ToolCall(BaseModel):
    name: str
    arguments: dict

class AgentResponse(BaseModel):
    thought: str
    tool_call: Optional[ToolCall] = None
    final_answer: Optional[str] = None

class StructuredAgent:
    """Agent using structured outputs for reliable parsing."""
    
    def __init__(self, llm_client, tools: List[dict]):
        self.llm = llm_client
        self.tools = {t["name"]: t["function"] for t in tools}
        self.tool_schemas = [t["schema"] for t in tools]
    
    def run(self, query: str) -> str:
        context = []
        
        for _ in range(10):
            response: AgentResponse = self.llm.generate_structured(
                prompt=self._build_prompt(query, context),
                response_format=AgentResponse,
                tools=self.tool_schemas
            )
            
            if response.final_answer:
                return response.final_answer
            
            if response.tool_call:
                result = self._execute_tool(response.tool_call)
                context.append({
                    "thought": response.thought,
                    "action": response.tool_call.name,
                    "result": result
                })
        
        return "Could not complete the task."
    
    def _execute_tool(self, tool_call: ToolCall) -> str:
        func = self.tools.get(tool_call.name)
        if not func:
            return f"Unknown tool: {tool_call.name}"
        
        try:
            return json.dumps(func(**tool_call.arguments))
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _build_prompt(self, query: str, context: list) -> str:
        context_str = "\n".join([
            f"Step: {c['thought']} → {c['action']} → {c['result']}"
            for c in context
        ])
        return f"Query: {query}\n\nPrevious steps:\n{context_str}"
```

---

## Pattern 3: Multi-Agent Pipeline

Multiple specialized agents working in sequence.

```python
class AgentPipeline:
    """Pipeline of specialized agents."""
    
    def __init__(self, agents: list):
        self.agents = agents
    
    def run(self, initial_input: dict) -> dict:
        current_state = initial_input
        
        for agent in self.agents:
            print(f"Running: {agent.name}")
            
            # Execute agent
            result = agent.process(current_state)
            
            # Merge result into state
            current_state = {**current_state, **result}
            
            # Check for early termination
            if result.get("terminate"):
                break
        
        return current_state


class IntakeAgent:
    name = "Intake Agent"
    
    def process(self, state: dict) -> dict:
        claim = state["claim"]
        # Validate claim data
        is_valid = all([
            claim.get("description"),
            claim.get("amount"),
            claim.get("policy_id")
        ])
        return {
            "validated": is_valid,
            "validation_errors": [] if is_valid else ["Missing required fields"]
        }

class FraudAgent:
    name = "Fraud Agent"
    
    def process(self, state: dict) -> dict:
        if not state.get("validated"):
            return {"fraud_score": None, "terminate": True}
        
        # Run fraud detection
        fraud_score = 0.3  # Simulated
        return {
            "fraud_score": fraud_score,
            "fraud_flags": []
        }

class DecisionAgent:
    name = "Decision Agent"
    
    def process(self, state: dict) -> dict:
        if state["fraud_score"] > 0.8:
            return {"decision": "ESCALATE", "reason": "High fraud risk"}
        
        return {
            "decision": "APPROVE",
            "reason": "Valid claim with low fraud risk"
        }


# Create and run pipeline
pipeline = AgentPipeline([
    IntakeAgent(),
    FraudAgent(),
    DecisionAgent()
])

result = pipeline.run({
    "claim": {
        "id": "CLM-001",
        "description": "Water damage to kitchen",
        "amount": 5000,
        "policy_id": "POL-123"
    }
})

print(f"Decision: {result['decision']}")
```

---

## Pattern 4: Agent with Memory

Agent that remembers past interactions.

```python
class MemoryAgent:
    """Agent with short-term and long-term memory."""
    
    def __init__(self, llm, vector_store):
        self.llm = llm
        self.vector_store = vector_store
        self.short_term = []  # Current session
        self.max_short_term = 10
    
    def run(self, query: str) -> str:
        # Recall relevant long-term memories
        memories = self.vector_store.search(query, k=3)
        
        # Build context
        context = self._build_context(query, memories)
        
        # Generate response
        response = self.llm.generate(context)
        
        # Store in short-term memory
        self._add_to_short_term(query, response)
        
        return response
    
    def _build_context(self, query: str, memories: list) -> str:
        memory_context = "\n".join([
            f"- {m['content']}" for m in memories
        ])
        
        recent_context = "\n".join([
            f"User: {m['query']}\nAssistant: {m['response']}"
            for m in self.short_term[-3:]  # Last 3 exchanges
        ])
        
        return f"""Relevant past information:
{memory_context}

Recent conversation:
{recent_context}

Current query: {query}

Response:"""
    
    def _add_to_short_term(self, query: str, response: str):
        self.short_term.append({"query": query, "response": response})
        
        # Consolidate if too long
        if len(self.short_term) > self.max_short_term:
            old = self.short_term.pop(0)
            self._store_long_term(old)
    
    def _store_long_term(self, memory: dict):
        content = f"Q: {memory['query']} A: {memory['response']}"
        self.vector_store.add(content)
```

---

## Pattern 5: Human-in-the-Loop Agent

Agent that requests human approval for high-stakes actions.

```python
class HITLAgent:
    """Agent with human-in-the-loop for critical decisions."""
    
    def __init__(self, llm, tools, approval_callback):
        self.llm = llm
        self.tools = tools
        self.approval_callback = approval_callback
        self.sensitive_actions = ["approve_claim", "deny_claim", "send_payment"]
    
    def run(self, query: str) -> str:
        action, params = self.determine_action(query)
        
        if action in self.sensitive_actions:
            # Request human approval
            approved = self.approval_callback(
                action=action,
                params=params,
                reasoning=self.get_reasoning()
            )
            
            if not approved:
                return "Action cancelled by human reviewer."
        
        # Execute action
        result = self.tools[action](**params)
        return f"Action completed: {result}"
    
    def determine_action(self, query: str) -> tuple:
        response = self.llm.generate(f"""
        Query: {query}
        Available actions: {list(self.tools.keys())}
        
        Determine the appropriate action and parameters.
        Format: ACTION: <action_name>
        PARAMS: <json_params>
        """)
        
        # Parse response
        action = re.search(r"ACTION:\s*(\w+)", response).group(1)
        params = json.loads(re.search(r"PARAMS:\s*({.+})", response).group(1))
        
        return action, params


# Example approval callback
def request_approval(action: str, params: dict, reasoning: str) -> bool:
    print(f"\n{'='*50}")
    print(f"APPROVAL REQUIRED")
    print(f"Action: {action}")
    print(f"Parameters: {params}")
    print(f"Reasoning: {reasoning}")
    print(f"{'='*50}")
    
    response = input("Approve? (yes/no): ")
    return response.lower() == "yes"
```

---

**Previous**: [← Advanced Topics](./08-advanced-topics.md) | **Next**: [Best Practices →](./10-best-practices.md)
