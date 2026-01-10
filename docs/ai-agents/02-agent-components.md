# 2. Agent Components

This chapter details the core components that make up an AI agent.

---

## Component Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         AI AGENT                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────────┐ │
│  │PERCEPTION│→ │REASONING │→ │ DECISION │→ │   ACTION    │ │
│  └──────────┘  └────┬─────┘  └──────────┘  └─────────────┘ │
│                     ↕                                       │
│               ┌──────────┐                                  │
│               │  MEMORY  │                                  │
│               └──────────┘                                  │
│                     ↕                                       │
│               ┌──────────┐                                  │
│               │ LEARNING │                                  │
│               └──────────┘                                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 1. Perception

Perception transforms raw input into internal representations the agent can reason about.

### Input Types
- **Text**: Natural language instructions, documents
- **Structured Data**: JSON, databases, APIs
- **Sensors**: Images, audio, IoT data
- **Events**: Webhooks, message queues

### Example: Text Perception

```python
class PerceptionModule:
    def __init__(self, embedder):
        self.embedder = embedder
    
    def perceive(self, raw_input: str) -> dict:
        """Convert raw text to structured perception."""
        return {
            "raw": raw_input,
            "embedding": self.embedder.encode(raw_input),
            "entities": self.extract_entities(raw_input),
            "intent": self.classify_intent(raw_input),
            "timestamp": datetime.utcnow()
        }
```

---

## 2. Reasoning

The reasoning engine processes perceptions to understand the current situation and determine appropriate responses.

### Reasoning Approaches

| Approach | Description | Use Case |
|----------|-------------|----------|
| **Rule-Based** | If-then logic | Simple, explainable decisions |
| **Symbolic** | Logic programming (Prolog) | Formal verification |
| **Statistical** | ML models | Pattern recognition |
| **Neural** | LLMs, transformers | Complex language understanding |

### LLM-Based Reasoning Example

```python
class ReasoningEngine:
    def __init__(self, llm_client):
        self.llm = llm_client
    
    def reason(self, perception: dict, context: str) -> str:
        prompt = f"""
        Current Situation: {perception}
        Context: {context}
        
        Analyze this situation and explain:
        1. What is happening?
        2. What are the key factors?
        3. What should be done next?
        """
        return self.llm.generate(prompt)
```

---

## 3. Decision-Making

Converts reasoning into action selection.

### Decision Strategies

```
┌─────────────────────────────────────────────────────────┐
│               DECISION-MAKING STRATEGIES                │
├─────────────────────────────────────────────────────────┤
│  Greedy       → Pick best immediate action              │
│  Look-ahead   → Consider future consequences            │
│  Utility      → Maximize expected value                 │
│  Probabilistic→ Sample from action distribution         │
│  Consensus    → Combine multiple decision sources       │
└─────────────────────────────────────────────────────────┘
```

### Example: Action Selection

```python
class DecisionMaker:
    def __init__(self, tools: list):
        self.available_tools = tools
    
    def select_action(self, reasoning_output: str) -> dict:
        """Select the best action based on reasoning."""
        
        # Parse the reasoning to identify required action
        if "search" in reasoning_output.lower():
            return {"tool": "search", "priority": "high"}
        elif "calculate" in reasoning_output.lower():
            return {"tool": "calculator", "priority": "medium"}
        else:
            return {"tool": "respond", "priority": "low"}
```

---

## 4. Action Execution

Carries out the selected action in the environment.

### Action Types
- **Tool Invocation**: Calling APIs, databases, external services
- **Communication**: Sending messages, emails, notifications
- **Data Modification**: Writing files, updating records
- **Physical**: Controlling robots, IoT devices

### Tool Execution Pattern

```python
class ActionExecutor:
    def __init__(self, tool_registry: dict):
        self.tools = tool_registry
    
    def execute(self, action: dict) -> dict:
        tool_name = action["tool"]
        params = action.get("params", {})
        
        if tool_name not in self.tools:
            return {"error": f"Unknown tool: {tool_name}"}
        
        try:
            result = self.tools[tool_name](**params)
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}
```

---

## 5. Memory

Memory allows agents to maintain context and learn from past experiences.

### Memory Types

| Type | Duration | Purpose | Example |
|------|----------|---------|---------|
| **Working Memory** | Current session | Active context | Conversation history |
| **Short-term** | Minutes to hours | Recent interactions | Last 10 messages |
| **Long-term** | Persistent | Knowledge base | User preferences |
| **Episodic** | Persistent | Specific experiences | Past problem solutions |

### Memory Implementation

```python
class AgentMemory:
    def __init__(self, vector_store):
        self.working_memory = []  # Current context
        self.vector_store = vector_store  # Long-term
    
    def add_to_working(self, item: dict):
        self.working_memory.append(item)
        if len(self.working_memory) > 20:
            self.consolidate()
    
    def consolidate(self):
        """Move old items to long-term storage."""
        old_items = self.working_memory[:-10]
        for item in old_items:
            self.vector_store.add(item)
        self.working_memory = self.working_memory[-10:]
    
    def recall(self, query: str, k: int = 5) -> list:
        """Retrieve relevant memories."""
        return self.vector_store.similarity_search(query, k=k)
```

---

## 6. Learning

Enables agents to improve over time.

### Learning Mechanisms

```
┌────────────────────────────────────────────────────────┐
│                  LEARNING APPROACHES                    │
├────────────────────────────────────────────────────────┤
│  Supervised    → Learn from labeled examples           │
│  Reinforcement → Learn from rewards/penalties          │
│  Self-supervised→ Learn from data structure            │
│  In-context    → LLM learns from prompt examples       │
│  Fine-tuning   → Adjust model weights                  │
└────────────────────────────────────────────────────────┘
```

### Feedback-Based Improvement

```python
class LearningModule:
    def __init__(self):
        self.feedback_log = []
    
    def record_feedback(self, action: dict, outcome: str, score: float):
        self.feedback_log.append({
            "action": action,
            "outcome": outcome,
            "score": score,
            "timestamp": datetime.utcnow()
        })
    
    def get_improvement_suggestions(self) -> list:
        """Analyze patterns in low-scoring actions."""
        poor_outcomes = [f for f in self.feedback_log if f["score"] < 0.5]
        # Identify common patterns in failures
        return self.analyze_patterns(poor_outcomes)
```

---

## Component Integration

### Complete Agent Flow

```python
class IntegratedAgent:
    def __init__(self, perception, reasoning, decision, executor, memory):
        self.perception = perception
        self.reasoning = reasoning
        self.decision = decision
        self.executor = executor
        self.memory = memory
    
    def run(self, input_data: str) -> str:
        # 1. Perceive
        percept = self.perception.perceive(input_data)
        
        # 2. Retrieve relevant memories
        context = self.memory.recall(input_data)
        
        # 3. Reason
        analysis = self.reasoning.reason(percept, context)
        
        # 4. Decide
        action = self.decision.select_action(analysis)
        
        # 5. Execute
        result = self.executor.execute(action)
        
        # 6. Store in memory
        self.memory.add_to_working({
            "input": input_data,
            "action": action,
            "result": result
        })
        
        return result
```

---

**Previous**: [← Fundamentals](./01-fundamentals.md) | **Next**: [Multi-Agent Systems →](./03-multi-agent-systems.md)
