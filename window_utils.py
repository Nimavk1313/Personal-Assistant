"""
Window management and process information utilities for the Personal Assistant application.
"""
import platform
import psutil
from typing import Optional
from models import WindowInfo

# Platform-specific imports
system = platform.system().lower()
if system == "windows":
    import ctypes
    import ctypes.wintypes as wintypes
elif system == "darwin":  # macOS
    try:
        from AppKit import NSWorkspace, NSApplication
        from Quartz import CGWindowListCopyWindowInfo, kCGWindowListOptionOnScreenOnly, kCGNullWindowID
    except ImportError:
        # Fallback if AppKit/Quartz not available
        NSWorkspace = None
        NSApplication = None
        CGWindowListCopyWindowInfo = None


class WindowManager:
    """Handles window management and process information across platforms."""
    
    def __init__(self):
        self.system = platform.system().lower()
        if self.system == "windows":
            self.user32 = ctypes.windll.user32
            self.kernel32 = ctypes.windll.kernel32
        elif self.system == "darwin":
            self.workspace = NSWorkspace.sharedWorkspace() if NSWorkspace else None
    
    def get_active_window_info(self) -> WindowInfo:
        """Get information about the currently active window."""
        if self.system == "windows":
            return self._get_active_window_info_windows()
        elif self.system == "darwin":
            return self._get_active_window_info_macos()
        else:
            return WindowInfo(title="", process_name="")
    
    def _get_active_window_info_windows(self) -> WindowInfo:
        """Get active window info on Windows."""
        try:
            hwnd = self.user32.GetForegroundWindow()
            if not hwnd:
                return WindowInfo(title="", process_name="")
            
            # Get window title
            length = self.user32.GetWindowTextLengthW(hwnd)
            if length == 0:
                return WindowInfo(title="", process_name="")
            
            buf = ctypes.create_unicode_buffer(length + 1)
            self.user32.GetWindowTextW(hwnd, buf, length + 1)
            title = buf.value
            
            # Get process information
            pid = wintypes.DWORD()
            self.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            
            process_name = ""
            try:
                if pid.value:
                    p = psutil.Process(pid.value)
                    process_name = p.name()
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                process_name = ""
            
            return WindowInfo(
                title=title,
                process_name=process_name,
                pid=pid.value if pid.value else None
            )
        except Exception:
            return WindowInfo(title="", process_name="")
    
    def _get_active_window_info_macos(self) -> WindowInfo:
        """Get active window info on macOS."""
        try:
            if not self.workspace:
                return WindowInfo(title="", process_name="")
            
            # Get the frontmost application
            frontmost_app = self.workspace.frontmostApplication()
            if not frontmost_app:
                return WindowInfo(title="", process_name="")
            
            app_name = frontmost_app.localizedName() or ""
            pid = frontmost_app.processIdentifier()
            
            # Try to get window title from window list
            title = ""
            if CGWindowListCopyWindowInfo:
                window_list = CGWindowListCopyWindowInfo(kCGWindowListOptionOnScreenOnly, kCGNullWindowID)
                for window in window_list:
                    window_pid = window.get('kCGWindowOwnerPID', 0)
                    if window_pid == pid:
                        window_title = window.get('kCGWindowName', '')
                        if window_title:
                            title = window_title
                            break
            
            return WindowInfo(
                title=title,
                process_name=app_name,
                pid=pid if pid else None
            )
        except Exception:
            return WindowInfo(title="", process_name="")
    
    def get_active_window_title(self) -> str:
        """Get just the active window title."""
        window_info = self.get_active_window_info()
        return window_info.title
    
    def get_active_process_name(self) -> str:
        """Get just the active process name."""
        window_info = self.get_active_window_info()
        return window_info.process_name
    
    def format_window_info(self, window_info: WindowInfo) -> str:
        """Format window information as a string."""
        if not window_info.title:
            return ""
        
        info = f"Active window: {window_info.title}"
        if window_info.process_name:
            info += f" (process: {window_info.process_name})"
        
        return info
    
    def get_formatted_active_window(self) -> str:
        """Get formatted active window information."""
        window_info = self.get_active_window_info()
        return self.format_window_info(window_info)
    
    def is_window_focused(self, window_title: str) -> bool:
        """Check if a specific window is focused by title."""
        try:
            current_title = self.get_active_window_title()
            return window_title.lower() in current_title.lower()
        except Exception:
            return False
    
    def get_all_windows(self) -> list[WindowInfo]:
        """Get information about all visible windows."""
        windows = []
        try:
            def enum_windows_callback(hwnd, lparam):
                if self.user32.IsWindowVisible(hwnd):
                    length = self.user32.GetWindowTextLengthW(hwnd)
                    if length > 0:
                        buf = ctypes.create_unicode_buffer(length + 1)
                        self.user32.GetWindowTextW(hwnd, buf, length + 1)
                        title = buf.value
                        
                        if title:  # Only add windows with titles
                            pid = wintypes.DWORD()
                            self.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
                            
                            process_name = ""
                            try:
                                if pid.value:
                                    p = psutil.Process(pid.value)
                                    process_name = p.name()
                            except Exception:
                                pass
                            
                            windows.append(WindowInfo(
                                title=title,
                                process_name=process_name,
                                pid=pid.value if pid.value else None
                            ))
                return True
            
            # Define the callback function type
            EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
            callback = EnumWindowsProc(enum_windows_callback)
            
            # Enumerate all windows
            self.user32.EnumWindows(callback, 0)
            
        except Exception:
            pass
        
        return windows


# Global window manager instance
window_manager = WindowManager()
