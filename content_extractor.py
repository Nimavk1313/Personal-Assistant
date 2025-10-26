"""
Enhanced Content Extractor for Smart Assistant
Intelligently analyzes OCR content to extract key information and generate focused responses.
"""

import re
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
from enum import Enum
import json

class ContentType(Enum):
    """Types of content that can be extracted from OCR"""
    CODE = "code"
    ERROR_MESSAGE = "error_message"
    UI_ELEMENT = "ui_element"
    TEXT_DOCUMENT = "text_document"
    FORM_DATA = "form_data"
    TECHNICAL_INFO = "technical_info"
    NUMBERS_DATA = "numbers_data"
    URL_LINK = "url_link"
    EMAIL = "email"
    PHONE = "phone"
    DATE_TIME = "date_time"
    UNKNOWN = "unknown"

@dataclass
class ExtractedEntity:
    """Represents an extracted entity from OCR content"""
    type: ContentType
    value: str
    confidence: float
    context: str
    position: Optional[Tuple[int, int]] = None

@dataclass
class ContentAnalysis:
    """Complete analysis of OCR content"""
    primary_content_type: ContentType
    entities: List[ExtractedEntity]
    key_phrases: List[str]
    technical_terms: List[str]
    actionable_items: List[str]
    search_keywords: List[str]
    confidence_score: float
    summary: str

class ContentExtractor:
    """Enhanced content extractor for precise OCR analysis"""
    
    def __init__(self):
        self.code_patterns = [
            r'def\s+\w+\s*\(',  # Python functions
            r'function\s+\w+\s*\(',  # JavaScript functions
            r'class\s+\w+',  # Class definitions
            r'import\s+\w+',  # Import statements
            r'from\s+\w+\s+import',  # Python imports
            r'#include\s*<\w+>',  # C/C++ includes
            r'public\s+class\s+\w+',  # Java classes
            r'console\.log\(',  # JavaScript console
            r'print\s*\(',  # Print statements
            r'SELECT\s+.*FROM',  # SQL queries
            r'git\s+\w+',  # Git commands
            r'npm\s+\w+',  # NPM commands
            r'pip\s+install',  # Pip commands
        ]
        
        self.error_patterns = [
            r'Error:\s*.*',
            r'Exception:\s*.*',
            r'Traceback\s*\(.*\)',
            r'SyntaxError:\s*.*',
            r'TypeError:\s*.*',
            r'ValueError:\s*.*',
            r'AttributeError:\s*.*',
            r'ModuleNotFoundError:\s*.*',
            r'FileNotFoundError:\s*.*',
            r'Failed to\s+.*',
            r'Cannot\s+.*',
            r'Unable to\s+.*',
            r'404\s+Not Found',
            r'500\s+Internal Server Error',
            r'Access Denied',
            r'Permission denied',
        ]
        
        self.ui_patterns = [
            r'Button:\s*.*',
            r'Click\s+.*',
            r'Submit',
            r'Cancel',
            r'OK',
            r'Apply',
            r'Save',
            r'Delete',
            r'Edit',
            r'Add',
            r'Remove',
            r'Settings',
            r'Options',
            r'Preferences',
            r'Menu',
            r'Tab:\s*.*',
            r'Window:\s*.*',
            r'Dialog:\s*.*',
        ]
        
        self.technical_terms = {
            'programming': ['function', 'variable', 'class', 'method', 'object', 'array', 'string', 'integer', 'boolean', 'loop', 'condition', 'algorithm', 'database', 'API', 'framework', 'library', 'module', 'package'],
            'web': ['HTML', 'CSS', 'JavaScript', 'React', 'Vue', 'Angular', 'Node.js', 'Express', 'MongoDB', 'SQL', 'REST', 'GraphQL', 'JSON', 'XML', 'HTTP', 'HTTPS', 'URL', 'domain'],
            'system': ['CPU', 'RAM', 'memory', 'disk', 'process', 'thread', 'kernel', 'driver', 'registry', 'service', 'daemon', 'port', 'socket', 'network', 'firewall', 'protocol'],
            'tools': ['Git', 'Docker', 'Kubernetes', 'Jenkins', 'npm', 'pip', 'Maven', 'Gradle', 'Webpack', 'Babel', 'ESLint', 'Prettier', 'VS Code', 'IDE', 'terminal', 'command line']
        }
    
    def analyze_content(self, ocr_text: str, user_query: str = "") -> ContentAnalysis:
        """
        Perform comprehensive analysis of OCR content
        
        Args:
            ocr_text: Text extracted from OCR
            user_query: User's query for context
            
        Returns:
            ContentAnalysis with extracted information
        """
        if not ocr_text or not ocr_text.strip():
            return ContentAnalysis(
                primary_content_type=ContentType.UNKNOWN,
                entities=[],
                key_phrases=[],
                technical_terms=[],
                actionable_items=[],
                search_keywords=[],
                confidence_score=0.0,
                summary="No content to analyze"
            )
        
        # Extract entities
        entities = self._extract_entities(ocr_text)
        
        # Determine primary content type
        primary_type = self._determine_primary_type(entities, ocr_text)
        
        # Extract key phrases and technical terms
        key_phrases = self._extract_key_phrases(ocr_text, user_query)
        technical_terms = self._extract_technical_terms(ocr_text)
        
        # Find actionable items
        actionable_items = self._extract_actionable_items(ocr_text, entities)
        
        # Generate search keywords
        search_keywords = self._generate_search_keywords(ocr_text, user_query, entities, technical_terms)
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence(entities, ocr_text)
        
        # Generate summary
        summary = self._generate_summary(ocr_text, primary_type, entities, user_query)
        
        return ContentAnalysis(
            primary_content_type=primary_type,
            entities=entities,
            key_phrases=key_phrases,
            technical_terms=technical_terms,
            actionable_items=actionable_items,
            search_keywords=search_keywords,
            confidence_score=confidence_score,
            summary=summary
        )
    
    def _extract_entities(self, text: str) -> List[ExtractedEntity]:
        """Extract various entities from text"""
        entities = []
        
        # Extract code patterns
        for pattern in self.code_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                entities.append(ExtractedEntity(
                    type=ContentType.CODE,
                    value=match.group(),
                    confidence=0.9,
                    context=self._get_context(text, match.start(), match.end())
                ))
        
        # Extract error patterns
        for pattern in self.error_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                entities.append(ExtractedEntity(
                    type=ContentType.ERROR_MESSAGE,
                    value=match.group(),
                    confidence=0.95,
                    context=self._get_context(text, match.start(), match.end())
                ))
        
        # Extract UI elements
        for pattern in self.ui_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                entities.append(ExtractedEntity(
                    type=ContentType.UI_ELEMENT,
                    value=match.group(),
                    confidence=0.8,
                    context=self._get_context(text, match.start(), match.end())
                ))
        
        # Extract URLs
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        url_matches = re.finditer(url_pattern, text)
        for match in url_matches:
            entities.append(ExtractedEntity(
                type=ContentType.URL_LINK,
                value=match.group(),
                confidence=0.95,
                context=self._get_context(text, match.start(), match.end())
            ))
        
        # Extract emails
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_matches = re.finditer(email_pattern, text)
        for match in email_matches:
            entities.append(ExtractedEntity(
                type=ContentType.EMAIL,
                value=match.group(),
                confidence=0.9,
                context=self._get_context(text, match.start(), match.end())
            ))
        
        # Extract phone numbers
        phone_pattern = r'(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phone_matches = re.finditer(phone_pattern, text)
        for match in phone_matches:
            entities.append(ExtractedEntity(
                type=ContentType.PHONE,
                value=match.group(),
                confidence=0.85,
                context=self._get_context(text, match.start(), match.end())
            ))
        
        # Extract numbers and data
        number_pattern = r'\b\d+(?:\.\d+)?(?:\s*[%$€£¥]|\s*(?:MB|GB|TB|KB|Hz|GHz|MHz))\b'
        number_matches = re.finditer(number_pattern, text)
        for match in number_matches:
            entities.append(ExtractedEntity(
                type=ContentType.NUMBERS_DATA,
                value=match.group(),
                confidence=0.8,
                context=self._get_context(text, match.start(), match.end())
            ))
        
        return entities
    
    def _determine_primary_type(self, entities: List[ExtractedEntity], text: str) -> ContentType:
        """Determine the primary content type based on entities and text analysis"""
        type_counts = {}
        for entity in entities:
            type_counts[entity.type] = type_counts.get(entity.type, 0) + 1
        
        # Weight by confidence and frequency
        weighted_scores = {}
        for entity in entities:
            score = entity.confidence * type_counts[entity.type]
            weighted_scores[entity.type] = weighted_scores.get(entity.type, 0) + score
        
        if weighted_scores:
            return max(weighted_scores, key=weighted_scores.get)
        
        # Fallback analysis
        text_lower = text.lower()
        if any(keyword in text_lower for keyword in ['error', 'exception', 'failed', 'cannot']):
            return ContentType.ERROR_MESSAGE
        elif any(keyword in text_lower for keyword in ['def ', 'function', 'class ', 'import']):
            return ContentType.CODE
        elif any(keyword in text_lower for keyword in ['button', 'click', 'submit', 'form']):
            return ContentType.UI_ELEMENT
        else:
            return ContentType.TEXT_DOCUMENT
    
    def _extract_key_phrases(self, text: str, user_query: str) -> List[str]:
        """Extract key phrases relevant to the user query"""
        phrases = []
        
        # Split text into sentences
        sentences = re.split(r'[.!?]+', text)
        
        # Extract phrases that might be relevant to the query
        query_words = set(user_query.lower().split()) if user_query else set()
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10:  # Ignore very short sentences
                # Check if sentence contains query-related words
                sentence_words = set(sentence.lower().split())
                if query_words and query_words.intersection(sentence_words):
                    phrases.append(sentence)
                elif not query_words and len(sentence) < 100:  # Include shorter sentences if no query
                    phrases.append(sentence)
        
        return phrases[:5]  # Limit to top 5 phrases
    
    def _extract_technical_terms(self, text: str) -> List[str]:
        """Extract technical terms from text"""
        found_terms = []
        text_lower = text.lower()
        
        for category, terms in self.technical_terms.items():
            for term in terms:
                if term.lower() in text_lower:
                    found_terms.append(term)
        
        return list(set(found_terms))  # Remove duplicates
    
    def _extract_actionable_items(self, text: str, entities: List[ExtractedEntity]) -> List[str]:
        """Extract actionable items from text"""
        actionable = []
        
        # Look for error messages that suggest actions
        for entity in entities:
            if entity.type == ContentType.ERROR_MESSAGE:
                # Suggest debugging actions
                if "not found" in entity.value.lower():
                    actionable.append(f"Check if the missing item exists: {entity.value}")
                elif "permission" in entity.value.lower():
                    actionable.append(f"Check permissions for: {entity.value}")
                elif "syntax" in entity.value.lower():
                    actionable.append(f"Fix syntax error: {entity.value}")
        
        # Look for UI elements that suggest actions
        for entity in entities:
            if entity.type == ContentType.UI_ELEMENT:
                if any(word in entity.value.lower() for word in ['button', 'click', 'submit']):
                    actionable.append(f"Interact with UI element: {entity.value}")
        
        # Look for code that might need explanation
        for entity in entities:
            if entity.type == ContentType.CODE:
                actionable.append(f"Explain code: {entity.value}")
        
        return actionable[:3]  # Limit to top 3 actionable items
    
    def _generate_search_keywords(self, text: str, user_query: str, entities: List[ExtractedEntity], technical_terms: List[str]) -> List[str]:
        """Generate smart search keywords based on content analysis"""
        keywords = []
        
        # Add technical terms
        keywords.extend(technical_terms)
        
        # Add entity values (filtered)
        for entity in entities:
            if entity.type in [ContentType.ERROR_MESSAGE, ContentType.TECHNICAL_INFO]:
                # Clean up error messages for search
                clean_value = re.sub(r'[^\w\s]', ' ', entity.value)
                keywords.extend(clean_value.split()[:3])  # Take first 3 words
        
        # Add query-specific keywords
        if user_query:
            query_words = [word for word in user_query.split() if len(word) > 2]
            keywords.extend(query_words)
        
        # Remove duplicates and common words
        stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'}
        keywords = [kw for kw in set(keywords) if kw.lower() not in stop_words and len(kw) > 2]
        
        return keywords[:8]  # Limit to top 8 keywords
    
    def _calculate_confidence(self, entities: List[ExtractedEntity], text: str) -> float:
        """Calculate confidence score for the analysis"""
        if not entities:
            return 0.1
        
        # Average entity confidence
        avg_confidence = sum(entity.confidence for entity in entities) / len(entities)
        
        # Text quality factor
        text_quality = min(1.0, len(text.strip()) / 100)  # Normalize by text length
        
        # Entity diversity factor
        unique_types = len(set(entity.type for entity in entities))
        diversity_factor = min(1.0, unique_types / 5)
        
        return (avg_confidence * 0.6 + text_quality * 0.3 + diversity_factor * 0.1)
    
    def _generate_summary(self, text: str, primary_type: ContentType, entities: List[ExtractedEntity], user_query: str) -> str:
        """Generate a focused summary of the content"""
        if primary_type == ContentType.ERROR_MESSAGE:
            error_entities = [e for e in entities if e.type == ContentType.ERROR_MESSAGE]
            if error_entities:
                return f"Error detected: {error_entities[0].value}. This appears to be a technical issue that may need troubleshooting."
        
        elif primary_type == ContentType.CODE:
            code_entities = [e for e in entities if e.type == ContentType.CODE]
            if code_entities:
                return f"Code content detected: {code_entities[0].value}. This appears to be programming-related content."
        
        elif primary_type == ContentType.UI_ELEMENT:
            ui_entities = [e for e in entities if e.type == ContentType.UI_ELEMENT]
            if ui_entities:
                return f"UI elements detected: {', '.join([e.value for e in ui_entities[:3]])}. This appears to be interface-related content."
        
        # Generic summary
        text_preview = text.strip()[:150] + "..." if len(text.strip()) > 150 else text.strip()
        return f"Content analysis: {primary_type.value.replace('_', ' ').title()}. Preview: {text_preview}"
    
    def _get_context(self, text: str, start: int, end: int, window: int = 50) -> str:
        """Get context around a matched entity"""
        context_start = max(0, start - window)
        context_end = min(len(text), end + window)
        return text[context_start:context_end].strip()
    
    def get_focused_search_query(self, analysis: ContentAnalysis, user_query: str) -> str:
        """Generate a focused search query based on content analysis"""
        if not analysis.search_keywords:
            return user_query
        
        # Prioritize based on content type and user intent
        user_lower = user_query.lower() if user_query else ""
        
        # Error message handling - be very specific
        if analysis.primary_content_type == ContentType.ERROR_MESSAGE:
            error_keywords = [kw for kw in analysis.search_keywords if any(err in kw.lower() for err in ['error', 'exception', 'failed', 'warning'])]
            if error_keywords:
                # Check if user is asking for help/solution
                if any(word in user_lower for word in ['fix', 'solve', 'help', 'how', 'why']):
                    return f"how to fix {' '.join(error_keywords[:3])} solution"
                else:
                    return f"{' '.join(error_keywords[:3])} meaning cause"
        
        # Code content - provide tutorials or documentation
        elif analysis.primary_content_type == ContentType.CODE:
            tech_keywords = [kw for kw in analysis.technical_terms if kw in analysis.search_keywords]
            if tech_keywords:
                if any(word in user_lower for word in ['learn', 'tutorial', 'how', 'example']):
                    return f"{' '.join(tech_keywords[:2])} tutorial example guide"
                elif any(word in user_lower for word in ['documentation', 'docs', 'reference']):
                    return f"{' '.join(tech_keywords[:2])} documentation reference"
                else:
                    return f"{' '.join(tech_keywords[:2])} usage example"
        
        # UI elements - focus on user interaction
        elif analysis.primary_content_type == ContentType.UI_ELEMENT:
            ui_keywords = [kw for kw in analysis.search_keywords if len(kw) > 2]
            if ui_keywords and any(word in user_lower for word in ['click', 'use', 'access', 'find']):
                return f"how to use {' '.join(ui_keywords[:2])} interface"
        
        # Technical info - provide comprehensive information
        elif analysis.primary_content_type == ContentType.TECHNICAL_INFO:
            tech_keywords = analysis.technical_terms[:3]
            if tech_keywords:
                if any(word in user_lower for word in ['what', 'explain', 'meaning']):
                    return f"what is {' '.join(tech_keywords)} explanation"
                else:
                    return f"{' '.join(tech_keywords)} information guide"
        
        # Combine user query with top keywords intelligently
        top_keywords = analysis.search_keywords[:3]
        if user_query:
            # Remove redundant words between query and keywords
            query_words = set(user_query.lower().split())
            unique_keywords = [kw for kw in top_keywords if kw.lower() not in query_words]
            
            if unique_keywords:
                return f"{user_query} {' '.join(unique_keywords[:2])}"
            else:
                return user_query
        else:
            return ' '.join(top_keywords)