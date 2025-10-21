#!/usr/bin/env python3
"""
Arquivo principal do Sistema de Banco de Horas
Entry point limpo sem conflitos de nomes para Gunicorn
"""

import os
import sys

# Adicionar diretório atual ao path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Importar a aplicação usando importlib para evitar conflitos
import importlib.util

def get_flask_app():
    """Importa e retorna a aplicação Flask do app.py"""
    try:
        # Usar importlib para importar diretamente do arquivo app.py
        app_path = os.path.join(current_dir, "app.py")
        spec = importlib.util.spec_from_file_location("main_app", app_path)
        
        if spec is None or spec.loader is None:
            raise ImportError("Não foi possível criar spec para app.py")
            
        main_app_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(main_app_module)
        
        # Retornar a instância da aplicação Flask
        return main_app_module.app
        
    except Exception as e:
        print(f"❌ Erro ao importar aplicação Flask: {e}")
        raise

# Criar instância da aplicação
app = get_flask_app()

if __name__ == "__main__":
    # Executar aplicação em modo desenvolvimento
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '127.0.0.1')
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'
    
    print("🚀 Iniciando Sistema de Banco de Horas...")
    print(f"📍 Servidor: http://{host}:{port}")
    print(f"🔧 Modo: {'Desenvolvimento' if debug else 'Produção'}")
    
    app.run(
        host=host,
        port=port,
        debug=debug,
        use_reloader=debug
    )