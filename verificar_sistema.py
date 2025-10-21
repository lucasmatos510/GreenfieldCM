#!/usr/bin/env python3
"""
Script de Verificação do Sistema de Banco de Horas
Executa testes básicos para garantir que o sistema está funcionando corretamente.
"""

import sys
import os
import sqlite3
from datetime import datetime, date

def verificar_estrutura_banco():
    """Verifica se todas as tabelas estão criadas corretamente"""
    print("🔍 Verificando estrutura do banco de dados...")
    
    try:
        conn = sqlite3.connect('banco_horas.db')
        cursor = conn.cursor()
        
        # Verificar tabelas existentes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tabelas = [row[0] for row in cursor.fetchall()]
        
        tabelas_esperadas = ['area_atuacao', 'cargo', 'funcionario', 'registro_hora']
        
        for tabela in tabelas_esperadas:
            if tabela in tabelas:
                print(f"  ✅ Tabela {tabela} existe")
            else:
                print(f"  ❌ Tabela {tabela} não encontrada")
                return False
        
        conn.close()
        return True
    except Exception as e:
        print(f"  ❌ Erro ao verificar banco: {e}")
        return False

def verificar_arquivos_sistema():
    """Verifica se todos os arquivos essenciais existem"""
    print("\n📁 Verificando arquivos do sistema...")
    
    arquivos_essenciais = [
        'app.py',
        'config.py',
        'app/__init__.py',
        'app/models.py',
        'app/routes.py',
        'app/utils.py',
        'templates/base.html',
        'templates/dashboard.html',
        'templates/relatorios.html',
        'templates/horas/registrar.html',
        'templates/funcionarios/listar.html',
        'templates/funcionarios/novo.html',
        'templates/cargos/gerenciar.html',
        'templates/errors/404.html',
        'templates/errors/500.html'
    ]
    
    todos_existem = True
    for arquivo in arquivos_essenciais:
        if os.path.exists(arquivo):
            print(f"  ✅ {arquivo}")
        else:
            print(f"  ❌ {arquivo} não encontrado")
            todos_existem = False
    
    return todos_existem

def verificar_configuracao():
    """Verifica se a configuração está correta"""
    print("\n⚙️  Verificando configuração...")
    
    try:
        from config import config
        conf = config['development']
        
        print(f"  ✅ Configuração carregada: {conf.__name__}")
        print(f"  ✅ Banco de dados: {conf.SQLALCHEMY_DATABASE_URI}")
        print(f"  ✅ Debug: {getattr(conf, 'DEBUG', False)}")
        
        return True
    except Exception as e:
        print(f"  ❌ Erro na configuração: {e}")
        return False

def verificar_modelos():
    """Verifica se os modelos estão funcionando"""
    print("\n🏗️  Verificando modelos...")
    
    try:
        from app.models import db, Funcionario, Cargo, AreaAtuacao, RegistroHora
        print("  ✅ Modelos importados com sucesso")
        
        # Verificar se as classes têm os atributos esperados
        atributos_funcionario = ['nome', 'email', 'cargo_id', 'ativo']
        for attr in atributos_funcionario:
            if hasattr(Funcionario, attr):
                print(f"  ✅ Funcionario.{attr}")
            else:
                print(f"  ❌ Funcionario.{attr} não encontrado")
                return False
        
        return True
    except Exception as e:
        print(f"  ❌ Erro nos modelos: {e}")
        return False

def verificar_utils():
    """Verifica se as funções utilitárias estão funcionando"""
    print("\n🛠️  Verificando utilitários...")
    
    try:
        from app.utils import gerar_relatorio_excel
        print("  ✅ Função gerar_relatorio_excel importada")
        return True
    except Exception as e:
        print(f"  ❌ Erro nos utilitários: {e}")
        return False

def executar_teste_basico():
    """Executa um teste básico de funcionamento"""
    print("\n🧪 Executando teste básico...")
    
    try:
        # Simular importação da aplicação
        sys.path.insert(0, os.getcwd())
        
        # Teste de importação
        from app import create_app
        app = create_app('testing')
        
        with app.app_context():
            from app.models import db
            db.create_all()
            print("  ✅ Aplicação criada com sucesso")
            print("  ✅ Banco de dados inicializado")
        
        return True
    except Exception as e:
        print(f"  ❌ Erro no teste básico: {e}")
        return False

def main():
    """Função principal do script de verificação"""
    print("🚀 SISTEMA DE BANCO DE HORAS - VERIFICAÇÃO COMPLETA")
    print("=" * 60)
    
    resultados = []
    
    # Executar todas as verificações
    resultados.append(verificar_arquivos_sistema())
    resultados.append(verificar_configuracao())
    resultados.append(verificar_modelos())
    resultados.append(verificar_utils())
    resultados.append(verificar_estrutura_banco())
    resultados.append(executar_teste_basico())
    
    print("\n" + "=" * 60)
    print("📊 RESUMO DA VERIFICAÇÃO")
    
    if all(resultados):
        print("🎉 SUCESSO! Todos os testes passaram.")
        print("✅ O sistema está pronto para uso!")
        print("\n🚀 Para iniciar o sistema execute:")
        print("   python app.py")
        print("\n🌐 O sistema estará disponível em:")
        print("   http://127.0.0.1:5000")
        return 0
    else:
        print("❌ FALHA! Alguns testes falharam.")
        print("🔧 Verifique os erros acima e corrija-os antes de usar o sistema.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)