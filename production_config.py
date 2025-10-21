"""
Configuração de Produção para Deploy no Render
"""

import os

class ProductionConfig:
    """Configuração otimizada para produção no Render"""
    
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'fallback-secret-key-change-this'
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///sistema_banco_horas.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'connect_args': {
            'connect_timeout': 10,
            'application_name': 'sistema_banco_horas'
        } if 'postgresql' in os.environ.get('DATABASE_URL', '') else {}
    }
    
    # Flask
    ENV = 'production'
    DEBUG = False
    TESTING = False
    
    # File uploads
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # Session
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours
    
    # Security Headers
    SEND_FILE_MAX_AGE_DEFAULT = 31536000  # 1 year
    
    # Application specific
    TIMEZONE = 'America/Sao_Paulo'
    
    @staticmethod
    def init_app(app):
        """Inicialização específica para produção"""
        # Configurar logging para produção
        import logging
        from logging.handlers import SysLogHandler
        
        if not app.debug:
            # Log para stdout (Render captura automaticamente)
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(logging.INFO)
            stream_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            app.logger.addHandler(stream_handler)
            app.logger.setLevel(logging.INFO)
            app.logger.info('Sistema de Banco de Horas iniciado em produção')

class DevelopmentConfig:
    """Configuração para desenvolvimento local"""
    
    SECRET_KEY = 'dev-secret-key-not-for-production'
    WTF_CSRF_ENABLED = True
    
    # Database local
    SQLALCHEMY_DATABASE_URI = 'sqlite:///sistema_banco_horas.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Flask
    ENV = 'development'
    DEBUG = True
    TESTING = False
    
    # File uploads
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    TIMEZONE = 'America/Sao_Paulo'

# Configurações por ambiente
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Retorna a configuração baseada no ambiente"""
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])