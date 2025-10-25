"""
Pydantic models and data structures for the Personal Assistant application.
"""
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str
    use_ocr: bool = False
    use_web: bool = False


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str
    screen_text: str = ""
    window_info: str = ""
    web_results: str = ""


class StatusResponse(BaseModel):
    """Response model for status endpoint."""
    live_enabled: bool
    ocr_ready: bool
    frames_processed: int
    ocr_events: int
    last_error: str = ""


class TranscriptResponse(BaseModel):
    """Response model for transcript endpoint."""
    transcript: str


class LiveToggleResponse(BaseModel):
    """Response model for live toggle endpoint."""
    status: str


class AssistantConfig(BaseModel):
    """Configuration model for the assistant."""
    api_key: Optional[str] = None
    model: str = "llama3.1-8b"
    temperature: float = 0.2
    top_p: float = 0.9
    system_prompt: str = "You are a helpful personal assistant. Be concise and helpful."


class CaptureStats(BaseModel):
    """Statistics for screen capture."""
    frames: int = 0
    ocr_events: int = 0
    last_error: str = ""
    ocr_ready: bool = False


class OCRResult(BaseModel):
    """OCR result with timestamp."""
    timestamp: datetime
    text: str


class WindowInfo(BaseModel):
    """Active window information."""
    title: str
    process_name: str = ""
    pid: Optional[int] = None


class WebSearchResult(BaseModel):
    """Web search result."""
    title: str
    href: str
    body: str


class WebSearchResponse(BaseModel):
    """Web search response."""
    results: list[WebSearchResult]
    query: str
