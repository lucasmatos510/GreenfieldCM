#!/usr/bin/env python3
"""Script para criar dados de teste no sistema"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from app import models
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, time

# Configurar aplicação Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///banco_horas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Usar o db já configurado
db = models.db
db.init_app(app)

def criar_dados_teste():
    with app.app_context():
        # Verificar se já existem dados
        if models.Funcionario.query.count() > 0:
            print("Dados já existem no banco.")
            print(f"Cargos: {models.Cargo.query.count()}")
            print(f"Áreas: {models.AreaAtuacao.query.count()}")
            print(f"Funcionários: {models.Funcionario.query.count()}")
            print(f"Registros: {models.RegistroHora.query.count()}")
            return
        
        print("Criando dados de teste...")
        
        # Criar cargos
        cargo1 = models.Cargo(nome="Desenvolvedor", descricao="Desenvolvimento de software")
        cargo2 = models.Cargo(nome="Analista", descricao="Análise de sistemas")
        
        db.session.add(cargo1)
        db.session.add(cargo2)
        db.session.commit()
        
        # Criar áreas de atuação
        area1 = models.AreaAtuacao(nome="TI", descricao="Tecnologia da Informação")
        area2 = models.AreaAtuacao(nome="Administrativa", descricao="Área administrativa")
        
        db.session.add(area1)
        db.session.add(area2)
        db.session.commit()
        
        # Criar funcionários
        func1 = models.Funcionario(nome="João Silva", cargo_id=cargo1.id, area_atuacao_id=area1.id)
        func2 = models.Funcionario(nome="Maria Santos", cargo_id=cargo2.id, area_atuacao_id=area2.id)
        
        db.session.add(func1)
        db.session.add(func2)
        db.session.commit()
        
        # Criar registros de horas
        registro1 = models.RegistroHora(
            funcionario_id=func1.id,
            data=date.today(),
            hora_inicio=time(8, 0),
            hora_fim=time(17, 0),
            tipo_registro='normal',
            observacoes='Trabalho normal'
        )
        
        registro2 = models.RegistroHora(
            funcionario_id=func2.id,
            data=date.today(),
            hora_inicio=time(9, 0),
            hora_fim=time(18, 0),
            tipo_registro='normal',
            observacoes='Trabalho normal'
        )
        
        db.session.add(registro1)
        db.session.add(registro2)
        db.session.commit()
        
        print("Dados de teste criados com sucesso!")
        print(f"Cargos: {models.Cargo.query.count()}")
        print(f"Áreas: {models.AreaAtuacao.query.count()}")
        print(f"Funcionários: {models.Funcionario.query.count()}")
        print(f"Registros: {models.RegistroHora.query.count()}")

if __name__ == "__main__":
    criar_dados_teste()