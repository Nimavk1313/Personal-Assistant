#!/usr/bin/env python3
"""
Test script for performance optimization integration with smart context analysis.
Tests caching, rate limiting, and intelligent decision-making.
"""

import time
from smart_context_analyzer import smart_analyzer
from performance_optimizer import performance_optimizer
from data_fusion import data_fusion
from relevance_scorer import relevance_scorer

def test_performance_optimization():
    """Test performance optimization features."""
    print("=== Testing Performance Optimization ===")
    
    # Test 1: Rate limiting for OCR
    print("\n1. Testing OCR rate limiting:")
    for i in range(3):
        should_use = performance_optimizer.should_use_ocr("test query")
        print(f"  OCR call {i+1}: {should_use}")
        if not should_use:
            print(f"    Rate limited after {i+1} calls")
            break
    
    # Test 2: Rate limiting for web search
    print("\n2. Testing web search rate limiting:")
    for i in range(6):
        should_use = performance_optimizer.should_use_web_search("test query")
        print(f"  Web search call {i+1}: {should_use}")
        if not should_use:
            print(f"    Rate limited after {i+1} calls")
            break
    
    # Test 3: Caching
    print("\n3. Testing caching:")
    query = "What is Python programming?"
    
    # First call - should be allowed
    start_time = time.time()
    decision1 = smart_analyzer.analyze_query(query, has_live_ocr=True)
    time1 = time.time() - start_time
    print(f"  First call: {decision1.reasoning}")
    print(f"  Time: {time1:.4f}s")
    
    # Second call with same query - should use cache or be rate limited
    start_time = time.time()
    decision2 = smart_analyzer.analyze_query(query, has_live_ocr=True)
    time2 = time.time() - start_time
    print(f"  Second call: {decision2.reasoning}")
    print(f"  Time: {time2:.4f}s")
    
    # Test 4: Web search parameter optimization
    print("\n4. Testing web search parameter optimization:")
    test_queries = [
        "latest AI news today",
        "Python tutorial for beginners",
        "how to fix computer error"
    ]
    
    for query in test_queries:
        base_params = {"max_results": 5}
        optimized = performance_optimizer.optimize_web_search_params(query, base_params)
        print(f"  Query: '{query}'")
        print(f"    Optimized params: {optimized}")

def test_smart_integration_with_performance():
    """Test smart context analysis with performance optimization."""
    print("\n=== Testing Smart Integration with Performance ===")
    
    test_cases = [
        {
            "query": "What's happening on my screen?",
            "window_info": "Visual Studio Code - main.py",
            "has_live_ocr": True,
            "expected_ocr": True,
            "expected_web": False
        },
        {
            "query": "Latest news about AI developments",
            "window_info": "Browser - News Site",
            "has_live_ocr": False,
            "expected_ocr": False,
            "expected_web": True
        },
        {
            "query": "How do I use Python decorators?",
            "window_info": "Terminal",
            "has_live_ocr": False,
            "expected_ocr": False,
            "expected_web": True
        },
        {
            "query": "Help me with this code",
            "window_info": "IDE - Python file",
            "has_live_ocr": True,
            "expected_ocr": True,
            "expected_web": False
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: '{case['query']}'")
        
        decision = smart_analyzer.analyze_query(
            case["query"],
            window_info=case["window_info"],
            has_live_ocr=case["has_live_ocr"]
        )
        
        print(f"   Decision: OCR={decision.use_ocr}, Web={decision.use_web}")
        print(f"   Query type: {decision.query_type.value}")
        print(f"   Confidence: {decision.confidence:.2f}")
        print(f"   Reasoning: {decision.reasoning}")
        
        if decision.web_search_params:
            print(f"   Web params: {decision.web_search_params}")
        
        # Check if performance optimization affected the decision
        ocr_allowed = performance_optimizer.should_use_ocr(case["query"])
        web_allowed = performance_optimizer.should_use_web_search(case["query"])
        
        if not ocr_allowed and case["expected_ocr"]:
            print(f"   Note: OCR was expected but blocked by performance optimizer")
        if not web_allowed and case["expected_web"]:
            print(f"   Note: Web search was expected but blocked by performance optimizer")

def test_data_fusion_with_performance():
    """Test data fusion with performance-optimized context."""
    print("\n=== Testing Data Fusion with Performance Context ===")
    
    # Simulate context data that would be gathered based on performance decisions
    query = "How do I save this document?"
    
    # Get smart decision
    decision = smart_analyzer.analyze_query(query, has_live_ocr=True)
    print(f"Smart decision for '{query}':")
    print(f"  Use OCR: {decision.use_ocr}")
    print(f"  Use Web: {decision.use_web}")
    print(f"  Reasoning: {decision.reasoning}")
    
    # Simulate context data based on decision
    screen_text = ""
    web_results = ""
    window_info = "Microsoft Word - Document1.docx"
    
    if decision.use_ocr:
        screen_text = """
        File Edit View Insert Format Tools Table Window Help
        Document1 - Word
        [Save] [Save As] [Open] [New]
        
        Chapter 1: Introduction
        This document contains important information about...
        The quick brown fox jumps over the lazy dog.
        """
    
    if decision.use_web:
        web_results = """
        How to Save Documents in Microsoft Word
        1. Press Ctrl+S or click the Save button
        2. Choose a location to save your file
        3. Enter a filename and click Save
        
        Keyboard Shortcuts for Saving:
        - Ctrl+S: Save current document
        - F12: Save As dialog
        """
    
    # Test data fusion
    if screen_text or web_results or window_info:
        fused_context = data_fusion.fuse_contexts(
            query=query,
            screen_text=screen_text,
            web_results=web_results,
            window_info=window_info
        )
        
        print(f"\nData fusion results:")
        print(f"  Strategy: {fused_context.fusion_strategy}")
        print(f"  Primary context: {fused_context.primary_context[:100]}...")
        print(f"  Supporting context: {fused_context.supporting_context[:100]}...")
        print(f"  Relevance summary: {fused_context.relevance_summary}")
    else:
        print("\nNo context data available due to performance optimization")

def test_cache_performance():
    """Test caching performance improvements."""
    print("\n=== Testing Cache Performance ===")
    
    # Clear any existing cache
    performance_optimizer.cache.clear()
    
    query = "Python programming tutorial"
    
    # Test multiple calls to see caching effect
    times = []
    for i in range(3):
        start_time = time.time()
        decision = smart_analyzer.analyze_query(query, has_live_ocr=False)
        elapsed = time.time() - start_time
        times.append(elapsed)
        
        print(f"Call {i+1}: {elapsed:.4f}s - {decision.reasoning[:50]}...")
    
    print(f"\nPerformance improvement:")
    if len(times) > 1:
        improvement = ((times[0] - times[-1]) / times[0]) * 100
        print(f"  Speed improvement: {improvement:.1f}%")
    
    # Show cache stats
    cache_stats = performance_optimizer.get_cache_stats()
    print(f"  Cache entries: {cache_stats.get('total_entries', 0)}")
    print(f"  Cache hits: {cache_stats.get('hits', 0)}")
    print(f"  Cache misses: {cache_stats.get('misses', 0)}")

if __name__ == "__main__":
    print("Performance Integration Test Suite")
    print("=" * 50)
    
    try:
        test_performance_optimization()
        test_smart_integration_with_performance()
        test_data_fusion_with_performance()
        test_cache_performance()
        
        print("\n" + "=" * 50)
        print("All performance integration tests completed!")
        
    except Exception as e:
        print(f"\nError during testing: {e}")
        import traceback
        traceback.print_exc()