#!/usr/bin/env python3
"""
Complete system integration test for the smart assistant.
Tests the entire pipeline from query analysis to AI response generation.
"""

import time
from smart_context_analyzer import smart_analyzer
from data_fusion import data_fusion
from relevance_scorer import relevance_scorer
from performance_optimizer import performance_optimizer
from ai_client import AIClient

def test_complete_system_integration():
    """Test the complete smart assistant system end-to-end."""
    print("=== Complete System Integration Test ===")
    
    # Test scenarios that cover different query types and contexts
    test_scenarios = [
        {
            "name": "Screen Analysis Query",
            "query": "What's this error message on my screen?",
            "window_info": "Visual Studio Code - Python Error",
            "has_live_ocr": True,
            "simulated_ocr": """
            Python Error Console
            Traceback (most recent call last):
              File "main.py", line 15, in <module>
                result = divide_numbers(10, 0)
              File "main.py", line 8, in divide_numbers
                return a / b
            ZeroDivisionError: division by zero
            """,
            "expected_context_sources": ["screen"],
            "expected_ai_guidance": "error analysis"
        },
        {
            "name": "Current Events Query",
            "query": "What are the latest developments in AI technology today?",
            "window_info": "Browser - News",
            "has_live_ocr": False,
            "simulated_web_results": """
            Latest AI News - December 2024
            1. OpenAI releases GPT-5 with improved reasoning capabilities
            2. Google announces breakthrough in quantum AI computing
            3. Microsoft integrates advanced AI into Office suite
            4. New AI safety regulations proposed by EU
            """,
            "expected_context_sources": ["web"],
            "expected_ai_guidance": "current information"
        },
        {
            "name": "Mixed Context Query",
            "query": "How can I improve this code I'm working on?",
            "window_info": "IDE - Python Development",
            "has_live_ocr": True,
            "simulated_ocr": """
            def calculate_total(items):
                total = 0
                for item in items:
                    total = total + item.price
                return total
            """,
            "simulated_web_results": """
            Python Code Optimization Best Practices
            1. Use list comprehensions for better performance
            2. Leverage built-in functions like sum()
            3. Consider using generators for memory efficiency
            4. Profile your code to identify bottlenecks
            """,
            "expected_context_sources": ["screen", "web"],
            "expected_ai_guidance": "code improvement"
        },
        {
            "name": "General Knowledge Query",
            "query": "Explain the concept of machine learning",
            "window_info": "Browser - Educational Site",
            "has_live_ocr": False,
            "expected_context_sources": [],
            "expected_ai_guidance": "educational explanation"
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n{i}. Testing Scenario: {scenario['name']}")
        print(f"   Query: '{scenario['query']}'")
        
        # Step 1: Smart Context Analysis
        print("   Step 1: Smart Context Analysis")
        decision = smart_analyzer.analyze_query(
            scenario["query"],
            window_info=scenario["window_info"],
            has_live_ocr=scenario["has_live_ocr"]
        )
        
        print(f"     Decision: OCR={decision.use_ocr}, Web={decision.use_web}")
        print(f"     Query Type: {decision.query_type.value}")
        print(f"     Confidence: {decision.confidence:.2f}")
        print(f"     Reasoning: {decision.reasoning}")
        
        # Step 2: Simulate Context Gathering
        print("   Step 2: Context Gathering")
        screen_text = ""
        web_results = ""
        
        if decision.use_ocr and "simulated_ocr" in scenario:
            screen_text = scenario["simulated_ocr"]
            print("     ✓ OCR context gathered")
        
        if decision.use_web and "simulated_web_results" in scenario:
            web_results = scenario["simulated_web_results"]
            print("     ✓ Web search results gathered")
        
        if not decision.use_ocr and not decision.use_web:
            print("     ✓ Using AI knowledge only")
        
        # Step 3: Data Fusion
        print("   Step 3: Data Fusion")
        if screen_text or web_results or scenario["window_info"]:
            fused_context = data_fusion.fuse_contexts(
                query=scenario["query"],
                screen_text=screen_text,
                web_results=web_results,
                window_info=scenario["window_info"]
            )
            
            print(f"     Strategy: {fused_context.fusion_strategy}")
            print(f"     Primary context length: {len(fused_context.primary_context)}")
            print(f"     Supporting context length: {len(fused_context.supporting_context)}")
            print(f"     Relevance summary: {fused_context.relevance_summary[:100]}...")
        else:
            print("     No context fusion needed")
            fused_context = None
        
        # Step 4: AI Message Building (simulate)
        print("   Step 4: AI Message Preparation")
        try:
            # Create a mock AI client to test message building
            ai_client = AIClient()
            
            # Create a mock ChatRequest object
            from models import ChatRequest
            mock_request = ChatRequest(
                message=scenario["query"],
                model="gpt-4",
                temperature=0.7,
                max_tokens=1000
            )
            
            # Simulate the message building process
            messages = ai_client._build_messages(
                request=mock_request,
                screen_text=screen_text,
                window_info=scenario["window_info"],
                web_results=web_results
            )
            
            print(f"     Messages prepared: {len(messages)} messages")
            
            # Analyze the messages for expected content
            message_content = " ".join([msg.get("content", "") for msg in messages])
            
            if screen_text and screen_text.strip() in message_content:
                print("     ✓ Screen context included in messages")
            
            if web_results and any(phrase in message_content for phrase in ["web search", "search results", "latest"]):
                print("     ✓ Web context included in messages")
            
            if scenario["window_info"] in message_content:
                print("     ✓ Window context included in messages")
                
        except Exception as e:
            print(f"     Warning: AI message building simulation failed: {e}")
        
        # Step 5: Performance Metrics
        print("   Step 5: Performance Analysis")
        metrics = performance_optimizer.get_performance_metrics()
        cache_stats = performance_optimizer.get_cache_stats()
        
        print(f"     OCR calls saved: {metrics.ocr_calls_saved}")
        print(f"     Web calls saved: {metrics.web_calls_saved}")
        print(f"     Cache hit rate: {cache_stats['hit_rate']:.2%}")
        
        # Validation
        print("   Step 6: Validation")
        validation_passed = True
        
        # Check if expected context sources were used
        expected_sources = scenario.get("expected_context_sources", [])
        if "screen" in expected_sources and not decision.use_ocr:
            print("     ❌ Expected screen context but OCR not used")
            validation_passed = False
        if "web" in expected_sources and not decision.use_web:
            print("     ❌ Expected web context but web search not used")
            validation_passed = False
        
        if validation_passed:
            print("     ✅ Scenario validation passed")
        else:
            print("     ❌ Scenario validation failed")
        
        print("   " + "-" * 50)

def test_performance_under_load():
    """Test system performance under multiple rapid queries."""
    print("\n=== Performance Under Load Test ===")
    
    queries = [
        "What's on my screen?",
        "Latest AI news",
        "How to optimize Python code?",
        "Explain machine learning",
        "Debug this error",
        "Current weather",
        "Help with this function",
        "What is this interface?"
    ]
    
    start_time = time.time()
    results = []
    
    for i, query in enumerate(queries):
        query_start = time.time()
        
        decision = smart_analyzer.analyze_query(
            query,
            window_info=f"Application {i}",
            has_live_ocr=(i % 2 == 0)  # Alternate OCR availability
        )
        
        query_time = time.time() - query_start
        results.append({
            "query": query,
            "time": query_time,
            "decision": decision
        })
    
    total_time = time.time() - start_time
    avg_time = total_time / len(queries)
    
    print(f"Processed {len(queries)} queries in {total_time:.3f}s")
    print(f"Average time per query: {avg_time:.3f}s")
    print(f"Queries per second: {len(queries)/total_time:.1f}")
    
    # Show performance optimizations in action
    cache_stats = performance_optimizer.get_cache_stats()
    print(f"Cache hit rate: {cache_stats['hit_rate']:.2%}")
    print(f"Total cache entries: {cache_stats['total_entries']}")
    
    # Show decision distribution
    ocr_decisions = sum(1 for r in results if r["decision"].use_ocr)
    web_decisions = sum(1 for r in results if r["decision"].use_web)
    
    print(f"OCR decisions: {ocr_decisions}/{len(queries)} ({ocr_decisions/len(queries):.1%})")
    print(f"Web decisions: {web_decisions}/{len(queries)} ({web_decisions/len(queries):.1%})")

def test_edge_cases():
    """Test edge cases and error handling."""
    print("\n=== Edge Cases Test ===")
    
    edge_cases = [
        {
            "name": "Empty Query",
            "query": "",
            "window_info": "",
            "has_live_ocr": False
        },
        {
            "name": "Very Long Query",
            "query": "This is a very long query " * 50,
            "window_info": "Application",
            "has_live_ocr": True
        },
        {
            "name": "Special Characters",
            "query": "What's this? @#$%^&*()_+{}|:<>?",
            "window_info": "App with special chars: @#$%",
            "has_live_ocr": False
        },
        {
            "name": "Non-English Query",
            "query": "¿Qué es esto en mi pantalla?",
            "window_info": "Aplicación",
            "has_live_ocr": True
        }
    ]
    
    for case in edge_cases:
        print(f"\nTesting: {case['name']}")
        try:
            decision = smart_analyzer.analyze_query(
                case["query"],
                window_info=case["window_info"],
                has_live_ocr=case["has_live_ocr"]
            )
            print(f"  ✅ Handled successfully: {decision.reasoning[:50]}...")
        except Exception as e:
            print(f"  ❌ Error: {e}")

if __name__ == "__main__":
    print("Smart Assistant Complete System Test")
    print("=" * 60)
    
    try:
        # Clear cache for clean testing
        performance_optimizer.cache.clear()
        
        test_complete_system_integration()
        test_performance_under_load()
        test_edge_cases()
        
        print("\n" + "=" * 60)
        print("🎉 Complete system integration tests finished!")
        
        # Final system status
        print("\nSystem Status Summary:")
        cache_stats = performance_optimizer.get_cache_stats()
        metrics = performance_optimizer.get_performance_metrics()
        
        print(f"  Cache entries: {cache_stats['total_entries']}")
        print(f"  Cache hit rate: {cache_stats['hit_rate']:.2%}")
        print(f"  OCR calls saved: {metrics.ocr_calls_saved}")
        print(f"  Web calls saved: {metrics.web_calls_saved}")
        print(f"  Total response time saved: {metrics.total_response_time_saved:.3f}s")
        
    except Exception as e:
        print(f"\n❌ System test failed: {e}")
        import traceback
        traceback.print_exc()