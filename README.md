# 🎮 Pet Factory - Auto Pet Leveling para Godswar Origin

## 🤖 INSTRUCCIONES PARA AGENTE AI (SETUP AUTOMÁTICO)

Este documento contiene todos los pasos necesarios para configurar y ejecutar el programa Pet Factory. Sigue estos pasos en orden.

---

## PASO 1: Verificar Python está instalado

```powershell
python --version
```

**Resultado esperado:** Python 3.8 o superior
**Si falla:** Instalar Python desde https://www.python.org/downloads/ (versión 3.8+)

---

## PASO 2: Instalar Tesseract OCR (CRÍTICO)

Tesseract es un motor de OCR necesario para leer números del juego.

### Opción A - Instalación automática con Chocolatey:

```powershell
# Instalar Chocolatey si no está instalado
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Instalar Tesseract
choco install tesseract -y
```

### Opción B - Instalación manual:

1. Descargar: https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.3.3.20231005.exe
2. Ejecutar el instalador
3. Usar ruta por defecto: `C:\Program Files\Tesseract-OCR`
4. Completar instalación

### Verificar instalación:

```powershell
Test-Path "C:\Program Files\Tesseract-OCR\tesseract.exe"
```

**Resultado esperado:** True

---

## PASO 3: Instalar dependencias de Python

Navegar a la carpeta del proyecto:

```powershell
cd "c:\Users\diego\Escritorio\Godswar cosas\PetFactory"
```

Instalar todas las librerías necesarias:

```powershell
pip install pywin32 pytesseract opencv-python pillow pynput
```

### Verificar instalación:

```powershell
python -c "import win32gui, pytesseract, cv2, PIL, pynput; print('✓ Todas las dependencias instaladas correctamente')"
```

---

## PASO 4: Ejecutar el programa

### Método A - Ejecutar directamente (desarrollo):

```powershell
cd "c:\Users\diego\Escritorio\Godswar cosas\PetFactory"
python PetFactory.py
```

### Método B - Crear ejecutable (distribución):

```powershell
cd "c:\Users\diego\Escritorio\Godswar cosas\PetFactory"

# Instalar PyInstaller
pip install pyinstaller

# Crear el ejecutable
pyinstaller --onefile --name="PetFactory" --hidden-import=PIL._tkinter_finder --hidden-import=pynput.keyboard._win32 --hidden-import=pynput.mouse._win32 --collect-all pytesseract --collect-all cv2 --collect-all PIL --collect-all pynput PetFactory.py

# El ejecutable estará en: dist\PetFactory.exe
```

---

## PASO 5: Cómo usar el programa

### Pre-requisitos:

1. Tener Godswar Origin abierto (puede tener hasta 6 ventanas)
2. Las ventanas deben tener "Godswar Origin" en el título

### Flujo de uso:

1. **Ejecutar** el programa (PetFactory.py o PetFactory.exe)
2. **Click en "GET NAMES"** - Captura los nombres de las cuentas automáticamente
3. **Marcar checkbox (☐)** de las cuentas que quieres monitorear
4. **Double-click en "Not set"** en la columna "Target EXP" para configurar la EXP objetivo (ejemplo: 10000000)
5. **Click en "START MONITORING"** - El programa comenzará a trabajar

### Qué hace automáticamente:

- ✅ Analiza las 8 pets de cada personaje
- ✅ Monta la pet más cercana al objetivo
- ✅ Revisa cada 30 segundos la EXP actual
- ✅ Cuando una pet llega al objetivo, la marca como completada
- ✅ Monta automáticamente la siguiente pet
- ✅ Cuando las 8 pets están completas, muestra "🎉 All pets done!"

### Atajos:

- **D + F (simultáneo)**: Detener el monitoreo inmediatamente

---

## COORDENADAS Y CONFIGURACIÓN

El programa usa estas coordenadas fijas (relativas a la ventana del juego):

### Posiciones de las 8 pets:

- Pet 1: (170, 375)
- Pet 2: (240, 375)
- Pet 3: (310, 375)
- Pet 4: (380, 375)
- Pet 5: (170, 420)
- Pet 6: (240, 420)
- Pet 7: (310, 420)
- Pet 8: (380, 420)

### Botones:

- Panel de pets: (880, 717)
- Details: (280, 490)
- Carry: (200, 490)
- Exit details: (400, 100)

### Regiones de captura OCR:

- EXP de pet: (119, 564) a (314, 583)
- Nombre de cuenta: (123, 29) a (208, 46)

**NOTA:** Si el juego tiene una resolución o escala diferente, estas coordenadas pueden necesitar ajuste.

---

## TROUBLESHOOTING

### Error: "Could not read EXP"

**Causa:** Tesseract no está instalado o no se encuentra
**Solución:**

```powershell
# Verificar que existe
Test-Path "C:\Program Files\Tesseract-OCR\tesseract.exe"

# Si devuelve False, reinstalar Tesseract (ver PASO 2)
```

### Error: "ModuleNotFoundError: No module named 'X'"

**Causa:** Falta instalar una dependencia
**Solución:**

```powershell
pip install pywin32 pytesseract opencv-python pillow pynput
```

### Error: "No processes found" o no detecta ventanas

**Causa:** Las ventanas del juego no tienen "Godswar Origin" en el título
**Solución:**

- Verificar que el juego esté abierto
- Verificar que el título de la ventana contenga "godswar" y "origin" (case-insensitive)
- Reiniciar el programa

### El programa no hace click correctamente

**Causa:** Las coordenadas no coinciden con la resolución del juego
**Solución:** Puede requerir ajustar las coordenadas en las constantes del código

### Error al crear .exe con PyInstaller

**Causa:** Conflictos de versiones o rutas
**Solución:**

```powershell
pip install --upgrade pyinstaller
# Eliminar carpetas anteriores
Remove-Item -Recurse -Force build, dist, *.spec -ErrorAction SilentlyContinue
# Volver a ejecutar PyInstaller
```

---

## DEPENDENCIAS COMPLETAS

```
Python >= 3.8
pywin32 >= 305
pytesseract >= 0.3.10
opencv-python >= 4.8.0
pillow >= 10.0.0
pynput >= 1.7.6
pyinstaller >= 6.0.0 (solo para crear .exe)

SOFTWARE EXTERNO:
Tesseract-OCR >= 5.0 (instalado en C:\Program Files\Tesseract-OCR)
```

---

## ESTRUCTURA DEL PROYECTO

```
PetFactory/
├── PetFactory.py          (código principal)
├── build_exe.bat          (script para crear ejecutable)
├── INSTRUCCIONES.md       (instrucciones para usuario final)
├── README.md              (este archivo - guía completa)
├── build/                 (generado por PyInstaller)
├── dist/                  (ejecutable final aquí)
│   └── PetFactory.exe
└── PetFactory.spec        (configuración PyInstaller)
```

---

## COMANDOS RÁPIDOS (RESUMEN)

```powershell
# Setup completo desde cero
choco install tesseract -y
cd "c:\Users\diego\Escritorio\Godswar cosas\PetFactory"
pip install pywin32 pytesseract opencv-python pillow pynput
python PetFactory.py

# Crear ejecutable
pip install pyinstaller
pyinstaller --onefile --name="PetFactory" --hidden-import=PIL._tkinter_finder --hidden-import=pynput.keyboard._win32 --hidden-import=pynput.mouse._win32 --collect-all pytesseract PetFactory.py
```

---

## PARA DISTRIBUIR A USUARIO FINAL

Enviar una carpeta con:

1. **dist\PetFactory.exe** (el ejecutable)
2. **INSTRUCCIONES.md** (manual de usuario)
3. **Link de Tesseract:** https://github.com/UB-Mannheim/tesseract/wiki

El usuario debe:

1. Instalar Tesseract OCR en `C:\Program Files\Tesseract-OCR`
2. Ejecutar `PetFactory.exe`
3. Seguir las instrucciones en pantalla

**NO se necesita Python ni otras dependencias instaladas, todo está incluido en el .exe excepto Tesseract.**
