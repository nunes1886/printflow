import os
import time
import base64
import uuid 
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

# --- CONFIGURAÇÃO ---
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'chave-super-secreta-printflow'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'printflow.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# --- CONTROLE DE VERSÃO E SONS ---
ULTIMA_ATUALIZACAO = time.time()
ULTIMO_CHAT_ID = 0
ULTIMO_CARD_ID = 0 # Novo controle para som de card

def atualizar_versao():
    global ULTIMA_ATUALIZACAO
    ULTIMA_ATUALIZACAO = time.time()

# --- MODELOS ---

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)
    funcao = db.Column(db.String(20), nullable=False)

    def get_id(self):
        return str(self.id)

    @property
    def is_admin(self):
        return self.funcao == 'admin'

    def check_password(self, password):
        try: return check_password_hash(self.senha, password)
        except: return self.senha == password
    
    def set_password(self, password):
        self.senha = generate_password_hash(password)

class Setor(db.Model):
    __tablename__ = 'setores'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    ordem = db.Column(db.Integer, nullable=False)
    cards = db.relationship('Card', backref='setor_ref', lazy=True, order_by='Card.id')

class Status(db.Model):
    __tablename__ = 'status'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    cor = db.Column(db.String(20), default='#CCCCCC')

class Card(db.Model):
    __tablename__ = 'cards'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    cliente = db.Column(db.String(100), nullable=True)
    imagem_path = db.Column(db.Text, nullable=True)
    data_criacao = db.Column(db.String(50))
    setor_id = db.Column(db.Integer, db.ForeignKey('setores.id'))
    status_id = db.Column(db.Integer, db.ForeignKey('status.id'))
    status_ref = db.relationship('Status', lazy=True)
    
    # NOVOS CAMPOS
    created_by = db.Column(db.String(100)) # Quem criou
    is_archived = db.Column(db.Boolean, default=False) # Se está arquivado
    
    # --- NOVO CAMPO DO SEMÁFORO ---
    prazo = db.Column(db.String(20)) # Formato YYYY-MM-DD

class Mensagem(db.Model):
    __tablename__ = 'mensagens'
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(100))
    texto = db.Column(db.Text)
    data_envio = db.Column(db.String(50))

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

def salvar_imagem_base64(base64_string):
    if not base64_string: return None
    try:
        header, encoded = base64_string.split(",", 1)
        data = base64.b64decode(encoded)
        filename = f"{uuid.uuid4()}.png"
        folder = os.path.join(basedir, 'static', 'uploads')
        if not os.path.exists(folder): os.makedirs(folder)
        filepath = os.path.join(folder, filename)
        with open(filepath, "wb") as f: f.write(data)
        return filename
    except: return None

# --- ROTAS DE API (CHAT E UPDATE) ---

@app.route('/verificar_atualizacao')
def verificar_atualizacao():
    global ULTIMO_CARD_ID
    # Busca ID da ultima msg e ultimo card para tocar sons
    ultimo_msg = Mensagem.query.order_by(Mensagem.id.desc()).first()
    msg_id = ultimo_msg.id if ultimo_msg else 0
    
    # Se reiniciou o servidor, pega do banco
    if ULTIMO_CARD_ID == 0:
        last_c = Card.query.order_by(Card.id.desc()).first()
        if last_c: ULTIMO_CARD_ID = last_c.id

    return jsonify({
        'timestamp': ULTIMA_ATUALIZACAO, 
        'chat_id': msg_id,
        'last_card_id': ULTIMO_CARD_ID
    })

@app.route('/chat/enviar', methods=['POST'])
@login_required
def enviar_mensagem():
    data = request.get_json()
    msg = Mensagem(
        usuario=current_user.username,
        texto=data.get('texto'),
        data_envio=datetime.now().strftime("%H:%M")
    )
    db.session.add(msg)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/chat/listar')
@login_required
def listar_mensagens():
    msgs = Mensagem.query.order_by(Mensagem.id.asc()).all()[-50:]
    return jsonify([{
        'usuario': m.usuario,
        'texto': m.texto,
        'hora': m.data_envio,
        'eu_mesmo': m.usuario == current_user.username
    } for m in msgs])

# --- ROTAS PRINCIPAIS ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = Usuario.query.filter_by(username=request.form.get('username')).first()
        if user and user.check_password(request.form.get('password')):
            login_user(user)
            return redirect(url_for('index'))
        flash('Erro no login.')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    setores = Setor.query.order_by(Setor.ordem).all()
    lista_status = Status.query.all()
    return render_template('index.html', setores=setores, lista_status=lista_status, user=current_user)

@app.route('/usuarios')
@login_required
def usuarios():
    if not current_user.is_admin: return redirect(url_for('index'))
    users = Usuario.query.all()
    return render_template('usuarios.html', users=users, user=current_user)

@app.route('/usuario/salvar', methods=['POST'])
@login_required
def salvar_usuario():
    if not current_user.is_admin: return "Negado", 403
    uid, nome, senha, func = request.form.get('id'), request.form.get('username'), request.form.get('password'), request.form.get('is_admin')
    nova_funcao = 'admin' if func == 'on' else 'colaborador'
    
    if uid:
        u = Usuario.query.get(uid)
        u.username, u.funcao = nome, nova_funcao
        if senha: u.set_password(senha)
    else:
        if Usuario.query.filter_by(username=nome).first():
            flash('Usuário já existe.'); return redirect(url_for('usuarios'))
        u = Usuario(username=nome, funcao=nova_funcao)
        u.set_password(senha if senha else '1234')
        db.session.add(u)
    
    db.session.commit()
    return redirect(url_for('usuarios'))

@app.route('/usuario/excluir/<int:id>', methods=['POST'])
@login_required
def excluir_usuario(id):
    if not current_user.is_admin or id == current_user.id: return jsonify({'error': 'Erro'}), 400
    db.session.delete(Usuario.query.get(id))
    db.session.commit()
    return jsonify({'success': True})

# --- KANBAN ---

@app.route('/api/card/<int:card_id>')
@login_required
def get_card_data(card_id):
    card = Card.query.get_or_404(card_id)
    return jsonify({
        'id': card.id, 'titulo': card.titulo, 'descricao': card.descricao,
        'cliente': card.cliente, 'setor_id': card.setor_id, 'status_id': card.status_id,
        'imagem_path': card.imagem_path,
        'created_by': card.created_by,
        'created_at': card.data_criacao,
        'prazo': card.prazo # <--- Retorna o prazo para o modal
    })

@app.route('/adicionar', methods=['POST'])
@login_required
def adicionar():
    global ULTIMO_CARD_ID
    if not current_user.is_admin: return "Negado", 403
    nome_arquivo = salvar_imagem_base64(request.form.get('imagem_base64'))
    s = Setor.query.order_by(Setor.ordem).first()
    st = Status.query.first()
    
    c = Card(
        titulo=request.form.get('titulo'), 
        cliente=request.form.get('cliente'), 
        descricao=request.form.get('descricao'), 
        data_criacao=datetime.now().strftime("%d/%m %H:%M"),
        setor_id=s.id, 
        status_id=st.id, 
        imagem_path=nome_arquivo,
        created_by=current_user.username,
        is_archived=False,
        prazo=request.form.get('prazo') # <--- Salva o prazo do formulário
    )
    db.session.add(c)
    db.session.commit()
    
    ULTIMO_CARD_ID = c.id 
    atualizar_versao()
    
    return redirect(url_for('index'))

@app.route('/editar', methods=['POST'])
@login_required
def editar():
    c = Card.query.get(request.form.get('id'))
    if c:
        if request.form.get('status_id'): c.status_id = int(request.form.get('status_id'))
        if request.form.get('setor_id'): c.setor_id = int(request.form.get('setor_id'))
        if current_user.is_admin:
            c.titulo = request.form.get('titulo')
            c.cliente = request.form.get('cliente')
            c.descricao = request.form.get('descricao')
            c.prazo = request.form.get('prazo') # <--- Atualiza o prazo na edição
            
            img = salvar_imagem_base64(request.form.get('imagem_base64'))
            if img: c.imagem_path = img
        db.session.commit(); atualizar_versao()
    return redirect(url_for('index'))

@app.route('/mover', methods=['POST'])
@login_required
def mover():
    data = request.get_json()
    c = Card.query.get(data.get('id'))
    if c:
        if 'setor_id' in data: c.setor_id = data.get('setor_id')
        if 'status_id' in data: c.status_id = data.get('status_id')
        db.session.commit(); atualizar_versao()
        return jsonify({'success': True})
    return jsonify({'error': 'Erro'}), 404

# --- ARQUIVAR / EXCLUIR ---

@app.route('/arquivar/<int:id>', methods=['POST'])
@login_required
def arquivar(id):
    if not current_user.is_admin: return jsonify({'error': 'Negado'}), 403
    c = Card.query.get(id)
    if c:
        c.is_archived = True
        db.session.commit()
        atualizar_versao()
        return jsonify({'success': True})
    return jsonify({'error': 'Card não encontrado'}), 404

@app.route('/excluir/<int:id>', methods=['POST'])
@login_required
def excluir(id):
    if not current_user.is_admin: return jsonify({'error': 'Negado'}), 403
    db.session.delete(Card.query.get(id)); db.session.commit(); atualizar_versao()
    return jsonify({'success': True})

# --- CONFIGURAÇÕES ---
@app.route('/configuracoes')
@login_required
def configuracoes():
    if current_user.funcao != 'admin':
        return redirect(url_for('index'))
    
    setores = Setor.query.order_by(Setor.ordem).all()
    lista_status = Status.query.all()
    
    upload_folder = os.path.join(app.root_path, 'static', 'uploads')
    total_size = 0
    total_files = 0
    
    if os.path.exists(upload_folder):
        for path, dirs, files in os.walk(upload_folder):
            for f in files:
                fp = os.path.join(path, f)
                total_size += os.path.getsize(fp)
                total_files += 1
    
    size_mb = round(total_size / (1024 * 1024), 2)
    
    return render_template('configuracoes.html', 
                          setores=setores, 
                          lista_status=lista_status,
                          size_mb=size_mb, 
                          total_files=total_files,
                          user=current_user)

@app.route('/setor/adicionar', methods=['POST'])
@login_required
def adicionar_setor():
    if not current_user.is_admin: return "Negado", 403
    u = Setor.query.order_by(Setor.ordem.desc()).first()
    db.session.add(Setor(nome=request.form.get('nome'), ordem=(u.ordem + 1) if u else 1))
    db.session.commit(); atualizar_versao()
    return redirect(url_for('configuracoes'))

@app.route('/setor/excluir/<int:id>', methods=['POST'])
@login_required
def excluir_setor(id):
    s = Setor.query.get(id)
    if s and not s.cards: db.session.delete(s); db.session.commit(); atualizar_versao()
    else: flash('Setor com cards não pode ser excluído.')
    return redirect(url_for('configuracoes'))

@app.route('/status/adicionar', methods=['POST'])
@login_required
def adicionar_status():
    if not current_user.is_admin: return "Negado", 403
    db.session.add(Status(nome=request.form.get('nome'), cor=request.form.get('cor')))
    db.session.commit()
    return redirect(url_for('configuracoes'))

@app.route('/status/excluir/<int:id>', methods=['POST'])
@login_required
def excluir_status(id):
    s = Status.query.get(id)
    if s: db.session.delete(s); db.session.commit()
    return redirect(url_for('configuracoes'))

@app.route('/chat/limpar', methods=['POST'])
@login_required
def limpar_chat():
    if not current_user.is_admin:
        return jsonify({'error': 'Apenas admin pode limpar o chat.'}), 403
    try:
        Mensagem.query.delete()
        db.session.commit()
        atualizar_versao() 
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# --- NOVAS ROTAS PARA ARQUIVADOS ---

@app.route('/api/arquivados')
@login_required
def api_arquivados():
    cards = Card.query.filter_by(is_archived=True).order_by(Card.id.desc()).limit(50).all()
    lista = []
    for c in cards:
        lista.append({
            'id': c.id,
            'titulo': c.titulo,
            'cliente': c.cliente,
            'data': c.data_criacao,
            'criado_por': c.created_by
        })
    return jsonify(lista)

@app.route('/desarquivar/<int:card_id>', methods=['POST'])
@login_required
def desarquivar_card(card_id):
    if current_user.funcao != 'admin':
        return jsonify({'error': 'Apenas admin pode restaurar'}), 403
    
    card = Card.query.get(card_id)
    if card:
        card.is_archived = False
        db.session.commit()
        atualizar_versao() 
        return jsonify({'success': True})
    return jsonify({'error': 'Card não encontrado'}), 404

# --- ROTA DE LIMPEZA DE IMAGENS ---
@app.route('/api/limpar_imagens', methods=['POST'])
@login_required
def limpar_imagens():
    if current_user.funcao != 'admin':
        return jsonify({'error': 'Não autorizado'}), 403
        
    dias = int(request.json.get('dias', 60)) 
    
    data_limite_obj = datetime.now() - timedelta(days=dias)
    cards_arquivados = Card.query.filter_by(is_archived=True).all()
    
    imagens_apagadas = 0
    espaco_liberado = 0
    upload_folder = os.path.join(app.root_path, 'static', 'uploads')
    
    for card in cards_arquivados:
        try:
            if card.imagem_path:
                caminho_arquivo = os.path.join(upload_folder, card.imagem_path)
                if os.path.exists(caminho_arquivo):
                    timestamp_arquivo = os.path.getmtime(caminho_arquivo)
                    data_arquivo = datetime.fromtimestamp(timestamp_arquivo)
                    
                    if data_arquivo < data_limite_obj:
                        tamanho = os.path.getsize(caminho_arquivo)
                        os.remove(caminho_arquivo)
                        card.imagem_path = None
                        imagens_apagadas += 1
                        espaco_liberado += tamanho
        except Exception as e:
            print(f"Erro ao limpar card {card.id}: {e}")
            continue

    db.session.commit()
    mb_liberados = round(espaco_liberado / (1024 * 1024), 2)
    return jsonify({'success': True, 'qtd': imagens_apagadas, 'mb': mb_liberados})

# --- ROTA DO DASHBOARD (NOVIDADE V3.0) ---
# --- ROTA DO DASHBOARD COM FILTRO (v3.1) ---
@app.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_admin:
        return redirect(url_for('index'))
    
    # 1. Pega as datas do filtro (se existirem na URL)
    data_inicio = request.args.get('start')
    data_fim = request.args.get('end')

    # 2. Base da consulta (Apenas não arquivados)
    query = Card.query.filter_by(is_archived=False)

    # 3. Aplica o Filtro de Prazo (Se o usuário escolheu datas)
    if data_inicio:
        query = query.filter(Card.prazo >= data_inicio)
    if data_fim:
        query = query.filter(Card.prazo <= data_fim)

    # Executa a busca no banco
    cards_filtrados = query.all()

    # 4. Calcula os Totais em Memória (Python) usando a lista filtrada
    total_ativos = len(cards_filtrados)
    
    hoje_str = datetime.now().strftime('%Y-%m-%d')
    atrasados = 0
    para_hoje = 0
    
    # Dicionários para os Gráficos
    contagem_status = {}
    contagem_setor = {}

    for c in cards_filtrados:
        # Contagem de Prazos
        if c.prazo:
            if c.prazo < hoje_str:
                atrasados += 1
            elif c.prazo == hoje_str:
                para_hoje += 1
        
        # Contagem para Gráfico de Status
        nome_status = c.status_ref.nome if c.status_ref else 'Sem Status'
        cor_status = c.status_ref.cor if c.status_ref else '#cccccc'
        
        if nome_status not in contagem_status:
            contagem_status[nome_status] = {'qtd': 0, 'cor': cor_status}
        contagem_status[nome_status]['qtd'] += 1

        # Contagem para Gráfico de Setor
        nome_setor = c.setor_ref.nome if c.setor_ref else 'Sem Setor'
        if nome_setor not in contagem_setor:
            contagem_setor[nome_setor] = 0
        contagem_setor[nome_setor] += 1

    # Prepara dados para o Chart.js
    labels_status = list(contagem_status.keys())
    values_status = [v['qtd'] for v in contagem_status.values()]
    colors_status = [v['cor'] for v in contagem_status.values()]

    labels_setor = list(contagem_setor.keys())
    values_setor = list(contagem_setor.values())

    return render_template('dashboard.html', 
                           user=current_user,
                           total=total_ativos,
                           atrasados=atrasados,
                           para_hoje=para_hoje,
                           labels_status=labels_status,
                           colors_status=colors_status,
                           values_status=values_status,
                           labels_setor=labels_setor,
                           values_setor=values_setor,
                           start_date=data_inicio, # Devolve a data pro HTML preencher o campo
                           end_date=data_fim)

if __name__ == '__main__':
    if not os.path.exists(os.path.join(basedir, 'printflow.db')):
        with app.app_context():
            db.create_all()
            if not Usuario.query.filter_by(username='admin').first():
                u = Usuario(username='admin', funcao='admin')
                u.set_password('admin')
                db.session.add(u)
            if not Setor.query.first():
                 db.session.add(Setor(nome="Atendimento", ordem=1))
                 db.session.add(Setor(nome="Produção", ordem=2))
                 db.session.add(Setor(nome="Expedição", ordem=3))
            if not Status.query.first():
                db.session.add(Status(nome="Pendente", cor="gray"))
                db.session.add(Status(nome="Concluído", cor="green"))
            db.session.commit()
            
    app.run(debug=True, host='0.0.0.0', port=5000)