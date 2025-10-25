"""
Screen capture and OCR functionality for the Personal Assistant application.
"""
import io
import threading
import time
from collections import deque
from datetime import datetime, timedelta
from typing import Optional, List, Tuple
from config import config
from models import CaptureStats, OCRResult


class ScreenCapture:
    """Handles screen capture and OCR functionality."""
    
    def __init__(self):
        self._live_enabled = False
        self._capture_thread: Optional[threading.Thread] = None
        self._capture_stop: Optional[threading.Event] = None
        self._recent_ocr: deque = deque(maxlen=config.max_ocr_history)
        self._stats = CaptureStats()
        self._last_text = ""
        
        # Get optional imports
        self._imports = config.get_optional_imports()
        self.mss = self._imports.get('mss')
        self.Image = self._imports.get('Image')
        self.pytesseract = self._imports.get('pytesseract')
        
        # Set tesseract path explicitly if available
        if self.pytesseract:
            import os
            tesseract_paths = [
                r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
                "tesseract"  # fallback to PATH
            ]
            for path in tesseract_paths:
                if os.path.exists(path) or path == "tesseract":
                    self.pytesseract.pytesseract.tesseract_cmd = path
                    break
        
        # Check OCR readiness
        self._stats.ocr_ready = self._is_ocr_ready()
    
    def start_live_capture(self) -> None:
        """Start live screen capture."""
        if self._capture_thread and self._capture_thread.is_alive():
            return
        
        if not self.mss:
            raise RuntimeError("mss library not available for screen capture")
        
        self._live_enabled = True
        self._capture_stop = threading.Event()
        self._capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._capture_thread.start()
    
    def stop_live_capture(self) -> None:
        """Stop live screen capture."""
        self._live_enabled = False
        if self._capture_stop:
            self._capture_stop.set()
        self._capture_stop = None
        self._capture_thread = None
    
    def is_live_enabled(self) -> bool:
        """Check if live capture is enabled."""
        return self._live_enabled
    
    def get_stats(self) -> CaptureStats:
        """Get capture statistics."""
        return self._stats
    
    def _capture_loop(self) -> None:
        """Main capture loop."""
        while self._capture_stop and not self._capture_stop.is_set():
            try:
                png = self._capture_screen_bytes()
                if not png:
                    time.sleep(0.8)
                    continue
                
                self._stats.frames += 1
                
                if self.pytesseract:
                    text = self._ocr_image_bytes(png)
                    if text and text != self._last_text:
                        self._recent_ocr.append((datetime.utcnow(), text))
                        self._last_text = text
                        self._stats.ocr_events += 1
                        
            except Exception as e:
                self._stats.last_error = str(e)[:200]
            
            time.sleep(config.capture_interval)
    
    def _capture_screen_bytes(self) -> Optional[bytes]:
        """Capture screen and return PNG bytes."""
        if not self.mss or not self.Image:
            return None
        
        try:
            with self.mss.mss() as sct:
                monitor = sct.monitors[1] if len(sct.monitors) > 1 else sct.monitors[0]
                img = sct.grab(monitor)
                pil_img = self.Image.frombytes("RGB", img.size, img.rgb)
                buf = io.BytesIO()
                pil_img.save(buf, format="PNG")
                return buf.getvalue()
        except Exception:
            return None
    
    def _ocr_image_bytes(self, png_bytes: bytes) -> str:
        """Perform OCR on PNG bytes."""
        if not self.pytesseract or not self.Image:
            return ""
        
        try:
            img = self.Image.open(io.BytesIO(png_bytes))
            text = self.pytesseract.image_to_string(img)
            return text.strip()
        except Exception:
            return ""
    
    def _is_ocr_ready(self) -> bool:
        """Check if OCR is ready."""
        if not self.pytesseract:
            return False
        
        try:
            _ = self.pytesseract.get_tesseract_version()
            return True
        except Exception:
            return False
    
    def get_recent_ocr_text(self, seconds: int = None, max_chars: int = None) -> str:
        """Get recent OCR text."""
        if seconds is None:
            seconds = config.ocr_timeout
        if max_chars is None:
            max_chars = config.max_transcript_chars
        
        cutoff = datetime.utcnow() - timedelta(seconds=seconds)
        chunks: List[str] = []
        seen = set()
        
        for ts, txt in list(self._recent_ocr):
            if ts < cutoff:
                continue
            
            snippet = txt.strip()
            if not snippet:
                continue
            
            key = snippet[:200]
            if key in seen:
                continue
            
            seen.add(key)
            chunks.append(snippet)
            
            if sum(len(c) for c in chunks) >= max_chars:
                break
        
        return "\n---\n".join(chunks)[:max_chars]
    
    def capture_single_screen(self) -> Tuple[Optional[bytes], str]:
        """Capture a single screen and return PNG bytes and OCR text."""
        png_bytes = self._capture_screen_bytes()
        ocr_text = ""
        
        if png_bytes and self.pytesseract:
            ocr_text = self._ocr_image_bytes(png_bytes)
        
        return png_bytes, ocr_text
    
    def get_ocr_history(self) -> List[OCRResult]:
        """Get OCR history as OCRResult objects."""
        results = []
        for timestamp, text in self._recent_ocr:
            results.append(OCRResult(timestamp=timestamp, text=text))
        return results
    
    def clear_history(self) -> None:
        """Clear OCR history."""
        self._recent_ocr.clear()
        self._stats.frames = 0
        self._stats.ocr_events = 0
        self._stats.last_error = ""
