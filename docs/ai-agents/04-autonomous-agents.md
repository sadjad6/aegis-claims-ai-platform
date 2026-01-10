# 4. Autonomous Agents

Autonomous agents operate independently with minimal human intervention, pursuing goals over extended periods.

---

## Goal-Oriented Behavior

Autonomous agents are defined by their ability to pursue goals rather than execute fixed scripts.

### Goal Hierarchy

```
┌─────────────────────────────────────────┐
│           STRATEGIC GOALS               │
│    (Long-term: "Maximize customer       │
│     satisfaction")                      │
├─────────────────────────────────────────┤
│           TACTICAL GOALS                │
│    (Medium-term: "Resolve all claims    │
│     within 24 hours")                   │
├─────────────────────────────────────────┤
│          OPERATIONAL GOALS              │
│    (Short-term: "Process claim #123")   │
└─────────────────────────────────────────┘
```

### Goal Representation

```python
class Goal:
    def __init__(self, description: str, priority: int, 
                 success_criteria: callable):
        self.description = description
        self.priority = priority
        self.success_criteria = success_criteria
        self.status = "pending"
        self.subgoals = []
    
    def is_achieved(self, state: dict) -> bool:
        return self.success_criteria(state)
    
    def decompose(self) -> list:
        """Break into subgoals."""
        return self.subgoals
```

---

## Autonomy Levels

| Level | Description | Human Role | Example |
|-------|-------------|------------|---------|
| **0** | No autonomy | Full control | Manual data entry |
| **1** | Suggestion | Approves all | "Recommend this action" |
| **2** | Supervised | Reviews output | Agent processes, human verifies |
| **3** | Exceptions only | Handles edge cases | Agent decides routine, escalates complex |
| **4** | Full autonomy | Oversight only | Agent handles everything |

### Autonomy Configuration

```python
class AutonomyController:
    def __init__(self, level: int):
        self.level = level
        self.escalation_rules = []
    
    def should_proceed(self, action: dict, confidence: float) -> dict:
        if self.level == 4:  # Full autonomy
            return {"proceed": True}
        
        if self.level == 3:  # Exceptions only
            if confidence > 0.9 and not self.is_high_risk(action):
                return {"proceed": True}
            return {"proceed": False, "reason": "escalate_to_human"}
        
        if self.level <= 2:  # Supervised
            return {"proceed": False, "reason": "requires_approval"}
```

---

## Planning Algorithms

### Classical Planning (STRIPS-style)

```
Initial State: at(home), has(keys), ¬at(office)
Goal State: at(office)

Actions:
- drive(from, to): 
    Preconditions: at(from), has(keys)
    Effects: ¬at(from), at(to)

Plan: drive(home, office)
```

### Hierarchical Task Networks (HTN)

Decompose high-level tasks into primitive actions.

```
Task: ProcessClaim(claim_id)
  ├── ValidateDocuments(claim_id)
  │     ├── CheckCompleteness()
  │     └── VerifySignatures()
  ├── AssessRisk(claim_id)
  │     ├── RunFraudModel()
  │     └── CheckHistory()
  └── MakeDecision(claim_id)
        ├── ApplyRules()
        └── GenerateExplanation()
```

```python
class HTNPlanner:
    def __init__(self):
        self.methods = {}  # task -> decompositions
    
    def plan(self, task: str, state: dict) -> list:
        if self.is_primitive(task):
            return [task]
        
        for method in self.methods.get(task, []):
            if method.is_applicable(state):
                subtasks = method.decompose(task)
                plan = []
                for subtask in subtasks:
                    plan.extend(self.plan(subtask, state))
                return plan
        
        return []  # No plan found
```

---

### Reactive Planning

Plans in real-time, reacting to environment changes.

```python
class ReactivePlanner:
    def __init__(self):
        self.rules = []
    
    def add_rule(self, condition: callable, action: str, priority: int):
        self.rules.append({
            "condition": condition,
            "action": action,
            "priority": priority
        })
    
    def next_action(self, state: dict) -> str:
        applicable = [r for r in self.rules if r["condition"](state)]
        if not applicable:
            return "idle"
        
        # Select highest priority applicable rule
        best = max(applicable, key=lambda r: r["priority"])
        return best["action"]
```

---

## Execution Monitoring

Autonomous agents must monitor plan execution and handle failures.

```python
class ExecutionMonitor:
    def __init__(self, planner):
        self.planner = planner
        self.current_plan = []
        self.execution_log = []
    
    def execute_plan(self, goal: Goal, initial_state: dict):
        state = initial_state
        self.current_plan = self.planner.plan(goal, state)
        
        for action in self.current_plan:
            # Execute action
            result = self.execute_action(action, state)
            
            # Check for failure
            if not result["success"]:
                # Replan from current state
                remaining_plan = self.planner.plan(goal, state)
                if not remaining_plan:
                    return {"status": "failed", "reason": "no valid plan"}
                self.current_plan = remaining_plan
                continue
            
            # Update state
            state = result["new_state"]
            
            # Check goal achievement
            if goal.is_achieved(state):
                return {"status": "success", "state": state}
        
        return {"status": "completed", "state": state}
```

---

## Self-Reflection

Advanced autonomous agents can reflect on their own performance.

```python
class ReflectiveAgent:
    def __init__(self, base_agent):
        self.agent = base_agent
        self.performance_history = []
    
    def run_with_reflection(self, task: dict) -> dict:
        # Execute task
        result = self.agent.run(task)
        
        # Reflect on performance
        reflection = self.reflect(task, result)
        self.performance_history.append(reflection)
        
        # Adapt if needed
        if reflection["score"] < 0.7:
            self.adapt(reflection["issues"])
        
        return result
    
    def reflect(self, task: dict, result: dict) -> dict:
        """Analyze what went well and what didn't."""
        return {
            "task": task["id"],
            "score": self.evaluate_result(result),
            "issues": self.identify_issues(result),
            "improvements": self.suggest_improvements(result)
        }
```

---

**Previous**: [← Multi-Agent Systems](./03-multi-agent-systems.md) | **Next**: [LLM-Based Agents →](./05-llm-based-agents.md)
