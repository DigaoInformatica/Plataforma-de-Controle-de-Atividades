from flask import Blueprint, render_template, request, redirect, url_for, session
from models import db, Usuario

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return redirect(url_for('main.login'))


@main.route('/cadastro', methods=['GET','POST'])
def cadastro():

    if request.method == 'POST':

        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']

        novo_usuario = Usuario(nome=nome, email=email, senha=senha)

        db.session.add(novo_usuario)
        db.session.commit()

        return redirect(url_for('main.login'))

    return render_template('cadastro.html')


@main.route('/login', methods=['GET','POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        senha = request.form['senha']

        usuario = Usuario.query.filter_by(email=email, senha=senha).first()

        if usuario:

            # salva usuário na sessão
            session['usuario_nome'] = usuario.nome

            return redirect(url_for('main.home'))

        else:
            erro = "Email ou senha inválidos"
            return render_template('login.html', erro=erro)

    return render_template('login.html')


@main.route('/home')
def home():

    nome = session.get('usuario_nome')

    if not nome:
        return redirect(url_for('main.login'))

    return render_template('home.html', nome=nome)


@main.route('/logout')
def logout():

    session.clear()

    return redirect(url_for('main.login'))