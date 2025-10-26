"""
Configuration management for the Personal Assistant application.
"""
import os
from typing import Optional
from dotenv import load_dotenv
from models import AssistantConfig

# Load environment variables
load_dotenv()


class Config:
    """Configuration class for the Personal Assistant application."""
    
    def __init__(self):
        # Basic AI configuration
        self.api_key = os.environ.get("CEREBRAS_API_KEY")
        self.model = os.environ.get("ASSISTANT_MODEL", "llama3.1-8b")
        self.temperature = float(os.environ.get("ASSISTANT_TEMPERATURE", "0.2"))
        self.top_p = float(os.environ.get("ASSISTANT_TOP_P", "0.9"))
        self.system_prompt = os.environ.get("ASSISTANT_SYSTEM_PROMPT", 
                                          "You are a helpful personal assistant. Be concise and helpful.")
        
        # Advanced model parameters
        self.max_tokens = int(os.environ.get("ASSISTANT_MAX_TOKENS", "2048")) if os.environ.get("ASSISTANT_MAX_TOKENS") else None
        self.frequency_penalty = float(os.environ.get("ASSISTANT_FREQUENCY_PENALTY", "0.0"))
        self.presence_penalty = float(os.environ.get("ASSISTANT_PRESENCE_PENALTY", "0.0"))
        self.stop_sequences = os.environ.get("ASSISTANT_STOP_SEQUENCES", "").split(",") if os.environ.get("ASSISTANT_STOP_SEQUENCES") else None
        
        # Response behavior
        self.response_format = os.environ.get("ASSISTANT_RESPONSE_FORMAT", "text")
        self.response_style = os.environ.get("ASSISTANT_RESPONSE_STYLE", "balanced")
        self.max_response_length = int(os.environ.get("ASSISTANT_MAX_RESPONSE_LENGTH")) if os.environ.get("ASSISTANT_MAX_RESPONSE_LENGTH") else None
        
        # Context and memory
        self.conversation_memory = os.environ.get("ASSISTANT_CONVERSATION_MEMORY", "true").lower() == "true"
        self.max_context_messages = int(os.environ.get("ASSISTANT_MAX_CONTEXT_MESSAGES", "10"))
        self.context_window_size = int(os.environ.get("ASSISTANT_CONTEXT_WINDOW_SIZE", "4096"))
        self.auto_summarize_context = os.environ.get("ASSISTANT_AUTO_SUMMARIZE_CONTEXT", "false").lower() == "true"
        
        # Assistant modes
        self.assistant_mode = os.environ.get("ASSISTANT_MODE", "general")
        self.expertise_level = os.environ.get("ASSISTANT_EXPERTISE_LEVEL", "intermediate")
        
        # Privacy and security
        self.data_retention_hours = int(os.environ.get("ASSISTANT_DATA_RETENTION_HOURS", "24"))
        self.anonymize_data = os.environ.get("ASSISTANT_ANONYMIZE_DATA", "false").lower() == "true"
        self.secure_mode = os.environ.get("ASSISTANT_SECURE_MODE", "false").lower() == "true"
        
        # Performance settings
        self.response_timeout = int(os.environ.get("ASSISTANT_RESPONSE_TIMEOUT", "30"))
        self.retry_attempts = int(os.environ.get("ASSISTANT_RETRY_ATTEMPTS", "3"))
        self.cache_responses = os.environ.get("ASSISTANT_CACHE_RESPONSES", "true").lower() == "true"
        self.stream_responses = os.environ.get("ASSISTANT_STREAM_RESPONSES", "false").lower() == "true"
        
        # Thinking engine settings
        self.enable_thinking = os.environ.get("ASSISTANT_ENABLE_THINKING", "true").lower() == "true"
        self.max_thinking_searches = int(os.environ.get("ASSISTANT_MAX_THINKING_SEARCHES", "3"))
        self.thinking_timeout_seconds = int(os.environ.get("ASSISTANT_THINKING_TIMEOUT", "30"))
        self.thinking_depth = os.environ.get("ASSISTANT_THINKING_DEPTH", "standard")  # minimal, standard, deep
        
        # Optional dependencies flags
        self.has_mss = self._check_optional_dependency("mss")
        self.has_pil = self._check_optional_dependency("PIL")
        self.has_pytesseract = self._check_optional_dependency("pytesseract")
        self.has_pynput = self._check_optional_dependency("pynput")
        self.has_cerebras = self._check_optional_dependency("cerebras")
        # Check for both old and new duckduckgo packages
        self.has_duckduckgo = self._check_optional_dependency("duckduckgo_search") or self._check_optional_dependency("ddgs")
        
        # Capture settings
        self.capture_interval = float(os.environ.get("CAPTURE_INTERVAL", "0.75"))
        self.max_ocr_history = int(os.environ.get("MAX_OCR_HISTORY", "200"))
        self.ocr_timeout = int(os.environ.get("OCR_TIMEOUT", "25"))
        self.max_transcript_chars = int(os.environ.get("MAX_TRANSCRIPT_CHARS", "3000"))
        
        # Web search settings
        self.web_search_max_results = int(os.environ.get("WEB_SEARCH_MAX_RESULTS", "5"))
        self.web_search_safesearch = os.environ.get("WEB_SEARCH_SAFESEARCH", "moderate")
        self.web_search_timelimit = os.environ.get("WEB_SEARCH_TIMELIMIT", "y")
    
    def _check_optional_dependency(self, module_name: str) -> bool:
        """Check if an optional dependency is available."""
        try:
            if module_name == "mss":
                import mss
            elif module_name == "PIL":
                from PIL import Image
            elif module_name == "pytesseract":
                import pytesseract
            elif module_name == "pynput":
                import pynput
            elif module_name == "cerebras":
                from cerebras.cloud.sdk import Cerebras
            elif module_name == "duckduckgo_search":
                from duckduckgo_search import DDGS
            elif module_name == "ddgs":
                from ddgs import DDGS
            return True
        except ImportError:
            return False
    
    def to_assistant_config(self) -> AssistantConfig:
        """Convert to AssistantConfig model."""
        return AssistantConfig(
            # Basic configuration
            api_key=self.api_key,
            model=self.model,
            temperature=self.temperature,
            top_p=self.top_p,
            system_prompt=self.system_prompt,
            
            # Advanced model parameters
            max_tokens=self.max_tokens,
            frequency_penalty=self.frequency_penalty,
            presence_penalty=self.presence_penalty,
            stop_sequences=self.stop_sequences,
            
            # Response behavior
            response_format=self.response_format,
            response_style=self.response_style,
            max_response_length=self.max_response_length,
            
            # Context and memory
            conversation_memory=self.conversation_memory,
            max_context_messages=self.max_context_messages,
            context_window_size=self.context_window_size,
            auto_summarize_context=self.auto_summarize_context,
            
            # Assistant modes
            assistant_mode=self.assistant_mode,
            expertise_level=self.expertise_level,
            
            # Privacy and security
            data_retention_hours=self.data_retention_hours,
            anonymize_data=self.anonymize_data,
            secure_mode=self.secure_mode,
            
            # Performance settings
            response_timeout=self.response_timeout,
            retry_attempts=self.retry_attempts,
            cache_responses=self.cache_responses,
            stream_responses=self.stream_responses,
            
            # Thinking engine settings
            enable_thinking=self.enable_thinking,
            max_thinking_searches=self.max_thinking_searches,
            thinking_timeout_seconds=self.thinking_timeout_seconds,
            thinking_depth=self.thinking_depth
        )
    
    def get_optional_imports(self) -> dict:
        """Get optional imports if available."""
        imports = {}
        
        if self.has_mss:
            try:
                import mss
                imports['mss'] = mss
            except ImportError:
                pass
        
        if self.has_pil:
            try:
                from PIL import Image
                imports['Image'] = Image
            except ImportError:
                pass
        
        if self.has_pytesseract:
            try:
                import pytesseract
                imports['pytesseract'] = pytesseract
            except ImportError:
                pass
        
        if self.has_pynput:
            try:
                from pynput import keyboard
                imports['keyboard'] = keyboard
            except ImportError:
                pass
        
        if self.has_cerebras:
            try:
                from cerebras.cloud.sdk import Cerebras
                imports['Cerebras'] = Cerebras
            except ImportError:
                pass
        
        if self.has_duckduckgo:
            try:
                from ddgs import DDGS
                imports['DDGS'] = DDGS
            except ImportError:
                try:
                    from duckduckgo_search import DDGS
                    imports['DDGS'] = DDGS
                except ImportError:
                    pass
        
        return imports


# Global config instance
config = Config()
