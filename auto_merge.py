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
MOUNT_WAIT = 11  # Time for character to mount
TRANSPORTER_WAIT = 29  # Time to reach transporter
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
BAG_SEARCH_MAX_ATTEMPTS = 20
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
    Does 4 mini drag-and-drops of 1 pixel to ensure the element is grabbed,
    then moves to the final target position.
    Coordinates are relative to the window.
    """
    start_x = window.left + from_coord[0]
    start_y = window.top + from_coord[1]
    end_x = window.left + to_coord[0]
    end_y = window.top + to_coord[1]
    
    # Ensure mouse is released first (clean state)
    pyautogui.mouseUp()
    time.sleep(0.1)
    
    # Do 2 mini drag-and-drops to ensure element is grabbed
    for i in range(2):
        pyautogui.moveTo(start_x + i, start_y)
        time.sleep(0.1)
        pyautogui.mouseDown()
        time.sleep(0.1)
        pyautogui.moveTo(start_x + i + 1, start_y, duration=0.1)
        time.sleep(0.05)
        pyautogui.mouseUp()
        time.sleep(0.1)
    
    # Now do the final drag to the target
    pyautogui.moveTo(start_x + 2, start_y)
    time.sleep(0.2)
    pyautogui.mouseDown()
    time.sleep(0.2)
    
    # Move to destination slowly
    pyautogui.moveTo(end_x, end_y, duration=0.5)
    time.sleep(0.2)
    
    # Click at destination to place
    pyautogui.click(end_x, end_y)
    time.sleep(0.1)
    pyautogui.mouseUp()
    time.sleep(0.5)


# =============================================================================
# STEP 1: PORTAL TO ATHENS
# =============================================================================

# Portal click settings
PORTAL_CLICK_ATTEMPTS = 20
PORTAL_CLICK_DURATION = 4  # seconds total for all attempts

def portal_to_athens(window):
    """
    Step 1: Use portal to Athens
    Keeps retrying image search until portal is found, then clicks 20 times.
    Returns: True if successful, False otherwise
    """
    check_merge_stop()
    print("[AUTO_MERGE] Searching for Portal to Athens (will retry until found)...")
    
    clicks_performed = 0
    click_interval = PORTAL_CLICK_DURATION / PORTAL_CLICK_ATTEMPTS
    
    # Keep searching until we perform all 20 clicks
    while clicks_performed < PORTAL_CLICK_ATTEMPTS:
        check_merge_stop()
        
        coords = get_ui_coord(window, "PORTAL_ATHENS")
        if coords:
            click_at_window_position(window, coords[0], coords[1], delay=click_interval)
            clicks_performed += 1
            if clicks_performed == 1:
                print(f"[AUTO_MERGE] Portal found! Clicking {PORTAL_CLICK_ATTEMPTS}x...")
        else:
            # Portal not visible yet, wait before retry
            time.sleep(0.5)
            if clicks_performed == 0:
                print(f"[AUTO_MERGE] Portal not found, retrying search...")
    
    print(f"[AUTO_MERGE] Clicked Portal to Athens {PORTAL_CLICK_ATTEMPTS}x, waiting {PORTAL_WAIT}s")
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
    
    # Step 2: Click Search (retry until found)
    check_merge_stop()
    print("[AUTO_MERGE] Searching for Search button...")
    while True:
        check_merge_stop()
        search_coords = get_ui_coord(window, "SEARCH")
        if search_coords:
            click_at_window_position(window, search_coords[0], search_coords[1])
            print("[AUTO_MERGE] Clicked Search")
            break
        time.sleep(0.5)
    
    # Step 3: Click Pet Manager (retry until found)
    check_merge_stop()
    print("[AUTO_MERGE] Searching for Pet Manager...")
    while True:
        check_merge_stop()
        pm_coords = get_ui_coord(window, "PET_MANAGER")
        if pm_coords:
            click_at_window_position(window, pm_coords[0], pm_coords[1])
            print(f"[AUTO_MERGE] Clicked Pet Manager, waiting {PET_MANAGER_WAIT}s")
            time.sleep(PET_MANAGER_WAIT)
            break
        time.sleep(0.5)
    
    # Step 4: Open Pet Tab (retry until found)
    check_merge_stop()
    print("[AUTO_MERGE] Searching for Pet Tab...")
    while True:
        check_merge_stop()
        pet_tab_coords = get_ui_coord(window, "PET_TAB")
        if pet_tab_coords:
            click_at_window_position(window, pet_tab_coords[0], pet_tab_coords[1])
            print("[AUTO_MERGE] Opened Pet Tab")
            break
        time.sleep(0.5)
    
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
    
    # Step 5: Click on receiver pet and set to Carry (retry until found)
    print(f"[AUTO_MERGE] Searching for pet slot {receiver_slot + 1}...")
    while True:
        check_merge_stop()
        pet_coords = get_pet_coord(window, receiver_slot)
        if pet_coords:
            click_at_window_position(window, pet_coords[0], pet_coords[1])
            time.sleep(0.3)
            break
        time.sleep(0.5)
    
    print("[AUTO_MERGE] Searching for Carry button...")
    while True:
        check_merge_stop()
        carry_coords = get_ui_coord(window, "CARRY")
        if carry_coords:
            click_at_window_position(window, carry_coords[0], carry_coords[1])
            print(f"[AUTO_MERGE] Set pet {receiver_slot + 1} to Carry")
            break
        time.sleep(0.5)
    
    # Step 6: Click Merge button (retry until found)
    check_merge_stop()
    print("[AUTO_MERGE] Searching for Merge button...")
    while True:
        check_merge_stop()
        merge_coords = get_ui_coord(window, "MERGE")
        if merge_coords:
            click_at_window_position(window, merge_coords[0], merge_coords[1])
            print("[AUTO_MERGE] Opened Merge interface")
            time.sleep(0.5)
            break
        time.sleep(0.5)
    
    # Step 7: Reposition merge interface to top-right corner (only if not already there)
    # Check Slot A position to determine if interface needs repositioning
    check_merge_stop()
    slot_a_coords = get_ui_coord(window, "SLOT_A")
    if slot_a_coords:
        # If Slot A is near default position (around 150,300), drag to corner
        # If Slot A is already near top-right (around 700,150), skip
        if slot_a_coords[0] < 400:  # Interface is on the left side, needs repositioning
            drag_to_corner(window)
            print("[AUTO_MERGE] Repositioned merge interface")
        else:
            print("[AUTO_MERGE] Merge interface already positioned")
    
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
    
    # Step 8: Find receiver pet and drag to Slot A (retry until found)
    print(f"[AUTO_MERGE] Searching for receiver pet {receiver_slot + 1}...")
    while True:
        check_merge_stop()
        receiver_coords = get_pet_coord(window, receiver_slot)
        if receiver_coords:
            break
        time.sleep(0.5)
    
    print("[AUTO_MERGE] Searching for Slot A...")
    while True:
        check_merge_stop()
        slot_a_coords = get_ui_coord(window, "SLOT_A")
        if slot_a_coords:
            break
        time.sleep(0.5)
    
    drag_element_to_target(window, receiver_coords, slot_a_coords)
    print(f"[AUTO_MERGE] Dragged pet {receiver_slot + 1} to Slot A")
    
    # Step 9: Find provider pet and drag to Slot B (retry until found)
    check_merge_stop()
    print(f"[AUTO_MERGE] Searching for provider pet {provider_slot + 1}...")
    while True:
        check_merge_stop()
        provider_coords = get_pet_coord(window, provider_slot)
        if provider_coords:
            break
        time.sleep(0.5)
    
    print("[AUTO_MERGE] Searching for Slot B...")
    while True:
        check_merge_stop()
        slot_b_coords = get_ui_coord(window, "SLOT_B")
        if slot_b_coords:
            break
        time.sleep(0.5)
    
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
    
    # Step 12: Click Merging Pets 4 times (apply, merge, finish, close) - retry until found
    check_merge_stop()
    print("[AUTO_MERGE] Searching for Merging Pets button...")
    while True:
        check_merge_stop()
        merge_btn_coords = get_ui_coord(window, "MERGING_PETS")
        if merge_btn_coords:
            break
        time.sleep(0.5)
    
    for i in range(4):
        check_merge_stop()
        click_at_window_position(window, merge_btn_coords[0], merge_btn_coords[1], delay=0.8)
    print("[AUTO_MERGE] Completed merge clicks (4x)")
    
    # Step 13: Reopen merge interface (it closes after the 4 clicks)
    time.sleep(0.5)
    merge_coords = get_ui_coord(window, "MERGE")
    if merge_coords:
        click_at_window_position(window, merge_coords[0], merge_coords[1])
        print("[AUTO_MERGE] Reopened Merge interface")
        time.sleep(0.5)
    
    return True, spirits_available


# =============================================================================
# STEP 14: COLLECT NEW PETS FROM BAG
# =============================================================================

def collect_new_pets(window, provider_slot):
    """
    Step 14: Open bag, try to collect pets. If 3 consecutive attempts fail, 
    switch to New Bag and complete remaining attempts there.
    
    Args:
        window: pygetwindow Window object
        provider_slot: Slot where merged pet was, to set as carry if new pets found
    
    Returns: Number of right-clicks performed (max 20 total)
    """
    check_merge_stop()
    
    # Open main bag
    print("[AUTO_MERGE] Searching for Bag button...")
    while True:
        check_merge_stop()
        bag_coords = get_ui_coord(window, "BAG")
        if bag_coords:
            click_at_window_position(window, bag_coords[0], bag_coords[1])
            time.sleep(0.5)
            break
        time.sleep(0.5)
    
    pets_collected = 0
    consecutive_fails = 0
    attempts_made = 0
    switched_to_new_bag = False
    
    # Try up to BAG_SEARCH_MAX_ATTEMPTS total
    print("[AUTO_MERGE] Collecting pets from main bag...")
    while attempts_made < BAG_SEARCH_MAX_ATTEMPTS:
        check_merge_stop()
        
        # If 3 consecutive fails and haven't switched yet, switch to New Bag
        if consecutive_fails >= 3 and not switched_to_new_bag:
            print(f"[AUTO_MERGE] No pets found after 3 attempts. Switching to New Bag...")
            print("[AUTO_MERGE] Searching for New Bag tab...")
            while True:
                check_merge_stop()
                new_bag_coords = get_ui_coord(window, "NEW_BAG")
                if new_bag_coords:
                    click_at_window_position(window, new_bag_coords[0], new_bag_coords[1])
                    time.sleep(0.5)
                    break
                time.sleep(0.5)
            switched_to_new_bag = True
            consecutive_fails = 0
            print(f"[AUTO_MERGE] Continuing search in New Bag ({BAG_SEARCH_MAX_ATTEMPTS - attempts_made} attempts remaining)...")
        
        pet_coords = get_ui_coord(window, "PET_IN_BAG")
        if pet_coords:
            click_at_window_position(window, pet_coords[0], pet_coords[1], 
                                   delay=PET_BAG_DELAY, button='right')
            pets_collected += 1
            consecutive_fails = 0
        else:
            consecutive_fails += 1
        
        attempts_made += 1
    
    # Close bag
    click_at_window_position(window, bag_coords[0], bag_coords[1])
    print(f"[AUTO_MERGE] Total collected: {pets_collected} pets")
    
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
    
    # Step 16: Mount up (retry until found)
    check_merge_stop()
    print("[AUTO_MERGE] Searching for Mount button...")
    while True:
        check_merge_stop()
        mount_coords = get_ui_coord(window, "MOUNT")
        if mount_coords:
            click_at_window_position(window, mount_coords[0], mount_coords[1])
            print(f"[AUTO_MERGE] Mounting... waiting {MOUNT_WAIT}s for mount animation")
            time.sleep(MOUNT_WAIT)
            break
        time.sleep(0.5)
    
    # Step 17: Click Search (retry until found)
    check_merge_stop()
    print("[AUTO_MERGE] Searching for Search button...")
    while True:
        check_merge_stop()
        search_coords = get_ui_coord(window, "SEARCH")
        if search_coords:
            click_at_window_position(window, search_coords[0], search_coords[1])
            break
        time.sleep(0.5)
    
    # Step 18: Click Transporter in search menu (retry until found)
    check_merge_stop()
    print("[AUTO_MERGE] Searching for Transporter in search menu...")
    while True:
        check_merge_stop()
        trans_search_coords = get_ui_coord(window, "TRANSPORTER_SEARCH")
        if trans_search_coords:
            click_at_window_position(window, trans_search_coords[0], trans_search_coords[1])
            break
        time.sleep(0.5)
    
    print(f"[AUTO_MERGE] Going to Transporter, waiting {TRANSPORTER_WAIT}s")
    time.sleep(TRANSPORTER_WAIT)
    
    # Step 19: Click on Transporter NPC (retry until found)
    check_merge_stop()
    print("[AUTO_MERGE] Searching for Transporter NPC...")
    while True:
        check_merge_stop()
        transporter_coords = get_ui_coord(window, "TRANSPORTER_NPC")
        if transporter_coords:
            # Offset: 0px left, 170px down from the fixed anchor stone (user adjustment)
            target_x = transporter_coords[0]
            target_y = transporter_coords[1] + 170
            
            # Calculate absolute screen coordinates (required for directly using moveTo)
            abs_x = window.left + target_x
            abs_y = window.top + target_y
            
            # Move mouse and wait for inertia to stop
            pyautogui.moveTo(abs_x, abs_y)
            time.sleep(1.0)  # Wait for movement to settle
            
            # Click and wait for dialog
            pyautogui.click()
            time.sleep(2.5)  # Wait for dialog to open
            print("[AUTO_MERGE] Clicked Transporter NPC")
            break
        time.sleep(0.5)
    
    # Step 20: Click Transmit (retry until found)
    check_merge_stop()
    print("[AUTO_MERGE] Searching for Transmit button...")
    while True:
        check_merge_stop()
        transmit_coords = get_ui_coord(window, "TRANSMIT")
        if transmit_coords:
            click_at_window_position(window, transmit_coords[0], transmit_coords[1])
            time.sleep(0.5)
            print("[AUTO_MERGE] Clicked Transmit")
            break
        time.sleep(0.5)
    
    if destination.lower() == "thermopylae":
        return _travel_thermopylae(window)
    else:
        return _travel_larissa(window)


def _travel_thermopylae(window):
    """Travel to Thermopylae via Parnitha Port"""
    check_merge_stop()
    
    # Step 21: Click Parnitha Port (retry until found)
    print("[AUTO_MERGE] Searching for Parnitha Port...")
    while True:
        check_merge_stop()
        parnitha_coords = get_ui_coord(window, "PARNITHA_PORT")
        if parnitha_coords:
            click_at_window_position(window, parnitha_coords[0], parnitha_coords[1])
            break
        time.sleep(0.5)
    
    # Step 22: Click OK
    ok_coords = get_ui_coord(window, "OK")
    if ok_coords:
        click_at_window_position(window, ok_coords[0], ok_coords[1])
    time.sleep(OK_WAIT)
    
    # Step 23: Click Thermopylae button (retry until found)
    check_merge_stop()
    print("[AUTO_MERGE] Searching for Thermopylae button...")
    while True:
        check_merge_stop()
        thermo_coords = get_ui_coord(window, "THERMO_BTN")
        if thermo_coords:
            click_at_window_position(window, thermo_coords[0], thermo_coords[1])
            print(f"[AUTO_MERGE] Traveling to Thermopylae, waiting {THERMO_WAIT}s")
            time.sleep(THERMO_WAIT)
            break
        time.sleep(0.5)
    
    return True


def _travel_larissa(window):
    """Travel to Larissa via Thebes -> Mycenae -> Larissa"""
    check_merge_stop()
    
    # 1. Click Thebes destination (in Athens Transporter menu) - retry until found
    print("[AUTO_MERGE] Searching for Thebes destination...")
    while True:
        check_merge_stop()
        thebes_coords = get_ui_coord(window, "THEBES")
        if thebes_coords:
            click_at_window_position(window, thebes_coords[0], thebes_coords[1])
            break
        time.sleep(0.5)
    
    # 2. Click OK to travel to Thebes
    ok_coords = get_ui_coord(window, "OK")
    if ok_coords:
        click_at_window_position(window, ok_coords[0], ok_coords[1])
    
    # 3. Wait 5s for Thebes map load
    print("[AUTO_MERGE] Traveling to Thebes, waiting 5s")
    time.sleep(5.0)
    
    # 4. Click Mycenae Transporter (NPC in Thebes) - retry until found
    check_merge_stop()
    print("[AUTO_MERGE] Searching for Mycenae Transporter in Thebes...")
    while True:
        check_merge_stop()
        myc_trans_coords = get_ui_coord(window, "MYCENAE_TRANSPORTER")
        if not myc_trans_coords:
            myc_trans_coords = get_ui_coord(window, "TRANSPORTER_NPC")
        if myc_trans_coords:
            break
        time.sleep(0.5)
            
    # Move -> Wait -> Click pattern
    target_x = myc_trans_coords[0]
    target_y = myc_trans_coords[1]
    abs_x = window.left + target_x
    abs_y = window.top + target_y
    
    pyautogui.moveTo(abs_x, abs_y)
    time.sleep(1.0)
    pyautogui.click()
    
    # 5. Wait 3s
    time.sleep(3.0)
    
    # 6. Click Transmit of Thebes (to go to Mycenae) - retry until found
    print("[AUTO_MERGE] Searching for Transmit button in Thebes...")
    while True:
        check_merge_stop()
        transmit_coords = get_ui_coord(window, "TRANSMIT")
        if transmit_coords:
            click_at_window_position(window, transmit_coords[0], transmit_coords[1])
            break
        time.sleep(0.5)
    
    # 7. Click Go to Mycenae (retry until found)
    print("[AUTO_MERGE] Searching for 'Go to Mycenae' option...")
    while True:
        check_merge_stop()
        go_myc_coords = get_ui_coord(window, "GO_TO_MYCENAE")
        if go_myc_coords:
            click_at_window_position(window, go_myc_coords[0], go_myc_coords[1])
            break
        time.sleep(0.5)
    
    # 8. Click OK
    ok_coords = get_ui_coord(window, "OK")
    if ok_coords:
        click_at_window_position(window, ok_coords[0], ok_coords[1])
    
    # 9. Wait 2s (Teleport to Mycenae)
    print("[AUTO_MERGE] Traveling to Mycenae, waiting 2s")
    time.sleep(2.0)
    
    # 10. Click Transporter of Mycenae (inside Mycenae) - retry until found
    check_merge_stop()
    print("[AUTO_MERGE] Searching for Inner Transporter in Mycenae...")
    while True:
        check_merge_stop()
        myc_inner_trans_coords = get_ui_coord(window, "MYCENAE_INNER_TRANSPORTER")
        if not myc_inner_trans_coords:
            myc_inner_trans_coords = get_ui_coord(window, "TRANSPORTER_NPC")
        if myc_inner_trans_coords:
            break
        time.sleep(0.5)
    
    # Move -> Wait -> Click pattern
    target_x = myc_inner_trans_coords[0]
    target_y = myc_inner_trans_coords[1]
    abs_x = window.left + target_x
    abs_y = window.top + target_y
    
    pyautogui.moveTo(abs_x, abs_y)
    time.sleep(1.0)
    pyautogui.click()
    time.sleep(5.0) 
    
    # 11. Click Transmit of Mycenae (retry until found)
    print("[AUTO_MERGE] Searching for Transmit button in Mycenae...")
    while True:
        check_merge_stop()
        transmit_myc_coords = get_ui_coord(window, "TRANSMIT_MYCENAE")
        if not transmit_myc_coords:
            transmit_myc_coords = get_ui_coord(window, "TRANSMIT")
        if transmit_myc_coords:
            click_at_window_position(window, transmit_myc_coords[0], transmit_myc_coords[1])
            break
        time.sleep(0.5)
    
    # 12. Click Go to Larissa (retry until found)
    print("[AUTO_MERGE] Searching for 'Go to Larissa' option...")
    while True:
        check_merge_stop()
        go_lar_coords = get_ui_coord(window, "GO_TO_LARISSA")
        if go_lar_coords:
            click_at_window_position(window, go_lar_coords[0], go_lar_coords[1])
            break
        time.sleep(0.5)
    
    # 13. Click OK
    ok_coords = get_ui_coord(window, "OK")
    if ok_coords:
        click_at_window_position(window, ok_coords[0], ok_coords[1])
        
    # 14. Wait 2s
    time.sleep(2.0)
    
    # 15. Click Larissa Button (retry until found)
    check_merge_stop()
    print("[AUTO_MERGE] Searching for Larissa button...")
    while True:
        check_merge_stop()
        larissa_coords = get_ui_coord(window, "LARISSA_BTN")
        if larissa_coords:
            click_at_window_position(window, larissa_coords[0], larissa_coords[1])
            print(f"[AUTO_MERGE] Arrived in Larissa, waiting {LARISSA_WAIT}s")
            time.sleep(LARISSA_WAIT)
            break
        time.sleep(0.5)
    
    return True
    
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
    
    # Step 25: Click AFK (retry until found)
    check_merge_stop()
    print("[AUTO_MERGE] Searching for AFK button...")
    while True:
        check_merge_stop()
        afk_coords = get_ui_coord(window, "AFK")
        if afk_coords:
            click_at_window_position(window, afk_coords[0], afk_coords[1])
            break
        time.sleep(0.5)
    
    # Step 26: Click Start (retry until found)
    check_merge_stop()
    print("[AUTO_MERGE] Searching for Start button...")
    while True:
        check_merge_stop()
        start_coords = get_ui_coord(window, "START_AFK")
        if start_coords:
            click_at_window_position(window, start_coords[0], start_coords[1])
            print("[AUTO_MERGE] Started AFK mode")
            break
        time.sleep(0.5)
    
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
    # Calculate total pets to merge based on provider slot
    # If provider is slot 6 (index 5), we can merge slots 6, 7, 8 = 3 pets
    total_to_merge = 8 - provider_slot  # e.g., provider slot 6 (index 5) -> 8-5 = 3 merges
    
    spirits_available = use_spirit
    merges_completed = 0
    pets_collected = 0  # Initialize for debug mode
    
    def log(msg):
        print(msg)
        if gui_callback and hasattr(gui_callback, 'log'):
            gui_callback.root.after(0, lambda: gui_callback.log(msg))
    
    log(f"[AUTO_MERGE] Config received: receiver_slot={receiver_slot}, provider_slot={provider_slot}")
    log(f"[AUTO_MERGE] Starting auto merge: {total_to_merge} pets to merge")
    log(f"[AUTO_MERGE] Receiver: Pet {receiver_slot + 1}, Provider starts at: Pet {provider_slot + 1}")
    
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
        # NOTE: Always use the same provider_slot because after each merge,
        # the game automatically moves the next pet into that slot position
        while merges_completed < min(total_to_merge, max_merges):
            check_merge_stop()
            
            # Always use the same provider slot (game moves pets automatically)
            success, spirits_available = perform_single_merge(
                window, receiver_slot, provider_slot, use_spirit, spirits_available
            )
            
            if success:
                merges_completed += 1
                log(f"[AUTO_MERGE] Merge {merges_completed}/{total_to_merge} completed (always using slot {provider_slot + 1})")
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
