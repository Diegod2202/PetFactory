"""
Pet Manager Module
Handles the pet management process for tracked accounts
"""
import win32gui
import win32con
import win32process
import pyautogui
import pygetwindow as gw
import time
import os
import re
import keyboard
import threading
from file_cleaner import clean_pet_files
from pet_data import get_exp_for_level
from ui_assets import get_pet_coord, get_ui_coord

# Disable PyAutoGUI fail-safe
pyautogui.FAILSAFE = False




# Settings
CLICK_DELAY = 0.45
UPGRADE_CLICK_DELAY = 0.2
ALERT_CHECK_INTERVAL = 10  # seconds
PETEXP_FILE_PATH = r"C:\Godswar Origin\Localization\en_us\Settings\User"

# Global pause flag
is_paused = False
management_active = False


def check_stop():
    """Check if paused and wait until resumed"""
    global is_paused
    while is_paused:
        time.sleep(0.1)
    return False


def reset_stop_flag():
    """Reset the pause flag"""
    global is_paused
    is_paused = False


def get_window_by_pid(pid):
    """Find window handle by process ID"""
    def callback(hwnd, hwnds):
        if win32gui.IsWindowVisible(hwnd):
            _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
            if found_pid == pid:
                hwnds.append(hwnd)
        return True
    
    hwnds = []
    win32gui.EnumWindows(callback, hwnds)
    return hwnds[0] if hwnds else None


def bring_window_to_front(hwnd):
    """Bring window to front and get pygetwindow object"""
    if win32gui.IsIconic(hwnd):
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    win32gui.SetForegroundWindow(hwnd)
    time.sleep(0.8)
    
    try:
        title = win32gui.GetWindowText(hwnd)
        windows = gw.getWindowsWithTitle(title)
        if windows:
            window = windows[0]
            if window.isMinimized:
                window.restore()
            window.activate()
            time.sleep(0.3)
            return window
    except:
        pass
    
    return None


def minimize_window(hwnd):
    """Minimize window"""
    win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
    time.sleep(0.3)


def click_at_window_position(window, rel_x, rel_y, delay=None, button='left'):
    """Click at position relative to window"""
    if check_stop():
        return False
    
    if not window:
        return False
    
    screen_x = window.left + rel_x
    screen_y = window.top + rel_y
    
    # Validate coordinates are within screen bounds
    screen_width, screen_height = pyautogui.size()
    if screen_x < 0 or screen_x >= screen_width or screen_y < 0 or screen_y >= screen_height:
        print(f"Warning: Click coordinates ({screen_x}, {screen_y}) out of bounds")
        return False
    
    pyautogui.moveTo(screen_x, screen_y, duration=0.1)
    time.sleep(0.1)
    pyautogui.click(screen_x, screen_y, button=button)
    time.sleep(delay if delay else CLICK_DELAY)
    return True


def parse_petalert_file(file_path):
    """
    Parse the petalert file and extract information
    
    Format:
    Name: Damaged
    Database ID: 4084
    Pet Name: (ID: 68516)
    Pet Level: 1
    PET EXP ACTUAL: 10013326
    Target EXP: 10000000
    Timestamp: 2026-01-06 06:33:20
    
    Returns:
        dict: Alert information or None if parse failed
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        alert_data = {}
        for line in content.strip().split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                alert_data[key.strip()] = value.strip()
        
        return {
            'name': alert_data.get('Name', ''),
            'database_id': alert_data.get('Database ID', ''),
            'pet_id': alert_data.get('Pet Name', ''),
            'pet_level': int(alert_data.get('Pet Level', 0)),
            'current_exp': int(alert_data.get('PET EXP ACTUAL', 0)),
            'target_exp': int(alert_data.get('Target EXP', 0)),
            'timestamp': alert_data.get('Timestamp', '')
        }
    except Exception:
        return None


def delete_alert_file(account_name, alert_path=None):
    """Delete the petalert file for a specific account"""
    path = alert_path if alert_path else PETEXP_FILE_PATH
    file_path = os.path.join(path, f"{account_name}_petalert.txt")
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception:
        pass


def set_carry_for_pet(window, pet_index):
    """
    Set a pet to carry mode
    
    Args:
        window: pygetwindow Window object
        pet_index: Index of the pet (0-7)
    
    Returns:
        bool: Success status
    """
    # Open pet tab
    pet_tab_coords = get_ui_coord(window, "PET_TAB")
    if not pet_tab_coords or not click_at_window_position(window, *pet_tab_coords):
        return False
    
    # Click on pet
    pet_coords = get_pet_coord(window, pet_index)
    if not pet_coords or not click_at_window_position(window, *pet_coords):
        return False
    
    # Click Carry
    carry_coords = get_ui_coord(window, "CARRY")
    if not carry_coords or not click_at_window_position(window, *carry_coords):
        return False
    
    # Open Details so the game can detect when pet is ready
    details_coords = get_ui_coord(window, "DETAILS")
    if not details_coords or not click_at_window_position(window, *details_coords):
        return False
    
    # Close pet tab
    pet_tab_coords2 = get_ui_coord(window, "PET_TAB")
    if not pet_tab_coords2 or not click_at_window_position(window, *pet_tab_coords2):
        return False
    
    return True


def process_pet_alert(window, account_name, current_level, objective_level, alert_path=None):
    """
    Process a pet alert: open details, upgrade to objective level, close
    
    Args:
        window: pygetwindow Window object
        account_name: Name of the account
        current_level: Current level of the pet (from alert file)
        objective_level: Target level to reach
        alert_path: Path to alert files
    
    Returns:
        bool: Success status
    """
    # Calculate how many upgrades needed
    upgrade_clicks = max(0, objective_level - current_level)
    
    if upgrade_clicks == 0:
        # Pet already at or above objective level
        delete_alert_file(account_name, alert_path)
        return True
    
    # Click upgrade button (Details tab is already open) (dynamic amount based on level difference)
    upgrade_coords = get_ui_coord(window, "UPGRADE")
    if not upgrade_coords:
        return False
    for i in range(upgrade_clicks):
        if not click_at_window_position(window, *upgrade_coords, delay=UPGRADE_CLICK_DELAY):
            return False
    
    # Close pet details
    close_coords = get_ui_coord(window, "CLOSE_PET")
    if not close_coords or not click_at_window_position(window, *close_coords):
        return False
    
    # Delete the alert file
    delete_alert_file(account_name, alert_path)
    
    return True


def find_next_pet_to_carry(account_state, analysis_data, objective_level):
    """
    Find the next pet to set as carry
    
    Args:
        account_state: Current state of the account
        analysis_data: Analysis data if available
        objective_level: Target level for pets
    
    Returns:
        int: Pet index (0-7) or None if all pets completed
    """
    objective_exp = get_exp_for_level(objective_level)
    
    if analysis_data:
        # Find pet closest to objective that isn't completed and below objective level/exp
        best_pet = None
        best_exp = -1
        
        for i, pet in enumerate(analysis_data):
            # Skip if already completed or already at/above objective level or exp
            if account_state['completed_pets'][i]:
                continue
            
            if pet['level'] >= objective_level or pet['current_exp'] >= objective_exp:
                account_state['completed_pets'][i] = True  # Mark as completed if at level/exp
                continue
            
            if pet['current_exp'] > best_exp:
                best_exp = pet['current_exp']
                best_pet = i
        
        return best_pet
    else:
        # Sequential mode: find first non-completed pet
        for i in range(8):
            if not account_state['completed_pets'][i]:
                return i
        return None


def monitor_alerts(accounts_state, accounts_info, objective_level, gui_callback=None, ignored_pets=None):
    """
    Monitor for alert files and process them
    Runs in a separate thread
    """
    global management_active
    
    if ignored_pets is None:
        ignored_pets = {}
    
    def update_gui_status(pid, status=None, pets_done=None, total_pets=None):
        """Thread-safe GUI update"""
        if gui_callback and hasattr(gui_callback, 'root'):
            gui_callback.root.after(0, lambda: gui_callback.update_account_status(pid, status=status, pets_done=pets_done, total_pets=total_pets))
    
    def log_message(msg):
        """Thread-safe log"""
        if gui_callback and hasattr(gui_callback, 'root'):
            gui_callback.root.after(0, lambda: gui_callback.log(msg))
    
    while management_active and not check_stop():
        for pid, state in accounts_state.items():
            if check_stop():
                break
            
            if state['all_pets_completed']:
                continue
            
            # Check if disconnected
            if gui_callback and hasattr(gui_callback, 'disconnect_monitor'):
                if gui_callback.disconnect_monitor.is_disconnected(pid):
                    state['all_pets_completed'] = True
                    update_gui_status(pid, status="Disconnected")
                    continue
            
            account_name = accounts_info.get(pid, {}).get('name', '')
            alert_path = state.get('alert_path', PETEXP_FILE_PATH)
            alert_file = os.path.join(alert_path, f"{account_name}_petalert.txt")
            
            # Check if alert file exists
            if os.path.exists(alert_file):
                # Parse alert
                alert_data = parse_petalert_file(alert_file)
                if not alert_data:
                    continue
                
                # Get window
                hwnd = get_window_by_pid(pid)
                if not hwnd:
                    continue
                
                window = bring_window_to_front(hwnd)
                if not window:
                    continue
                
                # Update status - Upgrading
                current_pet = state['current_pet_index']
                pet_num = current_pet + 1 if current_pet is not None else "?"
                current_level = alert_data.get('pet_level', 1)
                upgrade_count = max(0, objective_level - current_level)
                update_gui_status(pid, status=f"Upgrading Pet {pet_num} (+{upgrade_count} lvls)")
                log_message(f"⬆️ {account_name}: Upgrading Pet {pet_num} from Lv{current_level} to Lv{objective_level}")
                
                # Process the alert with current level for dynamic upgrades
                if process_pet_alert(window, account_name, current_level, objective_level, alert_path):
                    # Mark current pet as completed
                    if current_pet is not None:
                        state['completed_pets'][current_pet] = True
                    
                    # Update pets done count (excluding ignored pets from both completed and total)
                    ignored_count = len(state.get('ignored_pets', []))
                    total_pets = 8 - ignored_count
                    # Count completed pets that are NOT ignored
                    completed_count = sum(1 for i, done in enumerate(state['completed_pets']) if done and i not in state.get('ignored_pets', []))
                    update_gui_status(pid, pets_done=completed_count, total_pets=total_pets)
                    log_message(f"✅ {account_name}: Pet {pet_num} reached Lv{objective_level} ({completed_count}/{total_pets})")
                    
                    # Find next pet
                    next_pet = find_next_pet_to_carry(state, state.get('analysis_data'), objective_level)
                    
                    if next_pet is not None:
                        # Update status - Setting carry
                        update_gui_status(pid, status=f"Setting Pet {next_pet + 1}")
                        
                        # Set next pet to carry
                        if set_carry_for_pet(window, next_pet):
                            state['current_pet_index'] = next_pet
                            update_gui_status(pid, status="Waiting")
                    else:
                        # All pets completed
                        state['all_pets_completed'] = True
                        ignored_count = len(state.get('ignored_pets', []))
                        total_pets = 8 - ignored_count
                        update_gui_status(pid, status="Complete", pets_done=total_pets, total_pets=total_pets)
                        log_message(f"🎉 {account_name}: All pets completed!")
                
                # Minimize window
                minimize_window(hwnd)
        
        # Wait before next check
        time.sleep(ALERT_CHECK_INTERVAL)


def start_pet_management(tracked_accounts, accounts_info, objective_level, 
                        analysis_results=None, game_folder_path=None, gui_callback=None,
                        ignored_pets=None):
    """
    Start the pet management process for selected accounts
    
    Args:
        tracked_accounts (list): List of PIDs to manage
        accounts_info (dict): Dictionary with account information {pid: {'name': str, ...}}
        objective_level (int): Target level for pets
        analysis_results (dict): Optional analysis results from analyze_pets()
        game_folder_path (str): Path to the game User settings folder
        gui_callback: Optional GUI object to check disconnect status
        ignored_pets (dict): Dict of {character_name: [list of ignored pet indices]}
    
    Returns:
        dict: Management results for each account
    """
    global is_paused, management_active
    reset_stop_flag()
    management_active = True
    
    if ignored_pets is None:
        ignored_pets = {}
    
    # Calculate objective EXP from level
    objective_exp = get_exp_for_level(objective_level)
    
    # Use provided path or default
    petalert_path = game_folder_path if game_folder_path else PETEXP_FILE_PATH
    
    # Clean up any existing pet files before starting
    clean_pet_files()
    
    # Initialize account states
    accounts_state = {}
    for pid in tracked_accounts:
        account_name = accounts_info.get(pid, {}).get('name', '')
        analysis_data = None
        carry_pet_index = None  # Will be set if analysis already determined carry
        completed_pets = [False] * 8
        
        # Get ignored pets for this account
        account_ignored = ignored_pets.get(account_name, [])
        
        # Mark ignored pets as completed so they're never selected
        for i in account_ignored:
            if 0 <= i < 8:
                completed_pets[i] = True
        
        if analysis_results and pid in analysis_results:
            result = analysis_results[pid]
            if not result.get('error') and result.get('all_pets'):
                # Use all_pets (unfiltered) for index-based operations
                analysis_data = result.get('all_pets', result.get('pets', []))
                # Get carry pet index from analysis (if already set)
                carry_pet_index = result.get('carry_pet_index')
                # Mark pets at or above objective level/exp as completed
                for i, pet in enumerate(analysis_data):
                    if i in account_ignored:
                        continue  # Already marked
                    if pet is None:
                        continue  # Skip None entries (ignored pets)
                    if pet['level'] >= objective_level or pet['current_exp'] >= objective_exp:
                        completed_pets[i] = True
        
        accounts_state[pid] = {
            'name': account_name,
            'analysis_data': analysis_data,
            'completed_pets': completed_pets,
            'ignored_pets': account_ignored,
            'carry_pet_index': carry_pet_index,  # Store carry index from analysis
            'current_pet_index': None,
            'all_pets_completed': False,
            'alert_path': petalert_path
        }
    
    # Helper for thread-safe GUI updates
    def update_gui_status(pid, status=None, pets_done=None, total_pets=None):
        if gui_callback and hasattr(gui_callback, 'root'):
            gui_callback.root.after(0, lambda: gui_callback.update_account_status(pid, status=status, pets_done=pets_done, total_pets=total_pets))
    
    def log_message(msg):
        if gui_callback and hasattr(gui_callback, 'root'):
            gui_callback.root.after(0, lambda: gui_callback.log(msg))
    
    # Set initial carry for each account
    for pid, state in accounts_state.items():
        if check_stop():
            break
        
        # Check if disconnected
        if gui_callback and hasattr(gui_callback, 'disconnect_monitor'):
            if gui_callback.disconnect_monitor.is_disconnected(pid):
                state['all_pets_completed'] = True
                update_gui_status(pid, status="Disconnected")
                continue
        
        account_name = state['name']
        
        # Calculate total pets for this account (excluding ignored)
        ignored_count = len(state.get('ignored_pets', []))
        total_pets = 8 - ignored_count
        
        # Check if analysis already set a pet to carry
        carry_from_analysis = state.get('carry_pet_index')
        
        if carry_from_analysis is not None:
            # Analysis already set carry, just update state without touching the window
            state['current_pet_index'] = carry_from_analysis
            completed_count = sum(1 for i, done in enumerate(state['completed_pets']) if done and i not in state.get('ignored_pets', []))
            update_gui_status(pid, status="Waiting", pets_done=completed_count, total_pets=total_pets)
            # Don't log again since analyzer already logged this
            continue
        
        # No analysis or no carry set - need to set it manually
        update_gui_status(pid, status="Starting")
        
        hwnd = get_window_by_pid(pid)
        if not hwnd:
            update_gui_status(pid, status="Window Error")
            continue
        
        window = bring_window_to_front(hwnd)
        if not window:
            update_gui_status(pid, status="Window Error")
            continue
        
        # Find first pet to carry
        next_pet = find_next_pet_to_carry(state, state['analysis_data'], objective_level)
        
        if next_pet is not None:
            # Update initial pets done count (excluding ignored pets)
            completed_count = sum(1 for i, done in enumerate(state['completed_pets']) if done and i not in state.get('ignored_pets', []))
            update_gui_status(pid, status=f"Setting Pet {next_pet + 1}", pets_done=completed_count, total_pets=total_pets)
            log_message(f"🎯 {account_name}: Setting Pet {next_pet + 1} to carry")
            
            if set_carry_for_pet(window, next_pet):
                state['current_pet_index'] = next_pet
                update_gui_status(pid, status="Waiting")
        else:
            # All pets already completed
            state['all_pets_completed'] = True
            update_gui_status(pid, status="Complete", pets_done=total_pets, total_pets=total_pets)
            log_message(f"🎉 {account_name}: All pets already complete!")
        
        minimize_window(hwnd)
    
    # Start monitoring thread
    monitor_thread = threading.Thread(
        target=monitor_alerts,
        args=(accounts_state, accounts_info, objective_level, gui_callback, ignored_pets),
        daemon=True
    )
    monitor_thread.start()
    
    # Wait for completion or stop
    while management_active and not check_stop():
        # Check if all accounts completed
        all_done = all(state['all_pets_completed'] for state in accounts_state.values())
        if all_done:
            management_active = False
            break
        
        time.sleep(1)
    
    management_active = False
    
    # Return results
    results = {}
    for pid, state in accounts_state.items():
        ignored_count = len(state.get('ignored_pets', []))
        total_pets = 8 - ignored_count
        # Count completed pets that are NOT ignored
        completed_count = sum(1 for i, done in enumerate(state['completed_pets']) if done and i not in state.get('ignored_pets', []))
        results[pid] = {
            'name': state['name'],
            'pets_completed': completed_count,
            'total_pets': total_pets,
            'all_completed': state['all_pets_completed'],
            'status': 'Completed' if state['all_pets_completed'] else f'{completed_count}/{total_pets} pets done'
        }
    
    return results


def format_management_results(results, objective_exp):
    """
    Format management results for display
    
    Args:
        results (dict): Management results from start_pet_management()
        objective_exp (int): Target experience points
    
    Returns:
        str: Formatted string ready for display
    """
    if not results:
        return "No results to display"
    
    lines = []
    lines.append(f"Starting pet management for {len(results)} account(s)")
    lines.append(f"Objective EXP: {objective_exp:,}\n")
    
    for pid, data in results.items():
        lines.append(f"Account: {data['name']}")
        lines.append(f"Status: {data['status']}")
        lines.append("")
    
    lines.append("Feature coming soon...")
    
    return "\n".join(lines)
