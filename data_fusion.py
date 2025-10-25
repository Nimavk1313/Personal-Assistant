"""
Intelligent data fusion module for combining OCR and web search results.
Provides smart context integration based on relevance and query type.
"""

import re
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
from relevance_scorer import relevance_scorer, ContentType


class RelevanceLevel(Enum):
    """Relevance levels for context data."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    IRRELEVANT = "irrelevant"


@dataclass
class ContextRelevance:
    """Represents relevance scoring for context data."""
    level: RelevanceLevel
    score: float  # 0.0 to 1.0
    reasoning: str
    key_matches: List[str]


@dataclass
class FusedContext:
    """Represents intelligently fused context data."""
    primary_context: str
    supporting_context: str
    relevance_summary: str
    fusion_strategy: str


class DataFusion:
    """Handles intelligent fusion of OCR and web search data."""
    
    def __init__(self):
        # Keywords that indicate screen-related queries
        self.screen_keywords = {
            'screen', 'display', 'window', 'button', 'click', 'interface', 'ui', 'menu',
            'dialog', 'form', 'text', 'image', 'icon', 'tab', 'page', 'website',
            'application', 'app', 'software', 'program', 'browser', 'document'
        }
        
        # Keywords that indicate web search relevance
        self.web_keywords = {
            'latest', 'recent', 'news', 'current', 'today', 'now', 'update', 'new',
            'price', 'cost', 'buy', 'purchase', 'review', 'compare', 'best',
            'how to', 'tutorial', 'guide', 'learn', 'explain', 'definition',
            'weather', 'stock', 'market', 'event', 'schedule', 'time'
        }
    
    def analyze_relevance(self, query: str, context_data: str, context_type: str, 
                          context_info: Dict = None) -> ContextRelevance:
        """Analyze relevance of context data to the query using advanced scoring."""
        if not context_data or not context_data.strip():
            return ContextRelevance(
                level=RelevanceLevel.IRRELEVANT,
                score=0.0,
                reasoning="No context data available",
                key_matches=[]
            )
        
        # Map context type to ContentType enum
        content_type_map = {
            "screen": ContentType.OCR_TEXT,
            "web": ContentType.WEB_RESULT,
            "window": ContentType.WINDOW_INFO
        }
        
        content_type = content_type_map.get(context_type, ContentType.OCR_TEXT)
        
        # Use advanced relevance scorer
        score_result = relevance_scorer.score_content_relevance(
            query=query,
            content=context_data,
            content_type=content_type,
            context_info=context_info or {}
        )
        
        # Map score to relevance level
        if score_result.total_score >= 0.7:
            level = RelevanceLevel.HIGH
        elif score_result.total_score >= 0.4:
            level = RelevanceLevel.MEDIUM
        elif score_result.total_score >= 0.2:
            level = RelevanceLevel.LOW
        else:
            level = RelevanceLevel.IRRELEVANT
        
        # Enhanced reasoning with score breakdown
        reasoning = (f"{score_result.explanation} "
                    f"(Total: {score_result.total_score:.2f}, "
                    f"Keywords: {score_result.keyword_score:.2f}, "
                    f"Semantic: {score_result.semantic_score:.2f}, "
                    f"Context: {score_result.context_score:.2f}, "
                    f"Confidence: {score_result.confidence:.2f})")
        
        return ContextRelevance(
             level=level,
             score=score_result.total_score,
             reasoning=reasoning,
             key_matches=[]  # Could be extracted from the scorer if needed
         )
    
    def _generate_relevance_reasoning(
        self, 
        level: RelevanceLevel, 
        score: float, 
        matches: set, 
        context_type: str,
        query_terms: set
    ) -> str:
        """Generate human-readable reasoning for relevance scoring."""
        if level == RelevanceLevel.IRRELEVANT:
            return f"No significant overlap between query and {context_type} context"
        
        match_count = len(matches)
        if match_count > 0:
            match_text = f"Found {match_count} matching terms: {', '.join(list(matches)[:3])}"
            if match_count > 3:
                match_text += "..."
        else:
            match_text = "No direct term matches"
        
        context_relevance = ""
        if context_type == "screen":
            screen_terms = query_terms.intersection(self.screen_keywords)
            if screen_terms:
                context_relevance = f", query contains screen-related terms: {', '.join(list(screen_terms)[:2])}"
        elif context_type == "web":
            web_terms = query_terms.intersection(self.web_keywords)
            if web_terms:
                context_relevance = f", query contains web-search terms: {', '.join(list(web_terms)[:2])}"
        
        return f"{match_text}{context_relevance} (score: {score:.2f})"
    
    def fuse_contexts(
        self, 
        query: str, 
        screen_text: str = "", 
        web_results: str = "", 
        window_info: str = ""
    ) -> FusedContext:
        """Intelligently fuse multiple context sources based on relevance."""
        
        # Prepare context info for advanced scoring
        context_info = {"window_info": window_info} if window_info else {}
        
        # Analyze relevance of each context source
        screen_relevance = self.analyze_relevance(query, screen_text, "screen", context_info)
        web_relevance = self.analyze_relevance(query, web_results, "web", context_info)
        window_relevance = self.analyze_relevance(query, window_info, "window", context_info)
        
        # Determine primary and supporting contexts
        contexts = [
            ("screen", screen_text, screen_relevance),
            ("web", web_results, web_relevance),
            ("window", window_info, window_relevance)
        ]
        
        # Sort by relevance score
        contexts.sort(key=lambda x: x[2].score, reverse=True)
        
        # Build fused context
        primary_context = ""
        supporting_context = ""
        fusion_strategy = ""
        
        high_relevance_contexts = [ctx for ctx in contexts if ctx[2].level == RelevanceLevel.HIGH]
        medium_relevance_contexts = [ctx for ctx in contexts if ctx[2].level == RelevanceLevel.MEDIUM]
        
        if high_relevance_contexts:
            # Use highest relevance as primary
            primary_type, primary_data, primary_rel = high_relevance_contexts[0]
            primary_context = self._format_context(primary_type, primary_data)
            
            # Add other high relevance as supporting
            for ctx_type, ctx_data, ctx_rel in high_relevance_contexts[1:]:
                if supporting_context:
                    supporting_context += "\n\n"
                supporting_context += self._format_context(ctx_type, ctx_data)
            
            # Add medium relevance as supporting if space allows
            for ctx_type, ctx_data, ctx_rel in medium_relevance_contexts[:1]:
                if supporting_context:
                    supporting_context += "\n\n"
                supporting_context += self._format_context(ctx_type, ctx_data, brief=True)
            
            fusion_strategy = f"Primary: {primary_type} (high relevance), Supporting: {len(high_relevance_contexts)-1 + min(1, len(medium_relevance_contexts))} sources"
            
        elif medium_relevance_contexts:
            # Use medium relevance contexts
            primary_type, primary_data, primary_rel = medium_relevance_contexts[0]
            primary_context = self._format_context(primary_type, primary_data)
            
            for ctx_type, ctx_data, ctx_rel in medium_relevance_contexts[1:2]:
                if supporting_context:
                    supporting_context += "\n\n"
                supporting_context += self._format_context(ctx_type, ctx_data, brief=True)
            
            fusion_strategy = f"Primary: {primary_type} (medium relevance), Supporting: {min(1, len(medium_relevance_contexts)-1)} sources"
            
        else:
            # Low relevance - provide minimal context
            if contexts and contexts[0][2].level != RelevanceLevel.IRRELEVANT:
                primary_type, primary_data, primary_rel = contexts[0]
                primary_context = self._format_context(primary_type, primary_data, brief=True)
                fusion_strategy = f"Limited context: {primary_type} (low relevance)"
            else:
                primary_context = "No relevant context available for this query."
                fusion_strategy = "No context fusion - insufficient relevance"
        
        # Generate relevance summary
        relevance_summary = self._generate_relevance_summary([ctx[2] for ctx in contexts])
        
        return FusedContext(
            primary_context=primary_context,
            supporting_context=supporting_context,
            relevance_summary=relevance_summary,
            fusion_strategy=fusion_strategy
        )
    
    def _format_context(self, context_type: str, context_data: str, brief: bool = False) -> str:
        """Format context data for presentation."""
        if not context_data or not context_data.strip():
            return ""
        
        if context_type == "screen":
            header = "Screen Content (OCR):"
            if brief:
                content = context_data[:500] + ("..." if len(context_data) > 500 else "")
            else:
                content = context_data[:1500] + ("..." if len(context_data) > 1500 else "")
        elif context_type == "web":
            header = "Web Search Results:"
            if brief:
                content = context_data[:600] + ("..." if len(context_data) > 600 else "")
            else:
                content = context_data[:2000] + ("..." if len(context_data) > 2000 else "")
        elif context_type == "window":
            header = "Active Window:"
            content = context_data  # Window info is usually brief
        else:
            header = f"{context_type.title()} Context:"
            content = context_data[:1000] + ("..." if len(context_data) > 1000 else "")
        
        return f"{header}\n{content}"
    
    def _generate_relevance_summary(self, relevances: List[ContextRelevance]) -> str:
        """Generate a summary of context relevance analysis."""
        if not relevances:
            return "No context sources analyzed"
        
        high_count = sum(1 for r in relevances if r.level == RelevanceLevel.HIGH)
        medium_count = sum(1 for r in relevances if r.level == RelevanceLevel.MEDIUM)
        low_count = sum(1 for r in relevances if r.level == RelevanceLevel.LOW)
        
        summary_parts = []
        if high_count > 0:
            summary_parts.append(f"{high_count} high-relevance")
        if medium_count > 0:
            summary_parts.append(f"{medium_count} medium-relevance")
        if low_count > 0:
            summary_parts.append(f"{low_count} low-relevance")
        
        if summary_parts:
            return f"Context analysis: {', '.join(summary_parts)} sources"
        else:
            return "Context analysis: No relevant sources found"


# Global instance
data_fusion = DataFusion()