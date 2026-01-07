"""
Disconnect Monitor Module
Detects and handles disconnected game instances
"""
import win32gui
import win32con
import win32process
import threading
import time


# Detection settings
DIALOG_CLASS = "#32770"
DIALOG_TITLE_KEYWORD = "Prompt"
DISCONNECT_KEYWORDS = ["Disconnected", "Disconected"]  # Include typo variants
POLL_INTERVAL_SEC = 5.0


class DisconnectMonitor:
    """Monitor for detecting disconnected game clients"""
    
    def __init__(self, gui_callback=None):
        self.gui_callback = gui_callback
        self.monitored_pids = set()
        self.disconnected_pids = set()
        self.running = False
        self.monitor_thread = None
    
    def add_pid(self, pid):
        """Add a PID to monitor"""
        self.monitored_pids.add(pid)
        # Clear from disconnected if re-adding
        self.disconnected_pids.discard(pid)
    
    def remove_pid(self, pid):
        """Remove a PID from monitoring"""
        self.monitored_pids.discard(pid)
        self.disconnected_pids.discard(pid)
    
    def is_disconnected(self, pid):
        """Check if a PID is marked as disconnected"""
        return pid in self.disconnected_pids
    
    def start_monitoring(self):
        """Start the disconnect monitoring thread"""
        if self.running:
            return
        
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop the disconnect monitoring thread"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
    
    def _get_window_text(self, hwnd):
        """Get window text safely"""
        try:
            return win32gui.GetWindowText(hwnd) or ""
        except:
            return ""
    
    def _get_class_name(self, hwnd):
        """Get window class name safely"""
        try:
            return win32gui.GetClassName(hwnd) or ""
        except:
            return ""
    
    def _get_owner_pid(self, hwnd):
        """Get PID that owns the window"""
        try:
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            return pid
        except:
            return None
    
    def _find_child_by_class(self, parent_hwnd, class_name):
        """Find child windows by class name"""
        found = []
        
        def enum_child(child_hwnd, _):
            if self._get_class_name(child_hwnd) == class_name:
                found.append(child_hwnd)
        
        try:
            win32gui.EnumChildWindows(parent_hwnd, enum_child, None)
        except:
            pass
        
        return found
    
    def _read_dialog_message(self, dialog_hwnd):
        """Read message text from dialog"""
        statics = self._find_child_by_class(dialog_hwnd, "Static")
        texts = []
        for s in statics:
            txt = self._get_window_text(s).strip()
            if txt:
                texts.append(txt)
        return " ".join(texts)
    
    def _click_dialog_button(self, dialog_hwnd):
        """Click the OK/Accept button on the dialog"""
        buttons = self._find_child_by_class(dialog_hwnd, "Button")
        if not buttons:
            return False
        
        # Look for OK/Accept button
        preferred = None
        for b in buttons:
            bt = self._get_window_text(b).strip().lower()
            if bt in ("aceptar", "ok", "accept"):
                preferred = b
                break
        
        target = preferred or buttons[0]
        try:
            win32gui.SendMessage(target, win32con.BM_CLICK, 0, 0)
            return True
        except:
            return False
    
    def _poll_disconnected_dialogs(self):
        """Poll for disconnected dialogs and return detected events"""
        events = []
        
        def enum_windows(hwnd, _):
            # Check if it's a dialog
            if self._get_class_name(hwnd) != DIALOG_CLASS:
                return
            
            # Check if title contains "Prompt"
            title = self._get_window_text(hwnd).strip()
            if DIALOG_TITLE_KEYWORD.lower() not in title.lower():
                return
            
            # Read dialog message
            msg = self._read_dialog_message(hwnd)
            if not msg:
                return
            
            # Check if message contains disconnect keywords
            if any(kw.lower() in msg.lower() for kw in DISCONNECT_KEYWORDS):
                pid = self._get_owner_pid(hwnd)
                
                # Only process if we're monitoring this PID
                if pid in self.monitored_pids and pid not in self.disconnected_pids:
                    clicked = self._click_dialog_button(hwnd)
                    
                    events.append({
                        'pid': pid,
                        'message': msg,
                        'clicked': clicked,
                        'hwnd': hwnd,
                        'title': title
                    })
        
        try:
            win32gui.EnumWindows(enum_windows, None)
        except:
            pass
        
        return events
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                events = self._poll_disconnected_dialogs()
                
                for event in events:
                    pid = event['pid']
                    self.disconnected_pids.add(pid)
                    
                    # Notify GUI
                    if self.gui_callback:
                        self.gui_callback.on_disconnect_detected(pid, event['message'])
                
            except Exception as e:
                print(f"Error in disconnect monitor: {e}")
            
            # Sleep until next poll
            time.sleep(POLL_INTERVAL_SEC)
