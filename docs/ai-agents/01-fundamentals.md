# 1. AI Agent Fundamentals

## What Are AI Agents?

An **AI Agent** is an autonomous or semi-autonomous computational entity that:
- **Perceives** its environment through sensors, APIs, or data inputs
- **Reasons** about the current state using rules, models, or AI
- **Acts** upon the environment to achieve specific goals
- **Adapts** based on feedback and experience

Unlike traditional software that follows predetermined scripts, agents are **goal-oriented** and can handle uncertainty and novel situations.

---

## Core Concepts

### The Agent-Environment Loop

```
         ┌─────────────────────────────────────┐
         │            ENVIRONMENT              │
         └─────────────────────────────────────┘
                 ↑ Actions          ↓ Percepts
         ┌───────┴─────────────────┴───────────┐
         │              AGENT                   │
         │  ┌─────────┐     ┌──────────────┐   │
         │  │ Sensors │ →   │  Agent       │   │
         │  └─────────┘     │  Function    │   │
         │                  │  (Reasoning) │   │
         │  ┌──────────┐ ← └──────────────┘   │
         │  │ Actuators│                       │
         │  └──────────┘                       │
         └─────────────────────────────────────┘
```

### Key Properties

| Property | Description |
|----------|-------------|
| **Autonomy** | Operates without continuous human intervention |
| **Reactivity** | Responds to changes in the environment |
| **Pro-activeness** | Takes initiative toward goals |
| **Social Ability** | Can interact with other agents or humans |

---

## Types of AI Agents

### 1. Simple Reflex Agents
Act based on current perception only using condition-action rules (if-then).

```python
def simple_reflex_agent(percept):
    if percept == "obstacle_detected":
        return "turn_left"
    elif percept == "goal_visible":
        return "move_forward"
    return "explore"
```

**Limitations**: No memory, can't handle partial observability.

---

### 2. Model-Based Reflex Agents
Maintain internal state to track aspects of the world not currently visible.

```python
class ModelBasedAgent:
    def __init__(self):
        self.internal_state = {}
    
    def update_state(self, percept):
        # Update internal model based on perception
        self.internal_state["last_position"] = percept.get("position")
        self.internal_state["obstacles"] = percept.get("obstacles", [])
    
    def choose_action(self):
        if self.internal_state.get("obstacles"):
            return "avoid_obstacle"
        return "proceed"
```

---

### 3. Goal-Based Agents
Use goal information to decide which action to take.

```
Percept → Internal State → Goal Check → Action Selection → Action
```

- Considers future consequences
- Can plan sequences of actions
- More flexible but computationally expensive

---

### 4. Utility-Based Agents
Maximize a utility function when multiple goals exist or trade-offs are needed.

```python
def utility_based_decision(options):
    best_action = None
    best_utility = float('-inf')
    
    for action in options:
        utility = calculate_utility(action)  # Speed, cost, risk
        if utility > best_utility:
            best_utility = utility
            best_action = action
    
    return best_action
```

---

### 5. Learning Agents
Improve performance over time through experience.

```
┌────────────────────────────────────────────────────────┐
│                    LEARNING AGENT                       │
│  ┌──────────────┐      ┌──────────────────────────┐    │
│  │   Learning   │ ←    │  Critic (Feedback)       │    │
│  │   Element    │      └──────────────────────────┘    │
│  └──────┬───────┘                ↑                     │
│         ↓                        │                     │
│  ┌──────────────┐      ┌─────────┴────────┐           │
│  │ Performance  │  →   │   Environment    │           │
│  │   Element    │      └──────────────────┘           │
│  └──────────────┘                                      │
└────────────────────────────────────────────────────────┘
```

---

## Agent Architectures

### Reactive Architecture
- Direct stimulus-response mappings
- No internal state or planning
- Fast but limited
- Example: Braitenberg vehicles

### Deliberative Architecture
- Uses symbolic reasoning and planning
- Maintains world model
- Slower but capable of complex behavior
- Example: STRIPS planners

### Hybrid Architecture (Layered)
Combines reactive and deliberative components:

```
┌─────────────────────────────────────┐
│     Deliberative Layer (Planning)   │  ← Slow, strategic
├─────────────────────────────────────┤
│     Reactive Layer (Behaviors)      │  ← Fast, tactical
├─────────────────────────────────────┤
│     Sensors          Actuators      │
└─────────────────────────────────────┘
```

**Example**: A robot that plans a path (deliberative) but avoids sudden obstacles (reactive).

---

## Summary

| Agent Type | Memory | Planning | Learning | Best For |
|------------|--------|----------|----------|----------|
| Simple Reflex | ❌ | ❌ | ❌ | Simple, static environments |
| Model-Based | ✅ | ❌ | ❌ | Partially observable environments |
| Goal-Based | ✅ | ✅ | ❌ | Complex decision-making |
| Utility-Based | ✅ | ✅ | ❌ | Multi-objective optimization |
| Learning | ✅ | ✅ | ✅ | Unknown or changing environments |

---

**Next**: [Agent Components →](./02-agent-components.md)
