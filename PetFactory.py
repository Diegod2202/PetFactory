"""
Pet Factory - Main GUI Application
Manages the user interface and coordinates pet management operations
"""
import tkinter as tk
from tkinter import messagebox, scrolledtext, Toplevel
from datetime import datetime
import os
import sys
import json
import keyboard

# Import custom modules
from memory_reader import get_all_process_ids, get_module_base_address, read_player_name
from pet_analyzer import analyze_pets
from pet_manager import start_pet_management
from disconnect_monitor import DisconnectMonitor
from pet_data import get_exp_for_level


class PetFactoryGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Pet Factory")
        self.root.geometry("1100x850")
        
        # Dark theme colors
        self.bg_dark = "#1a1a1a"
        self.bg_medium = "#2d2d2d"
        self.bg_light = "#3d3d3d"
        self.accent_green = "#00ff88"
        self.accent_blue = "#00b4ff"
        self.accent_orange = "#ff8800"
        self.text_color = "#e0e0e0"
        self.text_secondary = "#a0a0a0"
        
        # Configure root background
        self.root.configure(bg=self.bg_dark)
        
        # Variables
        self.accounts = {}  # {pid: {'name': str, 'track': BooleanVar}}
        self.analysis_results = {}  # Store analysis results for Start to use
        self.ignored_pets = {}  # {character_name: [list of ignored pet indices 0-7]}
        
        # Load ignored pets from file
        self._load_ignored_pets()
        
        # Initialize disconnect monitor
        self.disconnect_monitor = DisconnectMonitor(gui_callback=self)
        self.disconnect_monitor.start_monitoring()
        
        # Main container with two columns
        container = tk.Frame(root, bg=self.bg_dark)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Left panel (existing UI)
        left_panel = tk.Frame(container, bg=self.bg_dark, width=550)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(25, 10), pady=25)
        left_panel.pack_propagate(False)
        
        # Right panel (logs)
        right_panel = tk.Frame(container, bg=self.bg_dark)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 25), pady=25)
        
        # Setup left panel (existing UI)
        self._setup_left_panel(left_panel)
        
        # Setup right panel (logs)
        self._setup_right_panel(right_panel)
        
        # Setup global hotkeys (after log_text is created)
        self._setup_global_hotkeys()
        
        # Load accounts on startup
        self.refresh_accounts()
    
    def _setup_global_hotkeys(self):
        """Setup global hotkeys for the application"""
        try:
            # D+Q to quit
            keyboard.add_hotkey('d+q', self._quit_app)
            # D+F to pause/resume
            keyboard.add_hotkey('d+f', self._toggle_pause)
            self.log("Hotkeys registered: D+F pause/resume | D+Q quit")
        except Exception as e:
            self.log(f"Warning: Could not register hotkeys: {e}")
    
    def _toggle_pause(self):
        """Toggle pause state for analyzer and manager"""
        # Import here to avoid circular dependency
        import pet_analyzer
        import pet_manager
        
        # Toggle both modules
        pet_analyzer.is_paused = not pet_analyzer.is_paused
        pet_manager.is_paused = pet_analyzer.is_paused
        
        state = "PAUSED" if pet_analyzer.is_paused else "RESUMED"
        self.log(f"⏸️ Process {state}" if pet_analyzer.is_paused else f"▶️ Process {state}")
    
    def _quit_app(self):
        """Quit the application"""
        self.log("D+Q pressed - Closing application...")
        try:
            keyboard.unhook_all()
        except Exception:
            pass
        self.root.quit()
        self.root.destroy()
    
    def _setup_left_panel(self, parent):
        """Setup the left panel with existing UI"""
        # Header
        header_frame = tk.Frame(parent, bg=self.bg_medium, pady=15)
        header_frame.pack(fill=tk.X)
        
        tk.Label(header_frame, text="🐾 Pet Factory", font=("Segoe UI", 24, "bold"), 
                bg=self.bg_medium, fg=self.accent_green).pack()
        
        # Main container
        main_frame = tk.Frame(parent, pady=10, bg=self.bg_dark)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Accounts list section
        accounts_header_frame = tk.Frame(main_frame, bg=self.bg_dark)
        accounts_header_frame.pack(fill=tk.X, pady=(0, 12))
        
        accounts_label = tk.Label(accounts_header_frame, text="Origin Accounts:", 
                                 font=("Segoe UI", 13, "bold"),
                                 bg=self.bg_dark, fg=self.text_color)
        accounts_label.pack(side=tk.LEFT)
        
        # Refresh button
        refresh_btn = tk.Button(accounts_header_frame, text="🔄 Refresh",
                               command=self.refresh_accounts,
                               bg=self.accent_blue, fg="#000000",
                               font=("Segoe UI", 10, "bold"),
                               relief=tk.FLAT,
                               cursor="hand2",
                               padx=10)
        refresh_btn.pack(side=tk.RIGHT)
        
        # Frame for accounts (no scroll)
        self.accounts_frame = tk.Frame(main_frame, bg=self.bg_light, relief=tk.FLAT, borderwidth=0)
        self.accounts_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Game folder path section
        folder_label = tk.Label(main_frame, text="Game Folder Path:",
                               font=("Segoe UI", 11, "bold"),
                               bg=self.bg_dark, fg=self.text_color)
        folder_label.pack(anchor=tk.W, pady=(0, 3))
        
        # Warning about path
        warning_label = tk.Label(main_frame,
                                text="⚠️ Important: This must point to the User folder where pet files are saved",
                                font=("Segoe UI", 9, "italic"),
                                bg=self.bg_dark, fg="#ffaa00")
        warning_label.pack(anchor=tk.W, pady=(0, 5))
        
        folder_frame = tk.Frame(main_frame, bg=self.bg_dark)
        folder_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.game_folder_var = tk.StringVar(value=r"C:\Godswar Origin\Localization\en_us\Settings\User")
        folder_entry = tk.Entry(folder_frame, textvariable=self.game_folder_var,
                               font=("Segoe UI", 9), width=55,
                               bg=self.bg_medium, fg=self.text_color,
                               insertbackground=self.text_color,
                               relief=tk.FLAT, borderwidth=5)
        folder_entry.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)
        
        browse_btn = tk.Button(folder_frame, text="Browse...",
                              command=self.browse_folder,
                              bg=self.bg_light, fg=self.text_color,
                              font=("Segoe UI", 10),
                              relief=tk.FLAT,
                              cursor="hand2",
                              padx=15)
        browse_btn.pack(side=tk.LEFT)
        
        # Objective Level section
        level_frame = tk.Frame(main_frame, bg=self.bg_dark)
        level_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(level_frame, text="Objective Level:", 
                font=("Segoe UI", 11, "bold"),
                bg=self.bg_dark, fg=self.text_color).pack(side=tk.LEFT, padx=(0, 15))
        
        self.objective_level_var = tk.StringVar(value="30")
        level_entry = tk.Entry(level_frame, textvariable=self.objective_level_var, 
                              font=("Segoe UI", 11), width=8,
                              bg=self.bg_medium, fg=self.text_color,
                              insertbackground=self.text_color,
                              relief=tk.FLAT, borderwidth=5)
        level_entry.pack(side=tk.LEFT)
        
        # EXP info label (calculated from level)
        self.exp_info_label = tk.Label(level_frame, text="", 
                                       font=("Segoe UI", 10),
                                       bg=self.bg_dark, fg=self.accent_blue)
        self.exp_info_label.pack(side=tk.LEFT, padx=(15, 0))
        
        # Update EXP info when level changes
        self.objective_level_var.trace('w', self._update_exp_info)
        self._update_exp_info()  # Initial update
        
        # Disclaimer
        disclaimer_label = tk.Label(main_frame, 
                                   text="Note: If you skip analysis, the process assumes all pets start at 0 EXP\n"
                                        "and will process them sequentially (Pet 1 → Pet 2 → ... → Pet 8) as alerts arrive.",
                                   font=("Segoe UI", 9),
                                   bg=self.bg_dark, fg=self.text_secondary,
                                   justify=tk.LEFT)
        disclaimer_label.pack(fill=tk.X, pady=(0, 15))
        
        # Hotkey info
        hotkey_label = tk.Label(main_frame,
                               text="⌨ Hotkeys: D+F to pause/resume process | D+Q to quit application",
                               font=("Segoe UI", 10, "bold"),
                               bg=self.bg_dark, fg=self.accent_blue)
        hotkey_label.pack(fill=tk.X, pady=(0, 25))
        
        # Buttons section
        buttons_frame = tk.Frame(main_frame, bg=self.bg_dark)
        buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.start_btn = tk.Button(buttons_frame, text="▶ Start", 
                                   command=self.on_start,
                                   bg=self.accent_green, fg="#000000", 
                                   font=("Segoe UI", 14, "bold"),
                                   width=30, height=2,
                                   relief=tk.FLAT,
                                   cursor="hand2",
                                   activebackground="#00dd77",
                                   activeforeground="#000000")
        self.start_btn.pack(expand=True)
    
    def _setup_right_panel(self, parent):
        """Setup the right panel with logs console"""
        # Header
        log_header = tk.Label(parent, text="📋 Console Logs", 
                             font=("Segoe UI", 16, "bold"),
                             bg=self.bg_dark, fg=self.text_color)
        log_header.pack(anchor=tk.W, pady=(0, 10))
        
        # Log text area
        self.log_text = scrolledtext.ScrolledText(
            parent,
            font=("Consolas", 9),
            bg=self.bg_medium,
            fg=self.text_color,
            insertbackground=self.text_color,
            relief=tk.FLAT,
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Buttons frame at bottom
        bottom_buttons = tk.Frame(parent, bg=self.bg_dark)
        bottom_buttons.pack(pady=(10, 0), fill=tk.X)
        
        # Clear logs button
        clear_btn = tk.Button(bottom_buttons, text="Clear Logs",
                             command=self.clear_logs,
                             bg=self.bg_light, fg=self.text_color,
                             font=("Segoe UI", 10),
                             relief=tk.FLAT,
                             cursor="hand2")
        clear_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Restart button
        restart_btn = tk.Button(bottom_buttons, text="🔄 Restart",
                               command=self.restart_app,
                               bg=self.accent_orange, fg="#000000",
                               font=("Segoe UI", 10, "bold"),
                               relief=tk.FLAT,
                               cursor="hand2",
                               activebackground="#ff9933",
                               activeforeground="#000000")
        restart_btn.pack(side=tk.LEFT)
        
        # Initial log
        self.log("Pet Factory initialized")
    
    def _update_exp_info(self, *args):
        """Update the EXP info label when objective level changes"""
        try:
            level = int(self.objective_level_var.get())
            if 1 <= level <= 120:
                exp_needed = get_exp_for_level(level)
                self.exp_info_label.config(text=f"= {exp_needed:,} EXP needed")
            else:
                self.exp_info_label.config(text="Level must be 1-120")
        except ValueError:
            self.exp_info_label.config(text="")
    
    def _get_ignored_pets_file(self):
        """Get path to ignored pets JSON file"""
        return os.path.join(os.path.dirname(__file__), "ignored_pets.json")
    
    def _load_ignored_pets(self):
        """Load ignored pets from JSON file"""
        try:
            file_path = self._get_ignored_pets_file()
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    self.ignored_pets = json.load(f)
        except Exception:
            self.ignored_pets = {}
    
    def _save_ignored_pets(self):
        """Save ignored pets to JSON file"""
        try:
            file_path = self._get_ignored_pets_file()
            with open(file_path, 'w') as f:
                json.dump(self.ignored_pets, f, indent=2)
        except Exception:
            pass
    
    def _show_ignore_pets_dialog(self, pid):
        """Show dialog to select which pets to ignore for an account"""
        account = self.accounts.get(pid)
        if not account:
            return
        
        player_name = account['name']
        current_ignored = self.ignored_pets.get(player_name, [])
        
        # Create popup window
        dialog = Toplevel(self.root)
        dialog.title(f"Ignore Pets - {player_name}")
        dialog.geometry("300x320")
        dialog.configure(bg=self.bg_dark)
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center on parent
        dialog.geometry(f"+{self.root.winfo_x() + 400}+{self.root.winfo_y() + 200}")
        
        # Title
        tk.Label(dialog, text=f"Select pets to ignore for:", 
                font=("Segoe UI", 11, "bold"),
                bg=self.bg_dark, fg=self.text_color).pack(pady=(15, 0))
        tk.Label(dialog, text=player_name, 
                font=("Segoe UI", 12, "bold"),
                bg=self.bg_dark, fg=self.accent_blue).pack(pady=(0, 15))
        
        # Checkboxes frame
        check_frame = tk.Frame(dialog, bg=self.bg_medium, padx=20, pady=15)
        check_frame.pack(padx=20, pady=5, fill=tk.X)
        
        # Create 8 checkboxes in 2 columns
        pet_vars = []
        for i in range(8):
            var = tk.BooleanVar(value=(i in current_ignored))
            pet_vars.append(var)
            
            row = i % 4
            col = i // 4
            
            cb = tk.Checkbutton(check_frame, text=f"Pet {i + 1}", variable=var,
                               font=("Segoe UI", 10),
                               bg=self.bg_medium, fg=self.text_color,
                               activebackground=self.bg_medium,
                               activeforeground=self.text_color,
                               selectcolor=self.bg_dark,
                               cursor="hand2")
            cb.grid(row=row, column=col, sticky="w", padx=20, pady=3)
        
        # Buttons frame
        btn_frame = tk.Frame(dialog, bg=self.bg_dark)
        btn_frame.pack(pady=20)
        
        def save_and_close():
            # Collect ignored indices
            ignored = [i for i, var in enumerate(pet_vars) if var.get()]
            if ignored:
                self.ignored_pets[player_name] = ignored
            elif player_name in self.ignored_pets:
                del self.ignored_pets[player_name]
            self._save_ignored_pets()
            
            # Update button indicator
            self._update_ignore_button(pid)
            
            ignored_count = len(ignored)
            self.log(f"✓ {player_name}: Ignoring {ignored_count} pet(s)" if ignored_count else f"✓ {player_name}: No pets ignored")
            dialog.destroy()
        
        save_btn = tk.Button(btn_frame, text="Save", command=save_and_close,
                            bg=self.accent_green, fg="#000000",
                            font=("Segoe UI", 10, "bold"),
                            width=8, cursor="hand2")
        save_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = tk.Button(btn_frame, text="Cancel", command=dialog.destroy,
                              bg=self.bg_light, fg=self.text_color,
                              font=("Segoe UI", 10),
                              width=8, cursor="hand2")
        cancel_btn.pack(side=tk.LEFT, padx=5)
    
    def _update_ignore_button(self, pid):
        """Update ignore button to show if pets are ignored"""
        account = self.accounts.get(pid)
        if not account or 'ignore_btn' not in account:
            return
        
        player_name = account['name']
        ignored_count = len(self.ignored_pets.get(player_name, []))
        
        btn = account['ignore_btn']
        if ignored_count > 0:
            btn.config(text=f"⚙ {ignored_count}", fg=self.accent_orange)
        else:
            btn.config(text="⚙", fg=self.text_secondary)
    
    def log(self, message):
        """Add a message to the log console"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, log_message)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def clear_logs(self):
        """Clear all logs"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.log("Logs cleared")
    
    def update_account_status(self, pid, status=None, pets_done=None):
        """Update the status display for an account"""
        if pid not in self.accounts:
            return
        
        account = self.accounts[pid]
        
        if status is not None:
            account['status'] = status
            account['status_label'].config(text=status)
            # Color code status
            if status == "Idle":
                account['status_label'].config(fg=self.text_secondary)
            elif status == "Analyzing":
                account['status_label'].config(fg=self.accent_blue)
            elif status == "Analyzed":
                account['status_label'].config(fg="#ffcc00")  # Yellow/gold for analyzed
            elif status == "Running":
                account['status_label'].config(fg=self.accent_green)
            elif status == "Complete":
                account['status_label'].config(fg=self.accent_green)
            elif status == "Disconnected":
                account['status_label'].config(fg="#ff8800")
            elif "Error" in status:
                account['status_label'].config(fg="#ff4444")
        
        if pets_done is not None:
            account['pets_done'] = pets_done
            # During analysis, show progress; during management, show completed
            account['pets_done_label'].config(text=f"{pets_done}/8")
    
    def on_disconnect_detected(self, pid, message):
        """Called by DisconnectMonitor when a disconnect is detected"""
        if pid in self.accounts:
            account_name = self.accounts[pid]['name']
            self.update_account_status(pid, status="Disconnected")
            self.log(f"🔌 {account_name} disconnected - Stopped monitoring")
            self.log(f"   Message: {message}")
    
    def browse_folder(self):
        """Open folder browser dialog"""
        from tkinter import filedialog
        folder = filedialog.askdirectory(
            title="Select Game Settings Folder",
            initialdir=self.game_folder_var.get()
        )
        if folder:
            self.game_folder_var.set(folder)
            self.log(f"Game folder updated: {folder}")
    
    def restart_app(self):
        """Restart the application"""
        self.log("Restarting application...")
        try:
            keyboard.unhook_all()
        except Exception:
            pass
        
        # Get current Python executable and script
        python_exe = sys.executable
        script_path = os.path.abspath(__file__)
        
        # Close the current window
        self.root.destroy()
        
        # Start new process
        import subprocess
        subprocess.Popen([python_exe, script_path])
        
        # Exit current process
        sys.exit(0)
    
    def refresh_accounts(self):
        """Refresh the list of Origin.exe processes"""
        # Clear current list
        for widget in self.accounts_frame.winfo_children():
            widget.destroy()
        
        old_pids = set(self.accounts.keys())
        self.accounts.clear()
        
        # Get all Origin.exe processes
        pids = get_all_process_ids("Origin.exe")
        if (not pids):
            pids = get_all_process_ids("Godswar.exe")
        new_pids = set(pids)
        
        # Remove PIDs that no longer exist from disconnect monitor
        removed_pids = old_pids - new_pids
        for pid in removed_pids:
            self.disconnect_monitor.remove_pid(pid)
        
        if not pids:
            tk.Label(self.accounts_frame, text="No Origin.exe processes found", 
                    fg="#ff4444", font=("Segoe UI", 11),
                    bg=self.bg_light).pack(pady=30)
            self.log("No Origin.exe processes found")
            return
        
        self.log(f"Found {len(pids)} Origin.exe process(es)")
        
        # Add new PIDs to disconnect monitor
        for pid in pids:
            self.disconnect_monitor.add_pid(pid)
        
        # Create header row with proper grid expansion
        header_frame = tk.Frame(self.accounts_frame, bg=self.bg_medium)
        header_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Configure column weights for proper expansion (Character Name expands, others fixed)
        headers = ["Character Name", "Pets Done", "Status", "Ignore", "Track"]
        col_weights = [3, 1, 1, 1, 1]  # Character Name takes 3x space
        
        for col, (header, weight) in enumerate(zip(headers, col_weights)):
            anchor = tk.W if col == 0 else tk.CENTER
            lbl = tk.Label(header_frame, text=header, font=("Segoe UI", 11, "bold"),
                          bg=self.bg_medium, fg=self.text_secondary, anchor=anchor)
            lbl.grid(row=0, column=col, sticky="ew", padx=5, pady=10)
            header_frame.columnconfigure(col, weight=weight)
        
        # Add each account
        for i, pid in enumerate(pids):
            base_addr = get_module_base_address(pid)
            player_name = read_player_name(pid, base_addr)
            
            # Alternate row colors
            row_bg = self.bg_light if i % 2 == 0 else self.bg_medium
            
            account_frame = tk.Frame(self.accounts_frame, bg=row_bg)
            account_frame.pack(fill=tk.X, padx=5)
            
            # Configure columns with same weights as header
            for col, weight in enumerate(col_weights):
                account_frame.columnconfigure(col, weight=weight)
            
            # Character name (column 0)
            tk.Label(account_frame, text=player_name, font=("Segoe UI", 11),
                    anchor=tk.W, bg=row_bg, fg=self.text_color).grid(
                    row=0, column=0, sticky="ew", padx=5, pady=12)
            
            # Pets done label (column 1)
            pets_done_label = tk.Label(account_frame, text="-", font=("Segoe UI", 10),
                                      bg=row_bg, fg=self.text_secondary, anchor=tk.CENTER)
            pets_done_label.grid(row=0, column=1, sticky="ew", padx=5, pady=12)
            
            # Status label (column 2)
            status_label = tk.Label(account_frame, text="Idle", font=("Segoe UI", 10),
                                   bg=row_bg, fg=self.text_secondary, anchor=tk.CENTER)
            status_label.grid(row=0, column=2, sticky="ew", padx=5, pady=12)
            
            # Ignore button (column 3)
            ignored_count = len(self.ignored_pets.get(player_name, []))
            ignore_text = f"⚙ {ignored_count}" if ignored_count > 0 else "⚙"
            ignore_color = self.accent_orange if ignored_count > 0 else self.text_secondary
            
            ignore_btn = tk.Button(account_frame, text=ignore_text,
                                  font=("Segoe UI", 9),
                                  bg=row_bg, fg=ignore_color,
                                  activebackground=row_bg,
                                  activeforeground=self.accent_orange,
                                  relief=tk.FLAT, borderwidth=0,
                                  cursor="hand2",
                                  command=lambda p=pid: self._show_ignore_pets_dialog(p))
            ignore_btn.grid(row=0, column=3, pady=12)
            
            # Track checkbox (column 4)
            track_var = tk.BooleanVar(value=False)
            track_check = tk.Checkbutton(account_frame, variable=track_var,
                                        bg=row_bg, activebackground=row_bg,
                                        selectcolor=self.bg_dark,
                                        fg=self.accent_green,
                                        activeforeground=self.accent_green,
                                        cursor="hand2")
            track_check.grid(row=0, column=4, pady=12)
            
            # Store account info
            self.accounts[pid] = {
                'name': player_name,
                'track': track_var,
                'pets_done_label': pets_done_label,
                'status_label': status_label,
                'ignore_btn': ignore_btn,
                'pets_done': 0,
                'status': 'Idle'
            }
    
    def on_start(self):
        """Handle Start button click"""
        # Check if already running
        if hasattr(self, 'is_running') and self.is_running:
            messagebox.showinfo("Info", "Management is already running!")
            return
        
        # Get tracked accounts
        tracked = [pid for pid, info in self.accounts.items() if info['track'].get()]
        
        if not tracked:
            messagebox.showwarning("Warning", "No accounts selected for tracking!")
            return
        
        # Set running state
        self.is_running = True
        self.start_btn.config(text="⏳ Running...", bg=self.accent_orange, state=tk.DISABLED)
        
        self.log(f"Starting management for {len(tracked)} account(s)")
        
        # Get objective level and calculate required EXP
        try:
            objective_level = int(self.objective_level_var.get())
            if objective_level < 1 or objective_level > 120:
                messagebox.showerror("Error", "Objective Level must be between 1 and 120!")
                return
            objective_exp = get_exp_for_level(objective_level)
        except ValueError:
            messagebox.showerror("Error", "Invalid Objective Level value!")
            return
        
        self.log(f"Objective Level: {objective_level} (requires {objective_exp:,} EXP)")
        
        # Get game folder path
        game_folder = self.game_folder_var.get()
        if not os.path.exists(game_folder):
            self.log(f"⚠️ Warning: Game folder not found: {game_folder}")
            messagebox.showerror("Invalid Path", 
                               f"Game folder does not exist:\n{game_folder}\n\n"
                               "Please set the correct path to the User settings folder.")
            return
        
        # Check if analysis was already done
        analysis_results = None
        if hasattr(self, 'analysis_results') and self.analysis_results:
            # Use existing analysis
            analysis_results = self.analysis_results
            self.log("Using existing analysis results")
        else:
            # Ask if user wants to analyze first
            analyze_first = messagebox.askyesno(
                "Analyze Pets?",
                "Do you want to analyze pets before starting?\n\n"
                "Yes: Analyze pets to find the closest to completion\n"
                "No: Process pets sequentially (1→2→3...→8)"
            )
            
            if analyze_first:
                self.log("Starting pet analysis...")
                
                # Mark all tracked accounts as Analyzing
                for pid in tracked:
                    self.update_account_status(pid, status="Analyzing", pets_done=0)
                
                # Run analysis with game folder and GUI callback
                analysis_results = analyze_pets(tracked, self.accounts, objective_level,
                                              game_folder_path=game_folder, gui_callback=self,
                                              ignored_pets=self.ignored_pets)
                self.analysis_results = analysis_results
                
                # Update final status for all accounts
                for pid, result in analysis_results.items():
                    if result.get('error'):
                        self.update_account_status(pid, status="Error", pets_done=0)
                        self.log(f"❌ {result['name']}: {result['status']}")
                    else:
                        # Count pets that are already at objective level or have enough exp
                        completed_count = 0
                        if result.get('pets'):
                            for pet in result['pets']:
                                if pet['level'] >= objective_level or pet['current_exp'] >= objective_exp:
                                    completed_count += 1
                        
                        pets_count = len(result.get('pets', []))
                        self.update_account_status(pid, status="Analyzed", pets_done=completed_count)
                        self.log(f"✓ {result['name']}: Analysis complete ({pets_count}/8 pets found, {completed_count} ready)")
                
                # Check if analysis was successful
                successful = sum(1 for r in analysis_results.values() if not r.get('error', True))
                if successful == 0:
                    self.log("Analysis failed for all accounts")
                    messagebox.showerror("Analysis Failed", 
                                       "Could not analyze any accounts.\n"
                                       "Please check that Origin.exe is running.")
                    return
                self.log(f"Analysis complete: {successful} account(s) successful")
            else:
                self.log("Skipping analysis - sequential mode")
        
        # Start pet management in a separate thread
        import threading
        management_thread = threading.Thread(
            target=self._run_management,
            args=(tracked, objective_level, analysis_results, game_folder),
            daemon=True
        )
        management_thread.start()
        
        self.log("Pet management started (Press D+F to stop)")
    
    def _run_management(self, tracked, objective_level, analysis_results, game_folder):
        """Run management process in background thread"""
        results = start_pet_management(tracked, self.accounts, objective_level, 
                                      analysis_results, game_folder_path=game_folder, 
                                      gui_callback=self, ignored_pets=self.ignored_pets)
        
        # Show results in main thread
        self.root.after(0, lambda: self._show_management_results(results))
    
    def _show_management_results(self, results):
        """Show management results in logs"""
        # Restore Start button
        self.is_running = False
        self.start_btn.config(text="▶ Start", bg=self.accent_green, state=tk.NORMAL)
        
        self.log("=" * 40)
        self.log("Pet Management Complete")
        self.log("=" * 40)
        
        for pid, data in results.items():
            self.log(f"Account: {data['name']}")
            self.log(f"  Status: {data['status']}")
            self.log(f"  Pets Completed: {data['pets_completed']}/8")


def main():
    root = tk.Tk()
    app = PetFactoryGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
