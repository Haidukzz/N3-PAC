from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

load_dotenv()  # Carregar variáveis de ambiente do arquivo .env

app = Flask(__name__, static_folder='static', static_url_path='/projeto/static')

# Configuração do banco de dados MySQL
username = os.getenv('DB_USERNAME')
password = os.getenv('DB_PASSWORD')
database = os.getenv('DB_NAME')
host = os.getenv('DB_HOST')
app.secret_key = os.environ.get('SECRET_KEY')

# Construir a URI do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{username}:{password}@{host}/{database}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True  # Ativar o modo de debug do SQLAlchemy

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')  # Seu email
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')  # Sua senha ou senha de app

db = SQLAlchemy(app)

# Define Data Model
class Cachorro(db.Model):
    __tablename__ = 'cachorro'
    id = db.Column('idCachorro', db.Integer, primary_key=True)
    NomeCachorro = db.Column(db.String(100))
    IdadeCachorro = db.Column(db.Integer)
    RacaCachorro = db.Column(db.String(50))
    CorCachorro = db.Column(db.String(50))
    GeneroCachorro = db.Column(db.String(10))
    DescricaoCachorro = db.Column(db.Text)
    StatusAdocaoCachorro = db.Column(db.String(20))
    ImagemCachorro = db.Column(db.String(255))

    def __repr__(self):
        return f'<Cachorro {self.id}, {self.NomeCachorro}>'
    
# Define Data Model for Events
class Evento(db.Model):
    __tablename__ = 'eventos'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    data_horario = db.Column(db.DateTime, nullable=False, default=datetime.now)
    localizacao = db.Column(db.String(100), nullable=False)
    imagem_evento = db.Column(db.String(255), nullable=True)  # Caminho da imagem do evento

    def __repr__(self):
        return f'<Evento {self.id}, {self.titulo}>'

# Rota de Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        userId = request.form['userId']
        password = request.form['password']

        # Check if credentials are correct
        if userId == 'admin' and password == 'admin123':
            return redirect(url_for('administracao'))
        else:
            # Invalid credentials, set error message
            error = 'Credenciais inválidas. Por favor, tente novamente.'

    # Render login form if method is GET or credentials are incorrect
    return render_template('login.html', error=error)

class Estatisticas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    animais_adotados = db.Column(db.Integer, nullable=False, default=0)
    quilos_racao_doada = db.Column(db.Integer, nullable=False, default=0)
    reais_arrecadados = db.Column(db.Integer, nullable=False, default=0)
    campanhas_realizadas = db.Column(db.Integer, nullable=False, default=0)
    itens_doados = db.Column(db.Integer, nullable=False, default=0)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow)


@app.route('/editar_estatisticas', methods=['POST'])
def editar_estatisticas():
    animais_adotados = request.form.get('animais_adotados')
    quilos_racao_doada = request.form.get('quilos_racao_doada')
    reais_arrecadados = request.form.get('reais_arrecadados')
    campanhas_realizadas = request.form.get('campanhas_realizadas')
    itens_doados = request.form.get('itens_doados')

    # Atualizando o objeto estatísticas no banco de dados
    estatisticas = Estatisticas.query.first()  # Obtendo o primeiro (ou único) registro
    if estatisticas:
        estatisticas.animais_adotados = animais_adotados
        estatisticas.quilos_racao_doada = quilos_racao_doada
        estatisticas.reais_arrecadados = reais_arrecadados
        estatisticas.campanhas_realizadas = campanhas_realizadas
        estatisticas.itens_doados = itens_doados
        estatisticas.data_atualizacao = datetime.now()
        db.session.commit()
    else:
        nova_estatistica = Estatisticas(
            animais_adotados=animais_adotados,
            quilos_racao_doada=quilos_racao_doada,
            reais_arrecadados=reais_arrecadados,
            campanhas_realizadas=campanhas_realizadas,
            itens_doados=itens_doados,
            data_atualizacao=datetime.now()
        )
        db.session.add(nova_estatistica)
        db.session.commit()

    return redirect(url_for('administracao'))

@app.route('/administracao', methods=['GET', 'POST'])
def administracao():
    if request.method == 'POST':
        # Processar formulário de adicionar animal
        if 'nome' in request.form:
            nome = request.form['nome']
            idade = request.form['idade']
            raca = request.form['raca']
            cor = request.form['cor']
            genero = request.form['genero']
            descricao = request.form['descricao']
            status_adocao = request.form['status_adocao']
            foto = request.files['foto']

            # Salvar a foto no diretório correto
            if foto.filename != '':
                foto_dir = os.path.join('projeto', 'static', 'imagens')
                if not os.path.exists(foto_dir):
                    os.makedirs(foto_dir)
                
                foto_path = os.path.join(foto_dir, foto.filename)
                foto.save(foto_path)

            # Criar um novo cachorro no banco de dados
            novo_cachorro = Cachorro(
                NomeCachorro=nome,
                IdadeCachorro=idade,
                RacaCachorro=raca,
                CorCachorro=cor,
                GeneroCachorro=genero,
                DescricaoCachorro=descricao,
                StatusAdocaoCachorro=status_adocao,
                ImagemCachorro=f'imagens/{foto.filename}' if foto.filename != '' else ''
            )
            db.session.add(novo_cachorro)
            db.session.commit()

            return redirect(url_for('administracao'))

        # Processar formulário de adicionar evento
        elif 'titulo' in request.form:
            titulo = request.form['titulo']
            descricao = request.form['descricao']
            data_horario = request.form['data']
            localizacao = request.form['localizacao']

            novo_evento = Evento(
                titulo=titulo,
                descricao=descricao,
                data_horario=data_horario,
                localizacao=localizacao
            )
            db.session.add(novo_evento)
            db.session.commit()

            return redirect(url_for('administracao'))

    # Carregar animais e eventos para exibição
    cachorros = Cachorro.query.all()
    eventos = Evento.query.all()
    return render_template('administracao.html', animais=cachorros, eventos=eventos)

# Rota para remover cachorro
@app.route('/remover_cachorro/<int:id>', methods=['POST'])
def remover_cachorro(id):
    cachorro = Cachorro.query.get(id)
    if cachorro:
        db.session.delete(cachorro)
        db.session.commit()
    return redirect(url_for('administracao'))

# Rota para remover evento
@app.route('/remover_evento/<int:id>', methods=['POST'])
def remover_evento(id):
    evento = Evento.query.get(id)
    if evento:
        db.session.delete(evento)
        db.session.commit()
    return redirect(url_for('administracao'))

# Função para enviar email
def send_email(name, phone, email, message, tipo):
    sender_email = app.config['MAIL_USERNAME']
    receiver_email = "bredleybauer@gmail.com"

    if tipo == 'voluntariado':
        subject = "Novo Formulário de Voluntariado"
    elif tipo == 'adoção':
        subject = "Novo Formulário de Adoção"
    elif tipo == 'apadrinhamento':
        subject = "Novo Formulário de Padrinho"
    else:
        subject = "Novo Formulário"

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    body = f"""
    Nome: {name}
    Telefone: {phone}
    Email: {email}
    Mensagem: {message}
    """
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Conectar ao servidor SMTP do Gmail e enviar email
        with smtplib.SMTP(app.config['MAIL_SERVER'], app.config['MAIL_PORT']) as server:
            server.starttls()
            server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            server.sendmail(sender_email, receiver_email, msg.as_string())
            print("Email enviado com sucesso!")
    except Exception as e:
        print(f"Falha ao enviar email: {e}")

# Rota para o formulário de voluntariado
@app.route('/enviar_voluntariar', methods=['POST'])
def enviar_voluntariar():
    name = request.form['name']
    phone = request.form['phone']
    email = request.form['email']
    message = request.form['message']

    send_email(name, phone, email, message, 'voluntariado')
    return redirect(url_for('agenda'))  # Redireciona para a página agenda
    

# Rota para o formulário de adoção
@app.route('/enviar_adocao', methods=['POST'])
def enviar_adocao():
    name = request.form['name']
    phone = request.form['phone']
    email = request.form['email']
    message = request.form['message']

    send_email(name, phone, email, message, 'adoção')
    return redirect(url_for('adocao'))  # Redireciona para a página do catálogo

# Rota para o formulário de apadrinhamento
@app.route('/enviar_apadrinhar', methods=['POST'])
def enviar_apadrinhar():
    name = request.form['name']
    phone = request.form['phone']
    email = request.form['email']
    message = request.form['message']

    send_email(name, phone, email, message, 'apadrinhamento')
    return redirect(url_for('adocao'))  # Redireciona para a página do catálogo

@app.route('/')
@app.route('/home')
def home():
    estatisticas = Estatisticas.query.first()  # Recupera as estatísticas do banco de dados
    if estatisticas is not None:
        return render_template('home.html', css_file='/projeto/static/css/home.css', estatisticas=estatisticas)


@app.route('/')
@app.route('/faq')
def faq():
    return render_template('faq.html', css_file='/projeto/static/css/faq.css')

@app.route('/adocao')
def adocao():
    cachorros = Cachorro.query.all()
    return render_template('adocao.html', css_file='/projeto/static/css/adocao.css', animais=cachorros)

# Rota para a página de agenda (que agora lista eventos)
@app.route('/agenda')
def agenda():
    eventos = Evento.query.all()
    return render_template('agenda.html', css_file='/projeto/static/css/agenda.css', eventos=eventos)


@app.route('/adicionar_evento', methods=['POST'])
def adicionar_evento():
    titulo = request.form['titulo']
    descricao = request.form['descricao']
    data_horario = request.form['data_horario']  # Corrigido aqui
    localizacao = request.form['localizacao']
    foto = request.files['foto']

    if foto and foto.filename != '':
        foto_dir = os.path.join('projeto', 'static', 'imagens')
        if not os.path.exists(foto_dir):
            os.makedirs(foto_dir)
        
        foto_path = os.path.join(foto_dir, foto.filename)
        foto.save(foto_path)
        imagem_caminho = f'imagens/{foto.filename}'
    else:
        imagem_caminho = None

    novo_evento = Evento(
        titulo=titulo,
        descricao=descricao,
        data_horario=datetime.strptime(data_horario, '%Y-%m-%dT%H:%M'),  # Ajuste do formato se necessário
        localizacao=localizacao,
        imagem_evento=imagem_caminho
    )
    db.session.add(novo_evento)
    db.session.commit()

    return redirect(url_for('agenda'))


@app.route('/editar_evento/<int:id>', methods=['GET', 'POST'])
def editar_evento(id):
    evento = Evento.query.get_or_404(id)
    if request.method == 'POST':
        evento.titulo = request.form['titulo']
        evento.descricao = request.form['descricao']
        evento.data_horario = datetime.strptime(request.form['data_horario'], '%Y-%m-%dT%H:%M')
        evento.localizacao = request.form['localizacao']
        db.session.commit()
        return redirect(url_for('agenda'))
    return render_template('editar_evento.html', evento=evento)


@app.route('/editar_cachorro/<int:id>', methods=['GET', 'POST'])
def editar_cachorro(id):
    cachorro = Cachorro.query.get_or_404(id)
    if request.method == 'POST':
        cachorro.NomeCachorro = request.form['nome']
        cachorro.IdadeCachorro = request.form['idade']
        cachorro.RacaCachorro = request.form['raca']
        cachorro.CorCachorro = request.form['cor']
        cachorro.GeneroCachorro = request.form['genero']
        cachorro.DescricaoCachorro = request.form['descricao']
        cachorro.StatusAdocaoCachorro = request.form['status_adocao']
        db.session.commit()
        return redirect(url_for('administracao'))
    return render_template('editar_cachorro.html', cachorro=cachorro)


if __name__ == '__main__':
    app.run(debug=True)
