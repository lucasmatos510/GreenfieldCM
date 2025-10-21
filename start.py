#!/usr/bin/env python3
"""
Script de inicialização para Render
Garante que a aplicação seja iniciada corretamente independente da configuração
"""

import os
import sys
import subprocess
import time

def main():
    print("🚀 RENDER STARTUP SCRIPT")
    print("=" * 50)
    
    # 1. Debug do ambiente
    print("📊 1. Executando diagnóstico...")
    try:
        result = subprocess.run([sys.executable, "debug_render.py"], 
                              capture_output=True, text=True, timeout=60)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
    except Exception as e:
        print(f"❌ Erro no debug: {e}")
    
    # 2. Inicializar banco de dados
    print("📊 2. Inicializando banco de dados...")
    try:
        result = subprocess.run([sys.executable, "init_db.py"], 
                              capture_output=True, text=True, timeout=120)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
    except Exception as e:
        print(f"❌ Erro na inicialização do banco: {e}")
    
    # 3. Verificar se run.py funciona
    print("📊 3. Testando run.py...")
    try:
        result = subprocess.run([sys.executable, "-c", "from run import app; print('✅ run.py OK')"], 
                              capture_output=True, text=True, timeout=30)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
    except Exception as e:
        print(f"❌ Erro no teste do run.py: {e}")
    
    # 4. Iniciar Gunicorn
    print("📊 4. Iniciando Gunicorn...")
    
    port = os.environ.get('PORT', '10000')
    host = os.environ.get('HOST', '0.0.0.0')
    
    print(f"🌐 Configuração de rede: {host}:{port}")
    
    # Tentar diferentes configurações de app
    app_configs = ['run:app', 'run:application', 'main:app', 'app:app', 'application:app']
    
    for app_config in app_configs:
        print(f"🔧 Tentando: {app_config}")
        
        cmd = [
            'gunicorn',
            '--workers=1',
            '--timeout=300', 
            '--keep-alive=2',
            f'--bind={host}:{port}',
            '--access-logfile=-',
            '--error-logfile=-',
            app_config
        ]
        
        try:
            print(f"🚀 Executando: {' '.join(cmd)}")
            os.execvp('gunicorn', cmd)  # Substitui o processo atual
        except Exception as e:
            print(f"❌ Falha com {app_config}: {e}")
            continue
    
    print("❌ ERRO: Todas as configurações falharam!")
    sys.exit(1)

if __name__ == "__main__":
    main()