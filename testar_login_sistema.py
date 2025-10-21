#!/usr/bin/env python3
"""Script para testar login direto no sistema"""

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

def testar_login():
    with app.app_context():
        print("=== TESTANDO LOGIN DO SISTEMA ===")
        
        # Verificar se usuário existe
        usuario = models.Usuario.query.filter_by(username='alissonporto').first()
        
        if not usuario:
            print("❌ ERRO: Usuário 'alissonporto' não encontrado!")
            return False
        
        print(f"✅ Usuário encontrado: {usuario.username}")
        print(f"   ID: {usuario.id}")
        print(f"   Admin: {usuario.is_admin}")
        print(f"   Criado em: {usuario.created_at}")
        
        # Testar senha
        senha_correta = check_password_hash(usuario.password_hash, 'porto510')
        
        if senha_correta:
            print("✅ Senha está correta!")
            
            # Atualizar last_login
            from datetime import datetime
            usuario.last_login = datetime.now()
            db.session.commit()
            
            print("✅ Last login atualizado!")
            print("\n🎉 LOGIN FUNCIONAL!")
            print("👤 Usuário: alissonporto")  
            print("🔑 Senha: porto510")
            print("🌐 Acesse: http://127.0.0.1:5000/login")
            return True
        else:
            print("❌ ERRO: Senha incorreta!")
            return False

if __name__ == "__main__":
    testar_login()