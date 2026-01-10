# 8. Advanced Topics

This chapter covers advanced concepts in AI agent development.

---

## Agent Memory Systems

### Memory Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    MEMORY ARCHITECTURE                       │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │   Working    │  │  Short-term  │  │   Long-term     │   │
│  │   Memory     │  │   Memory     │  │   Memory        │   │
│  │  (Context)   │  │  (Session)   │  │  (Persistent)   │   │
│  └──────────────┘  └──────────────┘  └─────────────────┘   │
│        ↑                 ↕                   ↕              │
│        │           ┌──────────┐       ┌──────────────┐     │
│        │           │ Buffer   │       │ Vector Store │     │
│        │           │ (FIFO)   │       │ (Semantic)   │     │
│        │           └──────────┘       └──────────────┘     │
│        │                 ↓                   ↓              │
│        └─────────── Retrieval ←────────────→              │
└─────────────────────────────────────────────────────────────┘
```

### Memory Types

| Type | Duration | Storage | Access Pattern |
|------|----------|---------|----------------|
| **Working** | Current turn | In-memory | Direct |
| **Short-term** | Session | Buffer | Sequential |
| **Long-term** | Persistent | Vector DB | Semantic search |
| **Episodic** | Persistent | Graph DB | Event-based |

### Long-Term Memory Implementation

```python
from sentence_transformers import SentenceTransformer
import chromadb

class LongTermMemory:
    def __init__(self):
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        self.db = chromadb.Client()
        self.collection = self.db.create_collection("agent_memory")
    
    def store(self, content: str, metadata: dict):
        embedding = self.embedder.encode(content).tolist()
        self.collection.add(
            embeddings=[embedding],
            documents=[content],
            metadatas=[metadata],
            ids=[f"mem_{datetime.now().timestamp()}"]
        )
    
    def recall(self, query: str, k: int = 5) -> list:
        embedding = self.embedder.encode(query).tolist()
        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=k
        )
        return results["documents"][0]
```

### Episodic Memory

Stores specific experiences with temporal and causal information.

```python
class EpisodicMemory:
    def __init__(self):
        self.episodes = []
    
    def record_episode(self, 
                       trigger: str, 
                       actions: list, 
                       outcome: str,
                       success: bool):
        self.episodes.append({
            "trigger": trigger,
            "actions": actions,
            "outcome": outcome,
            "success": success,
            "timestamp": datetime.utcnow()
        })
    
    def recall_similar(self, current_situation: str) -> list:
        """Find similar past episodes."""
        # Semantic similarity search
        similar = self.semantic_search(current_situation)
        return [e for e in similar if e["success"]]
```

---

## Retrieval-Augmented Generation (RAG)

RAG combines retrieval with generation for grounded responses.

### RAG Architecture

```
Query → Retriever → Relevant Documents → LLM → Response
              ↓
        Vector Store
        (Embeddings)
```

### RAG Implementation

```python
class RAGAgent:
    def __init__(self, llm, retriever, chunk_size: int = 500):
        self.llm = llm
        self.retriever = retriever
        self.chunk_size = chunk_size
    
    async def answer(self, question: str) -> dict:
        # Retrieve relevant context
        docs = await self.retriever.search(question, k=5)
        
        # Build prompt with context
        context = "\n\n".join([d["content"] for d in docs])
        
        prompt = f"""
        Use the following context to answer the question.
        If the answer is not in the context, say "I don't know."
        
        Context:
        {context}
        
        Question: {question}
        
        Answer:
        """
        
        response = await self.llm.generate(prompt)
        
        return {
            "answer": response,
            "sources": [d["source"] for d in docs],
            "confidence": self.calculate_confidence(response, docs)
        }
```

---

## Multi-Step Reasoning Patterns

### Chain-of-Thought (CoT)

Force step-by-step reasoning:

```python
COT_PROMPT = """
Question: {question}

Let's think through this step by step:
1. First, I need to understand what is being asked...
2. Then, I should identify the relevant information...
3. Next, I'll apply the appropriate logic...
4. Finally, I'll formulate my answer...

Step-by-step reasoning:
"""
```

### Tree-of-Thoughts (ToT)

Explore multiple reasoning paths:

```python
class TreeOfThoughts:
    def __init__(self, llm, max_branches: int = 3):
        self.llm = llm
        self.max_branches = max_branches
    
    async def solve(self, problem: str) -> dict:
        # Generate initial thoughts
        thoughts = await self.generate_thoughts(problem)
        
        # Evaluate each thought
        evaluated = []
        for thought in thoughts[:self.max_branches]:
            score = await self.evaluate_thought(thought, problem)
            evaluated.append({"thought": thought, "score": score})
        
        # Expand best thought
        best = max(evaluated, key=lambda x: x["score"])
        
        # Continue or return
        if self.is_solution(best["thought"]):
            return {"solution": best["thought"]}
        else:
            return await self.solve(best["thought"])
```

### ReAct Pattern

Interleave reasoning and acting:

```
Thought: I need to check the claim details first.
Action: get_claim("CLM-001")
Observation: {"type": "water_damage", "amount": 5000}

Thought: Now I should verify policy coverage.
Action: check_coverage("POL-123", "water_damage")
Observation: {"covered": true, "limit": 10000}

Thought: The claim is covered and within limits.
Action: RESPOND
Response: The claim is approved for $5,000...
```

---

## Agent Evaluation

### Evaluation Dimensions

| Dimension | Metrics | Measurement |
|-----------|---------|-------------|
| **Accuracy** | Correct answers / Total | Benchmark datasets |
| **Efficiency** | Steps, tokens, time | Logging |
| **Reliability** | Success rate | Production monitoring |
| **Safety** | Harmful outputs | Red teaming |

### Trajectory Evaluation

```python
class TrajectoryEvaluator:
    def __init__(self, ground_truth: list):
        self.ground_truth = ground_truth
    
    def evaluate(self, agent_trajectory: list) -> dict:
        scores = {
            "action_accuracy": self.compare_actions(agent_trajectory),
            "step_efficiency": self.measure_efficiency(agent_trajectory),
            "final_answer_correct": self.check_answer(agent_trajectory)
        }
        
        scores["overall"] = sum(scores.values()) / len(scores)
        return scores
    
    def compare_actions(self, trajectory: list) -> float:
        """Check if agent took correct actions."""
        correct = 0
        for step, gt_step in zip(trajectory, self.ground_truth):
            if step["action"] == gt_step["action"]:
                correct += 1
        return correct / len(self.ground_truth)
```

### Benchmarking

```python
BENCHMARK_TASKS = [
    {
        "query": "Is claim CLM-001 covered?",
        "expected_tools": ["get_claim", "check_policy"],
        "expected_answer_contains": ["covered", "approved"]
    },
    {
        "query": "What is the fraud risk for CLM-002?",
        "expected_tools": ["get_claim", "run_fraud_check"],
        "expected_answer_contains": ["risk", "score"]
    }
]

def run_benchmark(agent, tasks: list) -> dict:
    results = []
    for task in tasks:
        result = agent.run(task["query"])
        results.append({
            "correct_tools": all(t in result["tools_used"] 
                                for t in task["expected_tools"]),
            "answer_quality": any(kw in result["answer"].lower() 
                                  for kw in task["expected_answer_contains"])
        })
    
    return {
        "tool_accuracy": sum(r["correct_tools"] for r in results) / len(results),
        "answer_quality": sum(r["answer_quality"] for r in results) / len(results)
    }
```

---

**Previous**: [← Real-World Applications](./07-real-world-applications.md) | **Next**: [Implementation Patterns →](./09-implementation-patterns.md)
