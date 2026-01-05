# Pet Factory - Instrucciones para tu amigo

## Requisitos previos (IMPORTANTE)

Antes de usar el programa, tu amigo DEBE instalar:

### 1. Tesseract OCR

- Descargar de: https://github.com/UB-Mannheim/tesseract/wiki
- Instalar en la ubicación por defecto: `C:\Program Files\Tesseract-OCR`
- Durante la instalación, asegurarse de marcar la opción de "Add to PATH"

## Cómo usar Pet Factory

### Primera vez:

1. Abrir el juego Godswar Origin (puede abrir hasta 6 ventanas)
2. Ejecutar `PetFactory.exe`
3. Click en "GET NAMES" para capturar los nombres de las cuentas
4. Marcar las casillas (☐) de las cuentas que quieres monitorear
5. Hacer doble-click en "Not set" para poner la EXP objetivo (ejemplo: 10,000,000)
6. Click en "START MONITORING"

### Proceso automático:

- El programa analiza las 8 pets de cada personaje
- Monta automáticamente la pet más cercana al objetivo
- Revisa cada 30 segundos
- Cuando una pet llega al objetivo, la marca como completada y monta la siguiente
- Cuando las 8 pets están completas, muestra "🎉 All pets done!"

### Atajos:

- **D + F**: Detener el monitoreo en cualquier momento

### Notas importantes:

- Las ventanas del juego se minimizarán/restaurarán automáticamente
- NO cerrar el programa mientras está monitoreando
- Cada cuenta puede tener su propio EXP objetivo
- El progreso se muestra en tiempo real

## Problemas comunes

### "Could not read EXP"

- Verifica que Tesseract esté instalado correctamente
- Las coordenadas del juego deben coincidir con la configuración

### "No Monitors Enabled"

- Asegúrate de marcar al menos una casilla
- Configura el EXP objetivo antes de habilitar

### El programa no detecta las ventanas

- Asegúrate que el título de la ventana contenga "Godswar Origin"
- Reinicia el programa si abriste el juego después
