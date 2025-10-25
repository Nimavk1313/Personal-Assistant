"""
AI/LLM client management for the Personal Assistant application.
"""
from typing import List, Dict, Any, Optional
from config import config
from models import AssistantConfig, ChatRequest, ChatResponse
from data_fusion import data_fusion


class AIClient:
    """Handles AI/LLM client operations."""
    
    def __init__(self):
        self._imports = config.get_optional_imports()
        self.Cerebras = self._imports.get('Cerebras')
        self._client = None
        self._config = config.to_assistant_config()
        self._available = self.Cerebras is not None and config.api_key is not None
        
        if self._available:
            try:
                self._client = self.Cerebras(api_key=config.api_key)
            except Exception:
                self._available = False
                self._client = None
    
    def is_available(self) -> bool:
        """Check if AI client is available."""
        return self._available and self._client is not None
    
    def get_config(self) -> AssistantConfig:
        """Get current configuration."""
        return self._config
    
    def update_config(self, new_config: AssistantConfig) -> None:
        """Update configuration."""
        self._config = new_config
        
        # Recreate client if API key changed
        if new_config.api_key != config.api_key:
            if new_config.api_key and self.Cerebras:
                try:
                    self._client = self.Cerebras(api_key=new_config.api_key)
                    self._available = True
                except Exception:
                    self._available = False
                    self._client = None
            else:
                self._available = False
                self._client = None
    
    def chat(self, request: ChatRequest, screen_text: str = "", window_info: str = "", web_results: str = "") -> ChatResponse:
        """Process chat request and return response."""
        if not self.is_available():
            raise RuntimeError("AI client not available")
        
        # Build messages
        messages = self._build_messages(request, screen_text, window_info, web_results)
        
        try:
            response = self._client.chat.completions.create(
                messages=messages,
                model=self._config.model,
                stream=False,
                max_completion_tokens=2000,
                temperature=self._config.temperature,
                top_p=self._config.top_p,
            )
            
            content = response.choices[0].message.content
            
            return ChatResponse(
                response=content or "",
                screen_text=screen_text,
                window_info=window_info,
                web_results=web_results
            )
            
        except Exception as e:
            raise RuntimeError(f"Chat error: {e}")
    
    def _build_messages(self, request: ChatRequest, screen_text: str, window_info: str, web_results: str) -> List[Dict[str, str]]:
        """Build messages for the AI client with intelligent context integration and data fusion."""
        
        # Use data fusion to intelligently combine and prioritize context sources
        fused_context = data_fusion.fuse_contexts(
            query=request.message,
            screen_text=screen_text,
            web_results=web_results,
            window_info=window_info
        )
        
        # Build enhanced system prompt
        enhanced_system_prompt = self._config.system_prompt
        
        # Add context guidance based on fusion analysis
        if fused_context.primary_context or fused_context.supporting_context:
            context_guidance = f"""

CONTEXT ANALYSIS: {fused_context.relevance_summary}
FUSION STRATEGY: {fused_context.fusion_strategy}

INSTRUCTIONS FOR CONTEXT USAGE:
- Focus primarily on the most relevant context provided
- Use supporting context to supplement your understanding when helpful
- If context seems irrelevant to the query, acknowledge this and focus on the direct question
- When referencing screen content, be specific about what you see
- When using web results, cite sources and focus on recent/relevant information
- Combine context sources intelligently when they complement each other
"""
            enhanced_system_prompt += context_guidance
        
        messages = [
            {"role": "system", "content": enhanced_system_prompt},
        ]
        
        # Add intelligently fused context
        if fused_context.primary_context:
            messages.append({
                "role": "user", 
                "content": f"PRIMARY CONTEXT (Most Relevant):\n{fused_context.primary_context}"
            })
        
        if fused_context.supporting_context:
            messages.append({
                "role": "user", 
                "content": f"SUPPORTING CONTEXT:\n{fused_context.supporting_context}"
            })
        
        # Add context analysis summary for transparency
        if fused_context.relevance_summary != "No context sources analyzed":
            messages.append({
                "role": "user", 
                "content": f"CONTEXT ANALYSIS: {fused_context.relevance_summary}"
            })
        
        # Add user's actual query
        messages.append({
            "role": "user", 
            "content": f"USER QUERY: {request.message}"
        })
        
        return messages
    
    def chat_simple(self, message: str, system_prompt: str = None) -> str:
        """Simple chat without additional context."""
        if not self.is_available():
            raise RuntimeError("AI client not available")
        
        messages = [
            {"role": "system", "content": system_prompt or self._config.system_prompt},
            {"role": "user", "content": message}
        ]
        
        try:
            response = self._client.chat.completions.create(
                messages=messages,
                model=self._config.model,
                stream=False,
                max_completion_tokens=2000,
                temperature=self._config.temperature,
                top_p=self._config.top_p,
            )
            
            return response.choices[0].message.content or ""
            
        except Exception as e:
            raise RuntimeError(f"Chat error: {e}")
    
    def get_available_models(self) -> List[str]:
        """Get list of available models."""
        # This would need to be implemented based on the Cerebras API
        # For now, return the configured model
        return [self._config.model]
    
    def test_connection(self) -> bool:
        """Test connection to the AI service."""
        if not self.is_available():
            return False
        
        try:
            # Simple test request
            response = self._client.chat.completions.create(
                messages=[{"role": "user", "content": "Hello"}],
                model=self._config.model,
                stream=False,
                max_completion_tokens=10,
            )
            return True
        except Exception:
            return False
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics (if available)."""
        # This would need to be implemented based on the Cerebras API
        return {
            "model": self._config.model,
            "temperature": self._config.temperature,
            "top_p": self._config.top_p,
            "available": self._available
        }


# Global AI client instance
ai_client = AIClient()
