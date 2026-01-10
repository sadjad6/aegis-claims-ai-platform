# 3. Multi-Agent Systems

Multi-Agent Systems (MAS) involve multiple agents working together (or competing) to solve complex problems that single agents cannot handle effectively.

---

## Overview

```
┌─────────────────────────────────────────────────────────────┐
│                   MULTI-AGENT SYSTEM                        │
│                                                             │
│   ┌─────────┐    ┌─────────┐    ┌─────────┐               │
│   │ Agent A │←──→│ Agent B │←──→│ Agent C │               │
│   └────┬────┘    └────┬────┘    └────┬────┘               │
│        │              │              │                     │
│        └──────────────┼──────────────┘                     │
│                       ▼                                     │
│              ┌─────────────────┐                           │
│              │ Shared Resource │                           │
│              │  (Environment)  │                           │
│              └─────────────────┘                           │
└─────────────────────────────────────────────────────────────┘
```

---

## Agent Communication

### Communication Protocols

| Protocol | Description | Example |
|----------|-------------|---------|
| **Direct Messaging** | Point-to-point | Agent A → Agent B |
| **Broadcast** | One to all | Announcement to all agents |
| **Publish-Subscribe** | Topic-based | Subscribe to "claims" topic |
| **Blackboard** | Shared memory | All agents read/write to shared state |

### Message Format Example

```python
class AgentMessage:
    def __init__(self, sender: str, receiver: str, 
                 performative: str, content: dict):
        self.sender = sender
        self.receiver = receiver
        self.performative = performative  # REQUEST, INFORM, PROPOSE, etc.
        self.content = content
        self.timestamp = datetime.utcnow()

# Example message
message = AgentMessage(
    sender="claims_intake_agent",
    receiver="fraud_detection_agent",
    performative="REQUEST",
    content={
        "action": "analyze_claim",
        "claim_id": "CLM-2024-001",
        "priority": "high"
    }
)
```

---

## Coordination Patterns

### 1. Manager-Worker Pattern

A central manager decomposes tasks and delegates to specialized workers.

```
                ┌────────────────┐
                │  Manager Agent │
                └───────┬────────┘
           ┌────────────┼────────────┐
           ▼            ▼            ▼
    ┌──────────┐ ┌──────────┐ ┌──────────┐
    │ Worker 1 │ │ Worker 2 │ │ Worker 3 │
    │(Research)│ │(Analysis)│ │(Writing) │
    └──────────┘ └──────────┘ └──────────┘
```

```python
class ManagerAgent:
    def __init__(self, workers: dict):
        self.workers = workers
    
    def delegate_task(self, task: dict) -> dict:
        subtasks = self.decompose(task)
        results = {}
        
        for subtask in subtasks:
            worker = self.select_worker(subtask)
            results[subtask["id"]] = worker.execute(subtask)
        
        return self.aggregate_results(results)
```

---

### 2. Pipeline Pattern

Agents process data in sequence, each transforming and passing to the next.

```
Input → [Agent A] → [Agent B] → [Agent C] → Output
         (Parse)    (Analyze)   (Format)
```

```python
class PipelineOrchestrator:
    def __init__(self, agents: list):
        self.pipeline = agents
    
    def run(self, initial_input: dict) -> dict:
        current = initial_input
        for agent in self.pipeline:
            current = agent.process(current)
        return current
```

---

### 3. Consensus Pattern

Multiple agents vote or debate to reach agreement.

```python
class ConsensusSystem:
    def __init__(self, agents: list, threshold: float = 0.6):
        self.agents = agents
        self.threshold = threshold
    
    def reach_consensus(self, question: dict) -> dict:
        votes = {}
        for agent in self.agents:
            vote = agent.vote(question)
            votes[agent.id] = vote
        
        # Count votes
        vote_counts = Counter(v["decision"] for v in votes.values())
        total = len(self.agents)
        
        for decision, count in vote_counts.items():
            if count / total >= self.threshold:
                return {"consensus": decision, "confidence": count/total}
        
        return {"consensus": None, "message": "No consensus reached"}
```

---

### 4. Blackboard Pattern

Agents contribute to a shared workspace when they have relevant expertise.

```
┌─────────────────────────────────────────────┐
│              BLACKBOARD                      │
│  ┌─────────────────────────────────────┐    │
│  │ problem_state: {...}                │    │
│  │ partial_solutions: [...]            │    │
│  │ current_focus: "fraud_analysis"     │    │
│  └─────────────────────────────────────┘    │
└─────────────────────────────────────────────┘
      ↑         ↑         ↑         ↑
┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
│ Expert1 │ │ Expert2 │ │ Expert3 │ │ Expert4 │
└─────────┘ └─────────┘ └─────────┘ └─────────┘
```

---

## Orchestration

### Orchestration vs. Choreography

| Aspect | Orchestration | Choreography |
|--------|---------------|--------------|
| Control | Central controller | Decentralized |
| Coupling | Tighter | Looser |
| Visibility | Single point of control | Distributed logic |
| Scalability | Can be a bottleneck | More scalable |

### Orchestrator Example

```python
class AgentOrchestrator:
    def __init__(self):
        self.agents = {}
        self.workflow = []
    
    def register_agent(self, name: str, agent):
        self.agents[name] = agent
    
    def define_workflow(self, steps: list):
        """Define execution order and conditions."""
        self.workflow = steps
    
    async def execute(self, initial_context: dict) -> dict:
        context = initial_context
        
        for step in self.workflow:
            agent = self.agents[step["agent"]]
            
            # Check preconditions
            if not self.check_conditions(step.get("conditions"), context):
                continue
            
            # Execute step
            result = await agent.run(context)
            context = {**context, **result}
            
            # Check for early termination
            if step.get("terminal") and result.get("complete"):
                break
        
        return context
```

---

## Conflict Resolution

When agents disagree or compete for resources:

1. **Priority-Based**: Higher priority agent wins
2. **Negotiation**: Agents bargain for resources
3. **Arbitration**: Third-party agent decides
4. **Voting**: Democratic decision

```python
class ConflictResolver:
    def resolve(self, conflicts: list) -> dict:
        # Sort by priority
        sorted_requests = sorted(
            conflicts, 
            key=lambda x: x["priority"], 
            reverse=True
        )
        
        # Grant to highest priority
        winner = sorted_requests[0]
        return {
            "granted_to": winner["agent_id"],
            "resource": winner["resource"]
        }
```

---

**Previous**: [← Agent Components](./02-agent-components.md) | **Next**: [Autonomous Agents →](./04-autonomous-agents.md)
