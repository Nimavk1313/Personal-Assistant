"""
AI Thinking Engine - Analyzes context and performs intelligent research.
""" 
import re
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import json

from models import ChatRequest, AssistantConfig
from web_search import web_searcher
from smart_context_analyzer import smart_analyzer


@dataclass
class ThinkingStep:
    """Represents a step in the thinking process."""
    step_type: str  # "analysis", "search", "synthesis"
    description: str
    content: str
    timestamp: datetime
    duration_ms: int = 0


@dataclass
class ThinkingResult:
    """Result of the thinking process."""
    steps: List[ThinkingStep]
    search_queries: List[str]
    search_results: str
    context_analysis: str
    key_insights: List[str]
    total_duration_ms: int


class ThinkingEngine:
    """Intelligent thinking engine that analyzes context and performs research."""
    
    def __init__(self, config: AssistantConfig):
        self.config = config
        self.thinking_enabled = getattr(config, 'enable_thinking', True)
        self.max_search_queries = getattr(config, 'max_thinking_searches', 3)
        self.thinking_timeout = getattr(config, 'thinking_timeout_seconds', 30)
    
    async def think(self, request: ChatRequest, screen_text: str = "", window_info: str = "", 
                   existing_web_results: str = "") -> ThinkingResult:
        """
        Perform intelligent thinking process:
        1. Analyze OCR content and context
        2. Generate relevant search queries
        3. Perform web searches
        4. Synthesize findings
        """
        if not self.thinking_enabled:
            return ThinkingResult([], [], existing_web_results, "", [], 0)
        
        start_time = datetime.now()
        steps = []
        
        try:
            # Step 1: Analyze OCR content and context
            analysis_step = await self._analyze_context(request, screen_text, window_info)
            steps.append(analysis_step)
            
            # Step 2: Generate search queries based on analysis
            query_step = await self._generate_search_queries(request, analysis_step.content, screen_text)
            steps.append(query_step)
            
            # Extract queries from the step
            search_queries = self._extract_queries_from_step(query_step.content)
            
            # Step 3: Perform intelligent web searches
            search_step = await self._perform_searches(search_queries, existing_web_results)
            steps.append(search_step)
            
            # Step 4: Synthesize insights
            synthesis_step = await self._synthesize_insights(request, analysis_step.content, search_step.content)
            steps.append(synthesis_step)
            
            # Extract key insights
            key_insights = self._extract_insights(synthesis_step.content)
            
            total_duration = int((datetime.now() - start_time).total_seconds() * 1000)
            
            return ThinkingResult(
                steps=steps,
                search_queries=search_queries,
                search_results=search_step.content,
                context_analysis=analysis_step.content,
                key_insights=key_insights,
                total_duration_ms=total_duration
            )
            
        except Exception as e:
            # If thinking fails, return minimal result
            error_step = ThinkingStep(
                step_type="error",
                description="Thinking process encountered an error",
                content=f"Error: {str(e)}",
                timestamp=datetime.now()
            )
            steps.append(error_step)
            
            total_duration = int((datetime.now() - start_time).total_seconds() * 1000)
            return ThinkingResult(steps, [], existing_web_results, "", [], total_duration)
    
    async def _analyze_context(self, request: ChatRequest, screen_text: str, window_info: str) -> ThinkingStep:
        """Perform comprehensive analysis of OCR content, context, and user intent."""
        step_start = datetime.now()
        
        # Add initial processing delay for thorough analysis
        await asyncio.sleep(1.2)
        
        analysis_parts = []
        
        # Deep analysis of user message
        user_message = request.message
        analysis_parts.append(f"User Message Deep Analysis:")
        analysis_parts.append(f"- Length: {len(user_message)} characters")
        analysis_parts.append(f"- Word count: {len(user_message.split())} words")
        analysis_parts.append(f"- Content type: {'Question' if '?' in user_message else 'Statement/Request'}")
        
        # Intent detection with processing delay
        await asyncio.sleep(0.8)
        
        intent_keywords = {
            'information_seeking': ['what', 'how', 'why', 'when', 'where', 'who', 'explain', 'tell me'],
            'problem_solving': ['help', 'fix', 'solve', 'issue', 'problem', 'error', 'debug'],
            'comparison': ['compare', 'vs', 'versus', 'difference', 'better', 'best'],
            'tutorial': ['tutorial', 'guide', 'step by step', 'how to', 'learn'],
            'analysis': ['analyze', 'review', 'evaluate', 'assess', 'examine']
        }
        
        detected_intents = []
        for intent, keywords in intent_keywords.items():
            if any(keyword in user_message.lower() for keyword in keywords):
                detected_intents.append(intent)
        
        analysis_parts.append(f"- Detected intents: {', '.join(detected_intents) if detected_intents else 'General inquiry'}")
        
        # Enhanced OCR and visual context analysis
        await asyncio.sleep(0.6)
        
        if screen_text and len(screen_text.strip()) > 10:
            # Comprehensive screen content analysis
            analysis_result = smart_analyzer.analyze_content(
                screen_text, 
                request.message, 
                window_info
            )
            
            analysis_parts.append(f"\nComprehensive OCR Content Analysis:")
            analysis_parts.append(f"- Content Type: {analysis_result.get('content_type', 'Unknown')}")
            analysis_parts.append(f"- Key Elements: {', '.join(analysis_result.get('key_elements', []))}")
            analysis_parts.append(f"- Context: {analysis_result.get('context_summary', 'No specific context detected')}")
            analysis_parts.append(f"- Relevance Score: {analysis_result.get('relevance_score', 0)}/10")
            
            # Advanced text pattern analysis
            technical_terms = len([word for word in screen_text.split() if word[0].isupper() and len(word) > 3])
            numbers_found = len([word for word in screen_text.split() if any(char.isdigit() for char in word)])
            
            analysis_parts.append(f"- Technical terms detected: {technical_terms}")
            analysis_parts.append(f"- Numerical data points: {numbers_found}")
            analysis_parts.append(f"- Text complexity: {'High' if len(screen_text) > 500 else 'Medium' if len(screen_text) > 100 else 'Low'}")
            
            analysis_parts.append(f"\nScreen Text Preview: {screen_text[:200]}{'...' if len(screen_text) > 200 else ''}")
            analysis_parts.append(f"Window Information: {window_info}")
        else:
            analysis_parts.append(f"\nVisual Context Analysis:")
            analysis_parts.append(f"- No significant OCR content detected")
            analysis_parts.append(f"- Window: {window_info}")
            analysis_parts.append(f"- Analysis: General query without specific visual context")
        
        # Conversation history analysis
        await asyncio.sleep(0.5)
        
        if hasattr(request, 'conversation_history') and request.conversation_history:
            history_length = len(request.conversation_history)
            analysis_parts.append(f"\nConversation Context Analysis:")
            analysis_parts.append(f"- History length: {history_length} messages")
            
            recent_messages = request.conversation_history[-3:] if history_length > 3 else request.conversation_history
            topics = []
            for msg in recent_messages:
                if len(msg.get('content', '')) > 20:
                    topics.append(msg.get('content', '')[:50] + "...")
            
            if topics:
                analysis_parts.append(f"- Recent topics: {'; '.join(topics)}")
        else:
            analysis_parts.append(f"\nConversation Context: Fresh conversation start")
        
        # Advanced complexity assessment
        complexity_indicators = ['explain in detail', 'comprehensive', 'thorough', 'complete guide', 'everything about']
        complexity_score = sum(1 for indicator in complexity_indicators if indicator in user_message.lower())
        
        analysis_parts.append(f"\nAdvanced Complexity Assessment:")
        analysis_parts.append(f"- Complexity score: {complexity_score + len(detected_intents)}/10")
        analysis_parts.append(f"- Research required: {'Yes - High complexity detected' if complexity_score > 0 or len(detected_intents) > 2 else 'Maybe - Context dependent'}")
        
        context_analysis = "\n".join(analysis_parts)
        
        duration = int((datetime.now() - step_start).total_seconds() * 1000)
        
        return ThinkingStep(
            step_type="analysis",
            description="Comprehensive OCR, context, and intent analysis with complexity assessment",
            content=context_analysis,
            timestamp=step_start,
            duration_ms=duration
        )
    
    async def _generate_search_queries(self, request: ChatRequest, context_analysis: str, screen_text: str) -> ThinkingStep:
        """Generate comprehensive and targeted search queries based on deep analysis."""
        step_start = datetime.now()
        
        # Add processing delay for thorough query generation
        await asyncio.sleep(1.0)
        
        query_candidates = []
        user_message = request.message.lower()
        
        # Advanced key term extraction with filtering
        stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'}
        
        # Extract meaningful terms from user message
        user_words = re.findall(r'\b\w{3,}\b', user_message)
        key_terms = [word for word in user_words if word not in stop_words]
        technical_terms = []
        action_words = []
        
        for word in key_terms:
            # Identify technical terms
            if any(tech in word for tech in ['code', 'program', 'software', 'api', 'framework', 'library', 'algorithm', 'database']):
                technical_terms.append(word)
            
            # Identify action words
            if any(action in word for action in ['create', 'build', 'make', 'develop', 'design', 'implement', 'fix', 'solve', 'debug', 'optimize']):
                action_words.append(word)
        
        # From OCR content (if available)
        if screen_text:
            # Extract potential technical terms, names, numbers
            ocr_technical = re.findall(r'\b[A-Z][a-z]+(?:[A-Z][a-z]+)*\b', screen_text)  # CamelCase
            numbers_with_context = re.findall(r'\b\d+(?:\.\d+)?\s*[a-zA-Z]+\b', screen_text)  # Numbers with units
            quoted_terms = re.findall(r'"([^"]+)"', screen_text)  # Quoted terms
            
            technical_terms.extend(ocr_technical[:5])
            query_candidates.extend(numbers_with_context[:3])
            query_candidates.extend(quoted_terms[:3])
        
        # Processing delay for query strategy planning
        await asyncio.sleep(0.6)
        
        # Generate comprehensive search queries
        search_queries = []
        
        # Primary query: Direct user question
        if len(request.message.strip()) > 5:
            search_queries.append(request.message.strip())
        
        # Intent-based query generation with enhanced patterns
        intent_patterns = {
            'how_to': ['how to', 'how do', 'how can', 'how should'],
            'what_is': ['what is', 'what are', 'what does', 'define'],
            'why': ['why', 'reason', 'because', 'explanation'],
            'best_practices': ['best', 'top', 'recommend', 'optimal', 'ideal'],
            'comparison': ['vs', 'versus', 'compare', 'difference', 'better'],
            'troubleshooting': ['error', 'problem', 'issue', 'fix', 'debug', 'solve'],
            'tutorial': ['tutorial', 'guide', 'learn', 'step by step', 'course'],
            'current': ['latest', 'new', 'recent', 'current', '2024', 'updated']
        }
        
        detected_intents = []
        for intent, patterns in intent_patterns.items():
            if any(pattern in user_message for pattern in patterns):
                detected_intents.append(intent)
        
        # Generate intent-specific queries
        for intent in detected_intents[:3]:  # Limit to top 3 intents
            if intent == 'how_to' and key_terms:
                search_queries.append(f"how to {' '.join(key_terms[:3])} tutorial")
            elif intent == 'what_is' and key_terms:
                search_queries.append(f"what is {' '.join(key_terms[:3])} explanation")
            elif intent == 'best_practices' and key_terms:
                search_queries.append(f"best {' '.join(key_terms[:3])} practices")
            elif intent == 'troubleshooting' and key_terms:
                search_queries.append(f"{' '.join(key_terms[:3])} error fix solution")
            elif intent == 'current' and key_terms:
                search_queries.append(f"latest {' '.join(key_terms[:3])} 2024")
        
        # Technical-specific queries
        if technical_terms:
            search_queries.append(f"{' '.join(technical_terms[:2])} documentation examples")
        
        # Context-enhanced queries from OCR analysis
        if "OCR Content Analysis" in context_analysis or "Comprehensive OCR Content Analysis" in context_analysis:
            if key_terms:
                search_queries.append(f"{' '.join(key_terms[:3])} visual interface tutorial")
        
        # Secondary queries: Context-specific
        if query_candidates and key_terms:
            # Combine user intent with key terms
            combined_terms = list(set(key_terms + query_candidates))[:3]
            for term in combined_terms:
                if len(term) > 2:
                    contextual_query = f"{term} {key_terms[0] if key_terms else 'information'}"
                    search_queries.append(contextual_query)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_queries = []
        for query in search_queries:
            if query not in seen and len(query.strip()) > 5:
                seen.add(query)
                unique_queries.append(query)
        
        # Limit to max queries
        final_queries = unique_queries[:self.max_search_queries]
        
        # Enhanced query analysis
        query_analysis = []
        query_analysis.append(f"Generated {len(final_queries)} comprehensive search queries:")
        
        for i, query in enumerate(final_queries):
            query_type = "General"
            if "how to" in query:
                query_type = "Instructional"
            elif "what is" in query:
                query_type = "Definitional"
            elif "best" in query or "top" in query:
                query_type = "Recommendation"
            elif "error" in query or "fix" in query:
                query_type = "Troubleshooting"
            elif "latest" in query or "2024" in query:
                query_type = "Current Information"
            elif "tutorial" in query or "guide" in query:
                query_type = "Educational"
            
            query_analysis.append(f"{i+1}. [{query_type}] {query}")
        
        query_analysis.append(f"\nQuery Strategy Analysis:")
        query_analysis.append(f"- Detected intents: {', '.join(detected_intents) if detected_intents else 'General inquiry'}")
        query_analysis.append(f"- Technical terms: {len(technical_terms)} identified")
        query_analysis.append(f"- Action words: {len(action_words)} identified")
        query_analysis.append(f"- Coverage approach: Multi-angle comprehensive search")
        
        query_content = "\n".join(query_analysis)
        
        duration = int((datetime.now() - step_start).total_seconds() * 1000)
        
        return ThinkingStep(
            step_type="search",
            description=f"Advanced generation of {len(final_queries)} targeted search queries with intent analysis",
            content=query_content,
            timestamp=step_start,
            duration_ms=duration
        )
    
    async def _perform_searches(self, search_queries: List[str], existing_results: str) -> ThinkingStep:
        """Perform comprehensive web searches with thorough analysis."""
        step_start = datetime.now()
        
        if not search_queries:
            return ThinkingStep(
                step_type="search",
                description="No search queries generated",
                content=existing_results or "No search performed",
                timestamp=step_start,
                duration_ms=0
            )
        
        all_results = []
        if existing_results:
            all_results.append(f"Existing Results:\n{existing_results}\n")
        
        # Add deliberate processing time for thorough analysis
        await asyncio.sleep(1)  # Initial analysis delay
        
        # Perform comprehensive searches with increased depth
        max_results_per_query = min(5, self.max_search_queries * 2)  # More results per query
        
        for i, query in enumerate(search_queries):
            try:
                # Add processing delay between searches for thoroughness
                if i > 0:
                    await asyncio.sleep(0.8)  # Delay between searches
                
                # Perform multiple search variations for comprehensive coverage
                base_result = web_searcher.search(query, max_results=max_results_per_query)
                
                # Try related searches for deeper insights
                related_queries = self._generate_related_queries(query)
                
                search_summary = f"Query {i+1}: {query}\n"
                if base_result and base_result.results:
                    search_summary += f"Found {len(base_result.results)} primary results\n"
                    for j, result in enumerate(base_result.results[:3]):  # Top 3 results
                        search_summary += f"  {j+1}. {result.title}\n     {result.body[:200]}...\n"
                    
                    # Perform related searches for additional context
                    for related_query in related_queries[:2]:  # Limit to 2 related searches
                        await asyncio.sleep(0.5)  # Processing delay
                        related_result = web_searcher.search(related_query, max_results=2)
                        if related_result and related_result.results:
                            search_summary += f"\n  Related search: {related_query}\n"
                            search_summary += f"    {related_result.results[0].title}\n"
                            search_summary += f"    {related_result.results[0].body[:150]}...\n"
                else:
                    search_summary += "No results found\n"
                
                all_results.append(search_summary)
                
            except Exception as e:
                all_results.append(f"Query {i+1}: {query}\nError: {str(e)}\n")
        
        # Final processing delay for result compilation
        await asyncio.sleep(0.5)
        
        search_content = "\n".join(all_results) if all_results else "No search results obtained"
        
        duration = int((datetime.now() - step_start).total_seconds() * 1000)
        
        return ThinkingStep(
            step_type="search",
            description=f"Comprehensive web research across {len(search_queries)} primary queries with related searches",
            content=search_content,
            timestamp=step_start,
            duration_ms=duration
        )
    
    def _generate_related_queries(self, base_query: str) -> List[str]:
        """Generate related search queries for deeper research."""
        related = []
        
        # Add contextual variations
        if "how to" not in base_query.lower():
            related.append(f"how to {base_query}")
        if "what is" not in base_query.lower():
            related.append(f"what is {base_query}")
        if "best" not in base_query.lower():
            related.append(f"best {base_query}")
        if "tutorial" not in base_query.lower():
            related.append(f"{base_query} tutorial")
        
        return related[:3]  # Limit to 3 related queries
    
    async def _synthesize_insights(self, request: ChatRequest, context_analysis: str, search_results: str) -> ThinkingStep:
        """Perform comprehensive synthesis of insights from context analysis and search results."""
        step_start = datetime.now()
        
        # Add processing delay for thorough synthesis
        await asyncio.sleep(1.5)
        
        insights = []
        confidence_scores = {}
        
        # Deep analysis of context relevance
        await asyncio.sleep(0.7)
        
        if "OCR Content Analysis" in context_analysis or "Comprehensive OCR Content Analysis" in context_analysis:
            insights.append("Visual context available - can provide screen-specific assistance")
            confidence_scores['visual_context'] = 9
            
            # Analyze OCR content quality
            if "Technical terms detected:" in context_analysis:
                insights.append("Technical content detected - specialized knowledge may be required")
                confidence_scores['technical_complexity'] = 8
            
            if "High" in context_analysis and "complexity" in context_analysis:
                insights.append("Complex visual content - detailed analysis recommended")
                confidence_scores['content_complexity'] = 8
        else:
            confidence_scores['visual_context'] = 3
        
        # Advanced search result quality analysis
        await asyncio.sleep(0.8)
        
        if search_results and len(search_results) > 100:
            insights.append("Comprehensive web search results obtained")
            confidence_scores['search_quality'] = 8
            
            # Pattern analysis with confidence scoring
            content_patterns = {
                'instructional': ['tutorial', 'guide', 'how to', 'step by step', 'instructions'],
                'troubleshooting': ['error', 'problem', 'issue', 'fix', 'solve', 'debug'],
                'current_info': ['latest', '2024', '2023', 'recent', 'new', 'updated'],
                'technical': ['code', 'programming', 'software', 'API', 'framework'],
                'comparative': ['vs', 'versus', 'compare', 'comparison', 'better', 'best']
            }
            
            detected_patterns = []
            for pattern_type, keywords in content_patterns.items():
                matches = sum(1 for term in keywords if term in search_results.lower())
                if matches > 0:
                    detected_patterns.append(f"{pattern_type} ({matches} matches)")
                    
                    if pattern_type == 'instructional' and matches >= 3:
                        insights.append("Strong instructional content found - can provide detailed step-by-step guidance")
                        confidence_scores['instructional_quality'] = 9
                    elif pattern_type == 'troubleshooting' and matches >= 2:
                        insights.append("Problem-solving information available with multiple solution approaches")
                        confidence_scores['problem_solving'] = 8
                    elif pattern_type == 'current_info' and matches >= 2:
                        insights.append("Recent/current information available - responses will be up-to-date")
                        confidence_scores['currency'] = 9
            
            if detected_patterns:
                insights.append(f"Content patterns detected: {', '.join(detected_patterns)}")
        else:
            confidence_scores['search_quality'] = 4
            insights.append("Limited search results - may need to rely more on general knowledge")
        
        # Enhanced user intent analysis
        await asyncio.sleep(0.6)
        
        intent_analysis = {
            'information_seeking': ['how', 'what', 'why', 'when', 'where', 'who', 'explain'],
            'problem_solving': ['help', 'fix', 'solve', 'problem', 'issue', 'error', 'debug'],
            'creation_task': ['create', 'make', 'build', 'generate', 'develop', 'design'],
            'comparison': ['compare', 'vs', 'versus', 'difference', 'better', 'best'],
            'learning': ['learn', 'understand', 'tutorial', 'guide', 'teach me']
        }
        
        detected_intents = []
        primary_intent = "general_inquiry"
        intent_confidence = 5
        
        for intent, keywords in intent_analysis.items():
            matches = sum(1 for keyword in keywords if keyword in request.message.lower())
            if matches > 0:
                detected_intents.append(f"{intent} (confidence: {min(matches * 2, 10)}/10)")
                if matches > intent_confidence:
                    primary_intent = intent
                    intent_confidence = matches
        
        if detected_intents:
            insights.append(f"Multiple user intents detected: {', '.join(detected_intents)}")
        
        confidence_scores['intent_clarity'] = min(intent_confidence * 2, 10)
        
        # Conversation continuity analysis
        if "Conversation Context Analysis:" in context_analysis:
            insights.append("Conversation context available - can maintain continuity")
            confidence_scores['context_continuity'] = 7
        
        # Overall confidence assessment
        overall_confidence = sum(confidence_scores.values()) / len(confidence_scores) if confidence_scores else 5
        
        # Response strategy determination
        await asyncio.sleep(0.4)
        
        response_strategies = []
        if confidence_scores.get('visual_context', 0) > 7:
            response_strategies.append("Leverage visual context for specific guidance")
        if confidence_scores.get('search_quality', 0) > 7:
            response_strategies.append("Integrate comprehensive web research findings")
        if confidence_scores.get('instructional_quality', 0) > 7:
            response_strategies.append("Provide detailed step-by-step instructions")
        if confidence_scores.get('problem_solving', 0) > 7:
            response_strategies.append("Focus on practical problem-solving approaches")
        
        synthesis_content = f"""
Comprehensive Insight Synthesis:
- Primary User Intent: {primary_intent} (confidence: {intent_confidence * 2}/10)
- Visual Context Quality: {'High' if confidence_scores.get('visual_context', 0) > 7 else 'Medium' if confidence_scores.get('visual_context', 0) > 4 else 'Low'}
- Search Coverage Quality: {'Comprehensive' if confidence_scores.get('search_quality', 0) > 7 else 'Moderate' if confidence_scores.get('search_quality', 0) > 4 else 'Limited'}
- Overall Confidence Score: {overall_confidence:.1f}/10

Detailed Insights:
{chr(10).join([f"• {insight}" for insight in insights])}

Confidence Breakdown:
{chr(10).join([f"- {key.replace('_', ' ').title()}: {score}/10" for key, score in confidence_scores.items()])}

Optimal Response Strategy:
{chr(10).join([f"• {strategy}" for strategy in response_strategies]) if response_strategies else '• Provide balanced general assistance'}

Recommended Response Approach:
- Combine visual context with web research findings
- Prioritize actionable, specific information
- Maintain appropriate confidence level based on available data
- Provide contextual guidance tailored to detected user intent
"""
        
        duration = int((datetime.now() - step_start).total_seconds() * 1000)
        
        return ThinkingStep(
            step_type="synthesis",
            description="Comprehensive insight synthesis with confidence assessment and strategy optimization",
            content=synthesis_content,
            timestamp=step_start,
            duration_ms=duration
        )
    
    def _extract_queries_from_step(self, step_content: str) -> List[str]:
        """Extract search queries from the query generation step."""
        queries = []
        lines = step_content.split('\n')
        
        for line in lines:
            # Look for numbered queries
            match = re.match(r'\d+\.\s*(.+)', line.strip())
            if match:
                queries.append(match.group(1).strip())
        
        return queries
    
    def _extract_insights(self, synthesis_content: str) -> List[str]:
        """Extract key insights from synthesis step."""
        insights = []
        lines = synthesis_content.split('\n')
        
        in_insights_section = False
        for line in lines:
            if "Key Insights:" in line:
                in_insights_section = True
                continue
            elif in_insights_section and line.strip().startswith('•'):
                insights.append(line.strip()[1:].strip())
            elif in_insights_section and line.strip() and not line.startswith(' '):
                break
        
        return insights


# Global thinking engine instance
thinking_engine = None

def get_thinking_engine(config: AssistantConfig) -> ThinkingEngine:
    """Get or create thinking engine instance."""
    global thinking_engine
    if thinking_engine is None:
        thinking_engine = ThinkingEngine(config)
    return thinking_engine