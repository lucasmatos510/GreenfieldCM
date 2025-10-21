#!/usr/bin/env python3
"""
WSGI entry point para Gunicorn
Resolve conflito entre pasta app/ e arquivo app.py
"""

import os
import sys

# Adicionar diretório atual ao Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def create_app():
    """Cria e retorna a aplicação Flask"""
    try:
        # Método 1: Importlib
        import importlib.util
        spec = importlib.util.spec_from_file_location("main_app", os.path.join(current_dir, "app.py"))
        if spec and spec.loader:
            main_app = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(main_app)
            return main_app.app
    except Exception as e:
        print(f"Método 1 falhou: {e}")
        
    try:
        # Método 2: Exec com namespace isolado
        namespace = {'__name__': '__main__'}
        app_path = os.path.join(current_dir, 'app.py')
        with open(app_path, 'r', encoding='utf-8') as f:
            exec(f.read(), namespace)
        return namespace['app']
    except Exception as e:
        print(f"Método 2 falhou: {e}")
        
    # Método 3: Import direto forçado
    try:
        # Remove app module se já estiver carregado
        if 'app' in sys.modules:
            del sys.modules['app']
        
        # Renomear pasta temporariamente se existir
        app_dir = os.path.join(current_dir, 'app')
        temp_dir = os.path.join(current_dir, 'app_temp')
        renamed = False
        
        if os.path.isdir(app_dir):
            os.rename(app_dir, temp_dir)
            renamed = True
            
        try:
            import app as app_module
            flask_app = app_module.app
        finally:
            if renamed and os.path.isdir(temp_dir):
                os.rename(temp_dir, app_dir)
                
        return flask_app
    except Exception as e:
        print(f"Método 3 falhou: {e}")
        raise RuntimeError("Não foi possível importar a aplicação Flask")

# Criar aplicação
app = create_app()

if __name__ == "__main__":
    app.run()