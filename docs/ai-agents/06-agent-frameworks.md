# 6. Agent Frameworks

This chapter covers popular frameworks for building AI agents.

---

## Framework Comparison

| Framework | Focus | Best For | Language |
|-----------|-------|----------|----------|
| **LangChain** | LLM application building | General-purpose agents | Python, JS |
| **CrewAI** | Multi-agent collaboration | Team-based workflows | Python |
| **AutoGPT** | Autonomous execution | High-autonomy tasks | Python |
| **BabyAGI** | Task management | Recursive task creation | Python |
| **Microsoft AutoGen** | Multi-agent conversation | Complex dialogues | Python |
| **DSPy** | Programmatic prompting | Optimized pipelines | Python |

---

## LangChain

The most popular framework for building LLM applications.

### Key Components

```
┌────────────────────────────────────────────────────┐
│                    LangChain                        │
├────────────────────────────────────────────────────┤
│  Models  │ Prompts │ Chains │ Agents │ Memory     │
├──────────┼─────────┼────────┼────────┼────────────┤
│  LLMs,   │Templates│ LCEL   │ ReAct, │ Buffer,    │
│  Chat,   │ Prompt  │ Pipes  │ Tools  │ Summary,   │
│  Embed   │ Compose │        │        │ Vector     │
└────────────────────────────────────────────────────┘
```

### LangChain Agent Example

```python
from langchain.agents import create_react_agent, AgentExecutor
from langchain.tools import Tool
from langchain_openai import ChatOpenAI

# Define tools
tools = [
    Tool(
        name="get_claim",
        func=lambda claim_id: get_claim_from_db(claim_id),
        description="Get claim details by ID"
    ),
    Tool(
        name="check_fraud",
        func=lambda claim_id: run_fraud_detection(claim_id),
        description="Check if a claim is potentially fraudulent"
    )
]

# Create agent
llm = ChatOpenAI(model="gpt-4")
agent = create_react_agent(llm, tools, prompt_template)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# Run
result = executor.invoke({"input": "Analyze claim CLM-001"})
```

---

## CrewAI

Designed for multi-agent collaboration with role-based agents.

### Core Concepts

- **Agent**: Individual with a role, goal, and backstory
- **Task**: Specific work item assigned to an agent
- **Crew**: Team of agents working together
- **Process**: Sequential or hierarchical execution

### CrewAI Example

```python
from crewai import Agent, Task, Crew

# Define agents
intake_agent = Agent(
    role="Claims Intake Specialist",
    goal="Validate and categorize incoming claims",
    backstory="Expert at reviewing claim documents",
    tools=[document_parser, validation_tool]
)

fraud_agent = Agent(
    role="Fraud Analyst",
    goal="Detect potentially fraudulent claims",
    backstory="Experienced in identifying fraud patterns",
    tools=[fraud_detection_tool, history_checker]
)

# Define tasks
intake_task = Task(
    description="Review claim {claim_id} and validate documents",
    agent=intake_agent
)

fraud_task = Task(
    description="Analyze claim for fraud indicators",
    agent=fraud_agent
)

# Create crew
crew = Crew(
    agents=[intake_agent, fraud_agent],
    tasks=[intake_task, fraud_task],
    process="sequential"
)

# Execute
result = crew.kickoff(inputs={"claim_id": "CLM-001"})
```

---

## AutoGPT

Fully autonomous agent that pursues goals with minimal intervention.

### Architecture

```
Goal → Task List → Execute → Evaluate → Repeat
         ↑                      │
         └──────────────────────┘
              (Self-generated tasks)
```

### Key Features

- **Self-prompting**: Generates its own prompts
- **Long-term memory**: Stores information across sessions
- **Internet access**: Can browse and research
- **Code execution**: Can write and run code

---

## BabyAGI

Simple task-driven AI agent focused on recursive task management.

### Core Loop

```python
def baby_agi_loop(objective: str, initial_task: str):
    task_list = [initial_task]
    completed = []
    
    while task_list:
        # Get next task
        current = task_list.pop(0)
        
        # Execute task
        result = execute_task(objective, current, completed)
        completed.append({"task": current, "result": result})
        
        # Generate new tasks
        new_tasks = create_tasks(objective, result, task_list)
        task_list.extend(new_tasks)
        
        # Prioritize
        task_list = prioritize_tasks(task_list, objective)
```

---

## Microsoft AutoGen

Framework for building multi-agent conversational systems.

### Conversation Patterns

```
┌──────────────┐     ┌──────────────┐
│  User Proxy  │ ←→  │  Assistant   │
└──────────────┘     └──────────────┘
                           ↕
                    ┌──────────────┐
                    │    Critic    │
                    └──────────────┘
```

### AutoGen Example

```python
from autogen import AssistantAgent, UserProxyAgent

# Create agents
assistant = AssistantAgent(
    name="claims_assistant",
    llm_config={"model": "gpt-4"},
    system_message="You are a claims processing expert."
)

user_proxy = UserProxyAgent(
    name="user",
    human_input_mode="TERMINATE",
    code_execution_config={"work_dir": "workspace"}
)

# Start conversation
user_proxy.initiate_chat(
    assistant,
    message="Analyze the claim in file claim_data.json"
)
```

---

## Choosing a Framework

| Use Case | Recommended Framework |
|----------|----------------------|
| Simple single agent | LangChain |
| Multi-agent with roles | CrewAI |
| Highly autonomous tasks | AutoGPT |
| Task decomposition | BabyAGI |
| Complex conversations | AutoGen |
| Production optimization | DSPy |

---

**Previous**: [← LLM-Based Agents](./05-llm-based-agents.md) | **Next**: [Real-World Applications →](./07-real-world-applications.md)
