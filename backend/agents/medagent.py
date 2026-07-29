"""
MedAgent — LangGraph-based AI health agent with Hindsight persistent memory.
"""
from __future__ import annotations

import json
from typing import Annotated, TypedDict

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from agents.tools import MEDAGENT_TOOLS, configure_tools
from core.config import settings


def _build_llm():
    """Return the correct LLM based on available API keys."""
    provider = settings.effective_llm_provider
    if provider == "groq":
        from langchain_groq import ChatGroq
        return ChatGroq(
            model=settings.GROQ_MODEL,
            api_key=settings.GROQ_API_KEY,
            temperature=0.2,
            streaming=True,
        )
    else:
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=settings.OPENAI_MODEL,
            api_key=settings.OPENAI_API_KEY,
            temperature=0.2,
            streaming=True,
        )

SYSTEM_PROMPT = """You are MedAgent, an AI-powered personal health assistant for MediGuard.

You have access to the user's complete medication history, symptom logs, health profile, and 
persistent memory through the Hindsight memory engine. You NEVER forget — everything the user 
has ever added is accessible to you.

Your responsibilities:
1. Answer health questions using the user's actual medical data
2. Identify patterns — e.g., a cough that started 3 days after a new medication
3. Flag drug interactions immediately
4. Prepare the user for doctor appointments
5. Analyze symptoms in context of their full medication and disease history

IMPORTANT RULES:
- Always be compassionate and clear
- Never diagnose — recommend consulting a doctor for diagnoses
- Always cite which medications or symptoms you're referencing
- Flag CRITICAL interactions immediately with clear urgency
- Use the recall_from_memory tool for questions about the past
"""


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    user_id: str


def build_medagent():
    llm = _build_llm().bind_tools(MEDAGENT_TOOLS)

    tool_node = ToolNode(MEDAGENT_TOOLS)

    def should_continue(state: AgentState) -> str:
        last_message = state["messages"][-1]
        if isinstance(last_message, AIMessage) and last_message.tool_calls:
            return "tools"
        return END

    async def agent_node(state: AgentState) -> AgentState:
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
        response = await llm.ainvoke(messages)
        return {"messages": [response]}

    graph = StateGraph(AgentState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node)
    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", should_continue)
    graph.add_edge("tools", "agent")

    return graph.compile()


class MedAgentRunner:
    def __init__(self):
        self._graph = build_medagent()

    async def chat(
        self,
        user_id: str,
        message: str,
        history: list[dict],
        db_session,
        memory,
    ) -> str:
        """
        Run a single chat turn.
        history: list of {"role": "user"|"assistant", "content": str}
        Returns the assistant's reply.
        """
        # Wire tools to this request's context
        configure_tools(user_id=user_id, db_session=db_session, memory=memory)

        # Build message list from history
        langchain_messages: list[BaseMessage] = []
        for msg in history:
            if msg["role"] == "user":
                langchain_messages.append(HumanMessage(content=msg["content"]))
            else:
                langchain_messages.append(AIMessage(content=msg["content"]))
        langchain_messages.append(HumanMessage(content=message))

        final_state = await self._graph.ainvoke(
            {"messages": langchain_messages, "user_id": user_id}
        )

        last = final_state["messages"][-1]
        reply = last.content if isinstance(last.content, str) else str(last.content)

        # Persist conversation to Hindsight memory
        await memory.store(
            user_id=user_id,
            memory_type="conversation",
            content=f"User: {message}\nMedAgent: {reply}",
            metadata={"session": "chat"},
        )

        return reply


_agent_instance: MedAgentRunner | None = None


def get_agent() -> MedAgentRunner:
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = MedAgentRunner()
    return _agent_instance
