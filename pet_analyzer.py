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
from ui_assets import get_pet_coord, get_ui_coord

# Disable PyAutoGUI fail-safe
pyautogui.FAILSAFE = False

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
    pet_coords = get_pet_coord(window, pet_index)
    if not pet_coords or not click_at_window_position(window, *pet_coords):
        return False
    
    # Click on Details
    details_coords = get_ui_coord(window, "DETAILS")
    if not details_coords or not click_at_window_position(window, *details_coords):
        return False
    
    # Click upgrade button (dynamic amount)
    upgrade_coords = get_ui_coord(window, "UPGRADE")
    if not upgrade_coords:
        return False
    for i in range(upgrade_clicks):
        if check_stop():
            return False
        screen_x = window.left + upgrade_coords[0]
        screen_y = window.top + upgrade_coords[1]
        pyautogui.moveTo(screen_x, screen_y, duration=0.1)
        time.sleep(0.1)
        pyautogui.click(screen_x, screen_y)
        time.sleep(UPGRADE_CLICK_DELAY)
    
    # Close pet
    close_coords = get_ui_coord(window, "CLOSE_PET")
    if not close_coords or not click_at_window_position(window, *close_coords):
        return False
    
    return True


def process_single_pet(window, pet_index, gui_callback=None):
    """
    Process a single pet (click through the UI sequence)
    
    Args:
        window: pygetwindow Window object
        pet_index (int): Index of the pet (0-7)
        gui_callback: Callback object for logging
    
    Returns:
        bool: True if completed, False if stopped
    """
    # Click on pet
    pet_coords = get_pet_coord(window, pet_index)
    if not pet_coords:
        # Retry once for pet slot
        time.sleep(0.5)
        pet_coords = get_pet_coord(window, pet_index)
        
    if not pet_coords or not click_at_window_position(window, *pet_coords):
        if gui_callback:
             gui_callback.log(f"[DEBUG] Failed to find/click PET_{pet_index+1}")
        return False
    
    # Click on Details
    details_coords = get_ui_coord(window, "DETAILS")
    if not details_coords or not click_at_window_position(window, *details_coords):
        return False
    
    # Click on Save - Retry logic as the window animation takes time
    save_coords = None
    for _ in range(3): # Try 3 times
        time.sleep(0.5) # Wait for animation
        save_coords = get_ui_coord(window, "SAVE")
        if save_coords:
            break
            
    if not save_coords or not click_at_window_position(window, *save_coords):
        print(f"[DEBUG] Failed to find SAVE button for PET_{pet_index+1}")
        return False
    
    # Click on Close Pet
    close_coords = get_ui_coord(window, "CLOSE_PET")
    if not close_coords or not click_at_window_position(window, *close_coords):
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
        pet_tab_coords = get_ui_coord(window, "PET_TAB")
        if not pet_tab_coords or not click_at_window_position(window, *pet_tab_coords):
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
            
            if not process_single_pet(window, pet_index, gui_callback):
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
            total_expected = 8 - len(account_ignored)  # Total pets we expected to process
            gui_callback.log(f"  ✓ Found {total_found} pets in file ({total_found}/{total_expected} expected)")
        
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
                pet_coords = get_pet_coord(window, best_pet_index)
                if pet_coords:
                    click_at_window_position(window, *pet_coords)
                carry_coords = get_ui_coord(window, "CARRY")
                if carry_coords:
                    click_at_window_position(window, *carry_coords)
                # Also open Details so the game can detect when pet is ready
                details_coords = get_ui_coord(window, "DETAILS")
                if details_coords:
                    click_at_window_position(window, *details_coords)
        
        # Delete the petexp and petalert files
        delete_petexp_file(petexp_file)
        petalert_file = os.path.join(petexp_path, f"{account_name}_petalert.txt")
        delete_petalert_file(petalert_file)
        
        # Close the pet window by clicking on Pet tab again
        pet_tab_coords = get_ui_coord(window, "PET_TAB")
        if pet_tab_coords:
            click_at_window_position(window, *pet_tab_coords)
        time.sleep(0.3)
        
        # Minimize the window
        minimize_window(hwnd)
        
        # Store results (with filtered pets, excluding ignored ones)
        ignored_count = len(account_ignored)
        total_expected = 8 - ignored_count  # Total pets we expected to process
        actual_valid = len(filtered_pets_data)
        
        status_msg = 'Success'
        if actual_valid < total_expected:
            status_msg = f'Only {actual_valid}/{total_expected} pets found'
        elif ignored_count > 0:
            status_msg = f'Success ({actual_valid} valid, {ignored_count} ignored)'
        
        results[pid] = {
            'name': account_name,
            'pets': filtered_pets_data,
            'all_pets': pets_data,  # Keep original for reference
            'ignored_indices': account_ignored,
            'total_pets': total_expected,  # Add total pets count (excluding ignored)
            'carry_pet_index': best_pet_index,  # Store which pet is currently set to carry
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
