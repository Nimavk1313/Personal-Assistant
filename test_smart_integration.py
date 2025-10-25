"""
Test script for smart integration functionality.
"""
import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from smart_context_analyzer import smart_analyzer
from data_fusion import data_fusion
from models import ChatRequest


def test_smart_context_analyzer():
    """Test the smart context analyzer with various query types."""
    print("=== Testing Smart Context Analyzer ===\n")
    
    test_queries = [
        "What does this button do?",  # Screen-related
        "What's the weather today?",  # Web search needed
        "How do I click the save button I see on screen?",  # Both
        "Explain quantum physics",  # Neither (knowledge-based)
        "What's the latest news about AI?",  # Web search
        "Help me fill out this form on my screen",  # Screen-related
    ]
    
    for query in test_queries:
        print(f"Query: '{query}'")
        
        try:
            decision = smart_analyzer.analyze_query(
                query=query,
                window_info="Active Window: Chrome - Google.com",
                has_live_ocr=False
            )
            
            print(f"  Use OCR: {decision.use_ocr}")
            print(f"  Use Web: {decision.use_web}")
            print(f"  Query Type: {decision.query_type.value}")
            print(f"  Reasoning: {decision.reasoning}")
            if decision.web_search_params:
                print(f"  Web Params: {decision.web_search_params}")
            print()
            
        except Exception as e:
            print(f"  Error: {e}\n")


def test_data_fusion():
    """Test the data fusion functionality."""
    print("=== Testing Data Fusion ===\n")
    
    # Test case 1: Screen-related query with screen content
    print("Test 1: Screen-related query")
    query = "What does this save button do?"
    screen_text = "File Edit View Tools Help\nSave Document - Click to save your current document to disk\nCancel\nOK"
    web_results = "How to save documents in Microsoft Word - comprehensive guide with tips and shortcuts..."
    window_info = "Active Window: Microsoft Word - Document1"
    
    fused = data_fusion.fuse_contexts(query, screen_text, web_results, window_info)
    print(f"Query: {query}")
    print(f"Fusion Strategy: {fused.fusion_strategy}")
    print(f"Relevance Summary: {fused.relevance_summary}")
    print(f"Primary Context Length: {len(fused.primary_context)}")
    print(f"Supporting Context Length: {len(fused.supporting_context)}")
    print()
    
    # Test case 2: Web search query
    print("Test 2: Web search query")
    query = "What's the latest news about artificial intelligence?"
    screen_text = "Welcome to Chrome\nNew Tab\nBookmarks"
    web_results = "Latest AI News: OpenAI releases new model with improved capabilities... Google announces breakthrough in AI reasoning... Microsoft integrates advanced AI into productivity tools..."
    window_info = "Active Window: Chrome - New Tab"
    
    fused = data_fusion.fuse_contexts(query, screen_text, web_results, window_info)
    print(f"Query: {query}")
    print(f"Fusion Strategy: {fused.fusion_strategy}")
    print(f"Relevance Summary: {fused.relevance_summary}")
    print(f"Primary Context Length: {len(fused.primary_context)}")
    print(f"Supporting Context Length: {len(fused.supporting_context)}")
    print()
    
    # Test case 3: Mixed relevance
    print("Test 3: Mixed relevance query")
    query = "How do I learn Python programming?"
    screen_text = "Python Tutorial\nChapter 1: Introduction to Python Programming\nVariables and Data Types - Learn the fundamentals"
    web_results = "Best Python courses online: Coursera Python specialization, Udemy complete Python bootcamp, edX MIT Python course..."
    window_info = "Active Window: Python Tutorial - Chapter 1"
    
    fused = data_fusion.fuse_contexts(query, screen_text, web_results, window_info)
    print(f"Query: {query}")
    print(f"Fusion Strategy: {fused.fusion_strategy}")
    print(f"Relevance Summary: {fused.relevance_summary}")
    print(f"Primary Context Length: {len(fused.primary_context)}")
    print(f"Supporting Context Length: {len(fused.supporting_context)}")
    print()


def test_integration():
    """Test the full integration."""
    print("=== Testing Full Integration ===\n")
    
    query = "What does this error message mean?"
    window_info = "Active Window: Visual Studio Code - main.py"
    
    # Test smart analyzer
    decision = smart_analyzer.analyze_query(query, window_info, False)
    print(f"Smart Analysis for: '{query}'")
    print(f"  Recommended OCR: {decision.use_ocr}")
    print(f"  Recommended Web: {decision.use_web}")
    print(f"  Reasoning: {decision.reasoning}")
    print()
    
    # Simulate context data based on decision
    screen_text = ""
    web_results = ""
    
    if decision.use_ocr:
        screen_text = "Error: NameError: name 'variabel' is not defined\nLine 15: print(variabel)\nTraceback (most recent call last):"
    
    if decision.use_web:
        web_results = "NameError in Python: This error occurs when you try to use a variable that hasn't been defined..."
    
    # Test data fusion
    fused = data_fusion.fuse_contexts(query, screen_text, web_results, window_info)
    print(f"Data Fusion Results:")
    print(f"  Strategy: {fused.fusion_strategy}")
    print(f"  Relevance: {fused.relevance_summary}")
    print(f"  Primary Context Preview: {fused.primary_context[:100]}...")
    print()


if __name__ == "__main__":
    print("Smart Integration Test Suite")
    print("=" * 50)
    print()
    
    try:
        test_smart_context_analyzer()
        test_data_fusion()
        test_integration()
        print("All tests completed successfully!")
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()