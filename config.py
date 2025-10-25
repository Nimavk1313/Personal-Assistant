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
        self.api_key = os.environ.get("CEREBRAS_API_KEY")
        self.model = os.environ.get("ASSISTANT_MODEL", "llama3.1-8b")
        self.temperature = float(os.environ.get("ASSISTANT_TEMPERATURE", "0.2"))
        self.top_p = float(os.environ.get("ASSISTANT_TOP_P", "0.9"))
        self.system_prompt = os.environ.get("ASSISTANT_SYSTEM_PROMPT", 
                                          "You are a helpful personal assistant. Be concise and helpful.")
        
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
            api_key=self.api_key,
            model=self.model,
            temperature=self.temperature,
            top_p=self.top_p,
            system_prompt=self.system_prompt
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
