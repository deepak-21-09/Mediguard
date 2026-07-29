# Why I Built a Medication Safety Platform Around Persistent Agent Memory

The thing that finally pushed me to build MediGuard wasn't a statistic — it was watching someone I know get discharged from hospital with three new prescriptions, no one having checked whether they interacted with the six they were already taking. The information was all there, scattered across a pharmacy system, a patient portal, and a notes app on their phone. The problem wasn't data. It was that nothing was reasoning over the whole picture at once, persistently, on their behalf.

That's the core premise of MediGuard: a FastAPI + Next.js platform where an AI agent called MedAgent has access to a patient's complete medication history, symptom logs, and health profile — and crucially, remembers everything across every session, not just the current conversation window.

## What the System Does

MediGuard is a health management platform with a Python/FastAPI backend, a Next.js frontend, and Supabase PostgreSQL as the primary store. The features cover what you'd expect: medication tracking, drug interaction detection, symptom logging, appointment preparation, reminder scheduling, and a one-tap emergency card showing current meds, allergies, and emergency contacts.

What makes the architecture interesting is the layer that sits on top of all of this: MedAgent, a LangGraph-based AI agent that has five tools wired to live database queries, plus a persistent memory engine backed by [Hindsight](https://github.com/vectorize-io/hindsight). The agent isn't a stateless Q&A bot. It accumulates context — every medication started, every symptom logged, every interaction flagged — and makes that context retrievable across separate sessions and requests.

The stack in full:

- **Backend**: FastAPI, SQLAlchemy (async), asyncpg, Supabase PostgreSQL
- **AI layer**: LangGraph, LangChain, Groq (`llama-3.1-8b-instant`) or OpenAI
- **Memory**: [Hindsight memory engine](https://hindsight.vectorize.io/) with Qdrant for vector-backed recall, in-process keyword fallback for dev
- **Frontend**: Next.js 14, Tailwind, Radix UI, TanStack Query
- **Auth**: Clerk (production), local JWT fallback (dev/test)

## The Core Technical Story: Memory as Infrastructure

Most AI integrations in production apps today are stateless by design. You send a message, you get a reply, the LLM forgets everything. Session history helps at the conversation level, but as soon as the user closes a tab and comes back three weeks later asking "why do I feel nauseous after breakfast?", you're starting from zero again.

The design question I kept coming back to was: what does it mean for an AI health assistant to *actually* know a patient? Not for the duration of a chat session, but permanently. The answer is that memory has to be first-class infrastructure, not an afterthought bolted onto the chat route.

[Agent memory](https://vectorize.io/what-is-agent-memory) is the mechanism that makes this work. Every significant health event — a new medication, a logged symptom, a flagged drug interaction, a completed conversation turn — gets written to Hindsight as a typed memory object. When MedAgent needs to answer a question, it can recall relevant memories by semantic similarity, not just keyword match, which means "why do I feel tired in the afternoons?" can surface a memory written two months ago that noted Lisinopril fatigue as a moderate side effect.

Here's the memory write path in `medication_service.py`, called every time a medication is added:

```python
await memory.store(
    user_id=user_id,
    memory_type="medication",
    content=(
        f"Started medication: {med.name} {med.dosage} {med.frequency}. "
        f"Purpose: {med.purpose or 'not specified'}. "
        f"Doctor: {med.prescribing_doctor or 'not specified'}."
    ),
    metadata={
        "medication_id": med.id,
        "status": med.status,
        "start_date": str(med.start_date) if med.start_date else None,
    },
)
```

It's deliberately written as a natural language sentence rather than raw JSON. The reason is that when Qdrant is backing the store, this content gets embedded. An embedding of `"Started medication: Metformin 500mg twice daily. Purpose: Type 2 Diabetes management"` will surface correctly when the query is `"diabetes medication history"` or `"anything that could cause lactic acidosis"` — neither of which contains the word "Metformin". Encoding the meaning rather than just the keys is what makes the recall useful.

Critical drug interactions get a second memory write, tagged as `memory_type="event"` with explicit urgency framing:

```python
if severity in (InteractionSeverity.HIGH, InteractionSeverity.CRITICAL):
    await memory.store(
        user_id=user_id,
        memory_type="event",
        content=(
            f"INTERACTION ALERT: {new_med.name} has a {severity} interaction "
            f"with {item.get('medication_b', 'unknown')}. "
            f"{item.get('description', '')}"
        ),
        metadata={"severity": severity, "type": "drug_interaction"},
    )
```

This means a future conversation — weeks or months later — can surface "there was a critical interaction alert involving Warfarin" without the user or the agent having to remember which session that was raised in.

## The Agent Graph

MedAgent is a LangGraph `StateGraph` with two nodes: an `agent` node and a `tools` node, connected by a conditional edge. The logic is simple: if the LLM's last message contains tool calls, route to the tool executor; otherwise, end.

```python
def should_continue(state: AgentState) -> str:
    last_message = state["messages"][-1]
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "tools"
    return END
```

The agent has five tools available, each backed by live async SQLAlchemy queries against the user's actual data: `get_medication_history`, `get_symptom_history`, `get_user_profile`, `recall_from_memory`, and `check_drug_interaction`. The last one is interesting because it itself calls the LLM — it pulls the current active medication list from Postgres, then sends a clinical pharmacist prompt to Groq asking for a structured interaction analysis in JSON. So a single user message can trigger: agent → tool call → DB query + LLM sub-call → tool result → agent final response. The whole thing is async end-to-end.

The tool context injection is worth noting. Because LangGraph tool nodes don't carry per-request session context natively, the design uses a module-level `configure_tools()` call at the start of each request to bind the current user ID, SQLAlchemy session, and memory instance:

```python
def configure_tools(user_id: str, db_session, memory):
    global _user_id, _db_session, _memory
    _user_id = user_id
    _db_session = db_session
    _memory = memory
```

This is a concession to simplicity. In a single-threaded async context it works correctly because FastAPI processes requests on the same event loop and the globals are overwritten before each agent invocation. At higher concurrency or with threading, you'd want to move context into the graph state itself or use contextvars. It's the kind of thing that's fine until it suddenly isn't.

## The Dual-Store Memory Design

The [Hindsight](https://github.com/vectorize-io/hindsight) integration uses a dual-class pattern with a clean protocol boundary. `QdrantMemory` is the production path: it embeds content using `text-embedding-3-small`, upserts vectors with full metadata payloads into Qdrant, and retrieves by cosine similarity with user-scoped filtering. `InMemoryFallback` is the dev/test path: it stores plain dicts in a process-local list and scores recall by counting keyword overlaps.

```python
HindsightMemory = QdrantMemory | InMemoryFallback

def get_memory():
    global _memory_instance
    if _memory_instance is None:
        if settings.QDRANT_ENABLED:
            try:
                _memory_instance = QdrantMemory()
            except Exception as e:
                _memory_instance = InMemoryFallback()
        else:
            _memory_instance = InMemoryFallback()
    return _memory_instance
```

Both classes implement the same `store` / `recall` / `recall_all_by_type` / `delete_memory` interface. The rest of the codebase — the agent, the services, the chat route — calls `get_memory()` and never needs to know which backend is active. This let me build and test the full agent pipeline end-to-end without Qdrant running locally, then drop in the vector-backed implementation for production without changing a line outside `hindsight.py`.

The memory types are also worth calling out: `medication`, `symptom`, `event`, and `conversation`. Tagging memories by type lets the agent filter recall by category when relevant. "What symptoms have I had this month?" should query `symptom` memories; "What did we discuss last time?" should search `conversation` memories. The LLM doesn't have to figure out where to look from context alone.

## What the Interaction Actually Looks Like

Here's a representative conversation exchange from the end-to-end test suite, where a patient is on Metformin and Aspirin:

**User:** "Do Metformin and Aspirin interact with each other? Check my current meds."

**MedAgent** (after invoking `check_drug_interaction`): "Based on the interaction check, there is a low-severity interaction between Metformin and Aspirin. Aspirin can increase the hypoglycemic effect of Metformin, which may cause your blood sugar to drop lower than expected. This is generally manageable — monitor your blood sugar more closely, especially after taking both medications together, and let your prescribing doctor know. It's not a reason to stop either medication without consulting them first."

The agent didn't fabricate from training data. It queried the database, confirmed the two medications are currently active for this user, and sent that specific pair to the pharmacist prompt. The structured JSON response from the LLM got parsed, the interaction record got written to `drug_interactions`, and a high-severity version of the event would also have been written to Hindsight memory for future reference.

The symptom analysis pipeline is similar. When a user logs "nausea, moderate severity, after taking Metformin this morning," the service fetches their active medications from Postgres and sends both to the LLM with a prompt asking for clinical interpretation. The response — analysis, possible causes, related medications, urgency level — is stored on the symptom row *and* written to Hindsight as a symptom memory. Three months later, when the patient asks "why do I keep getting nauseous?", the `recall_from_memory` tool will surface it.

## Lessons I'd Apply to the Next System

**Typed memory beats flat chat history.** Appending every message to a conversation array and hoping the model can find relevant context inside 20k tokens is fragile. Structuring memory by type — medication, symptom, event, conversation — and retrieving by semantic query gives the agent much faster, more accurate context. It also makes the memory auditable, which matters in healthcare.

**Write memory as sentences, not objects.** When you're embedding text for vector retrieval, `"Started medication: Metformin 500mg twice daily for Type 2 Diabetes"` retrieves on more queries than `{"name": "Metformin", "dosage": "500mg"}`. The embedding model is looking for semantic meaning; give it something that carries meaning.

**The dual-store pattern is genuinely worth the extra class.** Having `InMemoryFallback` implement the same interface as `QdrantMemory` cost maybe two hours. It bought a full development and test loop that doesn't require a vector database running. Every test in the e2e suite passes against the fallback, and the same tests run against Qdrant in production. That's a good tradeoff.

**Timezone-naive datetimes will bite you when your clients are timezone-aware.** Python's `datetime.utcnow()` returns a naive datetime. SQLAlchemy's `DateTime` column expects a naive datetime. But any modern HTTP client serializing `datetime.now(timezone.utc)` sends `2026-08-05T15:46:38+00:00`, which Pydantic parses as timezone-aware, which Postgres then refuses to store with the naive column type. The fix is a Pydantic `mode="after"` validator that strips `tzinfo` before the value reaches the ORM. It took longer to debug than it should have, because the error message — "can't subtract offset-naive and offset-aware datetimes" — appears deep in the asyncpg stack, not at the Pydantic layer.

**LLM sub-calls inside tools need their own failure budget.** The `check_drug_interaction` tool calls the LLM internally. If Groq is rate-limited or the network blips, the tool returns `{"interactions": [], "error": "..."}` and the agent continues gracefully. But the outer agent invocation also has a timeout. At higher load you want explicit retry logic with backoff inside the tool, not just a bare try/except that returns an empty result and silently swallows the error.

The full backend runs 26 end-to-end tests against live Supabase PostgreSQL — user registration, medication CRUD, interaction detection, symptom analysis with AI, appointment creation, reminder management, emergency card retrieval, and four chat tests including a multi-turn tool-call scenario — with zero failures under production settings (`DEBUG=false`, `ENVIRONMENT=production`, CORS locked to the deployment domain). The memory system, the agent graph, and the interaction detection pipeline all work together as a coherent unit rather than three separate features that happen to share a database.

The problem MediGuard is built to solve — medication errors from fragmented, stateless health information — is not going away. Persistent agent memory is one concrete, implementable part of the answer.
