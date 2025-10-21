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
    """Importa e retorna a aplicação Flask do app.py com múltiplos fallbacks"""
    
    print("🔄 Iniciando importação da aplicação Flask...")
    
    # Método 1: Importlib (preferido)
    try:
        print("📝 Tentativa 1: Usando importlib...")
        app_path = os.path.join(current_dir, "app.py")
        
        if not os.path.exists(app_path):
            raise FileNotFoundError(f"Arquivo app.py não encontrado em: {app_path}")
        
        spec = importlib.util.spec_from_file_location("main_app", app_path)
        
        if spec is None or spec.loader is None:
            raise ImportError("Não foi possível criar spec para app.py")
            
        main_app_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(main_app_module)
        
        if not hasattr(main_app_module, 'app'):
            raise AttributeError("Módulo app.py não possui atributo 'app'")
        
        flask_app = main_app_module.app
        print("✅ Importação com importlib bem-sucedida!")
        return flask_app
        
    except Exception as e:
        print(f"❌ Método 1 falhou: {e}")
    
    # Método 2: Exec direto
    try:
        print("📝 Tentativa 2: Usando exec...")
        app_path = os.path.join(current_dir, "app.py")
        
        namespace = {
            '__file__': app_path,
            '__name__': '__main__',
            '__package__': None
        }
        
        with open(app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        exec(code, namespace)
        
        if 'app' not in namespace:
            raise AttributeError("Variável 'app' não encontrada após exec")
        
        flask_app = namespace['app']
        print("✅ Importação com exec bem-sucedida!")
        return flask_app
        
    except Exception as e:
        print(f"❌ Método 2 falhou: {e}")
    
    # Método 3: Import direto com sys.path
    try:
        print("📝 Tentativa 3: Import direto...")
        
        # Remover módulo se já carregado
        if 'app' in sys.modules:
            del sys.modules['app']
        
        # Temporariamente renomear pasta app/ se existir
        app_dir = os.path.join(current_dir, 'app')
        temp_dir = os.path.join(current_dir, 'app_backup_temp')
        renamed = False
        
        if os.path.isdir(app_dir):
            os.rename(app_dir, temp_dir)
            renamed = True
        
        try:
            import app as app_module
            flask_app = app_module.app
            print("✅ Importação direta bem-sucedida!")
            return flask_app
        finally:
            # Restaurar pasta
            if renamed and os.path.isdir(temp_dir):
                os.rename(temp_dir, app_dir)
        
    except Exception as e:
        print(f"❌ Método 3 falhou: {e}")
    
    # Se chegou até aqui, todos os métodos falharam
    raise RuntimeError(
        "❌ ERRO CRÍTICO: Não foi possível importar a aplicação Flask por nenhum método!\n"
        f"📁 Diretório atual: {current_dir}\n"
        f"📄 Arquivos disponíveis: {os.listdir(current_dir)}"
    )

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