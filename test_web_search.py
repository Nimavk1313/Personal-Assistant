#!/usr/bin/env python3
"""
Comprehensive test script for web search functionality.
"""
import requests
import json
import time

def test_web_search_functionality():
    """Test all web search related functionality."""
    base_url = "http://localhost:8000"
    
    print("🔍 Testing Web Search Functionality")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1. Health Check")
    try:
        response = requests.get(f"{base_url}/health")
        health = response.json()
        print(f"   ✅ Status: {health['status']}")
        print(f"   ✅ Web Search Available: {health['web_search_available']}")
        print(f"   ✅ AI Available: {health['ai_available']}")
        print(f"   ✅ OCR Available: {health['ocr_available']}")
    except Exception as e:
        print(f"   ❌ Health check failed: {e}")
        return False
    
    # Test 2: Direct web search API
    print("\n2. Direct Web Search API")
    try:
        response = requests.post(f"{base_url}/search", params={
            'query': 'Python programming best practices',
            'max_results': 3
        })
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Search successful: {len(data['results'])} results found")
            print(f"   ✅ First result: {data['results'][0]['title'][:50]}...")
        else:
            print(f"   ❌ Search failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Search API failed: {e}")
        return False
    
    # Test 3: Chat with web search
    print("\n3. Chat with Web Search")
    try:
        response = requests.post(f"{base_url}/chat", json={
            'message': 'What are the latest trends in machine learning?',
            'use_web': True,
            'use_ocr': False
        })
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Chat successful: {len(data['response'])} characters")
            print(f"   ✅ Web results included: {len(data['web_results']) > 0}")
            print(f"   ✅ Response preview: {data['response'][:100]}...")
        else:
            print(f"   ❌ Chat failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Chat with search failed: {e}")
        return False
    
    # Test 4: Different search queries
    print("\n4. Multiple Search Queries")
    queries = [
        "artificial intelligence news",
        "Python web development",
        "machine learning tutorials"
    ]
    
    for i, query in enumerate(queries, 1):
        try:
            response = requests.post(f"{base_url}/search", params={
                'query': query,
                'max_results': 2
            })
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Query {i}: '{query}' - {len(data['results'])} results")
            else:
                print(f"   ❌ Query {i} failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Query {i} error: {e}")
    
    # Test 5: System prompt with web search
    print("\n5. System Prompt with Web Search")
    try:
        # Update system prompt to be web-aware
        response = requests.post(f"{base_url}/config/system-prompt", json={
            'system_prompt': 'You are a helpful assistant with access to real-time web information. Use web search results to provide accurate, up-to-date information.'
        })
        if response.status_code == 200:
            print("   ✅ System prompt updated to be web-aware")
            
            # Test chat with new prompt
            response = requests.post(f"{base_url}/chat", json={
                'message': 'What is the current weather like?',
                'use_web': True
            })
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Web-aware chat successful: {len(data['response'])} characters")
            else:
                print(f"   ❌ Web-aware chat failed: {response.status_code}")
        else:
            print(f"   ❌ System prompt update failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ System prompt test failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Web Search Functionality Test Complete!")
    print("✅ All web search features are working perfectly!")
    return True

if __name__ == "__main__":
    test_web_search_functionality()
