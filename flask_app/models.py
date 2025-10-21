from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, timedelta

db = SQLAlchemy()

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<Usuario {self.username}>'

class AreaAtuacao(db.Model):
    __tablename__ = 'areas_atuacao'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    descricao = db.Column(db.Text)
    ativo = db.Column(db.Boolean, default=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<AreaAtuacao {self.nome}>'

class Cargo(db.Model):
    __tablename__ = 'cargos'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    area_id = db.Column(db.Integer, db.ForeignKey('areas_atuacao.id'), nullable=True)
    salario_base = db.Column(db.Float)
    ativo = db.Column(db.Boolean, default=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    area = db.relationship('AreaAtuacao', backref='cargos')
    
    def __repr__(self):
        return f'<Cargo {self.nome}>'

class Funcionario(db.Model):
    __tablename__ = 'funcionarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cargo_id = db.Column(db.Integer, db.ForeignKey('cargos.id'), nullable=True)
    area_id = db.Column(db.Integer, db.ForeignKey('areas_atuacao.id'), nullable=True)
    ativo = db.Column(db.Boolean, default=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    cargo = db.relationship('Cargo', backref='funcionarios')
    area = db.relationship('AreaAtuacao', backref='funcionarios')
    
    def __repr__(self):
        return f'<Funcionario {self.nome}>'

class RegistroHora(db.Model):
    __tablename__ = 'registros_horas'
    
    id = db.Column(db.Integer, primary_key=True)
    funcionario_id = db.Column(db.Integer, db.ForeignKey('funcionarios.id'), nullable=False)
    data = db.Column(db.Date, nullable=False)
    horas = db.Column(db.Float, nullable=False)
    observacoes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    funcionario = db.relationship('Funcionario', backref='registros_horas')
    
    def __repr__(self):
        return f'<RegistroHora {self.data} - {self.horas}h>'

class ResumoDiario(db.Model):
    __tablename__ = 'resumos_diarios'
    
    id = db.Column(db.Integer, primary_key=True)
    funcionario_id = db.Column(db.Integer, db.ForeignKey('funcionarios.id'), nullable=False)
    cargo_id = db.Column(db.Integer, db.ForeignKey('cargos.id'), nullable=True)
    area_id = db.Column(db.Integer, db.ForeignKey('areas_atuacao.id'), nullable=True)
    data = db.Column(db.Date, nullable=False, index=True)
    total_horas = db.Column(db.Float, default=0)
    total_registros = db.Column(db.Integer, default=0)
    processado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    funcionario = db.relationship('Funcionario', backref='resumos_diarios')
    cargo = db.relationship('Cargo', backref='resumos_diarios')
    area = db.relationship('AreaAtuacao', backref='resumos_diarios')
    
    @classmethod
    def gerar_resumo_dia(cls, data_resumo):
        resumos_criados = 0
        registros = RegistroHora.query.filter_by(data=data_resumo).all()
        
        funcionarios_horas = {}
        for registro in registros:
            if registro.funcionario_id not in funcionarios_horas:
                funcionarios_horas[registro.funcionario_id] = {
                    'total_horas': 0,
                    'total_registros': 0,
                    'funcionario': registro.funcionario
                }
            funcionarios_horas[registro.funcionario_id]['total_horas'] += registro.horas
            funcionarios_horas[registro.funcionario_id]['total_registros'] += 1
        
        for funcionario_id, dados in funcionarios_horas.items():
            funcionario = dados['funcionario']
            resumo = cls.query.filter_by(funcionario_id=funcionario_id, data=data_resumo).first()
            
            if not resumo:
                resumo = cls(funcionario_id=funcionario_id, data=data_resumo)
                db.session.add(resumo)
                resumos_criados += 1
            
            resumo.total_horas = dados['total_horas']
            resumo.total_registros = dados['total_registros']
            resumo.cargo_id = funcionario.cargo_id
            resumo.area_id = funcionario.area_id
            resumo.atualizado_em = datetime.utcnow()
        
        db.session.commit()
        return resumos_criados
    
    def __repr__(self):
        funcionario_nome = self.funcionario.nome if self.funcionario else "N/A"
        return f'<ResumoDiario {funcionario_nome} - {self.data} - {self.total_horas}h>'
