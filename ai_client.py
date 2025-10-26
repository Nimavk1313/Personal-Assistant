"""
AI/LLM client management for the Personal Assistant application.
"""
from typing import List, Dict, Any, Optional
import asyncio
from config import config
from models import AssistantConfig, ChatRequest, ChatResponse
from data_fusion import data_fusion
from smart_context_analyzer import smart_analyzer
from conversation_memory import get_conversation_memory
from thinking_engine import get_thinking_engine


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
        
        # Get conversation memory
        memory = get_conversation_memory(self._config)
        session_id = memory.get_session_id(window_info)
        
        # Add user message to memory
        memory.add_message(session_id, "user", request.message, {
            "use_ocr": request.use_ocr,
            "use_web": request.use_web,
            "screen_text_length": len(screen_text),
            "web_results_length": len(web_results)
        })
        
        # Thinking phase: Analyze context and perform intelligent research
        enhanced_web_results = web_results
        thinking_insights = []
        
        if self._config.enable_thinking:
            try:
                thinking_engine = get_thinking_engine(self._config)
                thinking_result = asyncio.run(thinking_engine.think(
                    request, screen_text, window_info, web_results
                ))
                
                # Use enhanced search results from thinking
                if thinking_result.search_results:
                    enhanced_web_results = thinking_result.search_results
                
                # Store thinking insights for context
                thinking_insights = thinking_result.key_insights
                
            except Exception as e:
                # If thinking fails, continue with original web results
                print(f"Thinking engine error: {e}")
        
        # Build messages with conversation history and enhanced context
        messages = self._build_messages(request, screen_text, window_info, enhanced_web_results, session_id)
        
        # Apply response style modifications
        messages = self._apply_response_style(messages)
        
        try:
            # Prepare API parameters with new configuration options
            api_params = {
                "messages": messages,
                "model": self._config.model,
                "stream": self._config.stream_responses,
                "temperature": self._config.temperature,
                "top_p": self._config.top_p,
            }
            
            # Add optional parameters if configured
            if self._config.max_tokens:
                api_params["max_completion_tokens"] = self._config.max_tokens
            if self._config.frequency_penalty != 0.0:
                api_params["frequency_penalty"] = self._config.frequency_penalty
            if self._config.presence_penalty != 0.0:
                api_params["presence_penalty"] = self._config.presence_penalty
            if self._config.stop_sequences:
                api_params["stop"] = self._config.stop_sequences
            
            response = self._client.chat.completions.create(**api_params)
            
            content = response.choices[0].message.content
            
            # Apply response length limit if configured
            if self._config.max_response_length and content:
                content = content[:self._config.max_response_length]
            
            # Add assistant response to memory
            memory.add_message(session_id, "assistant", content or "", {
                "model": self._config.model,
                "response_style": self._config.response_style,
                "assistant_mode": self._config.assistant_mode
            })
            
            return ChatResponse(
                response=content or "",
                screen_text=screen_text,
                window_info=window_info,
                web_results=enhanced_web_results,
                thinking_insights=thinking_insights
            )
            
        except Exception as e:
            raise RuntimeError(f"Chat error: {e}")
    
    def _build_messages(self, request: ChatRequest, screen_text: str, window_info: str, web_results: str, session_id: str = None) -> List[Dict[str, str]]:
        """Build messages for the AI client with intelligent context integration and data fusion."""
        
        # First, perform enhanced OCR content analysis for better understanding
        ocr_analysis = None
        if screen_text and screen_text.strip():
            ocr_analysis = smart_analyzer.analyze_ocr_content(screen_text, request.message)
        
        # Check if we have comprehensive thinking results (longer web results indicate thinking engine output)
        has_thinking_results = web_results and len(web_results) > 3000
        
        if has_thinking_results:
            # For thinking engine results, bypass data fusion to preserve comprehensive web search data
            fused_context = None
        else:
            # Use data fusion to intelligently combine and prioritize context sources
            fused_context = data_fusion.fuse_contexts(
                query=request.message,
                screen_text=screen_text,
                web_results=web_results,
                window_info=window_info
            )
        
        # Build enhanced system prompt
        enhanced_system_prompt = self._config.system_prompt
        
        # Add OCR-focused guidance if available
        if ocr_analysis and ocr_analysis.confidence_score > 0.3:
            ocr_guidance = f"""

OCR CONTENT FOCUS:
- Primary content type detected: {ocr_analysis.primary_content_type.value.replace('_', ' ').title()}
- Key focus areas: {ocr_analysis.summary}
- Priority: Analyze OCR content FIRST, then supplement with other context

STRICT OCR-ONLY RESPONSE RULES:
- ONLY reference what is ACTUALLY VISIBLE in the provided OCR text
- DO NOT make assumptions about content not shown in the OCR
- DO NOT add information that is not explicitly present on the screen
- If asked about something not visible in OCR, clearly state "I can only see [what's actually in OCR]"
- Quote or reference specific text from the OCR when explaining
- If the OCR shows errors, reference the EXACT error message shown
- If the OCR shows code, explain only the code that is ACTUALLY visible
- If the OCR shows UI elements, reference only the elements that are ACTUALLY shown
- Be honest about limitations: "Based on what I can see on your screen..."
"""
            enhanced_system_prompt += ocr_guidance
        
        # Add context guidance based on fusion analysis or thinking results
        if has_thinking_results and web_results:
            context_guidance = f"""

COMPREHENSIVE RESEARCH CONTEXT:
- You have access to comprehensive research results from intelligent web search
- These results have been curated and analyzed for relevance to the user's query
- Use this information to provide well-informed, accurate responses
- Cite specific sources when referencing web information
- Combine research findings with screen content analysis when both are available
- PRIORITIZE ACCURACY and cite sources for factual claims
"""
            enhanced_system_prompt += context_guidance
        elif fused_context and (fused_context.primary_context or fused_context.supporting_context):
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
- PRIORITIZE PRECISION over comprehensiveness
"""
            enhanced_system_prompt += context_guidance
        
        messages = [
            {"role": "system", "content": enhanced_system_prompt},
        ]
        
        # Add conversation history if enabled and available
        if session_id and self._config.conversation_memory:
            memory = get_conversation_memory(self._config)
            history = memory.get_conversation_history(session_id, include_system=False)
            
            # Add context summary if available
            context_summary = memory.get_context_summary(session_id)
            if context_summary:
                messages.append({
                    "role": "system",
                    "content": f"CONVERSATION CONTEXT: {context_summary}"
                })
            
            # Add recent conversation history (excluding current message)
            for msg in history[:-1]:  # Exclude the current user message we just added
                messages.append(msg)
        
        # Add context based on whether we have thinking results or need fusion
        if has_thinking_results:
            # For thinking engine results, add comprehensive web results directly
            if web_results:
                messages.append({
                    "role": "user", 
                    "content": f"COMPREHENSIVE RESEARCH RESULTS:\n{web_results}"
                })
            
            # Also add screen text and window info directly when bypassing fusion
            if screen_text and screen_text.strip():
                messages.append({
                    "role": "user", 
                    "content": f"SCREEN CONTENT:\n{screen_text}"
                })
            
            if window_info and window_info.strip():
                messages.append({
                    "role": "user", 
                    "content": f"WINDOW INFORMATION:\n{window_info}"
                })
        else:
            # Add intelligently fused context for regular results
            if fused_context and fused_context.primary_context:
                messages.append({
                    "role": "user", 
                    "content": f"PRIMARY CONTEXT (Most Relevant):\n{fused_context.primary_context}"
                })
            
            if fused_context and fused_context.supporting_context:
                messages.append({
                    "role": "user", 
                    "content": f"SUPPORTING CONTEXT:\n{fused_context.supporting_context}"
                })
        
        # Add OCR content analysis for enhanced understanding
        if ocr_analysis and ocr_analysis.confidence_score > 0.3:
            analysis_info = f"""OCR CONTENT ANALYSIS:
- Content Type: {ocr_analysis.primary_content_type.value.replace('_', ' ').title()}
- Key Information: {ocr_analysis.summary}
- Technical Terms: {', '.join(ocr_analysis.technical_terms[:5]) if ocr_analysis.technical_terms else 'None'}
- Actionable Items: {'; '.join(ocr_analysis.actionable_items[:3]) if ocr_analysis.actionable_items else 'None'}
- Confidence: {ocr_analysis.confidence_score:.2f}"""
            
            messages.append({
                "role": "user", 
                "content": analysis_info
            })
        
        # Add context analysis summary for transparency
        if not has_thinking_results and fused_context and fused_context.relevance_summary != "No context sources analyzed":
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
    
    def _apply_response_style(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Apply response style modifications based on configuration."""
        if not messages:
            return messages
        
        # Get the system message to modify
        system_msg = messages[0] if messages[0]["role"] == "system" else None
        if not system_msg:
            return messages
        
        # Add style-specific instructions
        style_instructions = ""
        
        if self._config.response_style == "concise":
            style_instructions += "\n\nRESPONSE STYLE: Be extremely concise and direct. Use bullet points when appropriate. Avoid unnecessary explanations."
        elif self._config.response_style == "detailed":
            style_instructions += "\n\nRESPONSE STYLE: Provide comprehensive, detailed explanations. Include context, examples, and step-by-step guidance when helpful."
        elif self._config.response_style == "balanced":
            style_instructions += "\n\nRESPONSE STYLE: Balance conciseness with helpful detail. Be clear and informative without being verbose."
        
        # Add assistant mode instructions
        if self._config.assistant_mode == "coding":
            style_instructions += "\n\nASSISTANT MODE: Focus on code analysis, programming solutions, debugging, and technical implementation details."
        elif self._config.assistant_mode == "research":
            style_instructions += "\n\nASSISTANT MODE: Emphasize fact-checking, source analysis, comprehensive information gathering, and analytical thinking."
        elif self._config.assistant_mode == "creative":
            style_instructions += "\n\nASSISTANT MODE: Encourage creative thinking, brainstorming, innovative solutions, and imaginative approaches."
        elif self._config.assistant_mode == "technical":
            style_instructions += "\n\nASSISTANT MODE: Focus on technical accuracy, precise terminology, system analysis, and engineering perspectives."
        
        # Add expertise level adjustments
        if self._config.expertise_level == "beginner":
            style_instructions += "\n\nEXPERTISE LEVEL: Explain concepts clearly with basic terminology. Provide background context and avoid jargon."
        elif self._config.expertise_level == "expert":
            style_instructions += "\n\nEXPERTISE LEVEL: Use advanced terminology and assume deep knowledge. Focus on nuanced details and expert-level insights."
        
        # Add response format instructions
        if self._config.response_format == "json":
            style_instructions += "\n\nRESPONSE FORMAT: Structure your response as valid JSON when appropriate."
        elif self._config.response_format == "markdown":
            style_instructions += "\n\nRESPONSE FORMAT: Use markdown formatting for better readability (headers, lists, code blocks, etc.)."
        
        # Apply security considerations
        if self._config.secure_mode:
            style_instructions += "\n\nSECURITY MODE: Avoid discussing sensitive information, security vulnerabilities, or potentially harmful content."
        
        system_msg["content"] += style_instructions
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
