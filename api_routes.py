"""
FastAPI routes and endpoints for the Personal Assistant application.
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from models import (
    ChatRequest, ChatResponse, StatusResponse, TranscriptResponse, 
    LiveToggleResponse
)
from screen_capture import ScreenCapture
from window_utils import window_manager
from web_search import web_searcher
from ai_client import ai_client
from smart_context_analyzer import smart_analyzer


class APIRouterManager:
    """API router manager for the Personal Assistant application."""
    
    def __init__(self):
        self.screen_capture = ScreenCapture()
        self.router = APIRouter()
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup all API routes."""
        
        @self.router.get("/", response_class=HTMLResponse)
        async def read_root():
            """Serve the main HTML page."""
            try:
                with open("static/index.html", "r", encoding="utf-8") as f:
                    return HTMLResponse(content=f.read())
            except FileNotFoundError:
                return HTMLResponse(content="<h1>Personal Assistant</h1><p>Static files not found</p>")
        
        @self.router.post("/chat", response_model=ChatResponse)
        async def chat_endpoint(request: ChatRequest):
            """Handle chat requests with intelligent context analysis."""
            try:
                # Get window information first
                window_info = window_manager.get_formatted_active_window()
                
                # Use smart context analysis if not explicitly overridden
                if not hasattr(request, 'force_manual_mode') or not request.force_manual_mode:
                    # Analyze query to determine optimal context sources
                    context_decision = smart_analyzer.analyze_query(
                        request.message,
                        window_info,
                        self.screen_capture.is_live_enabled()
                    )
                    
                    # Override request flags with intelligent decisions
                    use_ocr = context_decision.use_ocr
                    use_web = context_decision.use_web
                    web_params = context_decision.web_search_params or {}
                else:
                    # Use manual mode (original behavior)
                    use_ocr = request.use_ocr
                    use_web = request.use_web
                    web_params = {}
                
                # Get screen text if needed
                screen_text = ""
                if use_ocr:
                    if self.screen_capture.is_live_enabled():
                        screen_text = self.screen_capture.get_recent_ocr_text()
                    else:
                        _, screen_text = self.screen_capture.capture_single_screen()
                
                # Get web results if needed
                web_results = ""
                if use_web and web_searcher.is_available():
                    # Use adaptive search parameters
                    max_results = web_params.get('max_results', 5)
                    timelimit = web_params.get('timelimit', None)
                    
                    web_results = web_searcher.search_formatted(
                        request.message, 
                        max_results=max_results,
                        timelimit=timelimit
                    )
                
                # Create enhanced request with smart decisions
                enhanced_request = ChatRequest(
                    message=request.message,
                    use_ocr=use_ocr,
                    use_web=use_web
                )
                
                # Process chat with intelligent context
                response = ai_client.chat(enhanced_request, screen_text, window_info, web_results)
                
                # Add context decision info to response if available
                if not hasattr(request, 'force_manual_mode') or not request.force_manual_mode:
                    # Add reasoning to the response for transparency
                    if hasattr(response, 'reasoning'):
                        response.reasoning = context_decision.reasoning
                
                return response
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e)) from e
        
        @self.router.post("/live/toggle", response_model=LiveToggleResponse)
        async def toggle_live():
            """Toggle live screen capture."""
            try:
                if self.screen_capture.is_live_enabled():
                    self.screen_capture.stop_live_capture()
                    return LiveToggleResponse(status="live_off")
                else:
                    self.screen_capture.start_live_capture()
                    return LiveToggleResponse(status="live_on")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e)) from e
        
        @self.router.get("/status", response_model=StatusResponse)
        async def get_status():
            """Get system status."""
            try:
                stats = self.screen_capture.get_stats()
                return StatusResponse(
                    live_enabled=self.screen_capture.is_live_enabled(),
                    ocr_ready=stats.ocr_ready,
                    frames_processed=stats.frames,
                    ocr_events=stats.ocr_events,
                    last_error=stats.last_error
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e)) from e
        
        @self.router.get("/transcript", response_model=TranscriptResponse)
        async def get_transcript():
            """Get live transcript."""
            try:
                if self.screen_capture.is_live_enabled():
                    transcript = self.screen_capture.get_recent_ocr_text(seconds=15, max_chars=1200)
                    return TranscriptResponse(transcript=transcript)
                else:
                    return TranscriptResponse(transcript="")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e)) from e
        
        @self.router.get("/health")
        async def health_check():
            """Health check endpoint."""
            return {
                "status": "healthy",
                "ai_available": ai_client.is_available(),
                "web_search_available": web_searcher.is_available(),
                "screen_capture_available": self.screen_capture.mss is not None,
                "ocr_available": self.screen_capture.pytesseract is not None
            }
        
        @self.router.get("/config")
        async def get_config():
            """Get current configuration."""
            try:
                return {
                    "ai_config": ai_client.get_config().dict(),
                    "capture_stats": self.screen_capture.get_stats().dict(),
                    "available_features": {
                        "ai": ai_client.is_available(),
                        "web_search": web_searcher.is_available(),
                        "screen_capture": self.screen_capture.mss is not None,
                        "ocr": self.screen_capture.pytesseract is not None
                    }
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e)) from e
        
        @self.router.post("/capture/single")
        async def capture_single():
            """Capture a single screen and return OCR text."""
            try:
                png_bytes, ocr_text = self.screen_capture.capture_single_screen()
                return {
                    "success": png_bytes is not None,
                    "ocr_text": ocr_text,
                    "has_image": png_bytes is not None
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e)) from e
        
        @self.router.get("/window/active")
        async def get_active_window():
            """Get active window information."""
            try:
                window_info = window_manager.get_active_window_info()
                return {
                    "title": window_info.title,
                    "process_name": window_info.process_name,
                    "pid": window_info.pid,
                    "formatted": window_manager.format_window_info(window_info)
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e)) from e
        
        @self.router.post("/search")
        async def web_search(query: str, max_results: int = 5):
            """Perform web search."""
            try:
                if not web_searcher.is_available():
                    raise HTTPException(status_code=503, detail="Web search not available")
                
                response = web_searcher.search(query, max_results)
                return {
                    "query": response.query,
                    "results": [result.dict() for result in response.results],
                    "formatted": web_searcher.search_formatted(query, max_results)
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e)) from e
        
        @self.router.post("/ai/test")
        async def test_ai():
            """Test AI connection."""
            try:
                if not ai_client.is_available():
                    raise HTTPException(status_code=503, detail="AI client not available")
                
                response = ai_client.chat_simple("Hello, this is a test message.")
                return {
                    "success": True,
                    "response": response,
                    "config": ai_client.get_config().dict()
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e)) from e
        
        @self.router.get("/config/system-prompt")
        async def get_system_prompt():
            """Get current system prompt."""
            try:
                config = ai_client.get_config()
                return {
                    "system_prompt": config.system_prompt,
                    "model": config.model,
                    "temperature": config.temperature,
                    "top_p": config.top_p
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e)) from e
        
        @self.router.post("/config/system-prompt")
        async def update_system_prompt(request: dict):
            """Update system prompt."""
            try:
                if not ai_client.is_available():
                    raise HTTPException(status_code=503, detail="AI client not available")
                
                new_system_prompt = request.get("system_prompt", "")
                if not new_system_prompt.strip():
                    raise HTTPException(status_code=400, detail="System prompt cannot be empty")
                
                # Update the configuration
                current_config = ai_client.get_config()
                current_config.system_prompt = new_system_prompt
                ai_client.update_config(current_config)
                
                return {
                    "success": True,
                    "message": "System prompt updated successfully",
                    "new_system_prompt": new_system_prompt
                }
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e)) from e
        
        @self.router.post("/config/ai")
        async def update_ai_config(request: dict):
            """Update AI configuration."""
            try:
                if not ai_client.is_available():
                    raise HTTPException(status_code=503, detail="AI client not available")
                
                current_config = ai_client.get_config()
                
                # Update fields if provided
                if "system_prompt" in request:
                    current_config.system_prompt = request["system_prompt"]
                if "model" in request:
                    current_config.model = request["model"]
                if "temperature" in request:
                    current_config.temperature = float(request["temperature"])
                if "top_p" in request:
                    current_config.top_p = float(request["top_p"])
                
                ai_client.update_config(current_config)
                
                return {
                    "success": True,
                    "message": "AI configuration updated successfully",
                    "config": current_config.dict()
                }
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e)) from e
    
    def get_router(self):
        """Get the FastAPI router."""
        return self.router


# Global API router instance
api_router = APIRouterManager()
