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
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def handle_errors(f):
    """Decorator para tratamento de erros padronizado"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Erro na rota {f.__name__}: {str(e)}")
            flash('Erro interno do sistema. Tente novamente.', 'error')
            return redirect(url_for('dashboard'))
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
        """Dashboard principal com estatísticas - OTIMIZADO"""
        try:
            # Cache data atual para evitar múltiplas chamadas
            hoje = date.today()
            primeiro_dia_mes = hoje.replace(day=1)
            
            # Query otimizada com join único para estatísticas
            stats_query = db.session.query(
                db.func.count(Funcionario.id.distinct()).label('total_funcionarios'),
                db.func.count(AreaAtuacao.id.distinct()).label('total_areas'),
                db.func.count(Cargo.id.distinct()).label('total_cargos')
            ).select_from(Funcionario).join(Cargo).join(AreaAtuacao).filter(
                Funcionario.ativo == True,
                AreaAtuacao.ativo == True,
                Cargo.ativo == True
            ).first()
            
            total_funcionarios = stats_query.total_funcionarios or 0
            total_areas = stats_query.total_areas or 0
            total_cargos = stats_query.total_cargos or 0
            
            # Query otimizada para horas do mês com agregação no banco
            horas_mes_query = db.session.query(
                db.func.sum(RegistroHora.minutos_trabalhados)
            ).filter(
                RegistroHora.data >= primeiro_dia_mes,
                RegistroHora.data <= hoje
            ).scalar()
            
            total_horas_mes = round((horas_mes_query or 0) / 60, 2)
            
            # Query otimizada para dados do gráfico com agregação
            dados_grafico_query = db.session.query(
                Funcionario.nome,
                db.func.sum(RegistroHora.minutos_trabalhados).label('total_minutos')
            ).join(RegistroHora).filter(
                Funcionario.ativo == True,
                RegistroHora.data >= primeiro_dia_mes,
                RegistroHora.data <= hoje
            ).group_by(Funcionario.id, Funcionario.nome).order_by(
                db.func.sum(RegistroHora.minutos_trabalhados).desc()
            ).limit(10).all()
            
            dados_grafico = [
                {
                    'nome': nome,
                    'horas': round((total_minutos or 0) / 60, 2)
                }
                for nome, total_minutos in dados_grafico_query
            ]
            
            # Últimos registros otimizado com joins específicos
            ultimos_registros = db.session.query(RegistroHora).join(
                Funcionario, RegistroHora.funcionario_id == Funcionario.id
            ).join(
                Cargo, Funcionario.cargo_id == Cargo.id
            ).order_by(
                RegistroHora.data_criacao.desc()
            ).limit(5).all()
            
            return render_template('dashboard.html',
                                 total_funcionarios=total_funcionarios,
                                 total_areas=total_areas,
                                 total_cargos=total_cargos,
                                 total_horas_mes=total_horas_mes,
                                 dados_grafico=dados_grafico,
                                 ultimos_registros=ultimos_registros)
        
        except Exception as e:
            # Log do erro e dados padrão em caso de falha
            print(f"Erro no dashboard: {e}")
            return render_template('dashboard.html',
                                 total_funcionarios=0,
                                 total_areas=0,
                                 total_cargos=0,
                                 total_horas_mes=0,
                                 dados_grafico=[],
                                 ultimos_registros=[])

    # === ROTAS DE FUNCIONÁRIOS ===
    @app.route('/funcionarios')
    def listar_funcionarios():
        funcionarios = Funcionario.query.filter_by(ativo=True).all()
        return render_template('funcionarios/listar.html', funcionarios=funcionarios)

    @app.route('/funcionarios/novo', methods=['GET', 'POST'])
    def novo_funcionario():
        if request.method == 'POST':
            # Validações de entrada robustas
            nome = request.form.get('nome', '').strip()
            cargo_id = request.form.get('cargo_id')
            area_atuacao_id = request.form.get('area_atuacao_id')
            
            # Lista de erros
            erros = []
            
            # Validar nome
            if not nome or len(nome) < 2:
                erros.append('Nome deve ter pelo menos 2 caracteres.')
            elif len(nome) > 100:
                erros.append('Nome muito longo (máximo 100 caracteres).')
            
            # Validar cargo
            if not cargo_id or not str(cargo_id).isdigit():
                erros.append('Selecione um cargo válido.')
            else:
                cargo = Cargo.query.filter_by(id=cargo_id, ativo=True).first()
                if not cargo:
                    erros.append('Cargo selecionado não existe.')
            
            # Validar área
            if not area_atuacao_id or not str(area_atuacao_id).isdigit():
                erros.append('Selecione uma área de atuação válida.')
            else:
                area = AreaAtuacao.query.filter_by(id=area_atuacao_id, ativo=True).first()
                if not area:
                    erros.append('Área de atuação selecionada não existe.')
            
            # Verificar duplicidade
            if nome:
                nome_existe = Funcionario.query.filter(
                    db.func.lower(Funcionario.nome) == nome.lower(),
                    Funcionario.ativo == True
                ).first()
                if nome_existe:
                    erros.append('Já existe um funcionário com este nome.')
            
            # Processar resultado
            if erros:
                for erro in erros:
                    flash(erro, 'error')
            else:
                try:
                    funcionario = Funcionario(
                        nome=nome,
                        cargo_id=int(cargo_id),
                        area_atuacao_id=int(area_atuacao_id)
                    )
                    
                    db.session.add(funcionario)
                    db.session.commit()
                    flash(f'Funcionário "{nome}" cadastrado com sucesso!', 'success')
                    return redirect(url_for('listar_funcionarios'))
                    
                except Exception as e:
                    db.session.rollback()
                    flash(f'Erro interno: {str(e)[:100]}', 'error')
        
        try:
            cargos = Cargo.query.filter_by(ativo=True).order_by(Cargo.nome).all()
            areas = AreaAtuacao.query.filter_by(ativo=True).order_by(AreaAtuacao.nome).all()
            return render_template('funcionarios/novo.html', cargos=cargos, areas=areas)
        except Exception as e:
            flash('Erro ao carregar dados.', 'error')
            return redirect(url_for('dashboard'))

    @app.route('/funcionarios/<int:funcionario_id>/editar', methods=['GET', 'POST'])
    def editar_funcionario(funcionario_id):
        funcionario = Funcionario.query.get_or_404(funcionario_id)
        
        if request.method == 'POST':
            funcionario.nome = request.form['nome']
            funcionario.cargo_id = request.form['cargo_id']
            funcionario.area_atuacao_id = request.form['area_atuacao_id']
            
            try:
                db.session.commit()
                flash('Funcionário atualizado com sucesso!', 'success')
                return redirect(url_for('listar_funcionarios'))
            except Exception as e:
                db.session.rollback()
                flash('Erro ao atualizar funcionário.', 'error')
        
        cargos = Cargo.query.filter_by(ativo=True).all()
        areas = AreaAtuacao.query.filter_by(ativo=True).all()
        return render_template('funcionarios/novo.html', funcionario=funcionario, cargos=cargos, areas=areas)

    # === ROTAS DE CARGOS ===
    @app.route('/cargos')
    def listar_cargos():
        cargos = Cargo.query.filter_by(ativo=True).all()
        areas = AreaAtuacao.query.filter_by(ativo=True).all()
        return render_template('cargos/gerenciar.html', cargos=cargos, areas=areas)

    @app.route('/cargos/novo', methods=['GET', 'POST'])
    def novo_cargo():
        if request.method == 'POST':
            cargo = Cargo(
                nome=request.form['nome'],
                area_atuacao_id=request.form['area_atuacao_id'],
                salario_base=float(request.form['salario_base']) if request.form.get('salario_base') else None
            )
            
            try:
                db.session.add(cargo)
                db.session.commit()
                flash('Cargo cadastrado com sucesso!', 'success')
                return redirect(url_for('listar_cargos'))
            except Exception as e:
                db.session.rollback()
                flash('Erro ao cadastrar cargo.', 'error')
        
        areas = AreaAtuacao.query.filter_by(ativo=True).all()
        return render_template('cargos/gerenciar.html', areas=areas)

    # === ROTAS DE HORAS ===
    @app.route('/areas')
    def listar_areas():
        areas = AreaAtuacao.query.filter_by(ativo=True).all()
        return render_template('cargos/gerenciar.html', areas=areas)

    @app.route('/areas/novo', methods=['GET', 'POST'])
    def nova_area():
        if request.method == 'POST':
            area = AreaAtuacao(
                nome=request.form['nome'],
                descricao=request.form.get('descricao')
            )
            
            try:
                db.session.add(area)
                db.session.commit()
                flash('Área de atuação cadastrada com sucesso!', 'success')
                return redirect(url_for('listar_areas'))
            except Exception as e:
                db.session.rollback()
                flash('Erro ao cadastrar área de atuação.', 'error')
        
        return render_template('cargos/gerenciar.html')

    # === ROTAS DE REGISTRO DE HORAS ===
    @app.route('/horas')
    def listar_registros():
        page = request.args.get('page', 1, type=int)
        funcionario_id = request.args.get('funcionario_id')
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        
        query = RegistroHora.query
        
        if funcionario_id:
            query = query.filter(RegistroHora.funcionario_id == funcionario_id)
        
        if data_inicio:
            query = query.filter(RegistroHora.data >= datetime.strptime(data_inicio, '%Y-%m-%d').date())
        
        if data_fim:
            query = query.filter(RegistroHora.data <= datetime.strptime(data_fim, '%Y-%m-%d').date())
        
        registros = query.order_by(RegistroHora.data.desc()).paginate(
            page=page, per_page=20, error_out=False
        )
        
        funcionarios = Funcionario.query.filter_by(ativo=True).all()
        return render_template('horas/registrar.html', registros=registros, funcionarios=funcionarios)

    @app.route('/horas/novo', methods=['GET', 'POST'])
    def novo_registro():
        if request.method == 'POST':
            try:
                # Validação de campos obrigatórios
                funcionario_id = request.form.get('funcionario_id', '').strip()
                data_str = request.form.get('data', '').strip()
                hora_inicio_str = request.form.get('hora_inicio', '').strip()
                hora_fim_str = request.form.get('hora_fim', '').strip()
                
                if not all([funcionario_id, data_str, hora_inicio_str]):
                    flash('Preencha todos os campos obrigatórios.', 'error')
                    funcionarios = Funcionario.query.filter_by(ativo=True).all()
                    return render_template('horas/registrar.html', funcionarios=funcionarios)
                
                # Validar se funcionário existe e está ativo
                funcionario = Funcionario.query.filter_by(id=funcionario_id, ativo=True).first()
                if not funcionario:
                    flash('Funcionário não encontrado ou inativo.', 'error')
                    funcionarios = Funcionario.query.filter_by(ativo=True).all()
                    return render_template('horas/registrar.html', funcionarios=funcionarios)
                
                # Converter e validar data
                try:
                    data = datetime.strptime(data_str, '%Y-%m-%d').date()
                    if data > date.today():
                        flash('Data não pode ser futura.', 'error')
                        funcionarios = Funcionario.query.filter_by(ativo=True).all()
                        return render_template('horas/registrar.html', funcionarios=funcionarios)
                except ValueError:
                    flash('Formato de data inválido.', 'error')
                    funcionarios = Funcionario.query.filter_by(ativo=True).all()
                    return render_template('horas/registrar.html', funcionarios=funcionarios)
                
                # Converter e validar horários
                try:
                    hora_inicio = datetime.strptime(hora_inicio_str, '%H:%M').time()
                    hora_fim = None
                    if hora_fim_str:
                        hora_fim = datetime.strptime(hora_fim_str, '%H:%M').time()
                        # Validar se hora fim é maior que hora início
                        if hora_fim <= hora_inicio:
                            flash('Hora de fim deve ser maior que hora de início.', 'error')
                            funcionarios = Funcionario.query.filter_by(ativo=True).all()
                            return render_template('horas/registrar.html', funcionarios=funcionarios)
                except ValueError:
                    flash('Formato de horário inválido. Use HH:MM', 'error')
                    funcionarios = Funcionario.query.filter_by(ativo=True).all()
                    return render_template('horas/registrar.html', funcionarios=funcionarios)
                
                # Verificar duplicatas no mesmo dia
                registro_existente = RegistroHora.query.filter_by(
                    funcionario_id=funcionario_id,
                    data=data,
                    hora_inicio=hora_inicio
                ).first()
                
                if registro_existente:
                    flash('Já existe um registro com os mesmos dados para este funcionário.', 'warning')
                    funcionarios = Funcionario.query.filter_by(ativo=True).all()
                    return render_template('horas/registrar.html', funcionarios=funcionarios)
                
                # Sanitizar observações
                observacoes = request.form.get('observacoes', '').strip()[:500]  # Limitar a 500 chars
                tipo_registro = request.form.get('tipo_registro', 'normal')
                
                # Validar tipo de registro
                tipos_validos = ['normal', 'extra', 'falta', 'feriado']
                if tipo_registro not in tipos_validos:
                    tipo_registro = 'normal'
                
                # Criar registro
                registro = RegistroHora(
                    funcionario_id=funcionario_id,
                    data=data,
                    hora_inicio=hora_inicio,
                    hora_fim=hora_fim,
                    tipo_registro=tipo_registro,
                    observacoes=observacoes
                )
                
                # Calcular minutos trabalhados
                registro.calcular_minutos()
                
                db.session.add(registro)
                db.session.commit()
                flash(f'Registro de horas para {funcionario.nome} cadastrado com sucesso!', 'success')
                return redirect(url_for('listar_registros'))
                
            except Exception as e:
                db.session.rollback()
                print(f"Erro ao cadastrar registro: {e}")  # Log do erro
                flash('Erro interno do sistema. Tente novamente.', 'error')
        
        funcionarios = Funcionario.query.filter_by(ativo=True).order_by(Funcionario.nome).all()
        return render_template('horas/registrar.html', funcionarios=funcionarios)

    # === ROTAS PARA CRIAR/EDITAR/EXCLUIR ===
    
    @app.route('/areas/criar', methods=['POST'])
    def criar_area():
        try:
            nome = request.form.get('nome', '').strip()
            descricao = request.form.get('descricao', '').strip()
            
            # Validação de entrada
            if not nome or len(nome) < 2:
                flash('Nome da área deve ter pelo menos 2 caracteres.', 'error')
                return redirect(url_for('listar_cargos'))
            
            if len(nome) > 100:
                flash('Nome da área deve ter no máximo 100 caracteres.', 'error')
                return redirect(url_for('listar_cargos'))
            
            # Verificar duplicatas (case-insensitive)
            area_existente = AreaAtuacao.query.filter(
                db.func.lower(AreaAtuacao.nome) == nome.lower()
            ).first()
            
            if area_existente:
                flash(f'Área "{nome}" já existe no sistema.', 'warning')
                return redirect(url_for('listar_cargos'))
            
            # Limitar descrição
            if len(descricao) > 500:
                descricao = descricao[:500]
            
            nova_area = AreaAtuacao(nome=nome, descricao=descricao)
            db.session.add(nova_area)
            db.session.commit()
            flash(f'Área "{nome}" criada com sucesso!', 'success')
            
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao criar área: {e}")
            flash('Erro interno do sistema. Tente novamente.', 'error')
        
        return redirect(url_for('listar_cargos'))
    
    @app.route('/areas/<int:id>/editar', methods=['POST'])
    def editar_area(id):
        try:
            area = AreaAtuacao.query.get_or_404(id)
            nome = request.form.get('nome', '').strip()
            descricao = request.form.get('descricao', '').strip()
            
            # Validação
            if not nome or len(nome) < 2:
                flash('Nome da área deve ter pelo menos 2 caracteres.', 'error')
                return redirect(url_for('listar_cargos'))
            
            if len(nome) > 100:
                flash('Nome da área deve ter no máximo 100 caracteres.', 'error')
                return redirect(url_for('listar_cargos'))
            
            # Verificar duplicatas (exceto a própria área)
            area_existente = AreaAtuacao.query.filter(
                db.func.lower(AreaAtuacao.nome) == nome.lower(),
                AreaAtuacao.id != id
            ).first()
            
            if area_existente:
                flash(f'Já existe outra área com o nome "{nome}".', 'warning')
                return redirect(url_for('listar_cargos'))
            
            # Atualizar dados
            area.nome = nome
            area.descricao = descricao[:500] if descricao else ''
            
            db.session.commit()
            flash(f'Área "{area.nome}" editada com sucesso!', 'success')
            
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao editar área: {e}")
            flash('Erro interno do sistema. Tente novamente.', 'error')
        
        return redirect(url_for('listar_cargos'))
    
    @app.route('/areas/<int:id>/excluir', methods=['POST'])
    def excluir_area(id):
        try:
            area = AreaAtuacao.query.get_or_404(id)
            nome_area = area.nome
            
            # Verificar se há cargos vinculados
            cargos_vinculados = Cargo.query.filter_by(area_atuacao_id=id).count()
            if cargos_vinculados > 0:
                flash(f'Não é possível excluir a área "{nome_area}" pois há {cargos_vinculados} cargo(s) vinculado(s).', 'error')
                return redirect(url_for('listar_cargos'))
            
            # Verificar se há funcionários com cargos desta área
            funcionarios_vinculados = db.session.query(Funcionario).join(Cargo).filter(
                Cargo.area_atuacao_id == id
            ).count()
            
            if funcionarios_vinculados > 0:
                flash(f'Não é possível excluir a área "{nome_area}" pois há funcionários vinculados.', 'error')
                return redirect(url_for('listar_cargos'))
            
            db.session.delete(area)
            db.session.commit()
            flash(f'Área "{nome_area}" excluída com sucesso!', 'success')
            
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao excluir área: {e}")
            flash('Erro interno do sistema. Tente novamente.', 'error')
        
        return redirect(url_for('listar_cargos'))
    
    @app.route('/cargos/criar', methods=['POST'])
    def criar_cargo():
        try:
            nome = request.form.get('nome', '').strip()
            area_atuacao_id = request.form.get('area_atuacao_id', '').strip()
            salario_base = request.form.get('salario_base', '').strip()
            
            # Validação de campos obrigatórios
            if not nome or len(nome) < 2:
                flash('Nome do cargo deve ter pelo menos 2 caracteres.', 'error')
                return redirect(url_for('listar_cargos'))
            
            if len(nome) > 100:
                flash('Nome do cargo deve ter no máximo 100 caracteres.', 'error')
                return redirect(url_for('listar_cargos'))
            
            if not area_atuacao_id:
                flash('Selecione uma área de atuação.', 'error')
                return redirect(url_for('listar_cargos'))
            
            # Validar área de atuação
            try:
                area_id = int(area_atuacao_id)
                area = AreaAtuacao.query.get(area_id)
                if not area:
                    flash('Área de atuação inválida.', 'error')
                    return redirect(url_for('listar_cargos'))
            except ValueError:
                flash('ID da área inválido.', 'error')
                return redirect(url_for('listar_cargos'))
            
            # Verificar duplicatas na mesma área
            cargo_existente = Cargo.query.filter(
                db.func.lower(Cargo.nome) == nome.lower(),
                Cargo.area_atuacao_id == area_id
            ).first()
            
            if cargo_existente:
                flash(f'Já existe um cargo "{nome}" nesta área.', 'warning')
                return redirect(url_for('listar_cargos'))
            
            # Validar salário
            salario_valor = None
            if salario_base:
                try:
                    salario_valor = float(salario_base.replace(',', '.'))
                    if salario_valor < 0:
                        flash('Salário não pode ser negativo.', 'error')
                        return redirect(url_for('listar_cargos'))
                    if salario_valor > 999999.99:
                        flash('Salário muito alto. Máximo: R$ 999.999,99', 'error')
                        return redirect(url_for('listar_cargos'))
                except ValueError:
                    flash('Valor de salário inválido.', 'error')
                    return redirect(url_for('listar_cargos'))
            
            novo_cargo = Cargo(
                nome=nome,
                area_atuacao_id=area_id,
                salario_base=salario_valor
            )
            
            db.session.add(novo_cargo)
            db.session.commit()
            flash(f'Cargo "{nome}" criado com sucesso na área "{area.nome}"!', 'success')
            
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao criar cargo: {e}")
            flash('Erro interno do sistema. Tente novamente.', 'error')
        
        return redirect(url_for('listar_cargos'))
    
    @app.route('/cargos/<int:id>/excluir', methods=['POST'])
    def excluir_cargo(id):
        try:
            cargo = Cargo.query.get_or_404(id)
            nome_cargo = cargo.nome
            
            # Verificar se há funcionários vinculados
            funcionarios_vinculados = Funcionario.query.filter_by(cargo_id=id).count()
            if funcionarios_vinculados > 0:
                flash(f'Não é possível excluir o cargo "{nome_cargo}" pois há {funcionarios_vinculados} funcionário(s) vinculado(s).', 'error')
                return redirect(url_for('listar_cargos'))
            
            # Verificar registros de horas vinculados através dos funcionários
            registros_vinculados = db.session.query(RegistroHora).join(Funcionario).filter(
                Funcionario.cargo_id == id
            ).count()
            
            if registros_vinculados > 0:
                flash(f'Não é possível excluir o cargo "{nome_cargo}" pois há registros de horas vinculados.', 'error')
                return redirect(url_for('listar_cargos'))
            
            db.session.delete(cargo)
            db.session.commit()
            flash(f'Cargo "{nome_cargo}" excluído com sucesso!', 'success')
            
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao excluir cargo: {e}")
            flash('Erro interno do sistema. Tente novamente.', 'error')
        
        return redirect(url_for('listar_cargos'))
    
    # === ROTAS DE RELATÓRIOS ===
    @app.route('/relatorios')
    def relatorios():
        try:
            # Obter parâmetros de filtro com validação
            funcionario_id = request.args.get('funcionario_id')
            data_inicio = request.args.get('data_inicio')
            data_fim = request.args.get('data_fim')
            tipo_relatorio = request.args.get('tipo_relatorio', 'detalhado')
            
            # Validar datas
            data_inicio_obj = None
            data_fim_obj = None
            
            if data_inicio:
                try:
                    data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d').date()
                except ValueError:
                    flash('Data de início inválida.', 'error')
                    data_inicio = None
            
            if data_fim:
                try:
                    data_fim_obj = datetime.strptime(data_fim, '%Y-%m-%d').date()
                except ValueError:
                    flash('Data de fim inválida.', 'error')
                    data_fim = None
            
            # Verificar se data início não é maior que data fim
            if data_inicio_obj and data_fim_obj and data_inicio_obj > data_fim_obj:
                flash('Data de início não pode ser maior que data de fim.', 'warning')
                data_inicio_obj = data_fim_obj = None
            
            # Query otimizada com eager loading
            query = RegistroHora.query.options(
                db.joinedload(RegistroHora.funcionario).joinedload(Funcionario.cargo).joinedload(Cargo.area_atuacao)
            )
            
            # Aplicar filtros validados
            if funcionario_id and funcionario_id.isdigit():
                # Verificar se funcionário existe
                if not Funcionario.query.get(int(funcionario_id)):
                    flash('Funcionário não encontrado.', 'error')
                    funcionario_id = None
                else:
                    query = query.filter(RegistroHora.funcionario_id == int(funcionario_id))
            
            if data_inicio_obj:
                query = query.filter(RegistroHora.data >= data_inicio_obj)
            
            if data_fim_obj:
                query = query.filter(RegistroHora.data <= data_fim_obj)
            
            # Limitar resultados para evitar sobrecarga (últimos 1000 registros)
            registros = query.order_by(
                RegistroHora.data.desc(), 
                RegistroHora.hora_inicio.desc()
            ).limit(1000).all()
            
            # Buscar funcionários ativos com eager loading
            funcionarios = Funcionario.query.options(
                db.joinedload(Funcionario.cargo)
            ).filter_by(ativo=True).order_by(Funcionario.nome).all()
            
            # Calcular estatísticas otimizadas
            estatisticas = None
            dados_grafico = None
            
            if registros:
                # Usar queries agregadas para melhor performance
                from sqlalchemy import func
                
                # Query para estatísticas agregadas
                stats_query = db.session.query(
                    func.count(func.distinct(RegistroHora.funcionario_id)).label('total_funcionarios'),
                    func.sum(RegistroHora.minutos_trabalhados).label('total_minutos'),
                    func.count(RegistroHora.id).label('total_registros')
                )
                
                # Aplicar mesmos filtros
                if funcionario_id and funcionario_id.isdigit():
                    stats_query = stats_query.filter(RegistroHora.funcionario_id == int(funcionario_id))
                if data_inicio_obj:
                    stats_query = stats_query.filter(RegistroHora.data >= data_inicio_obj)
                if data_fim_obj:
                    stats_query = stats_query.filter(RegistroHora.data <= data_fim_obj)
                
                stats_result = stats_query.first()
                
                total_funcionarios = stats_result.total_funcionarios or 0
                total_minutos = stats_result.total_minutos or 0
                total_horas = total_minutos / 60
                total_registros = stats_result.total_registros or 0
                media_horas_funcionario = total_horas / total_funcionarios if total_funcionarios > 0 else 0
                
                estatisticas = {
                    'total_funcionarios': total_funcionarios,
                    'total_horas': round(total_horas, 2),
                    'media_horas_funcionario': round(media_horas_funcionario, 2),
                    'total_registros': total_registros
                }
                
                # Query otimizada para dados do gráfico
                grafico_query = db.session.query(
                    Funcionario.nome,
                    func.sum(RegistroHora.minutos_trabalhados).label('total_minutos')
                ).join(RegistroHora).group_by(Funcionario.id, Funcionario.nome)
                
                # Aplicar mesmos filtros
                if funcionario_id and funcionario_id.isdigit():
                    grafico_query = grafico_query.filter(RegistroHora.funcionario_id == int(funcionario_id))
                if data_inicio_obj:
                    grafico_query = grafico_query.filter(RegistroHora.data >= data_inicio_obj)
                if data_fim_obj:
                    grafico_query = grafico_query.filter(RegistroHora.data <= data_fim_obj)
                
                grafico_results = grafico_query.limit(20).all()  # Limitar a 20 funcionários para o gráfico
                
                dados_grafico = {
                    'labels': [r.nome for r in grafico_results],
                    'valores': [round(r.total_minutos / 60, 2) for r in grafico_results]
                }
            
            return render_template('relatorios.html', 
                                 registros=registros,
                                 funcionarios=funcionarios,
                                 estatisticas=estatisticas,
                                 dados_grafico=dados_grafico,
                                 filtros={
                                     'funcionario_id': funcionario_id,
                                     'data_inicio': data_inicio,
                                     'data_fim': data_fim,
                                     'tipo_relatorio': tipo_relatorio
                                 })
        
        except Exception as e:
            print(f"Erro na rota de relatórios: {e}")
            flash('Erro ao carregar relatórios. Tente novamente.', 'error')
            funcionarios = Funcionario.query.filter_by(ativo=True).order_by(Funcionario.nome).all()
            return render_template('relatorios.html', 
                                 registros=[],
                                 funcionarios=funcionarios,
                                 estatisticas=None,
                                 dados_grafico=None)

    @app.route('/relatorios/exportar-excel')
    def exportar_excel():
        try:
            tipo = request.args.get('tipo', 'mensal')
            funcionario_id = request.args.get('funcionario_id')
            mes = request.args.get('mes')
            ano = request.args.get('ano')
            
            # Validar parâmetros
            tipos_validos = ['diario', 'mensal', 'anual']
            if tipo not in tipos_validos:
                flash('Tipo de relatório inválido.', 'error')
                return redirect(url_for('relatorios'))
            
            # Validar funcionário se fornecido
            if funcionario_id:
                if not funcionario_id.isdigit():
                    flash('ID do funcionário inválido.', 'error')
                    return redirect(url_for('relatorios'))
                
                funcionario = Funcionario.query.get(int(funcionario_id))
                if not funcionario:
                    flash('Funcionário não encontrado.', 'error')
                    return redirect(url_for('relatorios'))
            
            # Validar mês e ano
            if mes and not (mes.isdigit() and 1 <= int(mes) <= 12):
                flash('Mês inválido.', 'error')
                return redirect(url_for('relatorios'))
            
            if ano and not (ano.isdigit() and 2020 <= int(ano) <= 2030):
                flash('Ano inválido.', 'error')
                return redirect(url_for('relatorios'))
            
            # Gerar relatório
            from flask_app.utils import gerar_relatorio_excel
            arquivo = gerar_relatorio_excel(tipo, funcionario_id, mes, ano)
            
            if not arquivo:
                flash('Não foi possível gerar o relatório. Verifique os parâmetros.', 'error')
                return redirect(url_for('relatorios'))
            
            # Nome do arquivo para download
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_download = f'relatorio_horas_{tipo}_{timestamp}.xlsx'
            
            # Informar onde foi salvo
            downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
            caminho_salvo = os.path.join(downloads_path, nome_download)
            flash(f'Relatório salvo em: {caminho_salvo}', 'success')
            
            return send_file(
                arquivo,
                as_attachment=True,
                download_name=nome_download,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            
        except FileNotFoundError:
            flash('Arquivo de relatório não encontrado.', 'error')
            return redirect(url_for('relatorios'))
        except PermissionError:
            flash('Erro de permissão ao gerar relatório. Feche o Excel e tente novamente.', 'error')
            return redirect(url_for('relatorios'))
        except Exception as e:
            print(f"Erro ao exportar Excel: {e}")
            flash('Erro interno ao gerar relatório Excel. Tente novamente.', 'error')
            return redirect(url_for('relatorios'))

    # === API ENDPOINTS ===
    @app.route('/api/funcionarios/<int:funcionario_id>/horas')
    def api_horas_funcionario(funcionario_id):
        mes = request.args.get('mes', datetime.now().month)
        ano = request.args.get('ano', datetime.now().year)
        
        registros = RegistroHora.query.filter(
            RegistroHora.funcionario_id == funcionario_id,
            db.extract('month', RegistroHora.data) == mes,
            db.extract('year', RegistroHora.data) == ano
        ).all()
        
        dados = []
        for registro in registros:
            dados.append({
                'data': registro.data.strftime('%Y-%m-%d'),
                'hora_inicio': registro.hora_inicio.strftime('%H:%M'),
                'hora_fim': registro.hora_fim.strftime('%H:%M') if registro.hora_fim else '',
                'minutos': registro.minutos_trabalhados,
                'horas': round(registro.minutos_trabalhados / 60, 2)
            })
        
        return jsonify(dados)

    # === ROTAS PARA RESUMOS DIÁRIOS ===
    
    @app.route('/resumos/gerar', methods=['POST'])
    def gerar_resumos():
        """Gera resumos diários para uma data ou período"""
        try:
            data_inicio_str = request.form.get('data_inicio')
            data_fim_str = request.form.get('data_fim', data_inicio_str)
            
            if not data_inicio_str:
                flash('Data de início é obrigatória.', 'error')
                return redirect(url_for('relatorios'))
            
            # Converter datas
            from datetime import datetime
            data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
            data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date() if data_fim_str else data_inicio
            
            # Gerar resumos
            from flask_app.models import ResumoDiario
            resumos = ResumoDiario.gerar_resumos_periodo(data_inicio, data_fim)
            
            dias = (data_fim - data_inicio).days + 1
            flash(f'Resumos diários processados: {len(resumos)} registros para {dias} dia(s).', 'success')
            
        except ValueError:
            flash('Formato de data inválido. Use YYYY-MM-DD.', 'error')
        except Exception as e:
            flash('Erro ao gerar resumos diários.', 'error')
            print(f"Erro: {e}")
        
        return redirect(url_for('relatorios'))
    
    @app.route('/resumos/automatico', methods=['POST'])
    def processar_resumos_automatico():
        """Processa resumos diários automaticamente para os últimos 30 dias"""
        try:
            from datetime import date, timedelta
            from flask_app.models import ResumoDiario
            
            # Processar últimos 30 dias
            data_fim = date.today()
            data_inicio = data_fim - timedelta(days=30)
            
            resumos = ResumoDiario.gerar_resumos_periodo(data_inicio, data_fim)
            
            flash(f'Resumos automáticos processados: {len(resumos)} registros dos últimos 30 dias.', 'success')
            
        except Exception as e:
            flash('Erro no processamento automático de resumos.', 'error')
            print(f"Erro: {e}")
        
        return redirect(url_for('relatorios'))
    
    @app.route('/resumos/visualizar')
    def visualizar_resumos():
        """Visualiza resumos diários gerados"""
        try:
            from flask_app.models import ResumoDiario
            
            # Parâmetros de filtro
            funcionario_id = request.args.get('funcionario_id')
            data_inicio = request.args.get('data_inicio')
            data_fim = request.args.get('data_fim')
            
            # Query base
            query = ResumoDiario.query.options(
                db.joinedload(ResumoDiario.funcionario)
            )
            
            # Aplicar filtros
            if funcionario_id and funcionario_id.isdigit():
                query = query.filter(ResumoDiario.funcionario_id == int(funcionario_id))
            
            if data_inicio:
                data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d').date()
                query = query.filter(ResumoDiario.data >= data_inicio_obj)
            
            if data_fim:
                data_fim_obj = datetime.strptime(data_fim, '%Y-%m-%d').date()
                query = query.filter(ResumoDiario.data <= data_fim_obj)
            
            # Ordenar e paginar
            resumos = query.order_by(
                ResumoDiario.data.desc(), 
                ResumoDiario.funcionario_id
            ).limit(100).all()
            
            funcionarios = Funcionario.query.filter_by(ativo=True).order_by(Funcionario.nome).all()
            
            return render_template('resumos_diarios.html', 
                                 resumos=resumos,
                                 funcionarios=funcionarios)
            
        except Exception as e:
            flash('Erro ao carregar resumos diários.', 'error')
            return redirect(url_for('relatorios'))