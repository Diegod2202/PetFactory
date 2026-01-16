"""
Image Search Module
Searches for Base64 images on screen and returns coordinates
Enhanced with debugging capabilities and detailed logging
"""
import base64
import io
import os
import numpy as np
from PIL import Image
import pyautogui
import cv2
from datetime import datetime


# =============================================================================
# CONFIGURATION
# =============================================================================
DEBUG_MODE = True  # Set to True to enable detailed logging
LOG_THRESHOLD = 0.95  # Only log if confidence is below this (0.95 = 95%)
SAVE_FAILED_SCREENSHOTS = False  # Set to True to save screenshots when search fails
FAILED_SCREENSHOT_DIR = "debug_screenshots"  # Directory to save failed screenshots


def _log(message, force=False):
    """Internal logging function that respects DEBUG_MODE"""
    if DEBUG_MODE or force:
        print(f"[ImageSearch] {message}")


def _save_debug_screenshot(screenshot, template, element_name, confidence):
    """Save screenshot and template for debugging failed searches"""
    if not SAVE_FAILED_SCREENSHOTS:
        return
    
    try:
        os.makedirs(FAILED_SCREENSHOT_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save screenshot
        screenshot_path = os.path.join(FAILED_SCREENSHOT_DIR, f"{timestamp}_{element_name}_screenshot.png")
        cv2.imwrite(screenshot_path, screenshot)
        
        # Save template
        template_path = os.path.join(FAILED_SCREENSHOT_DIR, f"{timestamp}_{element_name}_template.png")
        cv2.imwrite(template_path, template)
        
        _log(f"Saved debug images: {screenshot_path}", force=True)
    except Exception as e:
        _log(f"Failed to save debug screenshot: {e}", force=True)


def search_image(b64_string, window, min_confidence=0.7, return_confidence=False, element_name="UNKNOWN"):
    """
    Search for a Base64 image within a window and return the best match coordinates.
    
    Uses a single screenshot capture and returns the best match found as long as
    it meets the minimum confidence threshold. This approach ensures finding the
    image if it exists with any confidence >= min_confidence.
    
    Args:
        b64_string: Base64 string of the image to search for
        window: pygetwindow Window object
        min_confidence: Minimum match threshold (0.0 to 1.0), default 0.7
        return_confidence: If True, returns (coords, confidence) tuple instead of just coords
        element_name: Name of element being searched (for logging)
    
    Returns:
        If return_confidence=False:
            tuple: (rel_x, rel_y) coordinates relative to the window, or None if not found
        If return_confidence=True:
            tuple: ((rel_x, rel_y), confidence_value) or (None, 0.0) if not found
    """
    # Validate input
    if not b64_string or b64_string == "#":
        _log(f"{element_name}: SKIPPED (empty or placeholder B64)")
        return (None, 0.0) if return_confidence else None
    
    # Decode b64 to OpenCV image
    try:
        image_bytes = base64.b64decode(b64_string)
        pil_image = Image.open(io.BytesIO(image_bytes))
        
        if pil_image.mode == 'RGBA':
            pil_image = pil_image.convert('RGB')
        
        template = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        template_h, template_w = template.shape[:2]
    except Exception as e:
        _log(f"{element_name}: ERROR decoding B64 - {e}", force=True)
        return (None, 0.0) if return_confidence else None
    
    # Validate window
    try:
        if window.width <= 0 or window.height <= 0:
            _log(f"{element_name}: ERROR window has invalid dimensions {window.width}x{window.height}", force=True)
            return (None, 0.0) if return_confidence else None
    except Exception as e:
        _log(f"{element_name}: ERROR accessing window - {e}", force=True)
        return (None, 0.0) if return_confidence else None
    
    # Capture window region (single capture for best performance)
    try:
        region = (window.left, window.top, window.width, window.height)
        screenshot = pyautogui.screenshot(region=region)
        screenshot_bgr = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    except Exception as e:
        _log(f"{element_name}: ERROR capturing screenshot - {e}", force=True)
        return (None, 0.0) if return_confidence else None
    
    # Check template fits in screenshot
    screenshot_h, screenshot_w = screenshot_bgr.shape[:2]
    if template_w > screenshot_w or template_h > screenshot_h:
        _log(f"{element_name}: Template ({template_w}x{template_h}) larger than window ({screenshot_w}x{screenshot_h})", force=True)
        return (None, 0.0) if return_confidence else None
    
    # Search for template - find the best match in a single pass
    result = cv2.matchTemplate(screenshot_bgr, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    
    # Return best match if it meets minimum confidence threshold
    if max_val >= min_confidence:
        rel_x = max_loc[0] + template_w // 2
        rel_y = max_loc[1] + template_h // 2
        coords = (rel_x, rel_y)
        # Only log if confidence is below LOG_THRESHOLD
        if max_val < LOG_THRESHOLD:
            _log(f"{element_name}: FOUND at ({rel_x}, {rel_y}) confidence={max_val:.2%} ⚠️")
        return (coords, max_val) if return_confidence else coords
    
    # NOT FOUND - log detailed information
    _log(f"{element_name}: NOT FOUND - best confidence={max_val:.2%} (threshold={min_confidence:.0%})", force=True)
    _log(f"{element_name}: Best match position was ({max_loc[0]}, {max_loc[1]})")
    
    # Save debug screenshots if enabled
    _save_debug_screenshot(screenshot_bgr, template, element_name, max_val)
    
    return (None, max_val) if return_confidence else None


def set_debug_mode(enabled):
    """Enable or disable debug logging"""
    global DEBUG_MODE
    DEBUG_MODE = enabled
    _log(f"Debug mode {'enabled' if enabled else 'disabled'}", force=True)


def set_save_failed_screenshots(enabled, directory=None):
    """Enable or disable saving screenshots when searches fail"""
    global SAVE_FAILED_SCREENSHOTS, FAILED_SCREENSHOT_DIR
    SAVE_FAILED_SCREENSHOTS = enabled
    if directory:
        FAILED_SCREENSHOT_DIR = directory
    _log(f"Save failed screenshots {'enabled' if enabled else 'disabled'}", force=True)
