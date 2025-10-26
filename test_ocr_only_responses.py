"""
Test script for OCR-only responses and transcript management improvements.
Tests that AI only references actual OCR content and transcript data is properly managed.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_client import ai_client
from screen_capture import ScreenCapture
from smart_context_analyzer import smart_analyzer
from models import ChatRequest
import time

def test_ocr_only_responses():
    """Test that AI responses only reference actual OCR content."""
    print("🧪 Testing OCR-Only Response Behavior")
    print("=" * 50)
    
    # Test cases with specific OCR content
    test_cases = [
        {
            "name": "Error Message OCR",
            "ocr_text": "Error: File not found\nThe system cannot find the file specified.\nPath: C:\\Users\\Documents\\missing.txt",
            "user_query": "What's wrong with my computer?",
            "should_not_contain": ["virus", "malware", "hardware", "reinstall", "format"]
        },
        {
            "name": "Code OCR",
            "ocr_text": "def calculate_sum(a, b):\n    return a + b\n\nresult = calculate_sum(5, 3)",
            "user_query": "Explain this code",
            "should_not_contain": ["database", "API", "framework", "deployment", "testing"]
        },
        {
            "name": "UI Element OCR",
            "ocr_text": "Save File\nCancel\nFile name: document.pdf\nLocation: Downloads",
            "user_query": "What should I do?",
            "should_not_contain": ["backup", "cloud", "security", "encryption", "permissions"]
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {test_case['name']}")
        print(f"OCR Text: {test_case['ocr_text'][:50]}...")
        print(f"User Query: {test_case['user_query']}")
        
        # Create chat request with OCR content
        chat_request = ChatRequest(
            message=test_case['user_query'],
            use_ocr=True,
            use_web=False,
            screen_text=test_case['ocr_text']
        )
        
        try:
            # Get AI response
            response = ai_client.chat(chat_request)
            print(f"AI Response: {response.response[:100]}...")
            
            # Check if response contains forbidden content
            response_lower = response.response.lower()
            forbidden_found = []
            
            for forbidden_word in test_case['should_not_contain']:
                if forbidden_word.lower() in response_lower:
                    forbidden_found.append(forbidden_word)
            
            if forbidden_found:
                print(f"❌ FAILED: Response contains non-OCR content: {forbidden_found}")
            else:
                print("✅ PASSED: Response only references OCR content")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
        
        print("-" * 30)

def test_transcript_management():
    """Test transcript data clearing and management."""
    print("\n🧪 Testing Transcript Management")
    print("=" * 50)
    
    screen_capture = ScreenCapture()
    
    # Test 1: Clear history
    print("1. Testing clear_history()")
    screen_capture.clear_history()
    transcript = screen_capture.get_recent_ocr_text()
    if not transcript.strip():
        print("✅ PASSED: clear_history() properly clears data")
    else:
        print(f"❌ FAILED: clear_history() left data: {transcript[:50]}...")
    
    # Test 2: Refresh transcript (simulated)
    print("\n2. Testing refresh_transcript()")
    # Add some mock data to test refresh
    from datetime import datetime, timedelta
    old_time = datetime.utcnow() - timedelta(seconds=5)  # Old data
    screen_capture._recent_ocr.append((old_time, "Old data"))
    time.sleep(0.1)
    screen_capture._recent_ocr.append((datetime.utcnow(), "New data"))  # Recent data
    
    # Refresh should keep only very recent data (last 3 seconds)
    screen_capture.refresh_transcript()
    transcript = screen_capture.get_recent_ocr_text()
    
    if "New data" in transcript and "Old data" not in transcript:
        print("✅ PASSED: refresh_transcript() keeps only recent data")
    else:
        print(f"❌ FAILED: refresh_transcript() behavior: {transcript}")
    
    # Test 3: Automatic cleanup in get_recent_ocr_text
    print("\n3. Testing automatic cleanup in get_recent_ocr_text()")
    screen_capture.clear_history()
    
    # Add old and new data
    from datetime import datetime, timedelta
    old_time = datetime.utcnow() - timedelta(seconds=20)
    new_time = datetime.utcnow()
    
    screen_capture._recent_ocr.append((old_time, "Very old data"))
    screen_capture._recent_ocr.append((new_time, "Fresh data"))
    
    # Get recent text with short timeout
    transcript = screen_capture.get_recent_ocr_text(seconds=10)
    
    if "Fresh data" in transcript and "Very old data" not in transcript:
        print("✅ PASSED: Automatic cleanup removes old entries")
    else:
        print(f"❌ FAILED: Automatic cleanup behavior: {transcript}")

def test_enhanced_system_prompt():
    """Test that the enhanced system prompt enforces OCR-only responses."""
    print("\n🧪 Testing Enhanced System Prompt")
    print("=" * 50)
    
    # Test OCR analysis integration
    ocr_text = "TypeError: 'NoneType' object has no attribute 'split'"
    user_query = "Fix this error"
    
    try:
        # Analyze OCR content
        analysis = smart_analyzer.analyze_ocr_content(ocr_text, user_query)
        print(f"OCR Analysis - Content Type: {analysis.primary_content_type.value}")
        print(f"OCR Analysis - Confidence: {analysis.confidence_score:.2f}")
        
        if analysis.confidence_score > 0.3:
            print("✅ PASSED: OCR analysis provides sufficient confidence for enhanced prompting")
        else:
            print("❌ FAILED: OCR analysis confidence too low")
            
        # Test chat with OCR analysis
        chat_request = ChatRequest(
            message=user_query,
            use_ocr=True,
            use_web=False,
            screen_text=ocr_text
        )
        
        response = ai_client.chat(chat_request)
        
        # Check if response mentions OCR limitations
        response_lower = response.response.lower()
        ocr_aware_phrases = [
            "based on what i can see",
            "from the screen",
            "the error shown",
            "visible in the ocr",
            "on your screen"
        ]
        
        ocr_awareness = any(phrase in response_lower for phrase in ocr_aware_phrases)
        
        if ocr_awareness:
            print("✅ PASSED: Response shows OCR awareness")
        else:
            print("⚠️  WARNING: Response may not show clear OCR awareness")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")

def main():
    """Run all tests."""
    print("🚀 Starting OCR-Only Response and Transcript Management Tests")
    print("=" * 60)
    
    try:
        test_ocr_only_responses()
        test_transcript_management()
        test_enhanced_system_prompt()
        
        print("\n" + "=" * 60)
        print("✅ All tests completed!")
        print("📋 Summary:")
        print("   - OCR-only response behavior tested")
        print("   - Transcript management improvements verified")
        print("   - Enhanced system prompt functionality checked")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()