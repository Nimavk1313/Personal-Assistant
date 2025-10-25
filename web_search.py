"""
Web search functionality for the Personal Assistant application.
"""
from typing import List, Optional
from config import config
from models import WebSearchResult, WebSearchResponse


class WebSearcher:
    """Handles web search functionality using DuckDuckGo."""
    
    def __init__(self):
        self._imports = config.get_optional_imports()
        self.DDGS = self._imports.get('DDGS')
        self._available = self.DDGS is not None
    
    def is_available(self) -> bool:
        """Check if web search is available."""
        return self._available
    
    def search(self, query: str, max_results: int = None, safesearch: str = None, timelimit: str = None) -> WebSearchResponse:
        """Perform web search and return results."""
        if not self._available:
            return WebSearchResponse(results=[], query=query)
        
        if max_results is None:
            max_results = config.web_search_max_results
        if safesearch is None:
            safesearch = config.web_search_safesearch
        if timelimit is None:
            timelimit = config.web_search_timelimit
        
        try:
            results = []
            with self.DDGS() as ddgs:
                for r in ddgs.text(
                    query, 
                    safesearch=safesearch, 
                    timelimit=timelimit, 
                    max_results=max_results
                ):
                    title = (r.get("title") or "").strip()
                    href = (r.get("href") or "").strip()
                    body = (r.get("body") or "").strip()
                    
                    if title or href or body:
                        results.append(WebSearchResult(
                            title=title,
                            href=href,
                            body=body
                        ))
                    
                    if len(results) >= max_results:
                        break
            
            return WebSearchResponse(results=results, query=query)
            
        except Exception:
            return WebSearchResponse(results=[], query=query)
    
    def search_formatted(self, query: str, max_results: int = None, timelimit: str = None) -> str:
        """Perform web search and return formatted results as string."""
        response = self.search(query, max_results, timelimit=timelimit)
        
        if not response.results:
            return ""
        
        formatted_results = []
        for result in response.results:
            formatted_results.append(f"- {result.title}\n  {result.href}\n  {result.body}")
        
        return "Web search results:\n" + "\n".join(formatted_results)
    
    def search_simple(self, query: str, max_results: int = None) -> List[str]:
        """Perform web search and return simple list of results."""
        response = self.search(query, max_results)
        return [f"{result.title} - {result.href}" for result in response.results]
    
    def get_search_suggestions(self, query: str) -> List[str]:
        """Get search suggestions for a query."""
        if not self._available:
            return []
        
        try:
            suggestions = []
            with self.DDGS() as ddgs:
                for suggestion in ddgs.suggestions(query):
                    suggestions.append(suggestion)
                    if len(suggestions) >= 5:  # Limit to 5 suggestions
                        break
            return suggestions
        except Exception:
            return []
    
    def search_news(self, query: str, max_results: int = None) -> WebSearchResponse:
        """Search for news articles."""
        if not self._available:
            return WebSearchResponse(results=[], query=query)
        
        if max_results is None:
            max_results = config.web_search_max_results
        
        try:
            results = []
            with self.DDGS() as ddgs:
                for r in ddgs.news(
                    query,
                    safesearch=config.web_search_safesearch,
                    timelimit=config.web_search_timelimit,
                    max_results=max_results
                ):
                    title = (r.get("title") or "").strip()
                    href = (r.get("url") or "").strip()
                    body = (r.get("body") or "").strip()
                    
                    if title or href or body:
                        results.append(WebSearchResult(
                            title=title,
                            href=href,
                            body=body
                        ))
                    
                    if len(results) >= max_results:
                        break
            
            return WebSearchResponse(results=results, query=query)
            
        except Exception:
            return WebSearchResponse(results=[], query=query)
    
    def search_images(self, query: str, max_results: int = None) -> List[dict]:
        """Search for images."""
        if not self._available:
            return []
        
        if max_results is None:
            max_results = config.web_search_max_results
        
        try:
            results = []
            with self.DDGS() as ddgs:
                for r in ddgs.images(
                    query,
                    safesearch=config.web_search_safesearch,
                    timelimit=config.web_search_timelimit,
                    max_results=max_results
                ):
                    results.append({
                        "title": r.get("title", ""),
                        "url": r.get("url", ""),
                        "thumbnail": r.get("thumbnail", ""),
                        "image": r.get("image", "")
                    })
                    
                    if len(results) >= max_results:
                        break
            
            return results
            
        except Exception:
            return []


# Global web searcher instance
web_searcher = WebSearcher()
