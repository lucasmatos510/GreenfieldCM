#!/usr/bin/env python3
"""Script para criar usuário administrador diretamente"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from app import models
from flask import Flask
from werkzeug.security import generate_password_hash
from datetime import datetime

# Configurar aplicação Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///banco_horas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'test-key'

# Usar o db já configurado
db = models.db
db.init_app(app)

def criar_usuario_admin():
    with app.app_context():
        print("=== CRIANDO USUARIO ADMINISTRADOR ===")
        
        # Criar todas as tabelas primeiro
        try:
            db.create_all()
            print("TABELAS criadas com sucesso!")
        except Exception as e:
            print(f"Erro ao criar tabelas: {e}")
        
        # Verificar se usuário já existe
        usuario_existente = models.Usuario.query.filter_by(username='alissonporto').first()
        if usuario_existente:
            print("USUARIO 'alissonporto' ja existe! Deletando...")
            db.session.delete(usuario_existente)
            db.session.commit()
        
        # Criar novo usuário
        try:
            novo_usuario = models.Usuario(
                username='alissonporto',
                password_hash=generate_password_hash('porto510'),
                is_admin=True,
                created_at=datetime.now()
            )
            
            db.session.add(novo_usuario)
            db.session.commit()
            
            print("SUCESSO: Usuario criado!")
            print("Username: alissonporto")
            print("Senha: porto510")
            print("Tipo: Administrador")
            print("URL: http://127.0.0.1:5000/login")
            
        except Exception as e:
            print(f"ERRO ao criar usuario: {e}")
            db.session.rollback()

if __name__ == "__main__":
    criar_usuario_admin()