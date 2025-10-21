"""
Configurações do Sistema de Banco de Horas
Arquivo de configuração centralizado para melhor organização e manutenção.
"""

import os
from datetime import timedelta

class Config:
    """Configuração base do sistema"""
    
    # Configurações básicas
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Configuração do banco de dados
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///banco_horas.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'echo': False  # Set True for SQL debugging
    }
    
    # Configurações de sessão
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    
    # Configurações de upload/arquivos
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max
    UPLOAD_FOLDER = 'uploads'
    
    # Configurações de segurança
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    
    # Configurações de performance
    SQLALCHEMY_RECORD_QUERIES = True
    DATABASE_QUERY_TIMEOUT = 30
    
    # Configurações de exportação
    EXCEL_EXPORT_PATH = os.path.expanduser('~/Downloads')
    MAX_EXPORT_RECORDS = 10000
    
    # Configurações de logging
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'sistema_banco_horas.log'
    
    # Configurações de paginação
    RECORDS_PER_PAGE = 20
    MAX_SEARCH_RESULTS = 1000
    
    # Configurações de validação
    MIN_EMPLOYEE_NAME_LENGTH = 2
    MAX_EMPLOYEE_NAME_LENGTH = 100
    MIN_POSITION_NAME_LENGTH = 2
    MAX_POSITION_NAME_LENGTH = 100
    MAX_DESCRIPTION_LENGTH = 500
    MAX_OBSERVATION_LENGTH = 500
    MAX_SALARY = 999999.99
    MIN_YEAR = 2020
    MAX_YEAR = 2030

class DevelopmentConfig(Config):
    """Configuração para desenvolvimento"""
    DEBUG = True
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'echo': True  # SQL debugging habilitado
    }

class ProductionConfig(Config):
    """Configuração para produção"""
    DEBUG = False
    # Configurações de segurança para produção
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

class TestingConfig(Config):
    """Configuração para testes"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

# Dicionário de configurações
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}