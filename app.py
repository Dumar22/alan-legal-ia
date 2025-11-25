#!/usr/bin/env python3
"""
WSGI Entry Point for Alana Legal Sense
Este archivo importa la aplicación Flask desde main.py para compatibilidad con Render/Heroku
"""

import os
import sys

# Asegurar que el directorio actual está en el path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar la aplicación Flask desde main.py
from main import app

# Para compatibilidad con diferentes servidores WSGI
application = app

if __name__ == "__main__":
    # Configuración para producción
    port = int(os.environ.get("PORT", 5000))
    debug_mode = os.environ.get("FLASK_ENV") != "production"
    
    print(f"🚀 Iniciando Alana Legal Sense via app.py en puerto {port}")
    
    app.run(host="0.0.0.0", port=port, debug=debug_mode)