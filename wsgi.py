"""
WSGI entry point para Gunicorn - Solução para conflito de nomes
"""

# Renomear temporariamente a pasta app para evitar conflito
import os
import sys

# Adicionar diretório atual ao path
sys.path.insert(0, '.')

try:
    # Tentar importar diretamente do arquivo app.py
    import importlib.util
    spec = importlib.util.spec_from_file_location("main_app", "app.py")
    main_app = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(main_app)
    app = main_app.app
except:
    # Fallback: exec direto
    namespace = {}
    with open('app.py', 'r', encoding='utf-8') as f:
        exec(f.read(), namespace)
    app = namespace['app']

if __name__ == "__main__":
    app.run()