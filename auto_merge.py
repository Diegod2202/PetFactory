"""
Auto Merge Module
Handles the automatic merging of pets into a main pet after leveling
"""
import time
import pyautogui
import pygetwindow as gw

from ui_assets import get_ui_coord, get_pet_coord

# =============================================================================
# CONSTANTS
# =============================================================================

# Timing constants (in seconds)
PORTAL_WAIT = 12
PET_MANAGER_WAIT = 21
MOUNT_WAIT = 8
TRANSPORTER_WAIT = 30
OK_WAIT = 3
THERMO_WAIT = 200  # 3 minutes 20 seconds
LARISSA_WAIT = 65  # 1 minute 5 seconds
MYCENAE_WAIT = 2

# Click delays
CLICK_DELAY = 0.5
SPIRIT_CLICK_DELAY = 0.3
PET_BAG_DELAY = 1.0

# Merge settings
SPIRITS_PER_MERGE = 6
BAG_SEARCH_MAX_ATTEMPTS = 10
CLOSE_INTERFACE_ATTEMPTS = 10

# Global state
is_merge_paused = False
merge_active = False


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def check_merge_stop():
    """Check if merge is paused and wait until resumed"""
    global is_merge_paused
    while is_merge_paused:
        time.sleep(0.5)


def click_at_window_position(window, rel_x, rel_y, delay=None, button='left'):
    """Click at position relative to window"""
    if delay is None:
        delay = CLICK_DELAY
    
    abs_x = window.left + rel_x
    abs_y = window.top + rel_y
    pyautogui.click(abs_x, abs_y, button=button)
    time.sleep(delay)


def drag_to_corner(window):
    """
    Drag an interface element to the top-right corner of the window.
    Used to reposition the merge interface for easier slot access.
    """
    # Start from center-left area and drag to top-right
    start_x = window.left + 200
    start_y = window.top + 300
    end_x = window.left + window.width - 100
    end_y = window.top + 100
    
    pyautogui.moveTo(start_x, start_y)
    time.sleep(0.2)
    pyautogui.mouseDown()
    time.sleep(0.1)
    pyautogui.moveTo(end_x, end_y, duration=0.5)
    pyautogui.mouseUp()
    time.sleep(0.3)


def drag_element_to_target(window, from_coord, to_coord):
    """
    Drag from one position to another within a window.
    Coordinates are relative to the window.
    """
    start_x = window.left + from_coord[0]
    start_y = window.top + from_coord[1]
    end_x = window.left + to_coord[0]
    end_y = window.top + to_coord[1]
    
    pyautogui.moveTo(start_x, start_y)
    time.sleep(0.2)
    pyautogui.mouseDown()
    time.sleep(0.1)
    pyautogui.moveTo(end_x, end_y, duration=0.3)
    pyautogui.mouseUp()
    time.sleep(0.3)


# =============================================================================
# STEP 1: PORTAL TO ATHENS
# =============================================================================

def portal_to_athens(window):
    """
    Step 1: Use portal to Athens
    Returns: True if successful, False otherwise
    """
    check_merge_stop()
    
    coords = get_ui_coord(window, "PORTAL_ATHENS")
    if not coords:
        print("[AUTO_MERGE] Could not find Portal to Athens")
        return False
    
    click_at_window_position(window, coords[0], coords[1])
    print(f"[AUTO_MERGE] Clicked Portal to Athens, waiting {PORTAL_WAIT}s")
    time.sleep(PORTAL_WAIT)
    return True


# =============================================================================
# STEPS 2-4: OPEN PET MANAGER
# =============================================================================

def open_pet_manager(window):
    """
    Steps 2-4: Click Search -> Pet Manager -> Pet Tab
    Returns: True if successful, False otherwise
    """
    check_merge_stop()
    
    # Step 2: Click Search
    search_coords = get_ui_coord(window, "SEARCH")
    if not search_coords:
        print("[AUTO_MERGE] Could not find Search button")
        return False
    click_at_window_position(window, search_coords[0], search_coords[1])
    print("[AUTO_MERGE] Clicked Search")
    
    # Step 3: Click Pet Manager
    check_merge_stop()
    pm_coords = get_ui_coord(window, "PET_MANAGER")
    if not pm_coords:
        print("[AUTO_MERGE] Could not find Pet Manager")
        return False
    click_at_window_position(window, pm_coords[0], pm_coords[1])
    print(f"[AUTO_MERGE] Clicked Pet Manager, waiting {PET_MANAGER_WAIT}s")
    time.sleep(PET_MANAGER_WAIT)
    
    # Step 4: Open Pet Tab
    check_merge_stop()
    pet_tab_coords = get_ui_coord(window, "PET_TAB")
    if not pet_tab_coords:
        print("[AUTO_MERGE] Could not find Pet Tab")
        return False
    click_at_window_position(window, pet_tab_coords[0], pet_tab_coords[1])
    print("[AUTO_MERGE] Opened Pet Tab")
    
    return True


# =============================================================================
# STEPS 5-7: SETUP MERGE INTERFACE
# =============================================================================

def setup_merge_interface(window, receiver_slot):
    """
    Steps 5-7: Set receiver pet to carry, open merge, position interface
    
    Args:
        window: pygetwindow Window object
        receiver_slot: Slot index of the pet to receive merges (0-7)
    
    Returns: True if successful, False otherwise
    """
    check_merge_stop()
    
    # Step 5: Click on receiver pet and set to Carry
    pet_coords = get_pet_coord(window, receiver_slot)
    if not pet_coords:
        print(f"[AUTO_MERGE] Could not find pet in slot {receiver_slot + 1}")
        return False
    
    click_at_window_position(window, pet_coords[0], pet_coords[1])
    time.sleep(0.3)
    
    carry_coords = get_ui_coord(window, "CARRY")
    if not carry_coords:
        print("[AUTO_MERGE] Could not find Carry button")
        return False
    click_at_window_position(window, carry_coords[0], carry_coords[1])
    print(f"[AUTO_MERGE] Set pet {receiver_slot + 1} to Carry")
    
    # Step 6: Click Merge button
    check_merge_stop()
    merge_coords = get_ui_coord(window, "MERGE")
    if not merge_coords:
        print("[AUTO_MERGE] Could not find Merge button")
        return False
    click_at_window_position(window, merge_coords[0], merge_coords[1])
    print("[AUTO_MERGE] Opened Merge interface")
    time.sleep(0.5)
    
    # Step 7: Reposition merge interface to top-right corner
    # This makes slot A more accessible
    check_merge_stop()
    drag_to_corner(window)
    print("[AUTO_MERGE] Repositioned merge interface")
    
    return True


# =============================================================================
# STEPS 8-12: PERFORM SINGLE MERGE
# =============================================================================

def perform_single_merge(window, receiver_slot, provider_slot, use_merged_spirit, spirits_available):
    """
    Steps 8-12: Execute one merge operation
    
    Args:
        window: pygetwindow Window object
        receiver_slot: Slot of pet receiving merge (0-7)
        provider_slot: Slot of pet being merged (0-7)
        use_merged_spirit: Whether to use merged spirits
        spirits_available: Whether spirits are still available
    
    Returns: Tuple (success, spirits_still_available)
    """
    check_merge_stop()
    
    # Step 8: Find receiver pet and drag to Slot A
    receiver_coords = get_pet_coord(window, receiver_slot)
    if not receiver_coords:
        print(f"[AUTO_MERGE] Could not find receiver pet {receiver_slot + 1}")
        return False, spirits_available
    
    slot_a_coords = get_ui_coord(window, "SLOT_A")
    if not slot_a_coords:
        print("[AUTO_MERGE] Could not find Slot A")
        return False, spirits_available
    
    drag_element_to_target(window, receiver_coords, slot_a_coords)
    print(f"[AUTO_MERGE] Dragged pet {receiver_slot + 1} to Slot A")
    
    # Step 9: Find provider pet and drag to Slot B
    check_merge_stop()
    provider_coords = get_pet_coord(window, provider_slot)
    if not provider_coords:
        print(f"[AUTO_MERGE] Could not find provider pet {provider_slot + 1}")
        return False, spirits_available
    
    slot_b_coords = get_ui_coord(window, "SLOT_B")
    if not slot_b_coords:
        print("[AUTO_MERGE] Could not find Slot B")
        return False, spirits_available
    
    drag_element_to_target(window, provider_coords, slot_b_coords)
    print(f"[AUTO_MERGE] Dragged pet {provider_slot + 1} to Slot B")
    
    # Step 10: Use merged spirits if enabled and available
    if use_merged_spirit and spirits_available:
        check_merge_stop()
        bag_coords = get_ui_coord(window, "BAG")
        if bag_coords:
            click_at_window_position(window, bag_coords[0], bag_coords[1])
            time.sleep(0.5)
            
            spirit_coords = get_ui_coord(window, "MERGED_SPIRIT")
            if spirit_coords:
                # Right-click 6 times to use spirits
                for i in range(SPIRITS_PER_MERGE):
                    check_merge_stop()
                    click_at_window_position(window, spirit_coords[0], spirit_coords[1], 
                                           delay=SPIRIT_CLICK_DELAY, button='right')
                print(f"[AUTO_MERGE] Used {SPIRITS_PER_MERGE} Merged Spirits")
            else:
                print("[AUTO_MERGE] No Merged Spirits found - continuing without")
                spirits_available = False
            
            # Step 11: Close bag
            click_at_window_position(window, bag_coords[0], bag_coords[1])
            time.sleep(0.3)
    
    # Step 12: Click Merging Pets 4 times (apply, merge, finish, close)
    check_merge_stop()
    merge_btn_coords = get_ui_coord(window, "MERGING_PETS")
    if not merge_btn_coords:
        print("[AUTO_MERGE] Could not find Merging Pets button")
        return False, spirits_available
    
    for i in range(4):
        check_merge_stop()
        click_at_window_position(window, merge_btn_coords[0], merge_btn_coords[1], delay=0.8)
    print("[AUTO_MERGE] Completed merge clicks (4x)")
    
    return True, spirits_available


# =============================================================================
# STEP 14: COLLECT NEW PETS FROM BAG
# =============================================================================

def collect_new_pets(window, provider_slot):
    """
    Step 14: Open bag, right-click all pets to collect them
    
    Args:
        window: pygetwindow Window object
        provider_slot: Slot where merged pet was, to set as carry if new pets found
    
    Returns: Number of pets collected
    """
    check_merge_stop()
    
    bag_coords = get_ui_coord(window, "BAG")
    if not bag_coords:
        print("[AUTO_MERGE] Could not find Bag button")
        return 0
    
    click_at_window_position(window, bag_coords[0], bag_coords[1])
    time.sleep(0.5)
    
    pets_collected = 0
    attempts = 0
    
    while attempts < BAG_SEARCH_MAX_ATTEMPTS:
        check_merge_stop()
        
        pet_coords = get_ui_coord(window, "PET_IN_BAG")
        if pet_coords:
            click_at_window_position(window, pet_coords[0], pet_coords[1], 
                                   delay=PET_BAG_DELAY, button='right')
            pets_collected += 1
            attempts = 0  # Reset attempts after finding a pet
        else:
            # Try clicking New Bag to search in other bag tabs
            new_bag_coords = get_ui_coord(window, "NEW_BAG")
            if new_bag_coords and attempts < BAG_SEARCH_MAX_ATTEMPTS // 2:
                click_at_window_position(window, new_bag_coords[0], new_bag_coords[1])
                time.sleep(0.3)
            attempts += 1
    
    # Close bag
    click_at_window_position(window, bag_coords[0], bag_coords[1])
    print(f"[AUTO_MERGE] Collected {pets_collected} pets from bag")
    
    return pets_collected


# =============================================================================
# STEP 15: CLOSE ALL INTERFACES
# =============================================================================

def close_all_interfaces(window):
    """
    Step 15: Find and click close button up to 10 times
    """
    for i in range(CLOSE_INTERFACE_ATTEMPTS):
        check_merge_stop()
        
        close_coords = get_ui_coord(window, "CLOSE_INTERFACE")
        if close_coords:
            click_at_window_position(window, close_coords[0], close_coords[1], delay=0.3)
        else:
            break
    
    print("[AUTO_MERGE] Closed interfaces")


# =============================================================================
# STEPS 16-23: TRAVEL TO AFK SPOT
# =============================================================================

def travel_to_afk_spot(window, destination):
    """
    Steps 16-23: Mount, travel to destination, dismount
    
    Args:
        window: pygetwindow Window object
        destination: "thermopylae" or "larissa"
    
    Returns: True if successful, False otherwise
    """
    check_merge_stop()
    
    # Step 16: Mount up
    mount_coords = get_ui_coord(window, "MOUNT")
    if not mount_coords:
        print("[AUTO_MERGE] Could not find Mount button")
        return False
    click_at_window_position(window, mount_coords[0], mount_coords[1])
    print(f"[AUTO_MERGE] Mounting, waiting {MOUNT_WAIT}s")
    time.sleep(MOUNT_WAIT)
    
    # Step 17: Click Search
    check_merge_stop()
    search_coords = get_ui_coord(window, "SEARCH")
    if not search_coords:
        print("[AUTO_MERGE] Could not find Search button")
        return False
    click_at_window_position(window, search_coords[0], search_coords[1])
    
    # Step 18: Click Transporter
    check_merge_stop()
    transporter_coords = get_ui_coord(window, "TRANSPORTER_NPC")
    if not transporter_coords:
        print("[AUTO_MERGE] Could not find Transporter")
        return False
    click_at_window_position(window, transporter_coords[0], transporter_coords[1])
    print(f"[AUTO_MERGE] Going to Transporter, waiting {TRANSPORTER_WAIT}s")
    time.sleep(TRANSPORTER_WAIT)
    
    # Step 19: Click on Transporter NPC
    check_merge_stop()
    transporter_coords = get_ui_coord(window, "TRANSPORTER_NPC")
    if transporter_coords:
        click_at_window_position(window, transporter_coords[0], transporter_coords[1])
        time.sleep(0.5)
    
    # Step 20: Click Transmit
    check_merge_stop()
    transmit_coords = get_ui_coord(window, "TRANSMIT")
    if not transmit_coords:
        print("[AUTO_MERGE] Could not find Transmit button")
        return False
    click_at_window_position(window, transmit_coords[0], transmit_coords[1])
    
    if destination.lower() == "thermopylae":
        return _travel_thermopylae(window)
    else:
        return _travel_larissa(window)


def _travel_thermopylae(window):
    """Travel to Thermopylae via Parnitha Port"""
    check_merge_stop()
    
    # Step 21: Click Parnitha Port
    parnitha_coords = get_ui_coord(window, "PARNITHA_PORT")
    if not parnitha_coords:
        print("[AUTO_MERGE] Could not find Parnitha Port")
        return False
    click_at_window_position(window, parnitha_coords[0], parnitha_coords[1])
    
    # Step 22: Click OK
    ok_coords = get_ui_coord(window, "OK")
    if ok_coords:
        click_at_window_position(window, ok_coords[0], ok_coords[1])
    time.sleep(OK_WAIT)
    
    # Step 23: Click Thermopylae button
    check_merge_stop()
    thermo_coords = get_ui_coord(window, "THERMO_BTN")
    if not thermo_coords:
        print("[AUTO_MERGE] Could not find Thermopylae button")
        return False
    click_at_window_position(window, thermo_coords[0], thermo_coords[1])
    print(f"[AUTO_MERGE] Traveling to Thermopylae, waiting {THERMO_WAIT}s")
    time.sleep(THERMO_WAIT)
    
    return True


def _travel_larissa(window):
    """Travel to Larissa via Thebes -> Mycenae -> Larissa"""
    check_merge_stop()
    
    # Athens to Thebes
    thebes_coords = get_ui_coord(window, "THEBES")
    if not thebes_coords:
        print("[AUTO_MERGE] Could not find Thebes")
        return False
    click_at_window_position(window, thebes_coords[0], thebes_coords[1])
    
    ok_coords = get_ui_coord(window, "OK")
    if ok_coords:
        click_at_window_position(window, ok_coords[0], ok_coords[1])
    time.sleep(OK_WAIT)
    
    # Mycenae transporter
    check_merge_stop()
    myc_trans_coords = get_ui_coord(window, "MYCENAE_TRANSPORTER")
    if not myc_trans_coords:
        print("[AUTO_MERGE] Could not find Mycenae Transporter")
        return False
    click_at_window_position(window, myc_trans_coords[0], myc_trans_coords[1])
    time.sleep(0.5)
    
    # Transmit in Mycenae
    transmit_coords = get_ui_coord(window, "TRANSMIT_MYCENAE")
    if transmit_coords:
        click_at_window_position(window, transmit_coords[0], transmit_coords[1])
    
    # Go to Mycenae
    check_merge_stop()
    go_myc_coords = get_ui_coord(window, "GO_TO_MYCENAE")
    if not go_myc_coords:
        print("[AUTO_MERGE] Could not find Go to Mycenae")
        return False
    click_at_window_position(window, go_myc_coords[0], go_myc_coords[1])
    
    ok_coords = get_ui_coord(window, "OK")
    if ok_coords:
        click_at_window_position(window, ok_coords[0], ok_coords[1])
    time.sleep(MYCENAE_WAIT)
    
    # Mycenae transporter again
    check_merge_stop()
    myc_trans_coords = get_ui_coord(window, "MYCENAE_TRANSPORTER")
    if myc_trans_coords:
        click_at_window_position(window, myc_trans_coords[0], myc_trans_coords[1])
        time.sleep(0.5)
    
    transmit_coords = get_ui_coord(window, "TRANSMIT_MYCENAE")
    if transmit_coords:
        click_at_window_position(window, transmit_coords[0], transmit_coords[1])
    
    # Go to Larissa
    check_merge_stop()
    go_lar_coords = get_ui_coord(window, "GO_TO_LARISSA")
    if not go_lar_coords:
        print("[AUTO_MERGE] Could not find Go to Larissa")
        return False
    click_at_window_position(window, go_lar_coords[0], go_lar_coords[1])
    
    ok_coords = get_ui_coord(window, "OK")
    if ok_coords:
        click_at_window_position(window, ok_coords[0], ok_coords[1])
    time.sleep(MYCENAE_WAIT)
    
    # Click Larissa button
    check_merge_stop()
    larissa_coords = get_ui_coord(window, "LARISSA_BTN")
    if not larissa_coords:
        print("[AUTO_MERGE] Could not find Larissa button")
        return False
    click_at_window_position(window, larissa_coords[0], larissa_coords[1])
    print(f"[AUTO_MERGE] Traveling to Larissa, waiting {LARISSA_WAIT}s")
    time.sleep(LARISSA_WAIT)
    
    return True


# =============================================================================
# STEPS 24-27: START AFK MODE
# =============================================================================

def start_afk_mode(window, final_pet_slot):
    """
    Steps 24-27: Dismount, set final pet to carry, start AFK
    
    Args:
        window: pygetwindow Window object
        final_pet_slot: The pet slot to set as carry after merges (0-7)
    
    Returns: True if successful, False otherwise
    """
    check_merge_stop()
    
    # Step 24: Dismount
    mount_coords = get_ui_coord(window, "MOUNT")
    if mount_coords:
        click_at_window_position(window, mount_coords[0], mount_coords[1])
        time.sleep(1.0)
    
    # Open pet tab and set final pet to carry
    pet_tab_coords = get_ui_coord(window, "PET_TAB")
    if pet_tab_coords:
        click_at_window_position(window, pet_tab_coords[0], pet_tab_coords[1])
        time.sleep(0.5)
        
        pet_coords = get_pet_coord(window, final_pet_slot)
        if pet_coords:
            click_at_window_position(window, pet_coords[0], pet_coords[1])
            time.sleep(0.3)
            
            carry_coords = get_ui_coord(window, "CARRY")
            if carry_coords:
                click_at_window_position(window, carry_coords[0], carry_coords[1])
                print(f"[AUTO_MERGE] Set pet {final_pet_slot + 1} to Carry")
    
    # Close pet window
    close_coords = get_ui_coord(window, "CLOSE_PET")
    if close_coords:
        click_at_window_position(window, close_coords[0], close_coords[1])
    
    # Step 25: Click AFK
    check_merge_stop()
    afk_coords = get_ui_coord(window, "AFK")
    if not afk_coords:
        print("[AUTO_MERGE] Could not find AFK button")
        return False
    click_at_window_position(window, afk_coords[0], afk_coords[1])
    
    # Step 26: Click Start
    check_merge_stop()
    start_coords = get_ui_coord(window, "START_AFK")
    if not start_coords:
        print("[AUTO_MERGE] Could not find Start button")
        return False
    click_at_window_position(window, start_coords[0], start_coords[1])
    print("[AUTO_MERGE] Started AFK mode")
    
    return True


# =============================================================================
# MAIN MERGE ORCHESTRATOR
# =============================================================================

def run_auto_merge(window, config, gui_callback=None):
    """
    Main entry point for the auto merge process.
    
    Args:
        window: pygetwindow Window object for the game
        config: Dictionary with merge configuration:
            - receiver_slot: Pet slot to receive merges (0-7)
            - provider_slot: Pet slot to provide merges (0-7)
            - use_merged_spirit: Boolean
            - max_merges: Maximum number of merges (default 999)
            - final_pet_slot: Pet to set as carry after merges (0-7)
            - afk_spot: "thermopylae" or "larissa"
            - total_pets_to_merge: Number of pets that were leveled up
        gui_callback: Optional GUI object for logging/status updates
    
    Returns: Dictionary with merge results
    """
    global merge_active
    merge_active = True
    
    receiver_slot = config.get('receiver_slot', 0)
    provider_slot = config.get('provider_slot', 7)
    use_spirit = config.get('use_merged_spirit', False)
    max_merges = config.get('max_merges', 999)
    final_pet_slot = config.get('final_pet_slot', 0)
    afk_spot = config.get('afk_spot', 'thermopylae')
    total_to_merge = config.get('total_pets_to_merge', 7)
    
    spirits_available = use_spirit
    merges_completed = 0
    
    def log(msg):
        print(msg)
        if gui_callback and hasattr(gui_callback, 'log'):
            gui_callback.root.after(0, lambda: gui_callback.log(msg))
    
    log(f"[AUTO_MERGE] Starting auto merge: {total_to_merge} pets to merge")
    log(f"[AUTO_MERGE] Receiver: Pet {receiver_slot + 1}, Provider: Pet {provider_slot + 1}")
    
    try:
        # Step 1: Portal to Athens
        if not portal_to_athens(window):
            log("[AUTO_MERGE] Failed at Step 1: Portal to Athens")
            merge_active = False
            return {'success': False, 'merges_completed': 0, 'error': 'Portal failed'}
        
        # Steps 2-4: Open Pet Manager
        if not open_pet_manager(window):
            log("[AUTO_MERGE] Failed at Steps 2-4: Open Pet Manager")
            merge_active = False
            return {'success': False, 'merges_completed': 0, 'error': 'Pet Manager failed'}
        
        # Steps 5-7: Setup merge interface
        if not setup_merge_interface(window, receiver_slot):
            log("[AUTO_MERGE] Failed at Steps 5-7: Setup Merge Interface")
            merge_active = False
            return {'success': False, 'merges_completed': 0, 'error': 'Setup failed'}
        
        # Steps 8-13: Perform merges in a loop
        while merges_completed < min(total_to_merge, max_merges):
            check_merge_stop()
            
            success, spirits_available = perform_single_merge(
                window, receiver_slot, provider_slot, use_spirit, spirits_available
            )
            
            if success:
                merges_completed += 1
                log(f"[AUTO_MERGE] Merge {merges_completed}/{total_to_merge} completed")
            else:
                log(f"[AUTO_MERGE] Merge failed at iteration {merges_completed + 1}")
                break
        
        # Step 14: Collect new pets from bag
        pets_collected = collect_new_pets(window, provider_slot)
        
        # Set carry based on whether we found new pets
        if pets_collected > 0:
            # New pets found, set provider slot pet to carry
            pet_coords = get_pet_coord(window, provider_slot)
            if pet_coords:
                click_at_window_position(window, pet_coords[0], pet_coords[1])
                carry_coords = get_ui_coord(window, "CARRY")
                if carry_coords:
                    click_at_window_position(window, carry_coords[0], carry_coords[1])
        else:
            # No new pets, keep receiver as carry
            pet_coords = get_pet_coord(window, receiver_slot)
            if pet_coords:
                click_at_window_position(window, pet_coords[0], pet_coords[1])
                carry_coords = get_ui_coord(window, "CARRY")
                if carry_coords:
                    click_at_window_position(window, carry_coords[0], carry_coords[1])
        
        # Step 15: Close all interfaces
        close_all_interfaces(window)
        
        # Steps 16-23: Travel to AFK spot
        if not travel_to_afk_spot(window, afk_spot):
            log(f"[AUTO_MERGE] Failed to travel to {afk_spot}")
        
        # Steps 24-27: Start AFK mode
        if not start_afk_mode(window, final_pet_slot):
            log("[AUTO_MERGE] Failed to start AFK mode")
        
        log(f"[AUTO_MERGE] Complete! {merges_completed} merges done")
        merge_active = False
        
        return {
            'success': True,
            'merges_completed': merges_completed,
            'pets_collected': pets_collected,
            'spirits_depleted': not spirits_available if use_spirit else False
        }
        
    except Exception as e:
        log(f"[AUTO_MERGE] Error: {str(e)}")
        merge_active = False
        return {'success': False, 'merges_completed': merges_completed, 'error': str(e)}
