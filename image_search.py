"""
Image Search - Busca imágenes b64 en pantalla y devuelve coordenadas
"""
import base64
import io
import numpy as np
from PIL import Image
import pyautogui
import cv2


def search_image(b64_string, window, confidence=0.8):
    """
    Busca una imagen b64 dentro de una ventana y devuelve las coordenadas.
    
    Args:
        b64_string: Código base64 de la imagen a buscar
        window: Objeto pygetwindow Window
        confidence: Umbral de coincidencia (0.0 a 1.0)
    
    Returns:
        tuple: (rel_x, rel_y) coordenadas relativas a la ventana, o None si no encontró
    """
    if not b64_string or b64_string == "#":
        return None
    
    # Decodificar b64 a imagen OpenCV
    try:
        image_bytes = base64.b64decode(b64_string)
        pil_image = Image.open(io.BytesIO(image_bytes))
        
        if pil_image.mode == 'RGBA':
            pil_image = pil_image.convert('RGB')
        
        template = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    except Exception:
        return None
    
    # Capturar región de la ventana
    region = (window.left, window.top, window.width, window.height)
    screenshot = pyautogui.screenshot(region=region)
    screenshot_bgr = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    
    # Buscar template
    result = cv2.matchTemplate(screenshot_bgr, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    
    if max_val >= confidence:
        template_h, template_w = template.shape[:2]
        rel_x = max_loc[0] + template_w // 2
        rel_y = max_loc[1] + template_h // 2
        return (rel_x, rel_y)
    
    return None
