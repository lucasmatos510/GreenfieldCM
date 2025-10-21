#!/usr/bin/env python3
"""
Entry point alternativo - application.py
Para casos onde Render procura por application:app
"""

# Importar do run.py (nosso entry point principal)
from run import app, application

# Expor com nomes alternativos
flask_app = app
server = app

if __name__ == "__main__":
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)