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
from pet_data import get_exp_for_level

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
SAVE_COORD = (287, 530)
CLOSE_PET_COORD = (400, 105)
UPGRADE_COORD = (282, 555)

# Settings
CLICK_DELAY = 0.7  # 700ms delay between clicks
UPGRADE_CLICK_DELAY = 0.2
PETEXP_FILE_PATH = r"C:\Godswar Origin\Localization\en_us\Settings\User"

# Global pause flag
is_paused = False


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


def upgrade_pet_levels(window, pet_index, current_level, objective_level):
    """
    Upgrade a pet's level to objective level
    
    Args:
        window: pygetwindow Window object
        pet_index: Index of the pet (0-7)
        current_level: Current level of the pet
        objective_level: Target level to reach
    
    Returns:
        bool: Success status
    """
    # Calculate upgrade clicks needed
    upgrade_clicks = max(0, objective_level - current_level)
    
    if upgrade_clicks == 0:
        return True  # Already at or above objective
    
    # Click on pet
    pet_x, pet_y = PET_COORDINATES[pet_index]
    if not click_at_window_position(window, pet_x, pet_y):
        return False
    
    # Click on Details
    if not click_at_window_position(window, *DETAILS_COORD):
        return False
    
    # Click upgrade button (dynamic amount)
    for i in range(upgrade_clicks):
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
    except Exception:
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


def analyze_pets(tracked_accounts, accounts_info, objective_level=None, 
                game_folder_path=None, gui_callback=None, ignored_pets=None):
    """
    Analyze pets for selected accounts
    
    Args:
        tracked_accounts (list): List of PIDs to analyze
        accounts_info (dict): Dictionary with account information {pid: {'name': str, ...}}
        objective_level (int): Optional target level for upgrading pets
        game_folder_path (str): Path to the game User settings folder
        gui_callback: Optional GUI object to update status
        ignored_pets (dict): Dict of {character_name: [list of ignored pet indices]}
    
    Returns:
        dict: Analysis results with pet information for each account
    """
    global is_paused
    reset_stop_flag()
    
    if ignored_pets is None:
        ignored_pets = {}
    
    # Calculate objective EXP from level if provided
    objective_exp = get_exp_for_level(objective_level) if objective_level else None
    
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
        
        # Update status to Analyzing
        if gui_callback:
            gui_callback.update_account_status(pid, status="Analyzing", pets_done=0)
            gui_callback.log(f"🔍 Analyzing {account_name}...")
        
        # Get window handle for this PID
        hwnd = get_window_by_pid(pid)
        if not hwnd:
            if gui_callback:
                gui_callback.update_account_status(pid, status="Window Error")
            results[pid] = {
                'name': account_name,
                'pets': [],
                'status': 'Window not found',
                'error': True
            }
            continue
        
        # Bring window to front and get window object
        if gui_callback:
            gui_callback.update_account_status(pid, status="Opening window")
        window = bring_window_to_front(hwnd)
        if not window:
            if gui_callback:
                gui_callback.update_account_status(pid, status="Window Error")
            results[pid] = {
                'name': account_name,
                'pets': [],
                'status': 'Could not get window object',
                'error': True
            }
            continue
        
        # Click on Pet tab
        if gui_callback:
            gui_callback.update_account_status(pid, status="Opening Pet tab")
        if not click_at_window_position(window, *PET_TAB_COORD):
            results[pid] = {
                'name': account_name,
                'pets': [],
                'status': 'Stopped by user',
                'error': True
            }
            break
        
        # Get ignored pet indices for this account
        account_ignored = ignored_pets.get(account_name, [])
        
        # Process all 8 pets (skipping ignored ones)
        if gui_callback:
            if account_ignored:
                gui_callback.log(f"  📝 Processing pets for {account_name} (ignoring pets: {[i+1 for i in account_ignored]})...")
            else:
                gui_callback.log(f"  📝 Processing 8 pets for {account_name}...")
        
        # Create mapping: file_index -> game_pet_index
        processed_pet_indices = []
        for pet_index in range(8):
            # Skip ignored pets
            if pet_index in account_ignored:
                if gui_callback:
                    gui_callback.log(f"    ⏭️ Skipping Pet {pet_index + 1} (ignored)")
                continue
            
            if gui_callback:
                gui_callback.update_account_status(pid, status=f"Scanning Pet {pet_index + 1}", pets_done=len(processed_pet_indices))
            
            if not process_single_pet(window, pet_index):
                results[pid] = {
                    'name': account_name,
                    'pets': [],
                    'status': 'Stopped by user',
                    'error': True
                }
                minimize_window(hwnd)
                return results
            
            processed_pet_indices.append(pet_index)
        
        # Update status - Reading file
        if gui_callback:
            gui_callback.update_account_status(pid, status="Reading data")
        
        # Wait a moment for file to be written
        time.sleep(2)
        
        # Read the petexp file (with .txt extension)
        petexp_file = os.path.join(petexp_path, f"{account_name}_petexp.txt")
        pets_data_raw = parse_petexp_file(petexp_file)
        
        # Map file indices to game pet indices
        # The file only contains pets that were processed (non-ignored)
        # So we need to map: file_index -> actual_game_pet_index
        pets_data = [None] * 8  # Create array with correct positions
        
        for file_idx, game_idx in enumerate(processed_pet_indices):
            if file_idx < len(pets_data_raw):
                pets_data[game_idx] = pets_data_raw[file_idx]
        
        # Count valid pets (non-None)
        valid_pets = [p for p in pets_data if p is not None]
        
        if gui_callback:
            total_found = len(valid_pets)
            ignored_count = len(account_ignored)
            gui_callback.log(f"  ✓ Found {total_found} pets in file ({total_found} processed, {ignored_count} ignored)")
        
        # Filter out ignored pets from data (remove None entries)
        filtered_pets_data = valid_pets
        
        # If objectives provided, upgrade pets that need it
        if objective_exp and objective_level and valid_pets:
            pets_to_upgrade = []
            best_pet_index = None
            best_pet_exp = -1
            
            # Iterate through actual game indices
            for game_idx in range(8):
                pet = pets_data[game_idx]
                
                # Skip if None (ignored or not processed)
                if pet is None:
                    continue
                
                # Check if pet has EXP but not level
                if pet['current_exp'] >= objective_exp and pet['level'] < objective_level:
                    pets_to_upgrade.append(game_idx)
                # Track best pet for carry
                elif pet['current_exp'] < objective_exp and pet['level'] < objective_level:
                    if pet['current_exp'] > best_pet_exp:
                        best_pet_exp = pet['current_exp']
                        best_pet_index = game_idx
            
            # Upgrade pets that need it (pet tab is still open from analysis)
            if pets_to_upgrade:
                if gui_callback:
                    gui_callback.update_account_status(pid, status=f"Upgrading {len(pets_to_upgrade)} pets")
                    gui_callback.log(f"  ⬆️ Upgrading {len(pets_to_upgrade)} pet(s) with sufficient EXP...")
                for game_idx in pets_to_upgrade:
                    pet = pets_data[game_idx]
                    pet_name = pet['name']
                    current_level = pet['level']
                    upgrade_count = objective_level - current_level
                    if gui_callback:
                        gui_callback.update_account_status(pid, status=f"Upgrading Pet {game_idx + 1}")
                        gui_callback.log(f"    • Upgrading {pet_name} (Pet {game_idx + 1}) from Lv{current_level} to Lv{objective_level} (+{upgrade_count})")
                    if not upgrade_pet_levels(window, game_idx, current_level, objective_level):
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
        
        # Store results (with filtered pets, excluding ignored ones)
        ignored_count = len(account_ignored)
        total_pets = len(pets_data)
        valid_pets = len(filtered_pets_data)
        
        status_msg = 'Success'
        if total_pets < 8:
            status_msg = f'Only {total_pets} pets found'
        elif ignored_count > 0:
            status_msg = f'Success ({valid_pets} valid, {ignored_count} ignored)'
        
        results[pid] = {
            'name': account_name,
            'pets': filtered_pets_data,
            'all_pets': pets_data,  # Keep original for reference
            'ignored_indices': account_ignored,
            'status': status_msg,
            'error': False
        }
    
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
