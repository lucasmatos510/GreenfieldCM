#!/usr/bin/env python3
"""
Arquivo de execução para Render - Múltiplas opções de import
Este arquivo garante que qualquer configuração do Render funcione:
- run:app, run:application
- app:app, app:application  
- main:app, main:application
"""

import os
import sys

# Adicionar diretório atual ao path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def get_app():
    """Importa a aplicação Flask usando múltiplos métodos"""
    print("🚀 [run.py] Iniciando importação da aplicação...")
    
    # Método 1: Importar do main.py
    try:
        print("📝 [run.py] Tentativa 1: Importando de main.py...")
        from main import app as main_app
        print("✅ [run.py] Sucesso com main.py!")
        return main_app
    except Exception as e:
        print(f"❌ [run.py] Falha com main.py: {e}")
    
    # Método 2: Importar do app.py usando importlib
    try:
        print("📝 [run.py] Tentativa 2: Importando de app.py com importlib...")
        import importlib.util
        
        app_path = os.path.join(current_dir, "app.py")
        spec = importlib.util.spec_from_file_location("app_module", app_path)
        app_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(app_module)
        
        flask_app = app_module.app
        print("✅ [run.py] Sucesso com app.py via importlib!")
        return flask_app
    except Exception as e:
        print(f"❌ [run.py] Falha com app.py importlib: {e}")
    
    # Método 3: Import direto forçado
    try:
        print("📝 [run.py] Tentativa 3: Import direto...")
        
        # Renomear pasta app temporariamente
        app_dir = os.path.join(current_dir, 'app')
        temp_dir = os.path.join(current_dir, 'app_temp_rename')
        renamed = False
        
        if os.path.isdir(app_dir) and not os.path.exists(temp_dir):
            os.rename(app_dir, temp_dir)
            renamed = True
            print("📁 [run.py] Pasta app/ renomeada temporariamente")
        
        try:
            # Remover do cache se existir
            if 'app' in sys.modules:
                del sys.modules['app']
            
            import app as app_module
            flask_app = app_module.app
            print("✅ [run.py] Sucesso com import direto!")
            return flask_app
        finally:
            # Restaurar nome da pasta
            if renamed and os.path.isdir(temp_dir):
                os.rename(temp_dir, app_dir)
                print("📁 [run.py] Pasta app/ restaurada")
        
    except Exception as e:
        print(f"❌ [run.py] Falha com import direto: {e}")
    
    raise RuntimeError("❌ [run.py] ERRO CRÍTICO: Não foi possível importar Flask app por nenhum método!")

# Importar aplicação
print("🔄 [run.py] Iniciando sistema...")
app = get_app()
application = app  # Gunicorn aceita tanto 'app' quanto 'application'

print(f"✅ [run.py] Aplicação Flask carregada com sucesso!")
print(f"📱 [run.py] Tipo: {type(app)}")
print(f"🏷️  [run.py] Nome: {app.name}")

if __name__ == "__main__":
    print("🚀 [run.py] Executando em modo desenvolvimento...")
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)