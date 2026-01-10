# 5. LLM-Based Agents

Large Language Models (LLMs) have revolutionized AI agents by providing a powerful, general-purpose reasoning engine that can understand natural language, decompose problems, and interact with tools.

---

## How LLMs Enable Agentic Behavior

```
┌─────────────────────────────────────────────────────────────┐
│                    LLM-BASED AGENT                          │
│                                                             │
│   User Input → [LLM Brain] → Tool Selection → Execution   │
│                     ↓              ↕                       │
│                 Reasoning      Tool Results                 │
│                     ↓              ↓                       │
│                 Response ← [LLM Brain] ← Observation       │
└─────────────────────────────────────────────────────────────┘
```

### Key Capabilities

| Capability | Description |
|------------|-------------|
| **Natural Language Understanding** | Parse complex instructions |
| **Reasoning** | Break down problems step-by-step |
| **Tool Selection** | Choose appropriate tools for tasks |
| **Summarization** | Compress information across steps |
| **Generation** | Produce human-readable responses |

---

## Prompt Engineering for Agents

### System Prompt Structure

```python
AGENT_SYSTEM_PROMPT = """
You are an AI Claims Processing Agent for an insurance company.

## Your Role
- Analyze insurance claims
- Verify policy coverage
- Detect potential fraud
- Make recommendations

## Available Tools
{tool_descriptions}

## Response Format
Always structure your response as:
1. THOUGHT: Your reasoning about the current situation
2. ACTION: The tool to use (or "RESPOND" to answer the user)
3. ACTION_INPUT: The input for the tool

## Rules
- Always verify before approving claims over $10,000
- Escalate fraud suspicions immediately
- Be thorough but efficient
"""
```

### Few-Shot Examples

```python
EXAMPLES = """
## Example 1
User: Check if claim CLM-001 is covered under policy POL-123

THOUGHT: I need to first retrieve the claim details, then check the policy.
ACTION: get_claim
ACTION_INPUT: {"claim_id": "CLM-001"}

OBSERVATION: {"claim_id": "CLM-001", "type": "water_damage", "amount": 5000}

THOUGHT: Now I have the claim. Let me check the policy for water damage coverage.
ACTION: check_policy_coverage
ACTION_INPUT: {"policy_id": "POL-123", "coverage_type": "water_damage"}

OBSERVATION: {"covered": true, "limit": 10000, "deductible": 500}

THOUGHT: The claim is covered. Water damage is included with a $10,000 limit.
ACTION: RESPOND
ACTION_INPUT: Claim CLM-001 for water damage ($5,000) is covered under policy POL-123. Coverage limit is $10,000 with a $500 deductible. Net payable: $4,500.
"""
```

---

## Tool Use and Function Calling

### Defining Tools

```python
from typing import Callable

class Tool:
    def __init__(self, name: str, description: str, 
                 function: Callable, parameters: dict):
        self.name = name
        self.description = description
        self.function = function
        self.parameters = parameters
    
    def to_schema(self) -> dict:
        """Convert to OpenAI function calling format."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": self.parameters,
                "required": list(self.parameters.keys())
            }
        }

# Example tools
tools = [
    Tool(
        name="get_claim",
        description="Retrieve claim details by ID",
        function=lambda claim_id: db.get_claim(claim_id),
        parameters={"claim_id": {"type": "string", "description": "The claim ID"}}
    ),
    Tool(
        name="check_policy",
        description="Check if a claim type is covered by a policy",
        function=lambda policy_id, claim_type: db.check_coverage(policy_id, claim_type),
        parameters={
            "policy_id": {"type": "string"},
            "claim_type": {"type": "string"}
        }
    ),
    Tool(
        name="run_fraud_check",
        description="Run fraud detection on a claim",
        function=lambda claim_id: fraud_model.predict(claim_id),
        parameters={"claim_id": {"type": "string"}}
    )
]
```

### Function Calling Flow

```
User Query
    ↓
┌───────────────────────────────────┐
│ LLM decides to call function      │
│ Output: {"name": "get_claim",     │
│          "arguments": {...}}      │
└───────────────────────────────────┘
    ↓
Execute function with arguments
    ↓
┌───────────────────────────────────┐
│ Return result to LLM              │
│ "Here is the claim data: {...}"   │
└───────────────────────────────────┘
    ↓
LLM continues reasoning...
```

---

## The ReAct Pattern

**ReAct** (Reasoning + Acting) interleaves reasoning traces with actions.

### ReAct Loop

```python
class ReActAgent:
    def __init__(self, llm, tools: list, max_iterations: int = 10):
        self.llm = llm
        self.tools = {t.name: t for t in tools}
        self.max_iterations = max_iterations
    
    def run(self, query: str) -> str:
        thoughts = []
        
        for i in range(self.max_iterations):
            # Get LLM response
            prompt = self.build_prompt(query, thoughts)
            response = self.llm.generate(prompt)
            
            # Parse response
            thought, action, action_input = self.parse_response(response)
            thoughts.append({"thought": thought, "action": action})
            
            # Check for final answer
            if action == "RESPOND":
                return action_input
            
            # Execute tool
            if action in self.tools:
                observation = self.tools[action].function(**action_input)
                thoughts.append({"observation": observation})
            else:
                thoughts.append({"observation": f"Unknown tool: {action}"})
        
        return "Max iterations reached without conclusion."
```

### ReAct Trace Example

```
Question: Is claim CLM-2024-001 fraudulent?

Thought 1: I need to retrieve the claim details first.
Action: get_claim
Action Input: {"claim_id": "CLM-2024-001"}
Observation: {"amount": 25000, "type": "theft", "filed_date": "2024-01-15"}

Thought 2: This is a high-value theft claim. I should run fraud detection.
Action: run_fraud_check
Action Input: {"claim_id": "CLM-2024-001"}
Observation: {"risk_score": 0.87, "flags": ["unusual_time", "repeat_claimant"]}

Thought 3: The fraud score is 0.87 (high risk) with concerning flags.
Action: RESPOND
Answer: Claim CLM-2024-001 has a high fraud risk (87%). Flagged issues:
unusual filing time and repeat claimant history. Recommend manual review.
```

---

## Chain-of-Thought Prompting

Force the LLM to reason step-by-step before answering.

```python
COT_PROMPT = """
Analyze this insurance claim step by step:

Claim: {claim_description}
Policy: {policy_details}

Think through this carefully:
1. What type of damage is being claimed?
2. Does the policy cover this type of damage?
3. What is the coverage limit?
4. Is the claim amount within the limit?
5. Are there any exclusions that apply?
6. What is your recommendation?

Let's work through each step:
"""
```

---

## Best Practices for LLM Agents

1. **Clear Tool Descriptions**: Be precise about what each tool does
2. **Structured Output**: Request JSON or specific formats
3. **Error Handling**: Tell the agent how to handle tool failures
4. **Guardrails**: Add safety checks before executing actions
5. **Token Management**: Summarize long histories to fit context

```python
def manage_context(history: list, max_tokens: int = 4000) -> list:
    """Compress history if it exceeds token limit."""
    current_tokens = count_tokens(history)
    
    if current_tokens <= max_tokens:
        return history
    
    # Summarize older entries
    summary = summarize_entries(history[:-5])
    return [{"role": "system", "content": f"Previous context: {summary}"}] + history[-5:]
```

---

**Previous**: [← Autonomous Agents](./04-autonomous-agents.md) | **Next**: [Agent Frameworks →](./06-agent-frameworks.md)
