#!/usr/bin/env python3
"""
Script de Inicialização para Deploy no Render
Cria as tabelas do banco e dados iniciais necessários.
"""

import os
import sys
from datetime import datetime

def init_database():
    """Inicializa o banco de dados no Render"""
    
    print("🔧 Iniciando configuração do banco de dados...")
    
    # Importar a aplicação
    from app import app
    
    with app.app_context():
        print("📊 Importando modelos...")
        from app.models import db, Usuario, AreaAtuacao, Cargo
        
        print("🗄️ Criando tabelas...")
        try:
            # Criar todas as tabelas
            db.create_all()
            print("✅ Tabelas criadas com sucesso!")
            
            # Verificar se já existem dados
            admin_exists = Usuario.query.filter_by(is_admin=True).first()
            if admin_exists:
                print("👤 Usuário admin já existe, pulando criação...")
                return
            
            print("👥 Criando dados iniciais...")
            
            # Criar áreas de atuação padrão
            areas_padrao = [
                {'nome': 'Tecnologia', 'descricao': 'Área de desenvolvimento e suporte técnico'},
                {'nome': 'Recursos Humanos', 'descricao': 'Gestão de pessoas e processos'},
                {'nome': 'Financeiro', 'descricao': 'Controladoria e gestão financeira'},
                {'nome': 'Comercial', 'descricao': 'Vendas e relacionamento com clientes'},
                {'nome': 'Operações', 'descricao': 'Processos operacionais e logística'}
            ]
            
            for area_data in areas_padrao:
                if not AreaAtuacao.query.filter_by(nome=area_data['nome']).first():
                    area = AreaAtuacao(
                        nome=area_data['nome'],
                        descricao=area_data['descricao']
                    )
                    db.session.add(area)
                    print(f"  ➕ Área criada: {area_data['nome']}")
            
            # Commit das áreas
            db.session.commit()
            
            # Criar cargos padrão para Tecnologia
            area_tech = AreaAtuacao.query.filter_by(nome='Tecnologia').first()
            if area_tech:
                cargos_tech = [
                    {'nome': 'Desenvolvedor', 'descricao': 'Desenvolvimento de software'},
                    {'nome': 'Analista de Sistemas', 'descricao': 'Análise e design de sistemas'},
                    {'nome': 'Administrador', 'descricao': 'Administração do sistema'}
                ]
                
                for cargo_data in cargos_tech:
                    if not Cargo.query.filter_by(nome=cargo_data['nome'], area_atuacao_id=area_tech.id).first():
                        cargo = Cargo(
                            nome=cargo_data['nome'],
                            descricao=cargo_data['descricao'],
                            area_atuacao_id=area_tech.id
                        )
                        db.session.add(cargo)
                        print(f"  💼 Cargo criado: {cargo_data['nome']}")
            
            # Criar usuário admin padrão
            cargo_admin = Cargo.query.filter_by(nome='Administrador').first()
            if cargo_admin and not Usuario.query.filter_by(username='admin').first():
                admin_user = Usuario(
                    username='admin',
                    email='admin@sistema.com',
                    nome_completo='Administrador do Sistema',
                    is_admin=True,
                    cargo_id=cargo_admin.id,
                    data_admissao=datetime.now().date(),
                    ativo=True
                )
                admin_user.set_password('admin123')  # Senha padrão - DEVE SER ALTERADA!
                db.session.add(admin_user)
                print("👤 Usuário admin criado (username: admin, senha: admin123)")
                print("⚠️  IMPORTANTE: Altere a senha do admin após o primeiro login!")
            
            # Commit final
            db.session.commit()
            print("✅ Dados iniciais criados com sucesso!")
            
        except Exception as e:
            print(f"❌ Erro ao criar banco de dados: {str(e)}")
            db.session.rollback()
            raise e
    
    print("🎉 Inicialização do banco concluída!")

if __name__ == '__main__':
    try:
        init_database()
        print("🚀 Sistema pronto para uso no Render!")
        sys.exit(0)
    except Exception as e:
        print(f"💥 Falha na inicialização: {str(e)}")
        sys.exit(1)