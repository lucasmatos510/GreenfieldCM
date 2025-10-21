#!/usr/bin/env python3
"""Script para redefinir senha do usuário Alissonporto"""

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

# Usar o db já configurado
db = models.db
db.init_app(app)

def redefinir_senha():
    with app.app_context():
        print("=== REDEFINIR SENHA - USUÁRIO ALISSONPORTO ===")
        
        usuario = models.Usuario.query.filter_by(username='Alissonporto').first()
        
        if not usuario:
            print("❌ Usuário 'Alissonporto' não encontrado!")
            return
        
        print(f"✅ Usuário encontrado: {usuario.username}")
        print(f"📅 Criado em: {usuario.created_at}")
        
        # Solicitar nova senha
        print(f"\n🔐 Digite uma nova senha para o usuário '{usuario.username}':")
        print("💡 Sugestões: 123456, admin123, Alissonporto123, etc.")
        
        nova_senha = input("Nova senha: ").strip()
        
        if not nova_senha:
            print("❌ Senha não pode estar vazia!")
            return
        
        if len(nova_senha) < 4:
            print("❌ Senha deve ter pelo menos 4 caracteres!")
            return
        
        # Confirmar senha
        confirmar = input(f"Confirme a nova senha '{nova_senha}': ").strip()
        
        if nova_senha != confirmar:
            print("❌ As senhas não coincidem!")
            return
        
        # Gerar novo hash da senha
        novo_hash = generate_password_hash(nova_senha)
        
        # Atualizar no banco
        usuario.password_hash = novo_hash
        usuario.last_login = None  # Resetar último login
        
        try:
            db.session.commit()
            print(f"\n🎉 SENHA REDEFINIDA COM SUCESSO!")
            print(f"📋 NOVOS DADOS DE ACESSO:")
            print(f"   👤 Username: {usuario.username}")
            print(f"   🔐 Nova Senha: {nova_senha}")
            print(f"   🌐 URL: http://127.0.0.1:5000/login")
            print(f"   👑 Tipo: Administrador")
            print(f"\n✅ Agora você pode fazer login no sistema!")
            
        except Exception as e:
            print(f"❌ Erro ao salvar nova senha: {e}")
            db.session.rollback()

if __name__ == "__main__":
    redefinir_senha()