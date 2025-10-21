#!/usr/bin/env python3
"""Script para criar dados de teste simples"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from app import models
from flask import Flask
from datetime import datetime, date

# Configurar aplicação Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///banco_horas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'test-key'

# Usar o db já configurado
db = models.db
db.init_app(app)

def criar_dados_simples():
    with app.app_context():
        print("=== CRIANDO DADOS DE TESTE ===")
        
        try:
            # Limpar dados existentes (exceto usuários)
            models.RegistroHora.query.delete()
            models.Funcionario.query.delete()
            models.Cargo.query.delete()
            models.AreaAtuacao.query.delete()
            
            # Criar áreas
            area1 = models.AreaAtuacao(nome="TI - Tecnologia", ativo=True)
            area2 = models.AreaAtuacao(nome="RH - Recursos Humanos", ativo=True)
            area3 = models.AreaAtuacao(nome="Financeiro", ativo=True)
            
            db.session.add_all([area1, area2, area3])
            db.session.flush()  # Para obter os IDs
            
            # Criar cargos
            cargo1 = models.Cargo(nome="Desenvolvedor", area_id=area1.id, ativo=True)
            cargo2 = models.Cargo(nome="Analista de Sistemas", area_id=area1.id, ativo=True)
            cargo3 = models.Cargo(nome="Analista de RH", area_id=area2.id, ativo=True)
            cargo4 = models.Cargo(nome="Contador", area_id=area3.id, ativo=True)
            
            db.session.add_all([cargo1, cargo2, cargo3, cargo4])
            db.session.flush()  # Para obter os IDs
            
            # Criar funcionários
            func1 = models.Funcionario(nome="João Silva", cargo_id=cargo1.id, area_id=area1.id, ativo=True)
            func2 = models.Funcionario(nome="Maria Santos", cargo_id=cargo2.id, area_id=area1.id, ativo=True)
            func3 = models.Funcionario(nome="Pedro Costa", cargo_id=cargo3.id, area_id=area2.id, ativo=True)
            func4 = models.Funcionario(nome="Ana Lima", cargo_id=cargo4.id, area_id=area3.id, ativo=True)
            func5 = models.Funcionario(nome="Carlos Souza", cargo_id=cargo1.id, area_id=area1.id, ativo=True)
            
            db.session.add_all([func1, func2, func3, func4, func5])
            db.session.flush()  # Para obter os IDs
            
            # Criar alguns registros de horas
            hoje = date.today()
            
            # Registros para João Silva
            reg1 = models.RegistroHora(funcionario_id=func1.id, data=hoje, horas=2.5, observacoes="Correção de bugs")
            reg2 = models.RegistroHora(funcionario_id=func1.id, data=date(hoje.year, hoje.month, hoje.day-1), horas=1.0, observacoes="Deploy de sistema")
            
            # Registros para Maria Santos
            reg3 = models.RegistroHora(funcionario_id=func2.id, data=hoje, horas=3.0, observacoes="Análise de requisitos")
            reg4 = models.RegistroHora(funcionario_id=func2.id, data=date(hoje.year, hoje.month, hoje.day-2), horas=1.5, observacoes="Documentação")
            
            # Registros para Pedro Costa
            reg5 = models.RegistroHora(funcionario_id=func3.id, data=hoje, horas=2.0, observacoes="Entrevistas")
            
            db.session.add_all([reg1, reg2, reg3, reg4, reg5])
            
            # Commit tudo
            db.session.commit()
            
            print("✅ DADOS DE TESTE CRIADOS COM SUCESSO!")
            print(f"- 3 Áreas de atuação")
            print(f"- 4 Cargos")
            print(f"- 5 Funcionários") 
            print(f"- 5 Registros de horas")
            print("\n🎯 Sistema pronto para uso!")
            print("👤 Login: alissonporto")
            print("🔑 Senha: porto510")
            print("🌐 URL: http://127.0.0.1:5000/login")
            
        except Exception as e:
            print(f"❌ ERRO: {e}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    criar_dados_simples()