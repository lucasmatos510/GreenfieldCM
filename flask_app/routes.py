from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file
from datetime import datetime, date, timedelta
from flask_app.models import db, Funcionario, Cargo, AreaAtuacao, RegistroHora, ResumoDiario
from flask_app.utils import gerar_relatorio_excel
from flask_app.auth import login_required
import json
import logging
import os
from functools import wraps
from sqlalchemy import text

# Criar blueprint principal
main_bp = Blueprint('main', __name__)

# Configurar logging
logger = logging.getLogger(__name__)

# Decorador para tratamento de erros
def handle_errors(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Erro na rota {f.__name__}: {str(e)}")
            print(f"Erro na rota {f.__name__}: {str(e)}")  # Debug
            # Não redirecionar para dashboard se o erro for no próprio dashboard
            if f.__name__ == 'dashboard':
                return f"<h1>Erro no Dashboard</h1><p>{str(e)}</p><a href='/'>Voltar</a>"
            flash(f'Erro interno: {str(e)}', 'error')
            return redirect(url_for('auth.login'))  # Redirecionar para login ao invés de dashboard
    return decorated_function

def init_routes(app):
    """Registrar blueprints na aplicação"""
    
    # Registrar blueprint principal
    app.register_blueprint(main_bp)
    
    # Configurar otimizações do SQLAlchemy
    @app.before_request
    def optimize_db():
        """Otimizações de performance do banco"""
        if request.endpoint and 'main.' in request.endpoint:
            # Habilitar cache de queries para rotas pesadas
            with db.engine.connect() as conn:
                conn.execute(text("PRAGMA cache_size = 10000"))
                conn.execute(text("PRAGMA temp_store = MEMORY"))

@main_bp.route('/dashboard')
@handle_errors
@login_required
def dashboard():
    """Dashboard principal otimizado"""
    hoje = date.today()
    primeiro_dia_mes = hoje.replace(day=1)
    
    # Queries otimizadas
    total_funcionarios = Funcionario.query.filter_by(ativo=True).count()
    total_areas = AreaAtuacao.query.filter_by(ativo=True).count()
    total_cargos = Cargo.query.filter_by(ativo=True).count()
    
    # Horas do mês
    horas_mes = db.session.query(
        db.func.coalesce(db.func.sum(RegistroHora.horas), 0)
    ).filter(
        RegistroHora.data >= primeiro_dia_mes,
        RegistroHora.data <= hoje
    ).scalar() or 0
    
    # Últimos 5 registros para atividade recente
    ultimos_registros = RegistroHora.query.options(
        db.joinedload(RegistroHora.funcionario).joinedload(Funcionario.cargo)
    ).order_by(
        RegistroHora.data.desc(),
        RegistroHora.created_at.desc()
    ).limit(5).all()
    
    return render_template('dashboard.html',
                         total_funcionarios=total_funcionarios,
                         total_areas=total_areas,
                         total_cargos=total_cargos,
                         total_horas_mes=int(horas_mes),
                         ultimos_registros=ultimos_registros)

@main_bp.route('/funcionarios')
@handle_errors
@login_required
def listar_funcionarios():
    """Listar funcionários com dados completos"""
    from datetime import datetime
    
    # Buscar funcionários com joins otimizados
    funcionarios = Funcionario.query.options(
        db.joinedload(Funcionario.cargo),
        db.joinedload(Funcionario.area),
        db.joinedload(Funcionario.registros_horas)
    ).filter_by(ativo=True).order_by(Funcionario.nome).all()
    
    # Buscar cargos e áreas para os modals
    cargos = Cargo.query.filter_by(ativo=True).order_by(Cargo.nome).all()
    areas = AreaAtuacao.query.filter_by(ativo=True).order_by(AreaAtuacao.nome).all()
    
    # Primeiro dia do mês atual para cálculo de horas
    primeiro_dia_mes = datetime.now().replace(day=1).date()
    
    return render_template('funcionarios/listar_clean.html', 
                         funcionarios=funcionarios,
                         cargos=cargos,
                         areas=areas,
                         primeiro_dia_mes=primeiro_dia_mes)

@main_bp.route('/funcionarios/novo', methods=['GET', 'POST'])
@handle_errors
@login_required
def novo_funcionario():
    """Criar novo funcionário"""
    if request.method == 'POST':
        try:
            nome = request.form.get('nome', '').strip()
            cargo_id = request.form.get('cargo_id')
            area_id = request.form.get('area_id')
            
            if not nome:
                flash('Nome é obrigatório.', 'error')
                return redirect(url_for('main.novo_funcionario'))
            
            # Verificar se já existe funcionário com mesmo nome
            funcionario_existente = Funcionario.query.filter_by(nome=nome, ativo=True).first()
            if funcionario_existente:
                flash('Já existe um funcionário ativo com este nome.', 'error')
                return redirect(url_for('main.novo_funcionario'))
            
            funcionario = Funcionario(
                nome=nome,
                cargo_id=int(cargo_id) if cargo_id else None,
                area_id=int(area_id) if area_id else None
            )
            
            db.session.add(funcionario)
            db.session.commit()
            
            flash('Funcionário criado com sucesso!', 'success')
            return redirect(url_for('main.listar_funcionarios'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao criar funcionário: {e}")
            flash('Erro ao criar funcionário.', 'error')
    
    # GET - Carregar dados para o formulário
    cargos = Cargo.query.filter_by(ativo=True).all()
    areas = AreaAtuacao.query.filter_by(ativo=True).all()
    return render_template('funcionarios/novo.html', cargos=cargos, areas=areas)

@main_bp.route('/cargos')
@handle_errors
@login_required
def gerenciar_cargos():
    """Gerenciar cargos"""
    cargos = Cargo.query.filter_by(ativo=True).all()
    areas = AreaAtuacao.query.filter_by(ativo=True).all()
    return render_template('cargos/gerenciar.html', cargos=cargos, areas=areas)

@main_bp.route('/criar_cargo', methods=['POST'])
@handle_errors
@login_required
def criar_cargo():
    """Criar novo cargo"""
    nome = request.form.get('nome', '').strip()
    descricao = request.form.get('descricao', '').strip()
    area_id = request.form.get('area_id')
    
    if not nome:
        flash('Nome do cargo é obrigatório', 'error')
        return redirect(url_for('main.gerenciar_cargos'))
    
    # Verificar se já existe
    existing = Cargo.query.filter_by(nome=nome, ativo=True).first()
    if existing:
        flash('Já existe um cargo com este nome', 'error')
        return redirect(url_for('main.gerenciar_cargos'))
    
    cargo = Cargo(nome=nome, descricao=descricao, area_id=area_id)
    db.session.add(cargo)
    db.session.commit()
    
    flash(f'Cargo "{nome}" criado com sucesso!', 'success')
    return redirect(url_for('main.gerenciar_cargos'))

@main_bp.route('/areas')
@handle_errors
@login_required
def gerenciar_areas():
    """Gerenciar áreas de atuação"""
    areas = AreaAtuacao.query.filter_by(ativo=True).all()
    return render_template('areas/gerenciar.html', areas=areas)

@main_bp.route('/criar_area', methods=['POST'])
@handle_errors
@login_required
def criar_area():
    """Criar nova área de atuação"""
    nome = request.form.get('nome', '').strip()
    descricao = request.form.get('descricao', '').strip()
    
    if not nome:
        flash('Nome da área é obrigatório', 'error')
        return redirect(url_for('main.gerenciar_areas'))
    
    # Verificar se já existe
    existing = AreaAtuacao.query.filter_by(nome=nome, ativo=True).first()
    if existing:
        flash('Já existe uma área com este nome', 'error')
        return redirect(url_for('main.gerenciar_areas'))
    
    area = AreaAtuacao(nome=nome, descricao=descricao)
    db.session.add(area)
    db.session.commit()
    
    flash(f'Área "{nome}" criada com sucesso!', 'success')
    return redirect(url_for('main.gerenciar_areas'))

@main_bp.route('/editar_area', methods=['POST'])
@handle_errors
@login_required
def editar_area():
    """Editar área de atuação"""
    area_id = request.form.get('area_id')
    nome = request.form.get('nome', '').strip()
    descricao = request.form.get('descricao', '').strip()
    
    if not area_id or not nome:
        flash('Dados inválidos', 'error')
        return redirect(url_for('main.gerenciar_areas'))
    
    area = AreaAtuacao.query.get_or_404(area_id)
    
    # Verificar se já existe outra área com mesmo nome
    existing = AreaAtuacao.query.filter(
        AreaAtuacao.nome == nome,
        AreaAtuacao.id != area_id,
        AreaAtuacao.ativo == True
    ).first()
    
    if existing:
        flash('Já existe uma área com este nome', 'error')
        return redirect(url_for('main.gerenciar_areas'))
    
    area.nome = nome
    area.descricao = descricao
    db.session.commit()
    
    flash(f'Área "{nome}" atualizada com sucesso!', 'success')
    return redirect(url_for('main.gerenciar_areas'))

@main_bp.route('/excluir_area', methods=['POST'])
@handle_errors
@login_required
def excluir_area():
    """Excluir área de atuação"""
    area_id = request.form.get('area_id')
    
    if not area_id:
        flash('ID da área não fornecido', 'error')
        return redirect(url_for('main.gerenciar_areas'))
    
    area = AreaAtuacao.query.get_or_404(area_id)
    
    # Verificar se há funcionários vinculados
    funcionarios_vinculados = Funcionario.query.filter_by(area_id=area_id, ativo=True).count()
    if funcionarios_vinculados > 0:
        flash(f'Não é possível excluir a área "{area.nome}" pois há {funcionarios_vinculados} funcionário(s) vinculado(s)', 'error')
        return redirect(url_for('main.gerenciar_areas'))
    
    # Soft delete
    area.ativo = False
    db.session.commit()
    
    flash(f'Área "{area.nome}" excluída com sucesso!', 'success')
    return redirect(url_for('main.gerenciar_areas'))

@main_bp.route('/editar_cargo', methods=['POST'])
@handle_errors
@login_required
def editar_cargo():
    """Editar cargo"""
    cargo_id = request.form.get('cargo_id')
    nome = request.form.get('nome', '').strip()
    descricao = request.form.get('descricao', '').strip()
    area_id = request.form.get('area_id')
    
    if not cargo_id or not nome:
        flash('Dados inválidos', 'error')
        return redirect(url_for('main.gerenciar_cargos'))
    
    cargo = Cargo.query.get_or_404(cargo_id)
    
    # Verificar se já existe outro cargo com mesmo nome
    existing = Cargo.query.filter(
        Cargo.nome == nome,
        Cargo.id != cargo_id,
        Cargo.ativo == True
    ).first()
    
    if existing:
        flash('Já existe um cargo com este nome', 'error')
        return redirect(url_for('main.gerenciar_cargos'))
    
    cargo.nome = nome
    cargo.descricao = descricao
    cargo.area_id = int(area_id) if area_id else None
    db.session.commit()
    
    flash(f'Cargo "{nome}" atualizado com sucesso!', 'success')
    return redirect(url_for('main.gerenciar_cargos'))

@main_bp.route('/excluir_cargo', methods=['POST'])
@handle_errors
@login_required
def excluir_cargo():
    """Excluir cargo"""
    cargo_id = request.form.get('cargo_id')
    
    if not cargo_id:
        flash('ID do cargo não fornecido', 'error')
        return redirect(url_for('main.gerenciar_cargos'))
    
    cargo = Cargo.query.get_or_404(cargo_id)
    
    # Verificar se há funcionários vinculados
    funcionarios_vinculados = Funcionario.query.filter_by(cargo_id=cargo_id, ativo=True).count()
    if funcionarios_vinculados > 0:
        flash(f'Não é possível excluir o cargo "{cargo.nome}" pois há {funcionarios_vinculados} funcionário(s) vinculado(s)', 'error')
        return redirect(url_for('main.gerenciar_cargos'))
    
    # Soft delete
    cargo.ativo = False
    db.session.commit()
    
    flash(f'Cargo "{cargo.nome}" excluído com sucesso!', 'success')
    return redirect(url_for('main.gerenciar_cargos'))

@main_bp.route('/salvar_funcionario', methods=['POST'])
@handle_errors
@login_required
def salvar_funcionario():
    """Salvar funcionário"""
    nome = request.form.get('nome', '').strip()
    cargo_id = request.form.get('cargo_id')
    area_id = request.form.get('area_id')
    
    if not nome:
        flash('Nome é obrigatório', 'error')
        return redirect(url_for('main.novo_funcionario'))
    
    if not cargo_id:
        flash('Cargo é obrigatório', 'error')
        return redirect(url_for('main.novo_funcionario'))
    
    # Verificar se já existe funcionário com mesmo nome
    existing = Funcionario.query.filter_by(nome=nome, ativo=True).first()
    if existing:
        flash('Já existe um funcionário com este nome', 'error')
        return redirect(url_for('main.novo_funcionario'))
    
    funcionario = Funcionario(
        nome=nome,
        cargo_id=cargo_id,
        area_id=area_id if area_id else None
    )
    
    db.session.add(funcionario)
    db.session.commit()
    
    flash(f'Funcionário "{nome}" criado com sucesso!', 'success')
    return redirect(url_for('main.listar_funcionarios'))

@main_bp.route('/funcionarios/editar', methods=['POST'])
@handle_errors
@login_required
def editar_funcionario():
    """Editar funcionário"""
    try:
        funcionario_id = request.form.get('funcionario_id')
        nome = request.form.get('nome', '').strip()
        cargo_id = request.form.get('cargo_id')
        area_id = request.form.get('area_id')
        
        if not funcionario_id or not nome:
            flash('ID do funcionário e nome são obrigatórios.', 'error')
            return redirect(url_for('main.listar_funcionarios'))
        
        funcionario = Funcionario.query.get_or_404(funcionario_id)
        
        # Verificar se já existe outro funcionário com o mesmo nome
        funcionario_existente = Funcionario.query.filter(
            Funcionario.nome == nome,
            Funcionario.id != funcionario_id,
            Funcionario.ativo == True
        ).first()
        
        if funcionario_existente:
            flash(f'Já existe um funcionário ativo com o nome "{nome}".', 'error')
            return redirect(url_for('main.listar_funcionarios'))
        
        # Atualizar dados
        funcionario.nome = nome
        funcionario.cargo_id = cargo_id if cargo_id else None
        funcionario.area_id = area_id if area_id else None
        
        db.session.commit()
        flash(f'Funcionário "{nome}" atualizado com sucesso!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao atualizar funcionário: {str(e)}', 'error')
    
    return redirect(url_for('main.listar_funcionarios'))

@main_bp.route('/funcionarios/excluir', methods=['POST'])
@handle_errors
@login_required
def excluir_funcionario():
    """Excluir funcionário (inativar)"""
    try:
        funcionario_id = request.form.get('funcionario_id')
        
        if not funcionario_id:
            flash('ID do funcionário é obrigatório.', 'error')
            return redirect(url_for('main.listar_funcionarios'))
        
        funcionario = Funcionario.query.get_or_404(funcionario_id)
        
        # Inativar em vez de excluir para manter histórico
        funcionario.ativo = False
        
        db.session.commit()
        flash(f'Funcionário "{funcionario.nome}" inativado com sucesso!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao inativar funcionário: {str(e)}', 'error')
    
    return redirect(url_for('main.listar_funcionarios'))

@main_bp.route('/horas')
@handle_errors
@login_required
def registrar_horas():
    """Página para registrar horas"""
    # Buscar funcionários ativos com seus cargos e áreas
    funcionarios = Funcionario.query.options(
        db.joinedload(Funcionario.cargo),
        db.joinedload(Funcionario.area)
    ).filter_by(ativo=True).order_by(Funcionario.nome).all()
    
    # Buscar registros do dia atual para exibição
    hoje = date.today()
    registros_hoje = RegistroHora.query.options(
        db.joinedload(RegistroHora.funcionario).joinedload(Funcionario.cargo),
        db.joinedload(RegistroHora.funcionario).joinedload(Funcionario.area)
    ).filter_by(data=hoje).order_by(RegistroHora.created_at.desc()).all()
    
    return render_template('horas/registrar.html', 
                         funcionarios=funcionarios,
                         registros_hoje=registros_hoje,
                         data_atual=hoje.strftime('%Y-%m-%d'))

@main_bp.route('/horas/registrar', methods=['POST'])
@handle_errors
@login_required
def processar_registro_horas():
    """Processar registro de horas"""
    try:
        funcionario_id = request.form.get('funcionario_id')
        data_str = request.form.get('data')
        horas = request.form.get('horas')
        minutos = request.form.get('minutos', '0')
        observacoes = request.form.get('observacoes', '').strip()
        
        # Validações
        if not funcionario_id or not data_str or not horas:
            flash('Funcionário, data e horas são obrigatórios.', 'error')
            return redirect(url_for('main.registrar_horas'))
        
        # Converter e validar dados
        funcionario_id = int(funcionario_id)
        data_registro = datetime.strptime(data_str, '%Y-%m-%d').date()
        horas_decimal = float(horas) + (float(minutos) / 60.0)
        
        if horas_decimal <= 0 or horas_decimal > 24:
            flash('Quantidade de horas deve ser entre 0 e 24.', 'error')
            return redirect(url_for('main.registrar_horas'))
        
        # Verificar se funcionário existe e está ativo
        funcionario = Funcionario.query.filter_by(id=funcionario_id, ativo=True).first()
        if not funcionario:
            flash('Funcionário não encontrado ou inativo.', 'error')
            return redirect(url_for('main.registrar_horas'))
        
        # Verificar se já existe registro para este funcionário na data
        registro_existente = RegistroHora.query.filter_by(
            funcionario_id=funcionario_id,
            data=data_registro
        ).first()
        
        if registro_existente:
            # Atualizar registro existente
            registro_existente.horas = horas_decimal
            registro_existente.observacoes = observacoes
            registro_existente.updated_at = datetime.utcnow()
            flash('Registro de horas atualizado com sucesso!', 'success')
        else:
            # Criar novo registro
            registro = RegistroHora(
                funcionario_id=funcionario_id,
                data=data_registro,
                horas=horas_decimal,
                observacoes=observacoes
            )
            db.session.add(registro)
            flash('Horas registradas com sucesso!', 'success')
        
        db.session.commit()
        
    except ValueError as e:
        db.session.rollback()
        logger.error(f"Erro de validação: {e}")
        flash('Dados inválidos. Verifique os valores inseridos.', 'error')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao registrar horas: {e}")
        flash('Erro ao registrar horas.', 'error')
    
    return redirect(url_for('main.registrar_horas'))

@main_bp.route('/relatorios')
@handle_errors
@login_required
def relatorios():
    """Página de relatórios com filtros otimizada"""
    try:
        # Obter parâmetros de filtro
        funcionario_id = request.args.get('funcionario_id', type=int)
        cargo_id = request.args.get('cargo_id', type=int)
        area_id = request.args.get('area_id', type=int)
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        
        # Construir query base otimizada
        query = RegistroHora.query.options(
            db.joinedload(RegistroHora.funcionario).joinedload(Funcionario.cargo),
            db.joinedload(RegistroHora.funcionario).joinedload(Funcionario.area)
        )
        
        # Aplicar filtros
        if funcionario_id:
            query = query.filter(RegistroHora.funcionario_id == funcionario_id)
        if cargo_id:
            query = query.join(Funcionario).filter(Funcionario.cargo_id == cargo_id)
        if area_id:
            query = query.join(Funcionario).filter(Funcionario.area_id == area_id)
        if data_inicio:
            data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d').date()
            query = query.filter(RegistroHora.data >= data_inicio_obj)
        if data_fim:
            data_fim_obj = datetime.strptime(data_fim, '%Y-%m-%d').date()
            query = query.filter(RegistroHora.data <= data_fim_obj)
        
        # Executar query com ordenação e limitação
        registros = query.order_by(RegistroHora.data.desc()).limit(1000).all()
        
        # Calcular totais
        total_horas = sum(r.horas for r in registros)
        total_registros = len(registros)
        
        # Carregar dados para filtros
        funcionarios = Funcionario.query.filter_by(ativo=True).order_by(Funcionario.nome).all()
        cargos = Cargo.query.filter_by(ativo=True).order_by(Cargo.nome).all()
        areas = AreaAtuacao.query.filter_by(ativo=True).order_by(AreaAtuacao.nome).all()
        
        return render_template('relatorios.html',
                             registros=registros,
                             funcionarios=funcionarios,
                             cargos=cargos,
                             areas=areas,
                             total_horas=total_horas,
                             total_registros=total_registros,
                             funcionario_selecionado=funcionario_id,
                             cargo_selecionado=cargo_id,
                             area_selecionada=area_id,
                             data_inicio=data_inicio,
                             data_fim=data_fim)
    
    except Exception as e:
        logger.error(f"Erro ao gerar relatórios: {e}")
        flash('Erro ao carregar relatórios.', 'error')
        return redirect(url_for('main.dashboard'))

@main_bp.route('/relatorios/exportar-excel')
@handle_errors
@login_required
def exportar_excel():
    """Exportar relatório para Excel"""
    try:
        # Obter mesmo filtros da página de relatórios
        funcionario_id = request.args.get('funcionario_id', type=int)
        cargo_id = request.args.get('cargo_id', type=int)
        area_id = request.args.get('area_id', type=int)
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        tipo = request.args.get('tipo', 'mensal')
        
        # Determinar período para Excel baseado nos filtros
        mes = None
        ano = None
        
        if data_inicio:
            data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d').date()
            mes = data_inicio_obj.month
            ano = data_inicio_obj.year
        else:
            mes = datetime.now().month
            ano = datetime.now().year
        
        # Gerar arquivo Excel
        arquivo_path = gerar_relatorio_excel(
            tipo=tipo,
            funcionario_id=funcionario_id,
            mes=mes,
            ano=ano
        )
        
        if arquivo_path and os.path.exists(arquivo_path):
            return send_file(
                arquivo_path,
                as_attachment=True,
                download_name=f'relatorio_horas_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx',
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        else:
            flash('Erro ao gerar arquivo Excel.', 'error')
            
    except Exception as e:
        logger.error(f"Erro ao exportar Excel: {e}")
        flash('Erro ao exportar relatório.', 'error')
    
    return redirect(url_for('main.relatorios'))

# APIs para funcionalidade dinâmica
@main_bp.route('/api/cargos', methods=['POST'])
@handle_errors
@login_required
def api_criar_cargo():
    """Criar novo cargo via API"""
    try:
        nome = request.form.get('nome', '').strip()
        if not nome:
            return jsonify({'success': False, 'message': 'Nome é obrigatório'})
        
        # Verificar se já existe
        if Cargo.query.filter_by(nome=nome, ativo=True).first():
            return jsonify({'success': False, 'message': 'Cargo já existe'})
        
        cargo = Cargo(nome=nome)
        db.session.add(cargo)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'cargo': {'id': cargo.id, 'nome': cargo.nome}
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@main_bp.route('/api/areas', methods=['POST'])
@handle_errors
@login_required
def api_criar_area():
    """Criar nova área via API"""
    try:
        nome = request.form.get('nome', '').strip()
        if not nome:
            return jsonify({'success': False, 'message': 'Nome é obrigatório'})
        
        # Verificar se já existe
        if AreaAtuacao.query.filter_by(nome=nome, ativo=True).first():
            return jsonify({'success': False, 'message': 'Área já existe'})
        
        area = AreaAtuacao(nome=nome)
        db.session.add(area)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'area': {'id': area.id, 'nome': area.nome}
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

# Rotas para resumos diários
@main_bp.route('/resumos-diarios')
@handle_errors
@login_required
def visualizar_resumos():
    """Visualizar resumos diários"""
    # Buscar resumos com filtros
    funcionario_id = request.args.get('funcionario_id', type=int)
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    
    query = ResumoDiario.query.options(
        db.joinedload(ResumoDiario.funcionario).joinedload(Funcionario.cargo),
        db.joinedload(ResumoDiario.funcionario).joinedload(Funcionario.area)
    )
    
    # Aplicar filtros
    if funcionario_id:
        query = query.filter(ResumoDiario.funcionario_id == funcionario_id)
    if data_inicio:
        data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d').date()
        query = query.filter(ResumoDiario.data >= data_inicio_obj)
    if data_fim:
        data_fim_obj = datetime.strptime(data_fim, '%Y-%m-%d').date()
        query = query.filter(ResumoDiario.data <= data_fim_obj)
    
    resumos = query.order_by(ResumoDiario.data.desc()).limit(200).all()
    
    # Buscar funcionários para o filtro
    funcionarios = Funcionario.query.filter_by(ativo=True).order_by(Funcionario.nome).all()
    
    return render_template('resumos_diarios.html', 
                         resumos=resumos,
                         funcionarios=funcionarios)

@main_bp.route('/resumos-diarios/gerar', methods=['POST'])
@handle_errors
@login_required
def gerar_resumo_dia():
    """Gerar resumo para um dia específico"""
    try:
        data_str = request.form.get('data')
        if not data_str:
            flash('Data é obrigatória.', 'error')
            return redirect(url_for('main.visualizar_resumos'))
        
        data_resumo = datetime.strptime(data_str, '%Y-%m-%d').date()
        
        # Gerar resumo
        resumos_criados = ResumoDiario.gerar_resumo_dia(data_resumo)
        
        flash(f'Resumo gerado com sucesso! {resumos_criados} registros criados para {data_resumo.strftime("%d/%m/%Y")}.', 'success')
        
    except Exception as e:
        logger.error(f"Erro ao gerar resumo: {e}")
        flash('Erro ao gerar resumo diário.', 'error')
    
    return redirect(url_for('main.visualizar_resumos'))