import abc
from typing import List, Dict, Any, Optional
import requests
from app.models.schemas import MessageItem
from app.core.config import settings

class BaseInterviewService(abc.ABC):
    """
    Abstract contract for the AI/Conversation Engine.
    Allows Mock, n8n, LangGraph, or direct LLM services to be swapped seamlessly.
    """

    @abc.abstractmethod
    def get_initial_question(self, session_id: str, candidate_name: str, resume_text: str) -> str:
        """Returns the opening interview question tailored to the candidate."""
        pass

    @abc.abstractmethod
    def generate_response(
        self,
        session_id: str,
        candidate_name: str,
        resume_text: str,
        conversation_history: List[MessageItem],
        candidate_message: str
    ) -> str:
        """Generates the next interviewer question or reply."""
        pass


class MockInterviewService(BaseInterviewService):
    """
    Deterministic mock conversational interviewer.
    Simulates a natural technical interviewer pacing through project discovery,
    architectural deep-dive, technical challenges, tradeoffs, and conclusion.
    """

    def get_initial_question(self, session_id: str, candidate_name: str, resume_text: str) -> str:
        first_name = candidate_name.split()[0] if candidate_name else "there"
        return (
            f"Hello {first_name}! Welcome to your technical mock interview. "
            "I've reviewed your resume. Let's start with the project you consider your most significant technical achievement. "
            "Could you give me an overview of its architecture and your direct role in building it?"
        )

    def generate_response(
        self,
        session_id: str,
        candidate_name: str,
        resume_text: str,
        conversation_history: List[MessageItem],
        candidate_message: str
    ) -> str:
        # Count candidate turns to progress through interview stages
        candidate_turns = sum(1 for msg in conversation_history if msg.role == "candidate")

        cleaned_input = candidate_message.strip()

        # Dynamic mock follow-ups based on interview progression
        if candidate_turns == 1:
            return (
                "That's a solid architectural overview. What were the key bottlenecks or technical constraints "
                "you encountered while designing that system, and how did you decide on the data storage and communication protocols?"
            )
        elif candidate_turns == 2:
            return (
                "Interesting tradeoff decisions. If your system experienced a sudden 10x increase in concurrent traffic "
                "or data throughput, where would it break first, and how would you optimize or re-architect it to maintain low latency?"
            )
        elif candidate_turns == 3:
            return (
                "Great analysis. How did you handle fault tolerance, error recovery, and data consistency across services "
                "during unexpected failures or network partitions?"
            )
        elif candidate_turns == 4:
            return (
                "Looking back at the implementation, if you had the opportunity to rebuild this system from scratch today, "
                "what architectural or tooling choice would you change, and why?"
            )
        else:
            return (
                "Thank you for walking me through those details thoroughly. You've clearly articulated the architecture, "
                "tradeoffs, and engineering considerations. Do you have any specific questions for me about the system design or role?"
            )


class N8NInterviewService(BaseInterviewService):
    """
    Integration layer for connecting to an external n8n Webhook workflow.
    Ready to be activated when n8n is deployed.
    """

    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_url = webhook_url or settings.N8N_WEBHOOK_URL

    def get_initial_question(self, session_id: str, candidate_name: str, resume_text: str) -> str:
        if not self.webhook_url:
            return f"Hello {candidate_name}! Let's start by discussing your key technical experience."
        
        try:
            payload = {
                "action": "start_interview",
                "session_id": session_id,
                "candidate_name": candidate_name,
                "resume_text": resume_text
            }
            resp = requests.post(self.webhook_url, json=payload, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            return data.get("response_text", "Welcome! Let's discuss your technical background.")
        except Exception as e:
            # Fallback gracefully
            return f"Welcome {candidate_name}! Could you introduce your primary technical focus area?"

    def generate_response(
        self,
        session_id: str,
        candidate_name: str,
        resume_text: str,
        conversation_history: List[MessageItem],
        candidate_message: str
    ) -> str:
        if not self.webhook_url:
            return "n8n Webhook URL is not configured. Please set N8N_WEBHOOK_URL."

        try:
            payload = {
                "action": "next_message",
                "session_id": session_id,
                "candidate_name": candidate_name,
                "resume_text": resume_text,
                "conversation_history": [msg.model_dump() for msg in conversation_history],
                "latest_candidate_message": candidate_message
            }
            resp = requests.post(self.webhook_url, json=payload, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            return data.get("response_text", "Thank you. Could you elaborate further?")
        except Exception as e:
            return f"Error communicating with AI engine: {str(e)}"


def get_interview_service() -> BaseInterviewService:
    """Factory to instantiate the configured AI conversation engine."""
    engine = settings.INTERVIEW_ENGINE.lower()
    if engine == "n8n":
        return N8NInterviewService()
    return MockInterviewService()

interview_service = get_interview_service()
