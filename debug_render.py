#!/usr/bin/env python3
"""
Script de debug para Render - Verifica ambiente e dependências
"""

import os
import sys
import traceback

def debug_render_environment():
    """Diagnóstica o ambiente Render"""
    
    print("=" * 60)
    print("🔍 DIAGNÓSTICO DO AMBIENTE RENDER")
    print("=" * 60)
    
    # Informações do sistema
    print(f"🐍 Python: {sys.version}")
    print(f"📂 Diretório atual: {os.getcwd()}")
    print(f"📄 Arquivos no diretório:")
    
    try:
        files = os.listdir('.')
        for file in sorted(files):
            if os.path.isdir(file):
                print(f"   📁 {file}/")
            else:
                print(f"   📄 {file}")
    except Exception as e:
        print(f"   ❌ Erro ao listar arquivos: {e}")
    
    # Variáveis de ambiente importantes
    print(f"\n🔧 Variáveis de ambiente:")
    env_vars = ['PORT', 'DATABASE_URL', 'FLASK_ENV', 'SECRET_KEY', 'PYTHON_PATH']
    for var in env_vars:
        value = os.environ.get(var, 'NÃO DEFINIDA')
        if var == 'SECRET_KEY' and value != 'NÃO DEFINIDA':
            value = f"***{value[-4:]}" if len(value) > 4 else "***"
        elif var == 'DATABASE_URL' and value != 'NÃO DEFINIDA':
            # Mostrar formato da URL para diagnóstico
            if value.startswith('postgres://'):
                print(f"   ⚠️  {var}: {value[:30]}... (FORMATO INCORRETO - precisa ser postgresql://)")
            elif value.startswith('postgresql://'):
                print(f"   ✅ {var}: {value[:30]}... (FORMATO CORRETO)")
            else:
                print(f"   ❓ {var}: {value[:30]}... (FORMATO DESCONHECIDO)")
            continue
        print(f"   {var}: {value}")
    
    # Teste de imports críticos
    print(f"\n📦 Testando imports:")
    
    modules_to_test = ['flask', 'sqlalchemy', 'psycopg2', 'gunicorn']
    for module in modules_to_test:
        try:
            __import__(module)
            print(f"   ✅ {module}")
        except ImportError as e:
            print(f"   ❌ {module}: {e}")
    
    # Teste do main.py
    print(f"\n🎯 Testando main.py:")
    try:
        from main import app
        print(f"   ✅ main.py importado com sucesso!")
        print(f"   📱 Tipo da app: {type(app)}")
        print(f"   🏷️  Nome da app: {app.name}")
        print(f"   ⚙️  Config SECRET_KEY: {'Definido' if app.config.get('SECRET_KEY') else 'NÃO definido'}")
        print(f"   🗄️  Database URI: {app.config.get('SQLALCHEMY_DATABASE_URI', 'NÃO definido')[:50]}...")
    except Exception as e:
        print(f"   ❌ Erro ao importar main.py:")
        print(f"      {e}")
        traceback.print_exc()
    
    # Teste do banco de dados
    print(f"\n🗄️  Testando conexão com banco:")
    try:
        from main import app
        with app.app_context():
            from flask_app.models import db
            db.engine.execute('SELECT 1')
            print(f"   ✅ Conexão com banco OK!")
    except Exception as e:
        print(f"   ❌ Erro na conexão com banco:")
        print(f"      {e}")
    
    print("=" * 60)
    print("✅ DIAGNÓSTICO CONCLUÍDO")
    print("=" * 60)

if __name__ == "__main__":
    debug_render_environment()