from typing import List, Literal, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class MessageItem(BaseModel):
    role: Literal["interviewer", "candidate", "system"]
    content: str
    timestamp: float = Field(default_factory=lambda: datetime.now().timestamp())

class ResumeUploadResponse(BaseModel):
    session_id: str
    candidate_name: str
    resume_uploaded: bool
    initial_message: str
    target_duration_seconds: int = 300

class InterviewMessageRequest(BaseModel):
    session_id: str
    message: str

class InterviewMessageResponse(BaseModel):
    session_id: str
    response_text: str
    message_type: str = "interviewer"
    should_speak: bool = True
    time_remaining_seconds: int
    is_finished: bool = False

class InterviewSessionState(BaseModel):
    session_id: str
    candidate_name: str
    start_time: Optional[float] = None
    target_duration_seconds: int = 300
    elapsed_seconds: int = 0
    time_remaining_seconds: int = 300
    is_paused: bool = False
    is_finished: bool = False
    conversation_history: List[MessageItem] = []

class AudioTranscribeResponse(BaseModel):
    text: str
    confidence: float = 1.0
