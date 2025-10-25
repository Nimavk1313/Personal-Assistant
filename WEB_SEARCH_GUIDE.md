# Web Search Functionality Guide

The Personal Assistant now has **perfectly working internet browsing capabilities** through DuckDuckGo search integration.

## 🌐 **Features**

- ✅ **Real-time web search** using DuckDuckGo
- ✅ **AI-powered responses** with web context
- ✅ **Multiple search types** (text, news, images)
- ✅ **Configurable search parameters**
- ✅ **API endpoints** for programmatic access
- ✅ **Web-aware system prompts**

## 🔧 **Setup & Installation**

### Dependencies
The system automatically handles the web search package:
- **Primary**: `ddgs` (new package)
- **Fallback**: `duckduckgo-search` (legacy package)

### Installation
```bash
pip install ddgs
# or
pip install -r requirements.txt
```

## 🚀 **Usage Methods**

### 1. **Web Interface**
1. Open `http://localhost:8000`
2. Check "Web Search" option
3. Ask questions that need current information
4. Get AI responses with real-time web data

### 2. **API Endpoints**

#### Direct Search
```bash
POST /search?query=machine+learning&max_results=5
```

#### Chat with Web Search
```bash
POST /chat
{
  "message": "What's the latest news about AI?",
  "use_web": true
}
```

### 3. **Python Integration**
```python
import requests

# Direct search
response = requests.post('http://localhost:8000/search', 
                        params={'query': 'Python programming', 'max_results': 3})
results = response.json()['results']

# Chat with web search
response = requests.post('http://localhost:8000/chat', 
                        json={'message': 'Latest AI trends', 'use_web': True})
ai_response = response.json()['response']
```

## 🎯 **Example Use Cases**

### Current Events
```
"What are the latest developments in quantum computing?"
"Tell me about recent breakthroughs in renewable energy"
"What's happening in the stock market today?"
```

### Technical Information
```
"What are the best practices for Python web development in 2024?"
"Compare different machine learning frameworks"
"Find tutorials for React.js hooks"
```

### Research & Analysis
```
"Analyze the current state of artificial intelligence"
"What are the pros and cons of different cloud providers?"
"Research the latest cybersecurity threats"
```

## ⚙️ **Configuration Options**

### Search Parameters
- **max_results**: Number of results (default: 5)
- **safesearch**: Search safety level (moderate, strict, off)
- **timelimit**: Time range (y=year, m=month, w=week, d=day)

### Environment Variables
```env
WEB_SEARCH_MAX_RESULTS=5
WEB_SEARCH_SAFESEARCH=moderate
WEB_SEARCH_TIMELIMIT=y
```

## 🔍 **Search Types**

### 1. **Text Search** (Default)
```python
results = web_searcher.search("Python programming")
```

### 2. **News Search**
```python
results = web_searcher.search_news("artificial intelligence")
```

### 3. **Image Search**
```python
results = web_searcher.search_images("machine learning diagrams")
```

### 4. **Search Suggestions**
```python
suggestions = web_searcher.get_search_suggestions("Python")
```

## 📊 **API Response Format**

### Search Results
```json
{
  "query": "machine learning",
  "results": [
    {
      "title": "Machine Learning Tutorial",
      "href": "https://example.com/tutorial",
      "body": "Comprehensive guide to ML..."
    }
  ],
  "formatted": "Web search results:\n- Title\n  URL\n  Description"
}
```

### Chat Response
```json
{
  "response": "AI-generated response with web context...",
  "screen_text": "",
  "window_info": "",
  "web_results": "Web search results:\n- Result 1\n- Result 2"
}
```

## 🎛️ **Advanced Configuration**

### System Prompt for Web-Aware Assistant
```python
# Update system prompt to be web-aware
requests.post('http://localhost:8000/config/system-prompt', 
              json={'system_prompt': 'You are a helpful assistant with access to real-time web information. Use web search results to provide accurate, up-to-date information.'})
```

### Full AI Configuration
```python
requests.post('http://localhost:8000/config/ai', 
              json={
                'system_prompt': 'You are a research assistant with web access.',
                'temperature': 0.3,
                'top_p': 0.9
              })
```

## 🧪 **Testing**

Run the comprehensive test:
```bash
python test_web_search.py
```

This tests:
- ✅ Health check
- ✅ Direct search API
- ✅ Chat with web search
- ✅ Multiple queries
- ✅ System prompt integration

## 🔧 **Troubleshooting**

### Common Issues

1. **No search results**
   - Check internet connection
   - Verify DuckDuckGo is accessible
   - Try different search terms

2. **Search timeout**
   - Reduce max_results
   - Check network stability
   - Try simpler queries

3. **Package conflicts**
   - Use `ddgs` instead of `duckduckgo-search`
   - Check for lxml version conflicts

### Debug Commands
```python
# Check web search availability
from web_search import web_searcher
print("Available:", web_searcher.is_available())

# Test direct search
result = web_searcher.search("test query", max_results=1)
print("Results:", len(result.results))
```

## 📈 **Performance Tips**

1. **Optimize queries**: Use specific, clear search terms
2. **Limit results**: Use appropriate max_results (3-5 for most cases)
3. **Cache results**: Implement caching for repeated queries
4. **Rate limiting**: Be respectful of search API limits

## 🎉 **Success Indicators**

- ✅ Health endpoint shows `web_search_available: true`
- ✅ Search API returns results
- ✅ Chat with `use_web: true` includes web context
- ✅ Multiple search types work
- ✅ No timeout or connection errors

Your Personal Assistant now has **perfect internet browsing capabilities**! 🌐✨
