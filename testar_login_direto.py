#!/usr/bin/env python3
"""Script para testar login diretamente no contexto Flask"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from app import models
from flask import Flask
from werkzeug.security import check_password_hash

# Configurar aplicação Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///banco_horas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'test-key'

# Usar o db já configurado
db = models.db
db.init_app(app)

def testar_login_direto():
    with app.app_context():
        print("=== TESTE DE LOGIN DIRETO ===")
        
        # Verificar usuário
        usuario = models.Usuario.query.filter_by(username='Alissonporto').first()
        
        if not usuario:
            print("❌ Usuário não encontrado!")
            return
            
        print(f"✅ Usuário encontrado: {usuario.username}")
        
        # Testar senha
        senha_teste = 'porto510'
        resultado = check_password_hash(usuario.password_hash, senha_teste)
        
        if resultado:
            print(f"✅ Senha '{senha_teste}' está CORRETA!")
            print("\nO problema deve estar nas rotas ou redirecionamentos.")
            
            # Verificar se todas as tabelas existem
            print("\n=== VERIFICANDO TABELAS ===")
            
            try:
                funcionarios = models.Funcionario.query.count()
                print(f"✅ Tabela funcionarios: {funcionarios} registros")
            except Exception as e:
                print(f"❌ Erro na tabela funcionarios: {e}")
            
            try:
                cargos = models.Cargo.query.count()
                print(f"✅ Tabela cargos: {cargos} registros")
            except Exception as e:
                print(f"❌ Erro na tabela cargos: {e}")
                
            try:
                areas = models.AreaAtuacao.query.count()
                print(f"✅ Tabela areas_atuacao: {areas} registros")
            except Exception as e:
                print(f"❌ Erro na tabela areas_atuacao: {e}")
                
        else:
            print(f"❌ Senha '{senha_teste}' está INCORRETA!")

if __name__ == "__main__":
    testar_login_direto()