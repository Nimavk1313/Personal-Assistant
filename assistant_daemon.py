"""
Refactored assistant daemon using modular structure.
"""
import threading
import queue
import time
import tkinter as tk
from tkinter import ttk
from typing import Optional

from config import config
from screen_capture import ScreenCapture
from window_utils import window_manager
from web_search import web_searcher
from ai_client import ai_client
from smart_context_analyzer import smart_analyzer


class AssistantDaemon:
    """Personal Assistant Daemon with GUI interface."""
    
    def __init__(self):
        self.screen_capture = ScreenCapture()
        self._kb_listener = None
        self._ui_thread: Optional[threading.Thread] = None
        self._requests: "queue.Queue[tuple[str, str]]" = queue.Queue()
        self._response_queue: "queue.Queue[str]" = queue.Queue()
        
        # Get optional imports
        self._imports = config.get_optional_imports()
        self.keyboard = self._imports.get('keyboard')
        
        # UI state
        self.enable_ocr = False
    
    def start(self) -> None:
        """Start the assistant daemon."""
        if self.keyboard is None:
            print("pynput not installed. Install with: pip install pynput")
        else:
            self._kb_listener = self.keyboard.GlobalHotKeys({
                '<ctrl>+<alt>+p': self._open_prompt_window,
                '<ctrl>+<alt>+o': self._toggle_ocr,
                '<ctrl>+<alt>+r': self._toggle_live,
            })
            self._kb_listener.start()

        self._ui_thread = threading.Thread(target=self._ui_loop, daemon=True)
        self._ui_thread.start()

        print("Assistant daemon running.")
        print("Hotkeys: Ctrl+Alt+P (ask), Ctrl+Alt+O (toggle OCR), Ctrl+Alt+R (live screen)")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass

    def _toggle_ocr(self) -> None:
        """Toggle OCR functionality."""
        self.enable_ocr = not self.enable_ocr
        print(f"OCR is {'ON' if self.enable_ocr else 'OFF'}")

    def _open_prompt_window(self) -> None:
        """Open the prompt window."""
        self._requests.put(("PROMPT", ""))

    def _toggle_live(self) -> None:
        """Toggle live screen capture."""
        if self.screen_capture.is_live_enabled():
            self.screen_capture.stop_live_capture()
            print("Live screen: OFF")
        else:
            self.screen_capture.start_live_capture()
            print("Live screen: ON")

    def _ui_loop(self) -> None:
        """Main UI loop."""
        root = tk.Tk()
        root.title("Assistant")
        root.attributes("-topmost", True)
        root.geometry("520x420+120+120")
        root.withdraw()

        frame = ttk.Frame(root, padding=8)
        frame.pack(fill=tk.BOTH, expand=True)

        # Prompt section
        prompt_label = ttk.Label(frame, text="Ask anything (Ctrl+Enter to send)")
        prompt_label.pack(anchor=tk.W)

        prompt_text = tk.Text(frame, height=6, wrap=tk.WORD)
        prompt_text.pack(fill=tk.X)

        # Options
        ocr_var = tk.BooleanVar(value=self.enable_ocr)
        ocr_check = ttk.Checkbutton(frame, text="Include screen OCR (single-shot)", variable=ocr_var)
        ocr_check.pack(anchor=tk.W, pady=(6, 6))

        live_label_var = tk.StringVar(value="Live screen: OFF (Ctrl+Alt+R)")
        live_label = ttk.Label(frame, textvariable=live_label_var)
        live_label.pack(anchor=tk.W)

        toggle_live_btn = ttk.Button(
            frame, 
            text="Toggle Live Screen (Ctrl+Alt+R)", 
            command=lambda: self._toggle_live_ui(live_label_var)
        )
        toggle_live_btn.pack(anchor=tk.W, pady=(4, 6))

        status_var = tk.StringVar(value="")
        status_label = ttk.Label(frame, textvariable=status_var)
        status_label.pack(anchor=tk.W)

        web_var = tk.BooleanVar(value=False)
        web_chk = ttk.Checkbutton(frame, text="Include web search results", variable=web_var)
        web_chk.pack(anchor=tk.W)

        smart_var = tk.BooleanVar(value=True)
        smart_chk = ttk.Checkbutton(frame, text="Smart mode (AI decides OCR/web automatically)", variable=smart_var)
        smart_chk.pack(anchor=tk.W, pady=(4, 0))

        send_btn = ttk.Button(
            frame, 
            text="Send", 
            command=lambda: self._send(prompt_text, ocr_var, web_var, smart_var, root)
        )
        send_btn.pack(anchor=tk.E)

        # Response section
        resp_label = ttk.Label(frame, text="Response")
        resp_label.pack(anchor=tk.W, pady=(8, 0))

        resp_text = tk.Text(frame, height=12, wrap=tk.WORD)
        resp_text.pack(fill=tk.BOTH, expand=True)

        # Transcript section
        transcript_label = ttk.Label(frame, text="Live transcript (recent OCR)")
        transcript_label.pack(anchor=tk.W, pady=(8, 0))
        transcript_text = tk.Text(frame, height=6, wrap=tk.WORD)
        transcript_text.configure(state=tk.DISABLED)
        transcript_text.pack(fill=tk.BOTH, expand=True)

        # Event handlers
        def on_key(event: tk.Event) -> None:
            if event.state & 4 and event.keysym == 'Return':  # Ctrl+Enter
                self._send(prompt_text, ocr_var, web_var, root)

        prompt_text.bind('<KeyPress>', on_key)

        def poll_requests() -> None:
            try:
                kind, _ = self._requests.get_nowait()
                if kind == "PROMPT":
                    root.deiconify()
                    root.lift()
                    root.attributes("-topmost", True)
                    prompt_text.focus_set()
            except queue.Empty:
                pass
            root.after(150, poll_requests)

        def poll_responses() -> None:
            try:
                text = self._response_queue.get_nowait()
                resp_text.delete("1.0", tk.END)
                resp_text.insert("1.0", text)
            except queue.Empty:
                pass
            root.after(300, poll_responses)

        def poll_transcript() -> None:
            try:
                if self.screen_capture.is_live_enabled():
                    latest = self.screen_capture.get_recent_ocr_text(seconds=15, max_chars=1200)
                else:
                    latest = "(Live screen OFF)"
                
                transcript_text.configure(state=tk.NORMAL)
                transcript_text.delete("1.0", tk.END)
                
                stats = self.screen_capture.get_stats()
                header = f"frames={stats.frames} ocr_events={stats.ocr_events} ocr_ready={stats.ocr_ready}\n"
                transcript_text.insert("1.0", header + latest)
                transcript_text.configure(state=tk.DISABLED)
                
                # Status line
                if not self.screen_capture.pytesseract:
                    status = "Status: pytesseract not installed"
                elif not stats.ocr_ready:
                    status = "Status: Tesseract not found on PATH"
                elif stats.last_error:
                    status = f"Status: error={stats.last_error}"
                else:
                    status = "Status: capturing"
                status_var.set(status)
            finally:
                root.after(800, poll_transcript)

        # Start polling
        poll_requests()
        poll_responses()
        poll_transcript()
        root.mainloop()

    def _toggle_live_ui(self, live_label_var: tk.StringVar) -> None:
        """Toggle live screen from UI."""
        self._toggle_live()
        live_label_var.set(f"Live screen: {'ON' if self.screen_capture.is_live_enabled() else 'OFF'} (Ctrl+Alt+R)")

    def _send(self, prompt_widget: tk.Text, ocr_var: tk.BooleanVar, web_var: tk.BooleanVar, smart_var: tk.BooleanVar, root: tk.Tk) -> None:
        """Send message for processing."""
        query = prompt_widget.get("1.0", tk.END).strip()
        if not query:
            return
        
        use_ocr = bool(ocr_var.get())
        use_web = bool(web_var.get())
        use_smart = bool(smart_var.get())
        
        threading.Thread(
            target=self._infer, 
            args=(query, use_ocr, use_web, use_smart), 
            daemon=True
        ).start()
        
        root.destroy()

    def _infer(self, query: str, use_ocr: bool, use_web: bool, use_smart: bool = False) -> None:
        """Process inference request with optional smart context analysis."""
        if not ai_client.is_available():
            self._response_queue.put("AI client not available. Check API key and configuration.")
            return

        # Get window information first
        window_info = window_manager.get_formatted_active_window()

        # Use smart context analysis if enabled
        if use_smart:
            try:
                context_decision = smart_analyzer.analyze_query(
                    query,
                    window_info,
                    self.screen_capture.is_live_enabled()
                )
                
                # Override manual settings with smart decisions
                use_ocr = context_decision.use_ocr
                use_web = context_decision.use_web
                web_params = context_decision.web_search_params or {}
                
                # Add reasoning to response
                reasoning_msg = f"Smart mode: {context_decision.reasoning}"
                self._response_queue.put(f"[{reasoning_msg}]\n")
                
            except Exception as e:
                self._response_queue.put(f"Smart analysis error (falling back to manual): {e}")
                # Fall back to manual settings
                web_params = {}
        else:
            web_params = {}

        # Get screen text if needed
        screen_text = ""
        if use_ocr:
            if self.screen_capture.is_live_enabled():
                screen_text = self.screen_capture.get_recent_ocr_text()
            else:
                _, screen_text = self.screen_capture.capture_single_screen()

        # Get web results if needed
        web_results = ""
        if use_web and web_searcher.is_available():
            try:
                max_results = web_params.get('max_results', 5)
                timelimit = web_params.get('timelimit', None)
                
                web_results = web_searcher.search_formatted(
                    query, 
                    max_results=max_results,
                    timelimit=timelimit
                )
            except Exception as e:
                self._response_queue.put(f"Web search error: {e}")

        # Create request
        from models import ChatRequest
        request = ChatRequest(
            message=query,
            use_ocr=use_ocr,
            use_web=use_web
        )

        try:
            response = ai_client.chat(request, screen_text, window_info, web_results)
            self._response_queue.put(response.response)
        except Exception as e:
            self._response_queue.put(f"Error: {e}")


def main() -> None:
    """Main entry point."""
    daemon = AssistantDaemon()
    daemon.start()


if __name__ == "__main__":
    main()


