"""
Sistema de Banco de Horas - Aplicação Principal
Sistema completo e otimizado para controle de horas trabalhadas.
Configurado para deploy no Render com PostgreSQL.
"""

from flask import Flask, render_template, redirect, url_for, session
import os
import logging
from datetime import datetime
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def create_app():
    """Factory function para criar a aplicação Flask otimizada para Render"""
    
    # Criar aplicação
    app = Flask(__name__)
    
    # Configuração para produção no Render
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    
    # Configuração do banco de dados
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        # Render PostgreSQL
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        # Desenvolvimento local
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sistema_banco_horas.db'
    
    # Configurações gerais
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['WTF_CSRF_ENABLED'] = True
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
    
    # Configurações de ambiente
    flask_env = os.environ.get('FLASK_ENV', 'development')
    app.config['ENV'] = flask_env
    app.debug = flask_env == 'development'
    
    # Configurar logging
    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = logging.FileHandler('logs/sistema_banco_horas.log')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s %(name)s %(message)s'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Sistema de Banco de Horas iniciado')
    
    # Inicializar extensões
    from app.models import db
    db.init_app(app)
    
    # Registrar blueprint de autenticação
    from app.auth import auth_bp
    app.register_blueprint(auth_bp)
    
    # Registrar rotas
    from app.routes import init_routes
    init_routes(app)
    
    # Configurar handlers de erro customizados
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    # Context processors para templates
    @app.context_processor
    def inject_config():
        return dict(
            app_name="Sistema de Banco de Horas",
            app_version="2.0.0",
            current_year=datetime.now().year
        )
    
    return app

# Criar aplicação
app = create_app()

# Rota inicial - redireciona para login ou setup
@app.route('/')
def index():
    # Verificar se já existe um usuário admin
    from app.models import Usuario
    if not Usuario.query.filter_by(is_admin=True).first():
        return redirect(url_for('auth.setup'))
    
    # Se não estiver logado, vai para login
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    # Se estiver logado, vai para dashboard
    return redirect(url_for('main.dashboard'))

if __name__ == '__main__':
    # Configuração para desenvolvimento local
    with app.app_context():
        from app.models import db
        db.create_all()
        
        # Log de inicialização
        app.logger.info("Sistema de Banco de Horas iniciado com sucesso!")
        print("🚀 Sistema de Banco de Horas iniciado!")
        print("📊 Dashboard disponível em: http://127.0.0.1:5000")
        print("📈 Relatórios disponíveis em: http://127.0.0.1:5000/relatorios")
    
    # Configuração de execução baseada no ambiente
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '127.0.0.1')
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'
    
    # Executar aplicação
    app.run(
        host=host,
        port=port,
        debug=debug,
        use_reloader=debug
    )