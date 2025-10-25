"""
Smart Context Analyzer for the Personal Assistant application.
Intelligently determines when to use OCR, web search, or both based on query analysis.
"""
import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
from performance_optimizer import performance_optimizer


class QueryType(Enum):
    """Types of queries that can be classified."""
    SCREEN_RELATED = "screen_related"
    WEB_SEARCH_NEEDED = "web_search_needed"
    CURRENT_EVENTS = "current_events"
    TECHNICAL_INFO = "technical_info"
    GENERAL_QUESTION = "general_question"
    MIXED_CONTEXT = "mixed_context"
    CONVERSATIONAL = "conversational"


class DataSource(Enum):
    """Available data sources."""
    OCR_ONLY = "ocr_only"
    WEB_ONLY = "web_only"
    BOTH = "both"
    NEITHER = "neither"


@dataclass
class ContextDecision:
    """Decision about which context sources to use."""
    use_ocr: bool
    use_web: bool
    query_type: QueryType
    confidence: float
    reasoning: str
    web_search_params: Optional[Dict] = None


class SmartContextAnalyzer:
    """Analyzes queries to determine optimal context sources."""
    
    def __init__(self):
        # Keywords that indicate screen-related queries
        self.screen_keywords = {
            'screen', 'display', 'window', 'application', 'app', 'interface', 'ui', 'gui',
            'button', 'menu', 'dialog', 'form', 'text', 'image', 'picture', 'screenshot',
            'visible', 'showing', 'displayed', 'current', 'open', 'running', 'active',
            'click', 'select', 'choose', 'navigate', 'scroll', 'type', 'enter',
            'what do you see', 'what is on', 'describe what', 'read this', 'what does this say',
            'help me with this', 'explain this', 'what is this', 'how do i', 'where is',
            'find the', 'locate the', 'show me', 'point to'
        }
        
        # Keywords that indicate web search is needed
        self.web_keywords = {
            'latest', 'recent', 'current', 'today', 'news', 'update', 'new', 'trending',
            'what happened', 'breaking', 'announcement', 'release', 'launch', 'event',
            'price', 'stock', 'market', 'weather', 'forecast', 'temperature',
            'search for', 'find information', 'look up', 'research', 'investigate',
            'compare', 'review', 'tutorial', 'guide', 'how to', 'best practices',
            'recommendations', 'suggestions', 'alternatives', 'options'
        }
        
        # Time-sensitive indicators
        self.time_indicators = {
            'today', 'yesterday', 'tomorrow', 'this week', 'this month', 'this year',
            'now', 'currently', 'recent', 'latest', 'new', 'updated', 'fresh',
            '2024', '2025', 'january', 'february', 'march', 'april', 'may', 'june',
            'july', 'august', 'september', 'october', 'november', 'december'
        }
        
        # Technical/factual query indicators
        self.technical_keywords = {
            'programming', 'code', 'software', 'development', 'framework', 'library',
            'algorithm', 'database', 'api', 'documentation', 'tutorial', 'example',
            'syntax', 'function', 'method', 'class', 'variable', 'error', 'bug',
            'install', 'setup', 'configure', 'deploy', 'build', 'compile'
        }
        
        # Conversational indicators (usually don't need external data)
        self.conversational_keywords = {
            'hello', 'hi', 'thanks', 'thank you', 'please', 'sorry', 'excuse me',
            'good morning', 'good afternoon', 'good evening', 'goodbye', 'bye',
            'how are you', 'nice to meet', 'pleasure', 'welcome'
        }
    
    def analyze_query(self, query: str, window_info: str = "", has_live_ocr: bool = False) -> ContextDecision:
        """
        Analyze a query to determine optimal context sources.
        
        Args:
            query: The user's query
            window_info: Information about the current window
            has_live_ocr: Whether live OCR is currently active
            
        Returns:
            ContextDecision with recommendations for data sources
        """
        if not query or not query.strip():
            return ContextDecision(
                use_ocr=False,
                use_web=False,
                query_type=QueryType.CONVERSATIONAL,
                confidence=0.0,
                reasoning="Empty query"
            )
        
        # Performance optimization checks
        should_use_ocr, ocr_reasoning = performance_optimizer.should_use_ocr(query, window_info)
        should_use_web, web_reasoning = performance_optimizer.should_use_web_search(query)
        
        # If performance optimizer says no to both, respect that
        if not should_use_ocr and not should_use_web:
            return ContextDecision(
                use_ocr=False,
                use_web=False,
                query_type=QueryType.GENERAL_QUESTION,
                confidence=0.8,
                reasoning=f"Performance optimization: {ocr_reasoning}; {web_reasoning}"
            )
        
        query_lower = query.lower()
        
        # Calculate keyword scores
        screen_score = self._calculate_keyword_score(query_lower, self.screen_keywords)
        web_score = self._calculate_keyword_score(query_lower, self.web_keywords)
        time_score = self._calculate_keyword_score(query_lower, self.time_indicators)
        technical_score = self._calculate_keyword_score(query_lower, self.technical_keywords)
        conversational_score = self._calculate_keyword_score(query_lower, self.conversational_keywords)
        
        # Analyze query patterns
        has_question_words = any(word in query_lower for word in ['what', 'how', 'where', 'when', 'why', 'which', 'who'])
        has_demonstratives = any(word in query_lower for word in ['this', 'that', 'these', 'those', 'here', 'there'])
        has_current_reference = any(word in query_lower for word in ['current', 'now', 'present', 'active', 'open'])
        
        # Determine query type and data source needs
        query_type, confidence = self._classify_query_type(
            screen_score, web_score, time_score, technical_score, conversational_score,
            has_question_words, has_demonstratives, has_current_reference
        )
        
        # Make context decision
        decision = self._make_context_decision(
            query_type, confidence, query_lower, window_info, has_live_ocr,
            screen_score, web_score, time_score
        )
        
        return decision
    
    def _calculate_keyword_score(self, text: str, keywords: set) -> float:
        """Calculate how many keywords from a set appear in the text."""
        words = set(re.findall(r'\b\w+\b', text))
        matches = len(words.intersection(keywords))
        return matches / len(keywords) if keywords else 0.0
    
    def _classify_query_type(self, screen_score: float, web_score: float, time_score: float,
                           technical_score: float, conversational_score: float,
                           has_question_words: bool, has_demonstratives: bool,
                           has_current_reference: bool) -> Tuple[QueryType, float]:
        """Classify the query type based on various scores and patterns."""
        
        # Conversational queries (high confidence)
        if conversational_score > 0.3:
            return QueryType.CONVERSATIONAL, 0.9
        
        # Screen-related queries
        if screen_score > 0.1 or (has_demonstratives and has_current_reference):
            confidence = min(0.9, 0.5 + screen_score * 2)
            return QueryType.SCREEN_RELATED, confidence
        
        # Current events (time-sensitive + web indicators)
        if time_score > 0.1 and web_score > 0.05:
            confidence = min(0.9, 0.6 + (time_score + web_score))
            return QueryType.CURRENT_EVENTS, confidence
        
        # Technical information
        if technical_score > 0.1:
            confidence = min(0.8, 0.5 + technical_score * 1.5)
            return QueryType.TECHNICAL_INFO, confidence
        
        # Web search needed
        if web_score > 0.05 or time_score > 0.05:
            confidence = min(0.8, 0.4 + (web_score + time_score) * 2)
            return QueryType.WEB_SEARCH_NEEDED, confidence
        
        # Mixed context (both screen and web indicators)
        if screen_score > 0.05 and web_score > 0.05:
            confidence = 0.7
            return QueryType.MIXED_CONTEXT, confidence
        
        # Default to general question
        return QueryType.GENERAL_QUESTION, 0.5
    
    def _make_context_decision(self, query_type: QueryType, confidence: float,
                             query_lower: str, window_info: str, has_live_ocr: bool,
                             screen_score: float, web_score: float, time_score: float) -> ContextDecision:
        """Make the final decision about which context sources to use."""
        
        use_ocr = False
        use_web = False
        reasoning = ""
        web_search_params = None
        
        # Get performance optimizer recommendations
        should_use_ocr, ocr_perf_reason = performance_optimizer.should_use_ocr(query_lower, window_info)
        should_use_web, web_perf_reason = performance_optimizer.should_use_web_search(query_lower)
        
        if query_type == QueryType.CONVERSATIONAL:
            reasoning = "Conversational query - no external context needed"
            
        elif query_type == QueryType.SCREEN_RELATED:
            use_ocr = should_use_ocr
            if use_ocr:
                reasoning = "Screen-related query detected - using OCR to analyze current display"
            else:
                reasoning = f"Screen-related query but OCR skipped: {ocr_perf_reason}"
            
        elif query_type == QueryType.CURRENT_EVENTS:
            use_web = should_use_web
            if use_web:
                reasoning = "Current events query - using web search for latest information"
                base_params = {"timelimit": "d", "max_results": 5}
                web_search_params = performance_optimizer.optimize_web_search_params(query_lower, base_params)
            else:
                reasoning = f"Current events query but web search skipped: {web_perf_reason}"
            
        elif query_type == QueryType.TECHNICAL_INFO:
            use_web = should_use_web
            if use_web:
                reasoning = "Technical query - using web search for documentation and tutorials"
                base_params = {"max_results": 3}
                web_search_params = performance_optimizer.optimize_web_search_params(query_lower, base_params)
            else:
                reasoning = f"Technical query but web search skipped: {web_perf_reason}"
            
        elif query_type == QueryType.WEB_SEARCH_NEEDED:
            use_web = should_use_web
            if use_web:
                reasoning = "Query requires external information - using web search"
                base_params = {"max_results": 5}
                web_search_params = performance_optimizer.optimize_web_search_params(query_lower, base_params)
            else:
                reasoning = f"Query requires external info but web search skipped: {web_perf_reason}"
            
        elif query_type == QueryType.MIXED_CONTEXT:
            use_ocr = should_use_ocr
            use_web = should_use_web
            if use_ocr and use_web:
                reasoning = "Mixed context query - using both screen OCR and web search"
                base_params = {"max_results": 3}
                web_search_params = performance_optimizer.optimize_web_search_params(query_lower, base_params)
            elif use_ocr:
                reasoning = f"Mixed context query - using OCR only (web skipped: {web_perf_reason})"
            elif use_web:
                reasoning = f"Mixed context query - using web only (OCR skipped: {ocr_perf_reason})"
                base_params = {"max_results": 5}
                web_search_params = performance_optimizer.optimize_web_search_params(query_lower, base_params)
            else:
                reasoning = f"Mixed context query - using AI only (OCR: {ocr_perf_reason}, Web: {web_perf_reason})"
            
        else:  # GENERAL_QUESTION
            # For general questions, use live OCR if available, otherwise web search
            if has_live_ocr and screen_score > 0.02 and should_use_ocr:
                use_ocr = True
                reasoning = "General query with live OCR available - including screen context"
            elif (web_score > 0.02 or time_score > 0.02) and should_use_web:
                use_web = True
                reasoning = "General query - using web search for comprehensive information"
                base_params = {"max_results": 3}
                web_search_params = performance_optimizer.optimize_web_search_params(query_lower, base_params)
            else:
                reasoning = "General query - using AI knowledge only"
        
        # Override decisions based on specific patterns (but respect performance limits)
        if ("help me with this" in query_lower or "what is this" in query_lower) and should_use_ocr:
            use_ocr = True
            reasoning += " (Override: demonstrative reference detected)"
        
        if any(word in query_lower for word in ["latest", "recent", "today", "news"]):
            use_web = True
            if not web_search_params:
                web_search_params = {"timelimit": "d"}
            reasoning += " (Override: time-sensitive information needed)"
        
        return ContextDecision(
            use_ocr=use_ocr,
            use_web=use_web,
            query_type=query_type,
            confidence=confidence,
            reasoning=reasoning,
            web_search_params=web_search_params
        )
    
    def get_adaptive_web_params(self, query: str, query_type: QueryType) -> Dict:
        """Get adaptive web search parameters based on query analysis."""
        params = {"max_results": 5, "safesearch": "moderate"}
        
        if query_type == QueryType.CURRENT_EVENTS:
            params.update({"timelimit": "d", "max_results": 5})
        elif query_type == QueryType.TECHNICAL_INFO:
            params.update({"max_results": 3, "timelimit": "y"})
        elif "tutorial" in query.lower() or "how to" in query.lower():
            params.update({"max_results": 3})
        elif "news" in query.lower():
            params.update({"timelimit": "w", "max_results": 5})
        
        return params


# Global smart context analyzer instance
smart_analyzer = SmartContextAnalyzer()