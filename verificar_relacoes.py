#!/usr/bin/env python3
"""Script para verificar relações no banco"""

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

def verificar_relacoes():
    with app.app_context():
        print("=== VERIFICANDO RELAÇÕES ===")
        
        # Testar a query dos relatórios
        try:
            query = models.RegistroHora.query.join(models.Funcionario).join(models.Cargo).join(models.AreaAtuacao)
            registros = query.all()
            print(f"Query com JOINs encontrou: {len(registros)} registros")
            
            for r in registros:
                print(f"Registro: {r.id}")
                print(f"Funcionário: {r.funcionario.nome}")
                print(f"Cargo: {r.funcionario.cargo.nome}")
                print(f"Área: {r.funcionario.area_atuacao.nome}")
                print("-" * 40)
                
        except Exception as e:
            print(f"Erro na query: {e}")
            
            # Verificar funcionário individual
            funcionario = models.Funcionario.query.get(1)
            if funcionario:
                print(f"Funcionário: {funcionario.nome}")
                print(f"Cargo ID: {funcionario.cargo_id}")
                print(f"Área ID: {funcionario.area_atuacao_id}")
                
                if funcionario.cargo:
                    print(f"Cargo: {funcionario.cargo.nome}")
                else:
                    print("ERRO: Cargo não encontrado!")
                    
                if funcionario.area_atuacao:
                    print(f"Área: {funcionario.area_atuacao.nome}")
                else:
                    print("ERRO: Área não encontrada!")

if __name__ == "__main__":
    verificar_relacoes()