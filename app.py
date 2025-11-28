"""
SAORI AI Core - Flask App Entry Point
Railway necesita un archivo app.py o main.py en la raíz para detectar Flask automáticamente
"""
import sys
import os
from pathlib import Path

# Agregar src/ al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / 'src'))

# Importar y ejecutar el bot
from whatsapp_bot import app

if __name__ == '__main__':
    # Railway asigna PORT automáticamente
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
