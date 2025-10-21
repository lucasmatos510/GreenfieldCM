from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from app.models import db, Usuario

auth_bp = Blueprint('auth', __name__)

# Decorador para verificar login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Acesso negado. Faça login para continuar.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = Usuario.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            
            flash(f'Bem-vindo, {user.username}!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Usuário ou senha incorretos.', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Logout realizado com sucesso.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/setup', methods=['GET', 'POST'])
def setup():
    # Verifica se já existe admin
    if Usuario.query.filter_by(is_admin=True).first():
        flash('Sistema já configurado. Faça login.', 'info')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('Senhas não conferem.', 'error')
            return render_template('auth/setup.html')
        
        if len(password) < 6:
            flash('Senha deve ter no mínimo 6 caracteres.', 'error')
            return render_template('auth/setup.html')
        
        # Criar usuário admin
        admin_user = Usuario(
            username=username,
            password_hash=generate_password_hash(password),
            is_admin=True
        )
        
        db.session.add(admin_user)
        db.session.commit()
        
        flash('Administrador criado com sucesso! Faça login.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/setup.html')