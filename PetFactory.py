"""
Pet Factory - Main GUI Application
Manages the user interface and coordinates pet management operations
"""
import tkinter as tk
from tkinter import messagebox, scrolledtext
from datetime import datetime
import os
import sys
import keyboard

# Import custom modules
from memory_reader import get_all_process_ids, get_module_base_address, read_player_name
from pet_analyzer import analyze_pets
from pet_manager import start_pet_management
from disconnect_monitor import DisconnectMonitor


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
            keyboard.add_hotkey('d+q', self._quit_app)
            self.log("Hotkey registered: D+Q to quit application")
        except Exception as e:
            self.log(f"Warning: Could not register D+Q hotkey: {e}")
    
    def _quit_app(self):
        """Quit the application"""
        self.log("D+Q pressed - Closing application...")
        try:
            keyboard.unhook_all()
        except:
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
        
        # Objective EXP section
        objective_frame = tk.Frame(main_frame, bg=self.bg_dark)
        objective_frame.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(objective_frame, text="Objective EXP:", 
                font=("Segoe UI", 11, "bold"),
                bg=self.bg_dark, fg=self.text_color).pack(side=tk.LEFT, padx=(0, 15))
        
        self.objective_exp_var = tk.StringVar(value="10000000")
        objective_entry = tk.Entry(objective_frame, textvariable=self.objective_exp_var, 
                                  font=("Segoe UI", 11), width=18,
                                  bg=self.bg_medium, fg=self.text_color,
                                  insertbackground=self.text_color,
                                  relief=tk.FLAT, borderwidth=5)
        objective_entry.pack(side=tk.LEFT)
        
        # Objective Level section
        level_frame = tk.Frame(main_frame, bg=self.bg_dark)
        level_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(level_frame, text="Objective Level:", 
                font=("Segoe UI", 11, "bold"),
                bg=self.bg_dark, fg=self.text_color).pack(side=tk.LEFT, padx=(0, 15))
        
        self.objective_level_var = tk.StringVar(value="30")
        level_entry = tk.Entry(level_frame, textvariable=self.objective_level_var, 
                              font=("Segoe UI", 11), width=18,
                              bg=self.bg_medium, fg=self.text_color,
                              insertbackground=self.text_color,
                              relief=tk.FLAT, borderwidth=5)
        level_entry.pack(side=tk.LEFT)
        
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
                                   width=22, height=2,
                                   relief=tk.FLAT,
                                   cursor="hand2",
                                   activebackground="#00dd77",
                                   activeforeground="#000000")
        self.start_btn.pack(side=tk.LEFT, padx=(0, 15))
        
        self.analyze_btn = tk.Button(buttons_frame, text="🔍 Analyze", 
                                     command=self.on_analyze,
                                     bg=self.accent_blue, fg="#000000", 
                                     font=("Segoe UI", 14, "bold"),
                                     width=22, height=2,
                                     relief=tk.FLAT,
                                     cursor="hand2",
                                     activebackground="#0099dd",
                                     activeforeground="#000000")
        self.analyze_btn.pack(side=tk.LEFT)
    
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
        except:
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
        
        # Create header
        header_frame = tk.Frame(self.accounts_frame, pady=10, bg=self.bg_medium)
        header_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(header_frame, text="Character Name", font=("Segoe UI", 11, "bold"), 
                width=20, bg=self.bg_medium, fg=self.text_secondary,
                anchor=tk.W).pack(side=tk.LEFT, padx=10)
        tk.Label(header_frame, text="Pets Done", font=("Segoe UI", 11, "bold"), 
                width=10, bg=self.bg_medium, fg=self.text_secondary).pack(side=tk.LEFT)
        tk.Label(header_frame, text="Status", font=("Segoe UI", 11, "bold"), 
                width=15, bg=self.bg_medium, fg=self.text_secondary).pack(side=tk.LEFT)
        tk.Label(header_frame, text="Track", font=("Segoe UI", 11, "bold"), 
                width=8, bg=self.bg_medium, fg=self.text_secondary).pack(side=tk.LEFT)
        
        # Add each account
        for i, pid in enumerate(pids):
            base_addr = get_module_base_address(pid)
            player_name = read_player_name(pid, base_addr)
            
            # Alternate row colors
            row_bg = self.bg_light if i % 2 == 0 else self.bg_medium
            
            account_frame = tk.Frame(self.accounts_frame, pady=12, bg=row_bg)
            account_frame.pack(fill=tk.X, padx=5)
            
            # Character name
            tk.Label(account_frame, text=player_name, font=("Segoe UI", 11), 
                    width=20, anchor=tk.W, bg=row_bg, fg=self.text_color).pack(side=tk.LEFT, padx=10)
            
            # Pets done label
            pets_done_label = tk.Label(account_frame, text="-", font=("Segoe UI", 10),
                                      width=10, bg=row_bg, fg=self.text_secondary)
            pets_done_label.pack(side=tk.LEFT)
            
            # Status label
            status_label = tk.Label(account_frame, text="Idle", font=("Segoe UI", 10),
                                   width=15, bg=row_bg, fg=self.text_secondary)
            status_label.pack(side=tk.LEFT)
            
            # Track checkbox
            track_var = tk.BooleanVar(value=False)
            track_check = tk.Checkbutton(account_frame, variable=track_var,
                                        bg=row_bg, activebackground=row_bg,
                                        selectcolor=self.bg_dark,
                                        fg=self.accent_green,
                                        activeforeground=self.accent_green,
                                        cursor="hand2")
            track_check.pack(side=tk.LEFT, padx=40)
            
            # Store account info
            self.accounts[pid] = {
                'name': player_name,
                'track': track_var,
                'pets_done_label': pets_done_label,
                'status_label': status_label,
                'pets_done': 0,
                'status': 'Idle'
            }
    
    def on_start(self):
        """Handle Start button click"""
        # Get tracked accounts
        tracked = [pid for pid, info in self.accounts.items() if info['track'].get()]
        
        if not tracked:
            messagebox.showwarning("Warning", "No accounts selected for tracking!")
            return
        
        self.log(f"Starting management for {len(tracked)} account(s)")
        
        # Get objective EXP and Level
        try:
            objective_exp = int(self.objective_exp_var.get())
            objective_level = int(self.objective_level_var.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid Objective EXP or Level value!")
            return
        
        self.log(f"Objective EXP: {objective_exp:,}, Level: {objective_level}")
        
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
                # Run analysis with game folder
                analysis_results = analyze_pets(tracked, self.accounts, game_folder_path=game_folder)
                self.analysis_results = analysis_results
                
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
            args=(tracked, objective_exp, objective_level, analysis_results, game_folder),
            daemon=True
        )
        management_thread.start()
        
        self.log("Pet management started (Press D+F to stop)")
    
    def _run_management(self, tracked, objective_exp, objective_level, analysis_results, game_folder):
        """Run management process in background thread"""
        results = start_pet_management(tracked, self.accounts, objective_exp, objective_level, 
                                      analysis_results, game_folder_path=game_folder, 
                                      gui_callback=self)
        
        # Show results in main thread
        self.root.after(0, lambda: self._show_management_results(results))
    
    def _show_management_results(self, results):
        """Show management results in logs"""
        self.log("=" * 40)
        self.log("Pet Management Complete")
        self.log("=" * 40)
        
        for pid, data in results.items():
            self.log(f"Account: {data['name']}")
            self.log(f"  Status: {data['status']}")
            self.log(f"  Pets Completed: {data['pets_completed']}/8")
    
    def on_analyze(self):
        """Handle Analyze button click"""
        # Get tracked accounts
        tracked = [pid for pid, info in self.accounts.items() if info['track'].get()]
        
        if not tracked:
            messagebox.showwarning("Warning", "No accounts selected for tracking!")
            return
        
        # Get objective values
        try:
            objective_exp = int(self.objective_exp_var.get()) if self.objective_exp_var.get() else None
            objective_level = int(self.objective_level_var.get()) if self.objective_level_var.get() else None
        except ValueError:
            self.log("Invalid objective values, analyzing without upgrades")
            objective_exp = None
            objective_level = None
        
        self.log(f"Starting analysis for {len(tracked)} account(s)...")
        
        # Get game folder path
        game_folder = self.game_folder_var.get()
        if not os.path.exists(game_folder):
            self.log(f"⚠️ Warning: Game folder not found: {game_folder}")
            messagebox.showerror("Invalid Path", 
                               f"Game folder does not exist:\n{game_folder}\n\n"
                               "Please set the correct path to the User settings folder.")
            return
        
        # Mark all tracked accounts as Analyzing
        for pid in tracked:
            self.update_account_status(pid, status="Analyzing", pets_done=0)
        
        # Analyze pets with objectives and game folder
        self.analysis_results = analyze_pets(tracked, self.accounts, objective_exp, objective_level, 
                                            game_folder_path=game_folder, gui_callback=self)
        
        # Update final status for all accounts
        for pid, result in self.analysis_results.items():
            if result.get('error'):
                self.update_account_status(pid, status="Error")
                self.log(f"❌ {result['name']}: {result['status']}")
            else:
                pets_count = len(result.get('pets', []))
                self.update_account_status(pid, status="Complete", pets_done=pets_count)
                self.log(f"✓ {result['name']}: {pets_count}/8 pets analyzed")
        
        # Check if analysis was successful
        successful = sum(1 for r in self.analysis_results.values() if not r.get('error', True))
        
        if successful > 0:
            self.log(f"Analysis complete: {successful} account(s) successful")
            self.log("Data ready for pet management")
        else:
            self.log("Analysis failed for all accounts")
            messagebox.showerror("Analysis Failed", 
                               "Could not analyze any accounts.\n"
                               "Please check that Origin.exe is running.")


def main():
    root = tk.Tk()
    app = PetFactoryGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
