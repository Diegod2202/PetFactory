"""
Pet Factory - Main GUI Application
Manages the user interface and coordinates pet management operations
"""
import tkinter as tk
from tkinter import messagebox

# Import custom modules
from memory_reader import get_all_process_ids, get_module_base_address, read_player_name
from pet_analyzer import analyze_pets
from pet_manager import start_pet_management, format_management_results


class PetFactoryGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Pet Factory")
        self.root.geometry("650x700")
        
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
        
        # Header
        header_frame = tk.Frame(root, bg=self.bg_medium, pady=15)
        header_frame.pack(fill=tk.X)
        
        tk.Label(header_frame, text="🐾 Pet Factory", font=("Segoe UI", 24, "bold"), 
                bg=self.bg_medium, fg=self.accent_green).pack()
        
        # Main container
        main_frame = tk.Frame(root, padx=25, pady=25, bg=self.bg_dark)
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
        objective_frame.pack(fill=tk.X, pady=(0, 25))
        
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
        
        # Buttons section
        buttons_frame = tk.Frame(main_frame, bg=self.bg_dark)
        buttons_frame.pack(fill=tk.X)
        
        self.start_btn = tk.Button(buttons_frame, text="▶ Start", 
                                   command=self.on_start,
                                   bg=self.accent_green, fg="#000000", 
                                   font=("Segoe UI", 13, "bold"),
                                   width=18, height=2,
                                   relief=tk.FLAT,
                                   cursor="hand2",
                                   activebackground="#00dd77",
                                   activeforeground="#000000")
        self.start_btn.pack(side=tk.LEFT, padx=(0, 15))
        
        self.analyze_btn = tk.Button(buttons_frame, text="🔍 Analyze", 
                                     command=self.on_analyze,
                                     bg=self.accent_blue, fg="#000000", 
                                     font=("Segoe UI", 13, "bold"),
                                     width=18, height=2,
                                     relief=tk.FLAT,
                                     cursor="hand2",
                                     activebackground="#0099dd",
                                     activeforeground="#000000")
        self.analyze_btn.pack(side=tk.LEFT)
        
        # Load accounts on startup
        self.refresh_accounts()
    
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
            return
        
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
        
        # Get objective EXP
        try:
            objective_exp = int(self.objective_exp_var.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid Objective EXP value!")
            return
        
        # Start pet management process
        results = start_pet_management(tracked, self.accounts, objective_exp)
        message = format_management_results(results, objective_exp)
        messagebox.showinfo("Pet Management", message)
    
    def on_analyze(self):
        """Handle Analyze button click"""
        # Get tracked accounts
        tracked = [pid for pid, info in self.accounts.items() if info['track'].get()]
        
        if not tracked:
            messagebox.showwarning("Warning", "No accounts selected for tracking!")
            return
        
        # Analyze pets
        self.analysis_results = analyze_pets(tracked, self.accounts)
        
        # Check if analysis was successful
        successful = sum(1 for r in self.analysis_results.values() if not r.get('error', True))
        
        if successful > 0:
            messagebox.showinfo("Analysis Complete", 
                              f"Successfully analyzed {successful} account(s).\n"
                              f"Data ready for pet management.")
        else:
            messagebox.showerror("Analysis Failed", 
                               "Could not analyze any accounts.\n"
                               "Please check that Origin.exe is running.")


def main():
    root = tk.Tk()
    app = PetFactoryGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
