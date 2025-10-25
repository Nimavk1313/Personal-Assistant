"""
Performance optimization module for intelligent OCR and web search usage.
Implements caching, rate limiting, and smart decision making to avoid unnecessary calls.
"""

import time
import hashlib
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum


class CacheType(Enum):
    """Types of cached data."""
    OCR_RESULT = "ocr_result"
    WEB_SEARCH = "web_search"
    CONTEXT_DECISION = "context_decision"


@dataclass
class CacheEntry:
    """Cache entry with metadata."""
    data: any
    timestamp: datetime
    access_count: int = 0
    last_accessed: datetime = field(default_factory=datetime.now)
    ttl_seconds: int = 300  # 5 minutes default


@dataclass
class PerformanceMetrics:
    """Performance tracking metrics."""
    ocr_calls_saved: int = 0
    web_calls_saved: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    total_response_time_saved: float = 0.0


class PerformanceOptimizer:
    """Optimizes performance by intelligent caching and decision making."""
    
    def __init__(self):
        self.cache: Dict[str, CacheEntry] = {}
        self.metrics = PerformanceMetrics()
        
        # Rate limiting
        self.ocr_rate_limit = 10  # Max OCR calls per minute
        self.web_rate_limit = 20  # Max web searches per minute
        self.ocr_call_times: List[datetime] = []
        self.web_call_times: List[datetime] = []
        
        # Cache settings
        self.max_cache_size = 1000
        self.default_ttl = {
            CacheType.OCR_RESULT: 60,      # OCR results valid for 1 minute
            CacheType.WEB_SEARCH: 300,     # Web results valid for 5 minutes
            CacheType.CONTEXT_DECISION: 30 # Context decisions valid for 30 seconds
        }
        
        # Performance thresholds
        self.min_query_length = 3
        self.similar_query_threshold = 0.8
        
    def should_use_ocr(self, query: str, window_info: str = "", 
                      force_check: bool = False) -> Tuple[bool, str]:
        """
        Determine if OCR should be used based on performance considerations.
        
        Returns:
            Tuple of (should_use_ocr, reasoning)
        """
        if force_check:
            return True, "Force check requested"
        
        # Check rate limiting
        if not self._check_ocr_rate_limit():
            self.metrics.ocr_calls_saved += 1
            return False, "OCR rate limit exceeded"
        
        # Check if query is too short or generic
        if len(query.strip()) < self.min_query_length:
            return False, "Query too short for OCR"
        
        # Check for generic queries that don't need screen context
        generic_patterns = [
            'what is', 'how to', 'explain', 'define', 'tell me about',
            'why does', 'when did', 'where is', 'who is'
        ]
        
        query_lower = query.lower()
        if any(pattern in query_lower for pattern in generic_patterns):
            # Only use OCR if query specifically mentions screen elements
            screen_indicators = ['screen', 'button', 'menu', 'window', 'this', 'here', 'current']
            if not any(indicator in query_lower for indicator in screen_indicators):
                return False, "Generic query without screen context indicators"
        
        # Check cache for similar recent OCR results
        cache_key = self._generate_cache_key(f"ocr_decision_{query}_{window_info}")
        cached_decision = self._get_from_cache(cache_key, CacheType.CONTEXT_DECISION)
        
        if cached_decision is not None:
            self.metrics.cache_hits += 1
            return cached_decision, "Cached decision"
        
        # Default to using OCR for screen-related queries
        should_use = self._has_screen_context_indicators(query)
        reasoning = "Screen context indicators found" if should_use else "No screen context needed"
        
        # Cache the decision
        self._add_to_cache(cache_key, should_use, CacheType.CONTEXT_DECISION)
        
        return should_use, reasoning
    
    def should_use_web_search(self, query: str, force_check: bool = False) -> Tuple[bool, str]:
        """
        Determine if web search should be used based on performance considerations.
        
        Returns:
            Tuple of (should_use_web, reasoning)
        """
        if force_check:
            return True, "Force check requested"
        
        # Check rate limiting
        if not self._check_web_rate_limit():
            self.metrics.web_calls_saved += 1
            return False, "Web search rate limit exceeded"
        
        # Check if query is too short
        if len(query.strip()) < self.min_query_length:
            return False, "Query too short for web search"
        
        # Check for queries that clearly need external information
        web_indicators = [
            'latest', 'recent', 'news', 'current', 'today', 'now', 'update',
            'what happened', 'breaking', 'announcement', 'release',
            'price', 'stock', 'weather', 'forecast', 'schedule'
        ]
        
        query_lower = query.lower()
        needs_web = any(indicator in query_lower for indicator in web_indicators)
        
        if needs_web:
            return True, "Time-sensitive or external information needed"
        
        # Check for local/screen-only queries
        local_indicators = [
            'this screen', 'this window', 'this application', 'this button',
            'here on screen', 'currently visible', 'what i see'
        ]
        
        is_local = any(indicator in query_lower for indicator in local_indicators)
        if is_local:
            return False, "Local screen query - no web search needed"
        
        # Check cache for similar queries
        similar_query = self._find_similar_cached_query(query)
        if similar_query:
            self.metrics.cache_hits += 1
            return False, f"Similar query recently cached: {similar_query[:50]}..."
        
        # Default decision based on query characteristics
        question_words = ['what', 'how', 'why', 'when', 'where', 'who', 'which']
        has_question = any(word in query_lower for word in question_words)
        
        if has_question and len(query.split()) > 3:
            return True, "Complex question likely needs external information"
        
        return False, "Simple query - using AI knowledge only"
    
    def get_cached_ocr_result(self, window_info: str) -> Optional[str]:
        """Get cached OCR result for the current window."""
        cache_key = self._generate_cache_key(f"ocr_{window_info}")
        result = self._get_from_cache(cache_key, CacheType.OCR_RESULT)
        
        if result is not None:
            self.metrics.cache_hits += 1
            self.metrics.ocr_calls_saved += 1
            return result
        
        self.metrics.cache_misses += 1
        return None
    
    def cache_ocr_result(self, window_info: str, ocr_result: str):
        """Cache OCR result for future use."""
        cache_key = self._generate_cache_key(f"ocr_{window_info}")
        self._add_to_cache(cache_key, ocr_result, CacheType.OCR_RESULT)
    
    def get_cached_web_result(self, query: str, search_params: Dict = None) -> Optional[str]:
        """Get cached web search result."""
        params_str = str(sorted(search_params.items())) if search_params else ""
        cache_key = self._generate_cache_key(f"web_{query}_{params_str}")
        result = self._get_from_cache(cache_key, CacheType.WEB_SEARCH)
        
        if result is not None:
            self.metrics.cache_hits += 1
            self.metrics.web_calls_saved += 1
            return result
        
        self.metrics.cache_misses += 1
        return None
    
    def cache_web_result(self, query: str, web_result: str, search_params: Dict = None):
        """Cache web search result for future use."""
        params_str = str(sorted(search_params.items())) if search_params else ""
        cache_key = self._generate_cache_key(f"web_{query}_{params_str}")
        self._add_to_cache(cache_key, web_result, CacheType.WEB_SEARCH)
    
    def optimize_web_search_params(self, query: str, base_params: Dict) -> Dict:
        """Optimize web search parameters for better performance."""
        optimized = base_params.copy()
        
        # Adjust max_results based on query complexity
        query_words = len(query.split())
        if query_words <= 3:
            optimized['max_results'] = min(optimized.get('max_results', 5), 3)
        elif query_words <= 6:
            optimized['max_results'] = min(optimized.get('max_results', 5), 5)
        else:
            optimized['max_results'] = min(optimized.get('max_results', 10), 8)
        
        # Adjust timelimit for performance
        if 'latest' in query.lower() or 'recent' in query.lower():
            optimized['timelimit'] = 'd'  # Last day
        elif 'news' in query.lower():
            optimized['timelimit'] = 'w'  # Last week
        else:
            optimized['timelimit'] = 'm'  # Last month
        
        return optimized
    
    def get_performance_metrics(self) -> PerformanceMetrics:
        """Get current performance metrics."""
        return self.metrics
    
    def get_cache_stats(self) -> Dict:
        """Get cache performance statistics."""
        total_requests = self.metrics.cache_hits + self.metrics.cache_misses
        hit_rate = self.metrics.cache_hits / max(1, total_requests)
        
        return {
            "total_entries": len(self.cache),
            "hits": self.metrics.cache_hits,
            "misses": self.metrics.cache_misses,
            "hit_rate": hit_rate,
            "ocr_calls_saved": self.metrics.ocr_calls_saved,
            "web_calls_saved": self.metrics.web_calls_saved,
            "total_response_time_saved": self.metrics.total_response_time_saved
        }
    
    def cleanup_cache(self):
        """Clean up expired cache entries."""
        current_time = datetime.now()
        expired_keys = []
        
        for key, entry in self.cache.items():
            if current_time - entry.timestamp > timedelta(seconds=entry.ttl_seconds):
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.cache[key]
        
        # If cache is still too large, remove least recently used entries
        if len(self.cache) > self.max_cache_size:
            sorted_entries = sorted(
                self.cache.items(),
                key=lambda x: x[1].last_accessed
            )
            
            entries_to_remove = len(self.cache) - self.max_cache_size
            for key, _ in sorted_entries[:entries_to_remove]:
                del self.cache[key]
    
    def _check_ocr_rate_limit(self) -> bool:
        """Check if OCR rate limit allows another call."""
        current_time = datetime.now()
        cutoff_time = current_time - timedelta(minutes=1)
        
        # Remove old entries
        self.ocr_call_times = [t for t in self.ocr_call_times if t > cutoff_time]
        
        if len(self.ocr_call_times) >= self.ocr_rate_limit:
            return False
        
        self.ocr_call_times.append(current_time)
        return True
    
    def _check_web_rate_limit(self) -> bool:
        """Check if web search rate limit allows another call."""
        current_time = datetime.now()
        cutoff_time = current_time - timedelta(minutes=1)
        
        # Remove old entries
        self.web_call_times = [t for t in self.web_call_times if t > cutoff_time]
        
        if len(self.web_call_times) >= self.web_rate_limit:
            return False
        
        self.web_call_times.append(current_time)
        return True
    
    def _has_screen_context_indicators(self, query: str) -> bool:
        """Check if query has indicators that suggest screen context is needed."""
        screen_indicators = [
            'screen', 'display', 'window', 'application', 'app', 'interface',
            'button', 'menu', 'dialog', 'form', 'text', 'image', 'visible',
            'showing', 'displayed', 'current', 'this', 'here', 'that',
            'click', 'select', 'choose', 'navigate', 'scroll', 'type'
        ]
        
        query_lower = query.lower()
        return any(indicator in query_lower for indicator in screen_indicators)
    
    def _find_similar_cached_query(self, query: str) -> Optional[str]:
        """Find similar cached query to avoid redundant web searches."""
        query_words = set(query.lower().split())
        
        for cache_key in self.cache.keys():
            if cache_key.startswith("web_"):
                cached_query = cache_key[4:].split("_")[0]  # Extract query part
                cached_words = set(cached_query.lower().split())
                
                # Calculate similarity
                if len(query_words) > 0 and len(cached_words) > 0:
                    intersection = query_words.intersection(cached_words)
                    union = query_words.union(cached_words)
                    similarity = len(intersection) / len(union)
                    
                    if similarity >= self.similar_query_threshold:
                        return cached_query
        
        return None
    
    def _generate_cache_key(self, data: str) -> str:
        """Generate a cache key from data."""
        return hashlib.md5(data.encode()).hexdigest()
    
    def _get_from_cache(self, key: str, cache_type: CacheType) -> any:
        """Get data from cache if valid."""
        if key not in self.cache:
            return None
        
        entry = self.cache[key]
        current_time = datetime.now()
        
        # Check if expired
        if current_time - entry.timestamp > timedelta(seconds=entry.ttl_seconds):
            del self.cache[key]
            return None
        
        # Update access info
        entry.access_count += 1
        entry.last_accessed = current_time
        
        return entry.data
    
    def _add_to_cache(self, key: str, data: any, cache_type: CacheType):
        """Add data to cache."""
        ttl = self.default_ttl.get(cache_type, 300)
        
        self.cache[key] = CacheEntry(
            data=data,
            timestamp=datetime.now(),
            ttl_seconds=ttl
        )
        
        # Clean up if cache is getting too large
        if len(self.cache) > self.max_cache_size * 1.1:
            self.cleanup_cache()


# Global instance
performance_optimizer = PerformanceOptimizer()