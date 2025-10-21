#!/usr/bin/env python3
"""Script para verificar dados no banco"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from app import models
from flask import Flask

# Configurar aplicação Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///banco_horas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Usar o db já configurado
db = models.db
db.init_app(app)

def verificar_dados():
    with app.app_context():
        print("=== VERIFICANDO DADOS NO BANCO ===")
        
        registros = models.RegistroHora.query.all()
        print(f"\nRegistros encontrados: {len(registros)}")
        
        for r in registros:
            print(f"ID: {r.id}")
            print(f"Funcionário ID: {r.funcionario_id}")
            print(f"Data: {r.data}")
            print(f"Hora Início: {r.hora_inicio}")
            print(f"Hora Fim: {r.hora_fim}")
            print(f"Minutos: {r.minutos_trabalhados}")
            print(f"Tipo: {r.tipo_registro}")
            print(f"Observações: {r.observacoes}")
            print("-" * 40)
        
        funcionarios = models.Funcionario.query.all()
        print(f"\nFuncionários encontrados: {len(funcionarios)}")
        
        for f in funcionarios:
            print(f"ID: {f.id}, Nome: {f.nome}, Ativo: {f.ativo}")

if __name__ == "__main__":
    verificar_dados()