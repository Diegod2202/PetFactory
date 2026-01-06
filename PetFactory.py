"""
Pet Factory - Main GUI Application
Manages the user interface and coordinates pet management operations
"""
import tkinter as tk
from tkinter import messagebox, scrolledtext
from datetime import datetime

# Import custom modules
from memory_reader import get_all_process_ids, get_module_base_address, read_player_name
from pet_analyzer import analyze_pets
from pet_manager import start_pet_management


class PetFactoryGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Pet Factory")
        self.root.geometry("1100x750")
        
        # Dark theme colors
        self.bg_dark = "#1a1a1a"
        self.bg_medium = "#2d2d2d"
        self.bg_light = "#3d3d3d"
        self.accent_green = "#00ff88"
        self.accent_blue = "#00b4ff"
        self.text_color = "#e0e0e0"
        self.text_secondary = "#a0a0a0"
        
        # Configure root background
        self.root.configure(bg=self.bg_dark)
        
        # Variables
        self.accounts = {}  # {pid: {'name': str, 'track': BooleanVar}}
        self.analysis_results = {}  # Store analysis results for Start to use
        
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
        
        # Load accounts on startup
        self.refresh_accounts()
    
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
        accounts_label = tk.Label(main_frame, text="Origin Accounts:", 
                                 font=("Segoe UI", 13, "bold"),
                                 bg=self.bg_dark, fg=self.text_color)
        accounts_label.pack(anchor=tk.W, pady=(0, 12))
        
        # Frame for accounts (no scroll)
        self.accounts_frame = tk.Frame(main_frame, bg=self.bg_light, relief=tk.FLAT, borderwidth=0)
        self.accounts_frame.pack(fill=tk.X, pady=(0, 20))
        
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
                               text="⌨ Press D+F to stop the process at any time",
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
        
        # Clear logs button
        clear_btn = tk.Button(parent, text="Clear Logs",
                             command=self.clear_logs,
                             bg=self.bg_light, fg=self.text_color,
                             font=("Segoe UI", 10),
                             relief=tk.FLAT,
                             cursor="hand2")
        clear_btn.pack(pady=(10, 0))
        
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
    
    def refresh_accounts(self):
        """Refresh the list of Origin.exe processes"""
        # Clear current list
        for widget in self.accounts_frame.winfo_children():
            widget.destroy()
        
        self.accounts.clear()
        
        # Get all Origin.exe processes
        pids = get_all_process_ids("Origin.exe")
        
        if not pids:
            tk.Label(self.accounts_frame, text="No Origin.exe processes found", 
                    fg="#ff4444", font=("Segoe UI", 11),
                    bg=self.bg_light).pack(pady=30)
            self.log("No Origin.exe processes found")
            return
        
        self.log(f"Found {len(pids)} Origin.exe process(es)")
        
        # Create header
        header_frame = tk.Frame(self.accounts_frame, pady=10, bg=self.bg_medium)
        header_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(header_frame, text="Character Name", font=("Segoe UI", 11, "bold"), 
                width=35, bg=self.bg_medium, fg=self.text_secondary,
                anchor=tk.W).pack(side=tk.LEFT, padx=10)
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
                    width=35, anchor=tk.W, bg=row_bg, fg=self.text_color).pack(side=tk.LEFT, padx=10)
            
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
                'track': track_var
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
                # Run analysis
                analysis_results = analyze_pets(tracked, self.accounts)
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
            args=(tracked, objective_exp, objective_level, analysis_results),
            daemon=True
        )
        management_thread.start()
        
        self.log("Pet management started (Press D+F to stop)")
    
    def _run_management(self, tracked, objective_exp, objective_level, analysis_results):
        """Run management process in background thread"""
        results = start_pet_management(tracked, self.accounts, objective_exp, objective_level, analysis_results)
        
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
        
        self.log(f"Starting analysis for {len(tracked)} account(s)...")
        
        # Analyze pets
        self.analysis_results = analyze_pets(tracked, self.accounts)
        
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
