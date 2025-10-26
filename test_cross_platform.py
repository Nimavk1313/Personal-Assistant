#!/usr/bin/env python3
"""
Cross-platform compatibility test for the Personal Assistant application.
Tests platform-specific functionality and dependencies.
"""

import platform
import sys
import importlib
from typing import Dict, List, Tuple


def test_platform_detection() -> Tuple[bool, str]:
    """Test platform detection."""
    try:
        system = platform.system().lower()
        supported_platforms = ["windows", "darwin", "linux"]
        
        if system in supported_platforms:
            return True, f"Platform detected: {system} ({platform.platform()})"
        else:
            return False, f"Unsupported platform: {system}"
    except Exception as e:
        return False, f"Platform detection failed: {e}"


def test_basic_imports() -> Tuple[bool, str]:
    """Test basic imports that should work on all platforms."""
    try:
        import psutil
        import mss
        import pytesseract
        from PIL import Image
        import fastapi
        import uvicorn
        
        return True, "All basic imports successful"
    except ImportError as e:
        return False, f"Import failed: {e}"


def test_platform_specific_imports() -> Tuple[bool, str]:
    """Test platform-specific imports."""
    system = platform.system().lower()
    
    try:
        if system == "windows":
            import ctypes
            import ctypes.wintypes as wintypes
            return True, "Windows-specific imports successful"
        
        elif system == "darwin":
            try:
                from AppKit import NSWorkspace, NSApplication
                from Quartz import CGWindowListCopyWindowInfo, kCGWindowListOptionOnScreenOnly, kCGNullWindowID
                return True, "macOS-specific imports successful"
            except ImportError:
                return False, "macOS frameworks not available. Install with: pip install pyobjc-framework-Cocoa pyobjc-framework-Quartz"
        
        elif system == "linux":
            # Linux doesn't require special imports for basic functionality
            return True, "Linux platform detected (limited window management)"
        
        else:
            return False, f"Unsupported platform: {system}"
            
    except ImportError as e:
        return False, f"Platform-specific import failed: {e}"


def test_tesseract_availability() -> Tuple[bool, str]:
    """Test Tesseract OCR availability."""
    try:
        import pytesseract
        import os
        
        system = platform.system().lower()
        tesseract_paths = []
        
        if system == "windows":
            tesseract_paths = [
                r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            ]
        elif system == "darwin":
            tesseract_paths = [
                "/usr/local/bin/tesseract",
                "/opt/homebrew/bin/tesseract",
                "/usr/bin/tesseract",
            ]
        elif system == "linux":
            tesseract_paths = [
                "/usr/bin/tesseract",
                "/usr/local/bin/tesseract",
            ]
        
        # Add fallback to PATH
        tesseract_paths.append("tesseract")
        
        for path in tesseract_paths:
            if os.path.exists(path) or path == "tesseract":
                try:
                    pytesseract.pytesseract.tesseract_cmd = path
                    # Test if tesseract works
                    pytesseract.get_tesseract_version()
                    return True, f"Tesseract found at: {path}"
                except:
                    continue
        
        return False, "Tesseract not found. Please install Tesseract OCR."
        
    except Exception as e:
        return False, f"Tesseract test failed: {e}"


def test_window_manager() -> Tuple[bool, str]:
    """Test window manager functionality."""
    try:
        from window_utils import WindowManager
        
        wm = WindowManager()
        window_info = wm.get_active_window_info()
        
        # Basic validation
        if hasattr(window_info, 'title') and hasattr(window_info, 'process_name'):
            return True, f"Window manager working. Current window: '{window_info.title}' ({window_info.process_name})"
        else:
            return False, "Window manager returned invalid data"
            
    except Exception as e:
        return False, f"Window manager test failed: {e}"


def test_screen_capture() -> Tuple[bool, str]:
    """Test screen capture functionality."""
    try:
        from screen_capture import ScreenCapture
        
        sc = ScreenCapture()
        stats = sc.get_stats()
        
        if hasattr(stats, 'ocr_ready'):
            return True, f"Screen capture initialized. OCR ready: {stats.ocr_ready}"
        else:
            return False, "Screen capture returned invalid stats"
            
    except Exception as e:
        return False, f"Screen capture test failed: {e}"


def run_all_tests() -> None:
    """Run all compatibility tests."""
    tests = [
        ("Platform Detection", test_platform_detection),
        ("Basic Imports", test_basic_imports),
        ("Platform-Specific Imports", test_platform_specific_imports),
        ("Tesseract Availability", test_tesseract_availability),
        ("Window Manager", test_window_manager),
        ("Screen Capture", test_screen_capture),
    ]
    
    print("=" * 60)
    print("Personal Assistant - Cross-Platform Compatibility Test")
    print("=" * 60)
    print(f"Python: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print("=" * 60)
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n[{test_name}]")
        try:
            success, message = test_func()
            if success:
                print(f"✅ PASS: {message}")
                passed += 1
            else:
                print(f"❌ FAIL: {message}")
        except Exception as e:
            print(f"❌ ERROR: {e}")
    
    print("\n" + "=" * 60)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your system is compatible.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()