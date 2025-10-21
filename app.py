"""
Sistema de Banco de Horas - Aplicação Principal
Sistema completo e otimizado para controle de horas trabalhadas.
"""

from flask import Flask, render_template, redirect, url_for, session
import os
import logging
from datetime import datetime
from config import config

def create_app(config_name=None):
    """Factory function para criar a aplicação Flask"""
    
    # Determinar ambiente
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'development')
    
    # Criar aplicação
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Garantir que SECRET_KEY está definida
    if not app.config.get('SECRET_KEY'):
        app.config['SECRET_KEY'] = 'super-secret-key-for-development'
    
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
    # Criar tabelas se não existirem
    with app.app_context():
        from app.models import db
        db.create_all()
        
        # Log de inicialização
        app.logger.info("Sistema de Banco de Horas iniciado com sucesso!")
        print("🚀 Sistema de Banco de Horas iniciado!")
        print("📊 Dashboard disponível em: http://127.0.0.1:5000")
        print("📈 Relatórios disponíveis em: http://127.0.0.1:5000/relatorios")
    
    # Executar aplicação
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=True,
        use_reloader=True
    )