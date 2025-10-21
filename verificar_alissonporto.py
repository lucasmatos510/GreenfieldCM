#!/usr/bin/env python3
"""Script para verificar usuário alissonporto no banco"""

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

with app.app_context():
    print("=== VERIFICANDO USUÁRIO: Alissonporto ===")
    
    usuario = models.Usuario.query.filter_by(username='Alissonporto').first()
    
    if usuario:
        print(f"✅ Usuário encontrado:")
        print(f"📝 Username: {usuario.username}")
        print(f"👑 É admin: {usuario.is_admin}")
        print(f"📅 Criado em: {usuario.created_at}")
        print(f"🔐 Hash da senha: {usuario.password_hash}")
        print(f"\n⚠️  IMPORTANTE: A senha foi criptografada.")
        
        print(f"\n🔍 Testando possíveis senhas:")
        
        # Lista expandida de senhas possíveis
        senhas_teste = [
            '123456', 'admin', 'password', 
            'alissonporto', 'Alissonporto', 'ALISSONPORTO',
            'alissonporto123', 'Alissonporto123', 'ALISSONPORTO123',
            'alisson', 'Alisson', 'porto', 'Porto',
            'alisson123', 'Alisson123', 'porto123', 'Porto123',
            '12345678', 'qwerty', '123123', 'abc123',
            'Alisson@123', 'alisson@123', 'Alissonporto@123'
        ]
        
        senha_encontrada = None
        for senha in senhas_teste:
            if check_password_hash(usuario.password_hash, senha):
                print(f"✅ SENHA ENCONTRADA: '{senha}'")
                senha_encontrada = senha
                break
            else:
                print(f"❌ '{senha}' - não é a senha")
        
        if not senha_encontrada:
            print(f"\n🔒 RESULTADO: Nenhuma das senhas testadas funcionou.")
            print(f"\n📋 DADOS DE ACESSO CONHECIDOS:")
            print(f"   👤 Username: {usuario.username}")
            print(f"   🔐 Senha: [DESCONHECIDA - Você deve lembrar da senha que definiu]")
            print(f"   🌐 URL: http://127.0.0.1:5000/login")
            print(f"\n💡 SOLUÇÕES:")
            print(f"   1. Tente lembrar da senha que você definiu")
            print(f"   2. Delete o arquivo 'banco_horas.db' e configure novamente")
            print(f"   3. Execute o sistema e acesse /setup para criar novo admin")
        else:
            print(f"\n🎉 DADOS DE ACESSO COMPLETOS:")
            print(f"   👤 Username: {usuario.username}")
            print(f"   🔐 Senha: {senha_encontrada}")
            print(f"   🌐 URL: http://127.0.0.1:5000/login")
            print(f"   👑 Tipo: Administrador")
        
    else:
        print(f"❌ Usuário 'Alissonporto' não foi encontrado.")
        
        # Listar todos os usuários
        todos_usuarios = models.Usuario.query.all()
        print(f"\n📋 Usuários cadastrados ({len(todos_usuarios)}):")
        for user in todos_usuarios:
            print(f"  - {user.username} (Admin: {user.is_admin}) - {user.created_at}")