#!/usr/bin/env python3
"""Script para verificar usuário específico no banco"""

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

# Usar o db já configurado
db = models.db
db.init_app(app)

def verificar_usuario(username):
    with app.app_context():
        print(f"=== VERIFICANDO USUÁRIO: {username} ===")
        
        usuario = models.Usuario.query.filter_by(username=username).first()
        
        if usuario:
            print(f"✅ Usuário encontrado:")
            print(f"📝 Username: {usuario.username}")
            print(f"👑 É admin: {usuario.is_admin}")
            print(f"📅 Criado em: {usuario.created_at}")
            print(f"🔐 Hash da senha: {usuario.password_hash}")
            print(f"\n⚠️  IMPORTANTE: A senha está criptografada e não pode ser recuperada.")
            print(f"💡 Para testar uma senha, use a função check_password_hash().")
            
            # Tentar algumas senhas comuns
            senhas_teste = ['123456', 'admin', 'password', 'alissonporto', 'Alissonporto', 'alissonporto123']
            print(f"\n🔍 Testando senhas comuns:")
            for senha in senhas_teste:
                if check_password_hash(usuario.password_hash, senha):
                    print(f"✅ SENHA ENCONTRADA: '{senha}'")
                    return senha
                else:
                    print(f"❌ '{senha}' - não é a senha")
            
            print(f"\n🔒 Nenhuma das senhas comuns funcionou.")
            print(f"📋 Para redefinir a senha, você pode:")
            print(f"1. Deletar o banco de dados e configurar novamente")
            print(f"2. Criar um script para alterar a senha")
            print(f"3. Usar a interface de setup para criar novo usuário")
            
        else:
            print(f"❌ Usuário '{username}' não foi encontrado no banco de dados.")
            
            # Listar todos os usuários
            todos_usuarios = models.Usuario.query.all()
            print(f"\n📋 Usuários cadastrados no sistema ({len(todos_usuarios)}):")
            for user in todos_usuarios:
                print(f"  - {user.username} (Admin: {user.is_admin}) - Criado: {user.created_at}")

if __name__ == "__main__":
    username = input("Digite o username para verificar (ou pressione Enter para 'alissonporto'): ").strip()
    if not username:
        username = 'alissonporto'
    
    verificar_usuario(username)