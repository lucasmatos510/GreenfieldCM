"""
Sistema de Banco de Horas - Aplicação Principal
Sistema completo e otimizado para controle de horas trabalhadas.
Configurado para deploy no Render com PostgreSQL.
"""

from flask import Flask, render_template, redirect, url_for, session
import os
import logging
from datetime import datetime

# Variáveis de ambiente são carregadas automaticamente pelo sistema
# No Render, as environment variables são injetadas automaticamente

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
    
    # Criar tabelas automaticamente se não existirem
    with app.app_context():
        try:
            db.create_all()
            
            # Criar dados iniciais se necessário (apenas em produção)
            if flask_env == 'production':
                from app.models import Usuario, AreaAtuacao, Cargo
                
                # Verificar se já existe admin
                if not Usuario.query.filter_by(is_admin=True).first():
                    # Criar área padrão
                    if not AreaAtuacao.query.first():
                        area = AreaAtuacao(nome='Tecnologia', descricao='Área de TI')
                        db.session.add(area)
                        db.session.flush()
                        
                        # Criar cargo padrão
                        cargo = Cargo(nome='Administrador', descricao='Administrador do Sistema', area_atuacao_id=area.id)
                        db.session.add(cargo)
                        db.session.flush()
                        
                        # Criar usuário admin
                        admin = Usuario(
                            username='admin',
                            email='admin@sistema.com',
                            nome_completo='Administrador',
                            is_admin=True,
                            cargo_id=cargo.id,
                            data_admissao=datetime.now().date(),
                            ativo=True
                        )
                        admin.set_password('admin123')
                        db.session.add(admin)
                        db.session.commit()
                        
                        app.logger.info("Dados iniciais criados com sucesso!")
                        
        except Exception as e:
            app.logger.error(f"Erro na inicialização do banco: {e}")
            # Não falhar a aplicação por problemas de inicialização
            pass
    
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

# EMERGÊNCIA: Expor app no namespace global para Gunicorn app:app
# Esta linha garante que 'app' esteja disponível mesmo com conflitos
application = app  # Gunicorn também aceita 'application'
flask_app = app    # Backup adicional

# Health check endpoint para Render
@app.route('/health')
def health_check():
    try:
        # Verificar conexão com o banco
        from app.models import db
        db.engine.execute('SELECT 1')
        return {'status': 'healthy', 'database': 'connected'}, 200
    except Exception as e:
        return {'status': 'unhealthy', 'error': str(e)}, 503

# Rota inicial - redireciona para login ou setup
@app.route('/')
def index():
    try:
        # Verificar se já existe um usuário admin
        from app.models import Usuario
        if not Usuario.query.filter_by(is_admin=True).first():
            return redirect(url_for('auth.setup'))
        
        # Se não estiver logado, vai para login
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        
        # Se estiver logado, vai para dashboard
        return redirect(url_for('main.dashboard'))
    except Exception as e:
        app.logger.error(f"Erro na rota inicial: {e}")
        return f"Sistema inicializando... Aguarde alguns minutos. Erro: {e}", 503

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