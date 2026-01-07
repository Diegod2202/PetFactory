"""
Pet Analyzer Module
Handles the analysis of pets for tracked accounts
"""
import win32gui
import win32con
import win32process
import pyautogui
import pygetwindow as gw
import time
import os
import re
from pathlib import Path
import keyboard
from file_cleaner import clean_pet_files

# Disable PyAutoGUI fail-safe
pyautogui.FAILSAFE = False


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
DETAILS_COORD = (278, 486)
SAVE_COORD = (287, 580)
CLOSE_PET_COORD = (400, 105)
UPGRADE_COORD = (282, 555)

# Settings
CLICK_DELAY = 0.7  # 700ms delay between clicks
UPGRADE_CLICKS = 30
UPGRADE_CLICK_DELAY = 0.2
PETEXP_FILE_PATH = r"C:\Godswar Origin\Localization\en_us\Settings\User"

# Global pause flag
is_paused = False


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


def minimize_origin_windows(all_pids):
    """
    Minimize all Origin.exe windows
    
    Args:
        all_pids (list): List of all Origin.exe PIDs
    """
    for pid in all_pids:
        hwnd = get_window_by_pid(pid)
        if hwnd:
            win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
    time.sleep(0.5)


def get_window_by_pid(pid):
    """
    Find window handle by process ID
    
    Args:
        pid (int): Process ID
    
    Returns:
        int: Window handle (HWND) or None if not found
    """
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
    """
    Bring window to front and restore if minimized
    
    Args:
        hwnd (int): Window handle
    
    Returns:
        object: pygetwindow Window object or None
    """
    if win32gui.IsIconic(hwnd):
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    win32gui.SetForegroundWindow(hwnd)
    time.sleep(0.8)  # Wait for window to be fully active
    
    # Get window title and find it with pygetwindow
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


def click_at_window_position(window, rel_x, rel_y):
    """
    Click at position relative to window using pygetwindow
    
    Args:
        window: pygetwindow Window object
        rel_x (int): X coordinate relative to window
        rel_y (int): Y coordinate relative to window
    """
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
    
    # Move mouse first to ensure it's visible
    pyautogui.moveTo(screen_x, screen_y, duration=0.1)
    time.sleep(0.1)
    pyautogui.click(screen_x, screen_y)
    time.sleep(CLICK_DELAY)
    return True


def minimize_window(hwnd):
    """
    Minimize window
    
    Args:
        hwnd (int): Window handle
    """
    win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
    time.sleep(0.3)


def upgrade_pet_levels(window, pet_index):
    """
    Upgrade a pet's level 30 times
    
    Args:
        window: pygetwindow Window object
        pet_index: Index of the pet (0-7)
    
    Returns:
        bool: Success status
    """
    # Click on pet
    pet_x, pet_y = PET_COORDINATES[pet_index]
    if not click_at_window_position(window, pet_x, pet_y):
        return False
    
    # Click on Details
    if not click_at_window_position(window, *DETAILS_COORD):
        return False
    
    # Click upgrade button 30 times
    for i in range(UPGRADE_CLICKS):
        if check_stop():
            return False
        screen_x = window.left + UPGRADE_COORD[0]
        screen_y = window.top + UPGRADE_COORD[1]
        pyautogui.moveTo(screen_x, screen_y, duration=0.1)
        time.sleep(0.1)
        pyautogui.click(screen_x, screen_y)
        time.sleep(UPGRADE_CLICK_DELAY)
    
    # Close pet
    if not click_at_window_position(window, *CLOSE_PET_COORD):
        return False
    
    return True


def process_single_pet(window, pet_index):
    """
    Process a single pet (click through the UI sequence)
    
    Args:
        window: pygetwindow Window object
        pet_index (int): Index of the pet (0-7)
    
    Returns:
        bool: True if completed, False if stopped
    """
    # Click on pet
    pet_x, pet_y = PET_COORDINATES[pet_index]
    if not click_at_window_position(window, pet_x, pet_y):
        return False
    
    # Click on Details
    if not click_at_window_position(window, *DETAILS_COORD):
        return False
    
    # Click on Save
    if not click_at_window_position(window, *SAVE_COORD):
        return False
    
    # Click on Close Pet
    if not click_at_window_position(window, *CLOSE_PET_COORD):
        return False
    
    return True


def parse_petexp_file(file_path):
    """
    Parse the petexp file and extract pet information
    
    Args:
        file_path (str): Path to the petexp file
    
    Returns:
        list: List of dictionaries with pet information
    """
    pets = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Parse each line with pet information
        # Format: [Name] Pet: (ID: 66073) | Level: 4 | Current EXP: 2068398 | Next Level EXP: 10500 | Date: 2026-01-06 05:08:07
        pattern = r'\[(.*?)\] Pet: \(ID: (\d+)\) \| Level: (\d+) \| Current EXP: (\d+) \| Next Level EXP: (\d+) \| Date: (.+)'
        
        for line in content.strip().split('\n'):
            match = re.match(pattern, line)
            if match:
                pets.append({
                    'name': match.group(1),
                    'id': int(match.group(2)),
                    'level': int(match.group(3)),
                    'current_exp': int(match.group(4)),
                    'next_level_exp': int(match.group(5)),
                    'date': match.group(6)
                })
    
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"Error parsing petexp file: {e}")
    
    return pets


def delete_petexp_file(file_path):
    """
    Delete the petexp file
    
    Args:
        file_path (str): Path to the petexp file
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except:
        pass


def delete_petalert_file(file_path):
    """
    Delete the petalert file
    
    Args:
        file_path (str): Path to the petalert file
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except:
        pass


def analyze_pets(tracked_accounts, accounts_info, objective_exp=None, objective_level=None, 
                game_folder_path=None, gui_callback=None):
    """
    Analyze pets for selected accounts
    
    Args:
        tracked_accounts (list): List of PIDs to analyze
        accounts_info (dict): Dictionary with account information {pid: {'name': str, ...}}
        objective_exp (int): Optional target EXP for upgrading pets
        objective_level (int): Optional target level for upgrading pets
        game_folder_path (str): Path to the game User settings folder
        gui_callback: Optional GUI object to update status
    
    Returns:
        dict: Analysis results with pet information for each account
    """
    global is_paused
    reset_stop_flag()
    setup_stop_hotkey()
    
    # Use provided path or default
    petexp_path = game_folder_path if game_folder_path else PETEXP_FILE_PATH
    
    # Clean up any existing pet files before starting
    clean_pet_files()
    if gui_callback:
        gui_callback.log("🧹 Cleaned up existing pet files")
    
    results = {}
    
    # Get all Origin.exe PIDs and minimize them
    all_pids = list(accounts_info.keys())
    minimize_origin_windows(all_pids)
    if gui_callback:
        gui_callback.log(f"📦 Minimized {len(all_pids)} Origin windows")
    
    for pid in tracked_accounts:
        if check_stop():
            results[pid] = {
                'name': accounts_info.get(pid, {}).get('name', 'Unknown'),
                'pets': [],
                'status': 'Stopped by user',
                'error': True
            }
            break
        
        # Check if disconnected
        if gui_callback and hasattr(gui_callback, 'disconnect_monitor'):
            if gui_callback.disconnect_monitor.is_disconnected(pid):
                account_name = accounts_info.get(pid, {}).get('name', 'Unknown')
                results[pid] = {
                    'name': account_name,
                    'pets': [],
                    'status': 'Disconnected',
                    'error': True
                }
                if gui_callback:
                    gui_callback.log(f"⏭️ Skipping {account_name} (disconnected)")
                continue
        
        account_name = accounts_info.get(pid, {}).get('name', 'Unknown')
        if gui_callback:
            gui_callback.log(f"🔍 Analyzing {account_name}...")
        
        # Get window handle for this PID
        hwnd = get_window_by_pid(pid)
        if not hwnd:
            results[pid] = {
                'name': account_name,
                'pets': [],
                'status': 'Window not found',
                'error': True
            }
            continue
        
        # Bring window to front and get window object
        window = bring_window_to_front(hwnd)
        if not window:
            results[pid] = {
                'name': account_name,
                'pets': [],
                'status': 'Could not get window object',
                'error': True
            }
            continue
        
        # Click on Pet tab
        if not click_at_window_position(window, *PET_TAB_COORD):
            results[pid] = {
                'name': account_name,
                'pets': [],
                'status': 'Stopped by user',
                'error': True
            }
            break
        
        # Process all 8 pets
        if gui_callback:
            gui_callback.log(f"  📝 Processing 8 pets for {account_name}...")
        
        for pet_index in range(8):
            if gui_callback:
                gui_callback.update_account_status(pid, pets_done=pet_index)
            if not process_single_pet(window, pet_index):
                results[pid] = {
                    'name': account_name,
                    'pets': [],
                    'status': 'Stopped by user',
                    'error': True
                }
                minimize_window(hwnd)
                return results
        
        # Wait a moment for file to be written
        time.sleep(2)
        
        # Read the petexp file (with .txt extension)
        petexp_file = os.path.join(petexp_path, f"{account_name}_petexp.txt")
        pets_data = parse_petexp_file(petexp_file)
        
        if gui_callback:
            gui_callback.log(f"  ✓ Found {len(pets_data)} pets in file")
        
        # If objectives provided, upgrade pets that need it
        if objective_exp and objective_level and pets_data:
            pets_to_upgrade = []
            best_pet_index = None
            best_pet_exp = -1
            
            for i, pet in enumerate(pets_data):
                # Check if pet has EXP but not level
                if pet['current_exp'] >= objective_exp and pet['level'] < objective_level:
                    pets_to_upgrade.append(i)
                # Track best pet for carry
                elif pet['current_exp'] < objective_exp and pet['level'] < objective_level:
                    if pet['current_exp'] > best_pet_exp:
                        best_pet_exp = pet['current_exp']
                        best_pet_index = i
            
            # Upgrade pets that need it (pet tab is still open from analysis)
            if pets_to_upgrade:
                if gui_callback:
                    gui_callback.log(f"  ⬆️ Upgrading {len(pets_to_upgrade)} pet(s) with sufficient EXP...")
                for pet_index in pets_to_upgrade:
                    pet_name = pets_data[pet_index]['name']
                    if gui_callback:
                        gui_callback.log(f"    • Upgrading {pet_name} (Pet {pet_index + 1})...")
                    if not upgrade_pet_levels(window, pet_index):
                        break
            
            # Set best pet to carry if found
            if best_pet_index is not None:
                best_pet_name = pets_data[best_pet_index]['name']
                if gui_callback:
                    gui_callback.log(f"  🎯 Setting {best_pet_name} (Pet {best_pet_index + 1}) to carry")
                pet_x, pet_y = PET_COORDINATES[best_pet_index]
                click_at_window_position(window, pet_x, pet_y)
                click_at_window_position(window, *CARRY_COORD)
        
        # Delete the petexp and petalert files
        delete_petexp_file(petexp_file)
        petalert_file = os.path.join(petexp_path, f"{account_name}_petalert.txt")
        delete_petalert_file(petalert_file)
        
        # Close the pet window by clicking on Pet tab again
        click_at_window_position(window, *PET_TAB_COORD)
        time.sleep(0.3)
        
        # Minimize the window
        minimize_window(hwnd)
        
        # Store results
        results[pid] = {
            'name': account_name,
            'pets': pets_data,
            'status': 'Success' if len(pets_data) == 8 else f'Only {len(pets_data)} pets found',
            'error': False
        }
    
    keyboard.remove_hotkey('d+f')
    return results


def format_analysis_results(results):
    """
    Format analysis results for display
    
    Args:
        results (dict): Analysis results from analyze_pets()
    
    Returns:
        str: Formatted string ready for display
    """
    if not results:
        return "No results to display"
    
    lines = []
    lines.append(f"Pet Analysis Complete for {len(results)} account(s)\n")
    lines.append("=" * 60)
    
    for pid, data in results.items():
        lines.append(f"\nAccount: {data['name']}")
        lines.append(f"Status: {data['status']}")
        
        if data.get('error'):
            lines.append("")
            continue
        
        if data['pets']:
            lines.append(f"Pets analyzed: {len(data['pets'])}\n")
            for i, pet in enumerate(data['pets'], 1):
                lines.append(f"  Pet {i}: {pet['name']}")
                lines.append(f"    Level: {pet['level']} | Current EXP: {pet['current_exp']:,} | Next Level: {pet['next_level_exp']:,}")
        else:
            lines.append("No pet data found")
        
        lines.append("")
    
    return "\n".join(lines)
