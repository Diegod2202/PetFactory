import tkinter as tk
from tkinter import ttk, simpledialog
import win32gui
import win32ui
import win32process
import win32api
import win32con
from ctypes import windll
from PIL import Image
import cv2
import numpy as np
import threading
import time
from pynput import keyboard

PW_RENDERFULLCONTENT = 0x00000002

# Pet management positions
PET_POSITIONS = {
    1: (170, 375),
    2: (240, 375),
    3: (310, 375),
    4: (380, 375),
    5: (170, 420),
    6: (240, 420),
    7: (310, 420),
    8: (380, 420)
}

PANEL_PETS_BTN = (880, 717)
DETAILS_BTN = (280, 490)
CARRY_BTN = (200, 490)
EXIT_DETAILS = (400, 100)

class DigitRecognizer:
    """Recognize digits using template matching"""
    
    def __init__(self):
        # Create digit templates (7-segment style templates)
        self.templates = self._create_templates()
    
    def _create_templates(self):
        """Create simple digit templates for 0-9"""
        templates = {}
        
        # We'll create these based on common game fonts
        # For now, we'll use a simple approach and refine later
        # Each template is a 10x15 pixel pattern
        
        return templates
    
    def recognize_number(self, img):
        """Recognize number from image - simple approach"""
        try:
            import pytesseract
            import re
            
            # Resize 4x for better OCR
            img_np = np.array(img)
            img_np = cv2.resize(img_np, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
            
            # Try multiple preprocessing methods
            results = []
            
            # Method 1: Simple grayscale
            gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
            text1 = pytesseract.image_to_string(gray, config='--psm 7 digits').strip()
            
            # Method 2: Binary threshold
            _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
            text2 = pytesseract.image_to_string(Image.fromarray(thresh), config='--psm 7 digits').strip()
            
            # Method 3: Inverted
            thresh_inv = cv2.bitwise_not(thresh)
            text3 = pytesseract.image_to_string(Image.fromarray(thresh_inv), config='--psm 7 digits').strip()
            
            # Method 4: OTSU threshold
            _, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            text4 = pytesseract.image_to_string(Image.fromarray(otsu), config='--psm 7 digits').strip()
            
            # Collect all results
            for text in [text1, text2, text3, text4]:
                numbers = re.findall(r'\d+', text)
                for num_str in numbers:
                    if len(num_str) >= 3:  # At least 3 digits
                        results.append(int(num_str))
            
            if results:
                # Return the most common or largest number
                from collections import Counter
                counts = Counter(results)
                most_common = counts.most_common(1)[0][0]
                return most_common
            
            return None
            
        except Exception as e:
            return None

class ProcessMonitor:
    """Monitor a single process"""
    
    def __init__(self, hwnd, pid, title):
        self.hwnd = hwnd
        self.pid = pid
        self.title = title
        self.account_name = None  # Will capture on first check
        self.current_exp = 0
        self.target_exp = 0
        self.enabled = False
        self.running = False
        self.thread = None
        self.recognizer = DigitRecognizer()
        self.status = "Idle"
        self.time_remaining = 0
        
        # Pet management
        self.pets = [{'position': i+1, 'exp': 0, 'completed': False} for i in range(8)]
        self.current_pet = None  # Index (0-7) of currently mounted pet
        self.pet_analysis_done = False
        self.last_check_time = 0
    
    def start(self):
        """Mark as ready for monitoring"""
        self.running = True
    
    def stop(self):
        """Stop monitoring"""
        self.running = False
    
    def check_once(self):
        """Perform one check cycle - called by coordinator"""
        try:
            if not self.enabled or self.target_exp == 0:
                self.status = "Idle"
                return
            
            # STEP 0: Bring window to front
            win32gui.ShowWindow(self.hwnd, 9)  # SW_RESTORE
            time.sleep(0.2)
            win32gui.SetForegroundWindow(self.hwnd)
            time.sleep(0.3)
            
            # STEP 0.5: Capture account name on first check
            if self.account_name is None:
                self.account_name = self._capture_account_name()
            
            # STEP 1: Analyze all pets if not done yet
            if not self.pet_analysis_done:
                self._analyze_all_pets()
                # After analysis, a pet should be mounted
                # Minimize and return
                win32gui.ShowWindow(self.hwnd, 6)
                time.sleep(0.2)
                return
            
            # STEP 2: Check current pet (every cycle - coordinator checks every 30s)
            if self.current_pet is None:
                # No pet mounted, nothing to check
                self.status = "No pet mounted"
                win32gui.ShowWindow(self.hwnd, 6)
                time.sleep(0.2)
                return
            
            # STEP 3: Open pet panel and check the mounted pet
            self.status = "Checking pet..."
            pet = self.pets[self.current_pet]
            pos = PET_POSITIONS[pet['position']]
            
            # Open pet panel
            self._click_at(*PANEL_PETS_BTN, wait_after=0.5)
            
            # Click on the current pet
            self._click_at(*pos, wait_after=0.3)
            
            # Click details button
            self._click_at(*DETAILS_BTN, wait_after=0.5)
            
            # STEP 4: Capture and read current pet EXP
            self.status = "Reading pet EXP..."
            img = self._capture_exp_region()
            
            if img:
                exp = self.recognizer.recognize_number(img)
                
                if exp is not None:
                    self.current_exp = exp
                    self.pets[self.current_pet]['exp'] = exp
                    
                    # Check if current pet reached target
                    if exp >= self.target_exp:
                        # Mark as completed
                        self.pets[self.current_pet]['completed'] = True
                        completed_count = sum(1 for p in self.pets if p['completed'])
                        
                        self.status = f"Pet {pet['position']} completed! ({completed_count}/8)"
                        
                        # Exit details and close panel
                        self._click_at(*EXIT_DETAILS, wait_after=0.3)
                        self._click_at(*PANEL_PETS_BTN, wait_after=0.3)
                        
                        # Try to mount next pet
                        self._mount_next_best_pet()
                    else:
                        # Not completed yet, update status
                        progress = (exp / self.target_exp * 100) if self.target_exp > 0 else 0
                        completed_count = sum(1 for p in self.pets if p['completed'])
                        self.status = f"Pet {pet['position']}: {progress:.1f}% ({completed_count}/8)"
                        
                        # Exit details and close panel
                        self._click_at(*EXIT_DETAILS, wait_after=0.3)
                        self._click_at(*PANEL_PETS_BTN, wait_after=0.3)
                else:
                    self.status = "Could not read EXP"
                    # Exit details and close panel anyway
                    self._click_at(*EXIT_DETAILS, wait_after=0.3)
                    self._click_at(*PANEL_PETS_BTN, wait_after=0.3)
            else:
                self.status = "Capture failed"
                # Exit details and close panel anyway
                self._click_at(*EXIT_DETAILS, wait_after=0.3)
                self._click_at(*PANEL_PETS_BTN, wait_after=0.3)
            
            # STEP 5: Minimize window
            win32gui.ShowWindow(self.hwnd, 6)
            time.sleep(0.2)
                
        except Exception as e:
            self.status = "Error"
            # Try to close any open panels
            try:
                self._click_at(*PANEL_PETS_BTN, wait_after=0.3)
            except:
                pass
    
    def _capture_exp_region(self):
        """Capture the exp region"""
        try:
            # Get window rect
            rect = win32gui.GetWindowRect(self.hwnd)
            width = rect[2] - rect[0]
            height = rect[3] - rect[1]
            
            # Create device context
            hwndDC = win32gui.GetWindowDC(self.hwnd)
            mfcDC = win32ui.CreateDCFromHandle(hwndDC)
            saveDC = mfcDC.CreateCompatibleDC()
            
            # Create bitmap
            saveBitMap = win32ui.CreateBitmap()
            saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
            saveDC.SelectObject(saveBitMap)
            
            # Capture
            result = windll.user32.PrintWindow(self.hwnd, saveDC.GetSafeHdc(), PW_RENDERFULLCONTENT)
            
            if result == 0:
                return None
            
            # Convert to PIL
            bmpinfo = saveBitMap.GetInfo()
            bmpstr = saveBitMap.GetBitmapBits(True)
            
            img = Image.frombuffer(
                'RGB',
                (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
                bmpstr, 'raw', 'BGRX', 0, 1
            )
            
            # Cleanup
            win32gui.DeleteObject(saveBitMap.GetHandle())
            saveDC.DeleteDC()
            mfcDC.DeleteDC()
            win32gui.ReleaseDC(self.hwnd, hwndDC)
            
            # Crop to exp region - EXACT coordinates as given
            # (119, 564) to (314, 583)
            img_cropped = img.crop((119, 564, 314, 583))
            
            return img_cropped
            
        except Exception as e:
            return None
    
    def _capture_account_name(self):
        """Capture account name from region (123,29) to (208,46)"""
        try:
            # Get window rect
            rect = win32gui.GetWindowRect(self.hwnd)
            width = rect[2] - rect[0]
            height = rect[3] - rect[1]
            
            # Create device context
            hwndDC = win32gui.GetWindowDC(self.hwnd)
            mfcDC = win32ui.CreateDCFromHandle(hwndDC)
            saveDC = mfcDC.CreateCompatibleDC()
            
            # Create bitmap
            saveBitMap = win32ui.CreateBitmap()
            saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
            saveDC.SelectObject(saveBitMap)
            
            # Capture
            result = windll.user32.PrintWindow(self.hwnd, saveDC.GetSafeHdc(), PW_RENDERFULLCONTENT)
            
            if result == 0:
                return "Unknown"
            
            # Convert to PIL
            bmpinfo = saveBitMap.GetInfo()
            bmpstr = saveBitMap.GetBitmapBits(True)
            
            img = Image.frombuffer(
                'RGB',
                (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
                bmpstr, 'raw', 'BGRX', 0, 1
            )
            
            # Cleanup
            win32gui.DeleteObject(saveBitMap.GetHandle())
            saveDC.DeleteDC()
            mfcDC.DeleteDC()
            win32gui.ReleaseDC(self.hwnd, hwndDC)
            
            # Crop to account name region: (123, 29) to (208, 46)
            img_name = img.crop((123, 29, 208, 46))
            
            # OCR
            import pytesseract
            text = pytesseract.image_to_string(img_name, config='--psm 7').strip()
            
            return text if text else "Unknown"
            
        except Exception as e:
            return "Unknown"
    

    
    def _click_pet_window(self):
        """Click at (70, 130) to open pet window using SendInput"""
        try:
            rect = win32gui.GetWindowRect(self.hwnd)
            screen_x = rect[0] + 70
            screen_y = rect[1] + 130
            
            import ctypes
            
            # Move mouse to position
            ctypes.windll.user32.SetCursorPos(screen_x, screen_y)
            time.sleep(0.05)
            
            # Right click down
            ctypes.windll.user32.mouse_event(8, 0, 0, 0, 0)  # MOUSEEVENTF_RIGHTDOWN
            time.sleep(0.05)
            
            # Right click up
            ctypes.windll.user32.mouse_event(16, 0, 0, 0, 0)  # MOUSEEVENTF_RIGHTUP
            
        except Exception as e:
            pass
    
    def _click_at(self, x, y, wait_after=0.3):
        """Click at specific position relative to window"""
        try:
            rect = win32gui.GetWindowRect(self.hwnd)
            screen_x = rect[0] + x
            screen_y = rect[1] + y
            
            import ctypes
            
            # Move mouse to position
            ctypes.windll.user32.SetCursorPos(screen_x, screen_y)
            time.sleep(0.05)
            
            # Left click down
            ctypes.windll.user32.mouse_event(2, 0, 0, 0, 0)  # MOUSEEVENTF_LEFTDOWN
            time.sleep(0.05)
            
            # Left click up
            ctypes.windll.user32.mouse_event(4, 0, 0, 0, 0)  # MOUSEEVENTF_LEFTUP
            
            if wait_after > 0:
                time.sleep(wait_after)
            
        except Exception as e:
            pass
    
    def _analyze_all_pets(self):
        """Analyze all 8 pets to check their EXP and completion status"""
        try:
            self.status = "Analyzing pets..."
            
            # Open pet panel
            self._click_at(*PANEL_PETS_BTN, wait_after=0.5)
            
            # Check each pet
            for i in range(8):
                pet = self.pets[i]
                pos = PET_POSITIONS[pet['position']]
                
                # Click on pet
                self._click_at(*pos, wait_after=0.3)
                
                # Click details button
                self._click_at(*DETAILS_BTN, wait_after=0.5)
                
                # Capture EXP
                img = self._capture_exp_region()
                if img:
                    exp = self.recognizer.recognize_number(img)
                    if exp is not None:
                        pet['exp'] = exp
                        
                        # Check if completed
                        if exp >= self.target_exp:
                            pet['completed'] = True
                
                # Exit details
                self._click_at(*EXIT_DETAILS, wait_after=0.3)
            
            # Close pet panel
            self._click_at(*PANEL_PETS_BTN, wait_after=0.3)
            
            self.pet_analysis_done = True
            
            # Select and mount the pet closest to target (not completed)
            self._mount_next_best_pet()
            
        except Exception as e:
            self.status = f"Analysis error"
            self._click_at(*PANEL_PETS_BTN, wait_after=0.3)  # Try to close panel
    
    def _mount_next_best_pet(self):
        """Find and mount the pet closest to target EXP that's not completed"""
        try:
            # Find incomplete pets
            incomplete_pets = [(i, pet) for i, pet in enumerate(self.pets) if not pet['completed']]
            
            if not incomplete_pets:
                # All pets completed!
                self.status = "🎉 All pets done!"
                self.current_pet = None
                self.enabled = False
                return
            
            # Sort by EXP (descending) to get closest to target
            incomplete_pets.sort(key=lambda x: x[1]['exp'], reverse=True)
            best_index, best_pet = incomplete_pets[0]
            
            # Mount this pet
            self._mount_pet(best_index)
            
        except Exception as e:
            self.status = "Mount error"
    
    def _mount_pet(self, pet_index):
        """Mount a specific pet (0-7 index)"""
        try:
            pet = self.pets[pet_index]
            pos = PET_POSITIONS[pet['position']]
            
            self.status = f"Mounting pet {pet['position']}..."
            
            # Open pet panel
            self._click_at(*PANEL_PETS_BTN, wait_after=0.5)
            
            # Click on pet
            self._click_at(*pos, wait_after=0.3)
            
            # Click carry button
            self._click_at(*CARRY_BTN, wait_after=0.5)
            
            # Close pet panel
            self._click_at(*PANEL_PETS_BTN, wait_after=0.3)
            
            self.current_pet = pet_index
            self.last_check_time = time.time()
            
            completed_count = sum(1 for p in self.pets if p['completed'])
            self.status = f"Carrying pet {pet['position']} ({completed_count}/8 done)"
            
        except Exception as e:
            self.status = "Mount error"
            self._click_at(*PANEL_PETS_BTN, wait_after=0.3)  # Try to close panel

class SimpleGUI:
    """Simple GUI to display EXP values"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Pet Factory - EXP Monitor")
        self.root.geometry("900x500")
        self.root.configure(bg='#2b2b2b')
        
        self.monitors = {}
        self.coordinator_running = False
        self.coordinator_thread = None
        self.next_check_time = 0
        self.is_monitoring = False  # Track if monitoring is active
        
        # Keyboard listener for D+F hotkey
        self.keys_pressed = set()
        self.keyboard_listener = None
        
        self._create_widgets()
        self._find_processes()
        self._start_keyboard_listener()
        self._update_display()
    
    def _create_widgets(self):
        """Create GUI"""
        # Title
        title = tk.Label(
            self.root,
            text="Pet Factory - Auto Pet Swap",
            font=("Arial", 14, "bold"),
            bg='#2b2b2b',
            fg='#ffffff'
        )
        title.pack(pady=15)
        
        # Info
        info = tk.Label(
            self.root,
            text="✓ Check box to enable | Double-click Target EXP to set | Press START | Hotkey: D+F to STOP",
            font=("Arial", 10),
            bg='#2b2b2b',
            fg='#ffaa00'
        )
        info.pack(pady=5)
        
        # Buttons
        button_frame = tk.Frame(self.root, bg='#2b2b2b')
        button_frame.pack(pady=5)
        
        self.get_names_button = tk.Button(
            button_frame,
            text="📋 GET NAMES",
            font=("Arial", 11, "bold"),
            bg='#0066cc',
            fg='#ffffff',
            command=self._get_all_names,
            width=15,
            height=1
        )
        self.get_names_button.pack(side=tk.LEFT, padx=5)
        
        self.start_button = tk.Button(
            button_frame,
            text="▶ START MONITORING",
            font=("Arial", 12, "bold"),
            bg='#00aa00',
            fg='#ffffff',
            command=self._toggle_monitoring,
            width=20,
            height=1
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        # Frame for tree
        tree_frame = tk.Frame(self.root, bg='#2b2b2b')
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Treeview
        self.tree = ttk.Treeview(
            tree_frame,
            columns=("Enable", "Account", "PID", "Current EXP", "Target EXP", "Status", "Time"),
            show='headings',
            height=15
        )
        
        self.tree.heading("Enable", text="Enable")
        self.tree.heading("Account", text="Account Name")
        self.tree.heading("PID", text="PID")
        self.tree.heading("Current EXP", text="Current EXP")
        self.tree.heading("Target EXP", text="Target EXP")
        self.tree.heading("Status", text="Status")
        self.tree.heading("Time", text="Next Check")
        
        self.tree.column("Enable", width=60, anchor=tk.CENTER)
        self.tree.column("Account", width=120, anchor=tk.CENTER)
        self.tree.column("PID", width=80, anchor=tk.CENTER)
        self.tree.column("Current EXP", width=120, anchor=tk.CENTER)
        self.tree.column("Target EXP", width=120, anchor=tk.CENTER)
        self.tree.column("Status", width=180, anchor=tk.CENTER)
        self.tree.column("Time", width=80, anchor=tk.CENTER)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Bind clicks
        self.tree.bind('<Button-1>', self._on_tree_click)
        self.tree.bind('<Double-Button-1>', self._on_tree_double_click)
    
    def _on_tree_click(self, event):
        """Handle tree click for checkbox toggle"""
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            return
        
        column = self.tree.identify_column(event.x)
        if column != "#1":  # Not the Enable column
            return
        
        item = self.tree.identify_row(event.y)
        if not item:
            return
        
        pid = int(item)
        if pid not in self.monitors:
            return
        
        monitor = self.monitors[pid]
        
        # Check if trying to enable without target EXP
        if not monitor.enabled and monitor.target_exp == 0:
            from tkinter import messagebox
            messagebox.showwarning(
                "Target EXP Required",
                f"Please set a Target EXP for PID {pid} before enabling.\n\nDouble-click on 'Not set' in the Target EXP column.",
                parent=self.root
            )
            return
        
        # Toggle enabled
        monitor.enabled = not monitor.enabled
    
    def _on_tree_double_click(self, event):
        """Handle double click to set target exp"""
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            return
        
        column = self.tree.identify_column(event.x)
        if column != "#5":  # Target EXP column
            return
        
        item = self.tree.identify_row(event.y)
        if not item:
            return
        
        pid = int(item)
        if pid not in self.monitors:
            return
        
        # Ask for target exp
        current_target = self.monitors[pid].target_exp
        result = simpledialog.askinteger(
            "Set Target EXP",
            f"Enter target EXP for PID {pid}:",
            initialvalue=current_target if current_target > 0 else 10000000,
            minvalue=1,
            maxvalue=1000000000,
            parent=self.root
        )
        
        if result:
            self.monitors[pid].target_exp = result
    
    def _find_processes(self):
        """Find Godswar processes"""
        def callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if "godswar" in title.lower() and "origin" in title.lower():
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    windows.append((hwnd, pid, title))
            return True
        
        windows = []
        win32gui.EnumWindows(callback, windows)
        
        for hwnd, pid, title in windows:
            monitor = ProcessMonitor(hwnd, pid, title)
            
            self.tree.insert('', tk.END, iid=str(pid), values=(
                "☐",
                "Not captured",  # Will capture on first check
                pid,
                "Idle",
                "Not set",
                "Idle",
                "-"
            ))
            
            monitor.start()
            self.monitors[pid] = monitor
    
    def _update_display(self):
        """Update display"""
        try:
            for pid, monitor in self.monitors.items():
                if self.tree.exists(str(pid)):
                    # Format time - use coordinator countdown
                    if monitor.enabled and monitor.target_exp > 0:
                        if self.next_check_time > 0:
                            time_str = f"{self.next_check_time}s"
                        else:
                            time_str = "Checking..."
                    else:
                        time_str = "-"
                    
                    # Format current exp display
                    if monitor.current_pet is not None and monitor.current_exp > 0:
                        exp_display = f"{monitor.current_exp:,}"
                    else:
                        exp_display = "Idle"
                    
                    values = (
                        "☑" if monitor.enabled else "☐",
                        monitor.account_name if monitor.account_name else "Not captured",
                        pid,
                        exp_display,
                        f"{monitor.target_exp:,}" if monitor.target_exp > 0 else "Not set",
                        monitor.status,
                        time_str
                    )
                    self.tree.item(str(pid), values=values)
        except Exception as e:
            pass
        finally:
            self.root.after(500, self._update_display)
    
    def _start_keyboard_listener(self):
        """Start keyboard listener for D+F hotkey"""
        def on_press(key):
            try:
                if hasattr(key, 'char') and key.char:
                    self.keys_pressed.add(key.char.lower())
                    
                    # Check if D and F are both pressed
                    if 'd' in self.keys_pressed and 'f' in self.keys_pressed:
                        if self.is_monitoring:
                            self.root.after(0, self._stop_monitoring_from_hotkey)
            except AttributeError:
                pass
        
        def on_release(key):
            try:
                if hasattr(key, 'char') and key.char:
                    self.keys_pressed.discard(key.char.lower())
            except AttributeError:
                pass
        
        self.keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        self.keyboard_listener.start()
    
    def _stop_monitoring_from_hotkey(self):
        """Stop monitoring triggered by hotkey"""
        if self.is_monitoring:
            self.is_monitoring = False
            self.start_button.config(
                text="▶ START MONITORING",
                bg='#00aa00'
            )
            self.coordinator_running = False
    
    def _get_all_names(self):
        """Capture account names for all processes"""
        if self.is_monitoring:
            from tkinter import messagebox
            messagebox.showwarning(
                "Stop Monitoring First",
                "Please stop monitoring before getting names.",
                parent=self.root
            )
            return
        
        self.get_names_button.config(state=tk.DISABLED, text="⏳ Getting...")
        
        # Run in thread to not block UI
        def capture_names():
            # Minimize all GW windows first
            for monitor in self.monitors.values():
                try:
                    win32gui.ShowWindow(monitor.hwnd, 6)  # SW_MINIMIZE
                except:
                    pass
            time.sleep(0.3)
            
            # Capture each one
            for monitor in self.monitors.values():
                try:
                    # Bring to front
                    win32gui.ShowWindow(monitor.hwnd, 9)  # SW_RESTORE
                    time.sleep(0.2)
                    win32gui.SetForegroundWindow(monitor.hwnd)
                    time.sleep(0.3)
                    
                    # Capture name
                    name = monitor._capture_account_name()
                    monitor.account_name = name
                    
                    # Minimize
                    win32gui.ShowWindow(monitor.hwnd, 6)
                    time.sleep(0.2)
                    
                except Exception as e:
                    pass
            
            self.root.after(0, lambda: self.get_names_button.config(state=tk.NORMAL, text="📋 GET NAMES"))
        
        threading.Thread(target=capture_names, daemon=True).start()
    
    def _toggle_monitoring(self):
        """Start/Stop monitoring"""
        if not self.is_monitoring:
            # Start monitoring
            enabled_count = sum(1 for m in self.monitors.values() if m.enabled and m.target_exp > 0)
            if enabled_count == 0:
                from tkinter import messagebox
                messagebox.showwarning(
                    "No Monitors Enabled",
                    "Please enable at least one process with a target EXP before starting.",
                    parent=self.root
                )
                return
            
            self.is_monitoring = True
            self.start_button.config(
                text="⏸ STOP MONITORING",
                bg='#aa0000'
            )
            self._start_coordinator()
        else:
            # Stop monitoring
            self.is_monitoring = False
            self.start_button.config(
                text="▶ START MONITORING",
                bg='#00aa00'
            )
            self.coordinator_running = False
    
    def _start_coordinator(self):
        """Start the coordinator thread that cycles through all monitors"""
        self.coordinator_running = True
        self.coordinator_thread = threading.Thread(target=self._coordinator_loop, daemon=True)
        self.coordinator_thread.start()
    
    def _coordinator_loop(self):
        """Main coordinator loop - cycles through monitors every 30 seconds"""
        
        # Minimize only Godswar Origin windows
        for monitor in self.monitors.values():
            try:
                win32gui.ShowWindow(monitor.hwnd, 6)  # SW_MINIMIZE
            except:
                pass
        time.sleep(0.5)
        
        while self.coordinator_running:
            try:
                # Get list of enabled monitors
                enabled_monitors = [m for m in self.monitors.values() if m.enabled and m.target_exp > 0]
                
                if enabled_monitors:
                    # Check each enabled monitor sequentially
                    for monitor in enabled_monitors:
                        if not self.coordinator_running:
                            break
                        monitor.check_once()
                    
                    # Wait 30 seconds before next cycle
                    for i in range(30):
                        if not self.coordinator_running:
                            break
                        self.next_check_time = 30 - i
                        time.sleep(1)
                    self.next_check_time = 0
                else:
                    # No enabled monitors, just wait
                    self.next_check_time = 0
                    time.sleep(1)
                    
            except Exception as e:
                time.sleep(30)
    
    def run(self):
        """Run the application"""
        self.root.mainloop()
        
        # Cleanup
        self.coordinator_running = False
        if self.coordinator_thread:
            self.coordinator_thread.join(timeout=2)
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        for monitor in self.monitors.values():
            monitor.stop()

if __name__ == "__main__":
    # Check for pytesseract
    try:
        import pytesseract
        import os
        
        tesseract_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        ]
        
        for path in tesseract_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                break
    except:
        pass
    
    app = SimpleGUI()
    app.run()
