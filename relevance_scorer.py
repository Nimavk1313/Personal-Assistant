"""
Advanced relevance scoring system for OCR text and web search results.
Provides sophisticated algorithms to determine content relevance based on query context.
"""

import re
import math
from typing import Dict, List, Tuple, Set
from dataclasses import dataclass
from enum import Enum


class ContentType(Enum):
    """Types of content for relevance scoring."""
    OCR_TEXT = "ocr_text"
    WEB_RESULT = "web_result"
    WINDOW_INFO = "window_info"


@dataclass
class RelevanceScore:
    """Detailed relevance score with breakdown."""
    total_score: float
    keyword_score: float
    semantic_score: float
    context_score: float
    freshness_score: float
    confidence: float
    explanation: str


class RelevanceScorer:
    """Advanced relevance scoring system."""
    
    def __init__(self):
        # Enhanced keyword categories
        self.action_keywords = {
            'click', 'select', 'choose', 'press', 'tap', 'touch', 'drag', 'drop',
            'scroll', 'swipe', 'type', 'enter', 'input', 'fill', 'submit',
            'navigate', 'go', 'open', 'close', 'minimize', 'maximize'
        }
        
        self.ui_elements = {
            'button', 'menu', 'dropdown', 'checkbox', 'radio', 'slider', 'tab',
            'dialog', 'popup', 'modal', 'form', 'field', 'textbox', 'label',
            'icon', 'image', 'link', 'hyperlink', 'toolbar', 'sidebar'
        }
        
        self.screen_references = {
            'screen', 'display', 'monitor', 'window', 'application', 'app',
            'interface', 'gui', 'ui', 'visible', 'showing', 'displayed',
            'current', 'active', 'open', 'running', 'this', 'here', 'that'
        }
        
        self.information_keywords = {
            'what', 'how', 'why', 'when', 'where', 'who', 'which', 'explain',
            'describe', 'tell', 'show', 'help', 'guide', 'tutorial', 'learn',
            'understand', 'know', 'find', 'search', 'lookup', 'information'
        }
        
        self.time_sensitive = {
            'latest', 'recent', 'new', 'current', 'today', 'now', 'update',
            'breaking', 'news', 'announcement', 'release', 'fresh', 'live'
        }
        
        # Stop words to filter out
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to',
            'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be',
            'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
            'will', 'would', 'could', 'should', 'may', 'might', 'can'
        }
    
    def score_content_relevance(self, query: str, content: str, 
                              content_type: ContentType, 
                              context_info: Dict = None) -> RelevanceScore:
        """
        Calculate comprehensive relevance score for content.
        
        Args:
            query: User's query
            content: Content to score (OCR text, web result, etc.)
            content_type: Type of content being scored
            context_info: Additional context (window info, timestamps, etc.)
        
        Returns:
            RelevanceScore with detailed breakdown
        """
        if not content or not query:
            return RelevanceScore(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, "Empty content or query")
        
        query_lower = query.lower()
        content_lower = content.lower()
        
        # Calculate individual score components
        keyword_score = self._calculate_keyword_relevance(query_lower, content_lower, content_type)
        semantic_score = self._calculate_semantic_relevance(query_lower, content_lower)
        context_score = self._calculate_context_relevance(query_lower, content_lower, content_type, context_info)
        freshness_score = self._calculate_freshness_score(content_type, context_info)
        
        # Weight the scores based on content type
        weights = self._get_content_type_weights(content_type)
        
        total_score = (
            keyword_score * weights['keyword'] +
            semantic_score * weights['semantic'] +
            context_score * weights['context'] +
            freshness_score * weights['freshness']
        )
        
        # Calculate confidence based on score distribution
        confidence = self._calculate_confidence(keyword_score, semantic_score, context_score)
        
        # Generate explanation
        explanation = self._generate_explanation(
            keyword_score, semantic_score, context_score, freshness_score, content_type
        )
        
        return RelevanceScore(
            total_score=min(total_score, 1.0),
            keyword_score=keyword_score,
            semantic_score=semantic_score,
            context_score=context_score,
            freshness_score=freshness_score,
            confidence=confidence,
            explanation=explanation
        )
    
    def _calculate_keyword_relevance(self, query: str, content: str, content_type: ContentType) -> float:
        """Calculate keyword-based relevance score."""
        query_words = set(re.findall(r'\b\w+\b', query)) - self.stop_words
        content_words = set(re.findall(r'\b\w+\b', content)) - self.stop_words
        
        if not query_words:
            return 0.0
        
        # Direct keyword matches
        direct_matches = query_words.intersection(content_words)
        match_ratio = len(direct_matches) / len(query_words)
        
        # Boost for important keyword categories
        category_boost = 0.0
        if content_type == ContentType.OCR_TEXT:
            # Boost for UI and action keywords in OCR content
            ui_matches = query_words.intersection(self.ui_elements)
            action_matches = query_words.intersection(self.action_keywords)
            screen_matches = query_words.intersection(self.screen_references)
            
            if ui_matches or action_matches or screen_matches:
                category_boost = 0.3
        
        elif content_type == ContentType.WEB_RESULT:
            # Boost for information and time-sensitive keywords in web content
            info_matches = query_words.intersection(self.information_keywords)
            time_matches = query_words.intersection(self.time_sensitive)
            
            if info_matches or time_matches:
                category_boost = 0.2
        
        # Partial word matches (for typos or variations)
        partial_score = 0.0
        for query_word in query_words:
            if len(query_word) > 3:
                for content_word in content_words:
                    if query_word in content_word or content_word in query_word:
                        partial_score += 0.1
        
        partial_score = min(partial_score, 0.3)  # Cap partial matches
        
        return min(match_ratio + category_boost + partial_score, 1.0)
    
    def _calculate_semantic_relevance(self, query: str, content: str) -> float:
        """Calculate semantic relevance using simple heuristics."""
        # Look for phrase matches
        query_phrases = [phrase.strip() for phrase in query.split() if len(phrase.strip()) > 2]
        phrase_score = 0.0
        
        for phrase in query_phrases:
            if phrase in content:
                phrase_score += 0.2
        
        phrase_score = min(phrase_score, 0.6)
        
        # Look for related concepts (simple approach)
        concept_score = 0.0
        
        # Technology concepts
        tech_concepts = {
            'programming': ['code', 'coding', 'development', 'software'],
            'python': ['programming', 'script', 'language', 'code'],
            'web': ['browser', 'internet', 'online', 'website'],
            'ai': ['artificial', 'intelligence', 'machine', 'learning'],
            'save': ['file', 'document', 'storage', 'disk']
        }
        
        for concept, related_words in tech_concepts.items():
            if concept in query:
                for word in related_words:
                    if word in content:
                        concept_score += 0.1
        
        concept_score = min(concept_score, 0.4)
        
        return phrase_score + concept_score
    
    def _calculate_context_relevance(self, query: str, content: str, 
                                   content_type: ContentType, context_info: Dict) -> float:
        """Calculate context-based relevance score."""
        if not context_info:
            return 0.0
        
        context_score = 0.0
        
        # Window/application context
        if 'window_info' in context_info:
            window_info = context_info['window_info'].lower()
            
            # Extract application name
            app_match = re.search(r'active window: ([^-]+)', window_info)
            if app_match:
                app_name = app_match.group(1).strip().lower()
                
                # Boost if query mentions the application
                if app_name in query or any(word in query for word in app_name.split()):
                    context_score += 0.3
                
                # Boost if content is relevant to the application
                if app_name in content:
                    context_score += 0.2
        
        # Content type specific context
        if content_type == ContentType.OCR_TEXT:
            # OCR content is more relevant for screen-related queries
            screen_indicators = ['this', 'here', 'current', 'visible', 'showing']
            if any(indicator in query for indicator in screen_indicators):
                context_score += 0.4
        
        elif content_type == ContentType.WEB_RESULT:
            # Web content is more relevant for information queries
            info_indicators = ['what', 'how', 'why', 'latest', 'news', 'information']
            if any(indicator in query for indicator in info_indicators):
                context_score += 0.3
        
        return min(context_score, 1.0)
    
    def _calculate_freshness_score(self, content_type: ContentType, context_info: Dict) -> float:
        """Calculate freshness/recency score."""
        if content_type == ContentType.WEB_RESULT:
            # Web results get higher freshness score
            return 0.8
        elif content_type == ContentType.OCR_TEXT:
            # OCR text is always current
            return 1.0
        else:
            return 0.5
    
    def _get_content_type_weights(self, content_type: ContentType) -> Dict[str, float]:
        """Get scoring weights for different content types."""
        if content_type == ContentType.OCR_TEXT:
            return {
                'keyword': 0.4,
                'semantic': 0.2,
                'context': 0.3,
                'freshness': 0.1
            }
        elif content_type == ContentType.WEB_RESULT:
            return {
                'keyword': 0.3,
                'semantic': 0.3,
                'context': 0.2,
                'freshness': 0.2
            }
        else:
            return {
                'keyword': 0.4,
                'semantic': 0.3,
                'context': 0.2,
                'freshness': 0.1
            }
    
    def _calculate_confidence(self, keyword_score: float, semantic_score: float, context_score: float) -> float:
        """Calculate confidence in the relevance score."""
        # Higher confidence when multiple scoring methods agree
        scores = [keyword_score, semantic_score, context_score]
        non_zero_scores = [s for s in scores if s > 0.1]
        
        if len(non_zero_scores) >= 2:
            # Multiple indicators suggest higher confidence
            return min(0.9, sum(non_zero_scores) / len(non_zero_scores) + 0.2)
        elif len(non_zero_scores) == 1:
            # Single strong indicator
            return max(non_zero_scores) * 0.7
        else:
            # Low confidence
            return 0.3
    
    def _generate_explanation(self, keyword_score: float, semantic_score: float, 
                            context_score: float, freshness_score: float, 
                            content_type: ContentType) -> str:
        """Generate human-readable explanation of the score."""
        explanations = []
        
        if keyword_score > 0.5:
            explanations.append("strong keyword matches")
        elif keyword_score > 0.2:
            explanations.append("some keyword matches")
        
        if semantic_score > 0.3:
            explanations.append("semantic relevance")
        
        if context_score > 0.3:
            explanations.append("contextual relevance")
        
        if freshness_score > 0.7:
            explanations.append("current information")
        
        if not explanations:
            return f"Low relevance for {content_type.value}"
        
        return f"Relevant due to: {', '.join(explanations)}"


# Global instance
relevance_scorer = RelevanceScorer()