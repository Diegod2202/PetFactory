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


# Pet coordinates (relative to window)
PET_COORDINATES = [
    (172, 378),  # Pet 1
    (242, 378),  # Pet 2
    (307, 378),  # Pet 3
    (380, 378),  # Pet 4
    (172, 427),  # Pet 5
    (242, 427),  # Pet 6
    (307, 427),  # Pet 7
    (380, 427),  # Pet 8
]

# UI coordinates
PET_TAB_COORD = (885, 715)
CARRY_COORD = (183, 485)
DETAILS_COORD = (276, 488)
ALERT_DETAILS_COORD = (70, 134)
UPGRADE_COORD = (282, 555)
CLOSE_PET_COORD = (408, 109)

# Settings
CLICK_DELAY = 0.7
UPGRADE_CLICKS = 30
UPGRADE_CLICK_DELAY = 0.2
ALERT_CHECK_INTERVAL = 10  # seconds
PETEXP_FILE_PATH = r"C:\Godswar Origin\Localization\en_us\Settings\User"

# Global pause flag
is_paused = False
management_active = False


def setup_stop_hotkey():
    """Setup D+F hotkey to pause/resume the process"""
    keyboard.add_hotkey('d+f', lambda: toggle_pause())


def toggle_pause():
    """Toggle the pause state"""
    global is_paused
    is_paused = not is_paused
    print(f"Process {'PAUSED' if is_paused else 'RESUMED'}")


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
    except:
        return None


def delete_alert_file(account_name, alert_path=None):
    """Delete the petalert file for a specific account"""
    path = alert_path if alert_path else PETEXP_FILE_PATH
    file_path = os.path.join(path, f"{account_name}_petalert.txt")
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except:
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
    if not click_at_window_position(window, *PET_TAB_COORD):
        return False
    
    # Click on pet
    pet_x, pet_y = PET_COORDINATES[pet_index]
    if not click_at_window_position(window, pet_x, pet_y):
        return False
    
    # Click Carry
    if not click_at_window_position(window, *CARRY_COORD):
        return False
    
    # Open Details so the game can detect when pet is ready
    if not click_at_window_position(window, *DETAILS_COORD):
        return False
    
    # Close pet tab
    if not click_at_window_position(window, *PET_TAB_COORD):
        return False
    
    return True


def process_pet_alert(window, account_name, alert_path=None):
    """
    Process a pet alert: open details, upgrade 30 times, close
    
    Returns:
        bool: Success status
    """
    # Right-click on alert details
    if not click_at_window_position(window, *ALERT_DETAILS_COORD, button='right'):
        return False
    
    # Click upgrade button 30 times
    for i in range(UPGRADE_CLICKS):
        if not click_at_window_position(window, *UPGRADE_COORD, delay=UPGRADE_CLICK_DELAY):
            return False
    
    # Close pet details
    if not click_at_window_position(window, *CLOSE_PET_COORD):
        return False
    
    # Delete the alert file
    delete_alert_file(account_name, alert_path)
    
    return True


def find_next_pet_to_carry(account_state, analysis_data, objective_level, objective_exp):
    """
    Find the next pet to set as carry
    
    Args:
        account_state: Current state of the account
        analysis_data: Analysis data if available
        objective_level: Target level for pets
        objective_exp: Target experience for pets
    
    Returns:
        int: Pet index (0-7) or None if all pets completed
    """
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


def monitor_alerts(accounts_state, accounts_info, objective_level, objective_exp, gui_callback=None):
    """
    Monitor for alert files and process them
    Runs in a separate thread
    """
    global management_active
    
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
                
                # Process the alert
                if process_pet_alert(window, account_name, alert_path):
                    # Mark current pet as completed
                    current_pet = state['current_pet_index']
                    if current_pet is not None:
                        state['completed_pets'][current_pet] = True
                    
                    # Find next pet
                    next_pet = find_next_pet_to_carry(state, state.get('analysis_data'), objective_level, objective_exp)
                    
                    if next_pet is not None:
                        # Set next pet to carry
                        if set_carry_for_pet(window, next_pet):
                            state['current_pet_index'] = next_pet
                    else:
                        # All pets completed
                        state['all_pets_completed'] = True
                
                # Minimize window
                minimize_window(hwnd)
        
        # Wait before next check
        time.sleep(ALERT_CHECK_INTERVAL)


def start_pet_management(tracked_accounts, accounts_info, objective_exp, objective_level, 
                        analysis_results=None, game_folder_path=None, gui_callback=None):
    """
    Start the pet management process for selected accounts
    
    Args:
        tracked_accounts (list): List of PIDs to manage
        accounts_info (dict): Dictionary with account information {pid: {'name': str, ...}}
        objective_exp (int): Target experience points to achieve
        objective_level (int): Target level for pets
        analysis_results (dict): Optional analysis results from analyze_pets()
        game_folder_path (str): Path to the game User settings folder
        gui_callback: Optional GUI object to check disconnect status
    
    Returns:
        dict: Management results for each account
    """
    global is_paused, management_active
    reset_stop_flag()
    setup_stop_hotkey()
    management_active = True
    
    # Use provided path or default
    petalert_path = game_folder_path if game_folder_path else PETEXP_FILE_PATH
    
    # Clean up any existing pet files before starting
    clean_pet_files()
    
    # Initialize account states
    accounts_state = {}
    for pid in tracked_accounts:
        account_name = accounts_info.get(pid, {}).get('name', '')
        analysis_data = None
        completed_pets = [False] * 8
        
        if analysis_results and pid in analysis_results:
            result = analysis_results[pid]
            if not result.get('error') and result.get('pets'):
                analysis_data = result['pets']
                # Mark pets at or above objective level/exp as completed
                for i, pet in enumerate(analysis_data):
                    if pet['level'] >= objective_level or pet['current_exp'] >= objective_exp:
                        completed_pets[i] = True
        
        accounts_state[pid] = {
            'name': account_name,
            'analysis_data': analysis_data,
            'completed_pets': completed_pets,
            'current_pet_index': None,
            'all_pets_completed': False,
            'alert_path': petalert_path
        }
    
    # Set initial carry for each account
    for pid, state in accounts_state.items():
        if check_stop():
            break
        
        # Check if disconnected
        if gui_callback and hasattr(gui_callback, 'disconnect_monitor'):
            if gui_callback.disconnect_monitor.is_disconnected(pid):
                state['all_pets_completed'] = True
                continue
        
        hwnd = get_window_by_pid(pid)
        if not hwnd:
            continue
        
        window = bring_window_to_front(hwnd)
        if not window:
            continue
        
        # Find first pet to carry
        next_pet = find_next_pet_to_carry(state, state['analysis_data'], objective_level, objective_exp)
        if next_pet is not None:
            if set_carry_for_pet(window, next_pet):
                state['current_pet_index'] = next_pet
        else:
            # All pets already completed
            state['all_pets_completed'] = True
        
        minimize_window(hwnd)
    
    # Start monitoring thread
    monitor_thread = threading.Thread(
        target=monitor_alerts,
        args=(accounts_state, accounts_info, objective_level, objective_exp, gui_callback),
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
    keyboard.remove_hotkey('d+f')
    
    # Return results
    results = {}
    for pid, state in accounts_state.items():
        completed_count = sum(state['completed_pets'])
        results[pid] = {
            'name': state['name'],
            'pets_completed': completed_count,
            'all_completed': state['all_pets_completed'],
            'status': 'Completed' if state['all_pets_completed'] else f'{completed_count}/8 pets done'
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
