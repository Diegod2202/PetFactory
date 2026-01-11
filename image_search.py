"""
Image Search Module
Searches for Base64 images on screen and returns coordinates
"""
import base64
import io
import numpy as np
from PIL import Image
import pyautogui
import cv2


def search_image(b64_string, window, confidence=0.8):
    """
    Search for a Base64 image within a window and return coordinates.
    
    Args:
        b64_string: Base64 string of the image to search for
        window: pygetwindow Window object
        confidence: Match threshold (0.0 to 1.0)
    
    Returns:
        tuple: (rel_x, rel_y) coordinates relative to the window, or None if not found
    """
    if not b64_string or b64_string == "#":
        return None
    
    # Decode b64 to OpenCV image
    try:
        image_bytes = base64.b64decode(b64_string)
        pil_image = Image.open(io.BytesIO(image_bytes))
        
        if pil_image.mode == 'RGBA':
            pil_image = pil_image.convert('RGB')
        
        template = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    except Exception:
        return None
    
    # Capture window region
    region = (window.left, window.top, window.width, window.height)
    screenshot = pyautogui.screenshot(region=region)
    screenshot_bgr = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    
    # Search for template
    result = cv2.matchTemplate(screenshot_bgr, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    
    if max_val >= confidence:
        template_h, template_w = template.shape[:2]
        rel_x = max_loc[0] + template_w // 2
        rel_y = max_loc[1] + template_h // 2
        return (rel_x, rel_y)
    
    return None
