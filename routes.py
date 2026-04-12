from flask import Blueprint, render_template, request, redirect, url_for, session
from models import db, Usuario, Atividade

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return redirect(url_for('main.login'))

# =========================
# CADASTRO
# =========================
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


# =========================
# LOGIN
# =========================
@main.route('/login', methods=['GET','POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        senha = request.form['senha']

        usuario = Usuario.query.filter_by(email=email, senha=senha).first()

        if usuario:

            session['usuario_id'] = usuario.id
            session['usuario_nome'] = usuario.nome

            return redirect(url_for('main.home'))

        else:
            erro = "Email ou senha inválidos"
            return render_template('login.html', erro=erro)

    return render_template('login.html')


# =========================
# HOME + LISTAR TAREFAS
# =========================
@main.route('/home')
def home():

    if 'usuario_id' not in session:
        return redirect(url_for('main.login'))

    tarefas = Atividade.query.filter_by(
        usuario_id=session['usuario_id']
    ).all()

    return render_template(
        'home.html',
        usuario=session['usuario_nome'],
        tarefas=tarefas
    )


# =========================
# CRIAR TAREFA
# =========================
@main.route('/criar-tarefa', methods=['POST'])
def criar_tarefa():

    if 'usuario_id' not in session:
        return redirect(url_for('main.login'))

    descricao = request.form['descricao']

    nova = Atividade(
        descricao=descricao,
        usuario_id=session['usuario_id']
    )

    db.session.add(nova)
    db.session.commit()

    return redirect(url_for('main.home'))


# =========================
# EXCLUIR TAREFA
# =========================
@main.route('/excluir-tarefa/<int:id>')
def excluir_tarefa(id):

    if 'usuario_id' not in session:
        return redirect(url_for('main.login'))

    tarefa = Atividade.query.filter_by(
        id=id,
        usuario_id=session['usuario_id']
    ).first()

    if tarefa:
        db.session.delete(tarefa)
        db.session.commit()

    return redirect(url_for('main.home'))


# =========================
# EDITAR TAREFA
# =========================
@main.route('/editar-tarefa/<int:id>', methods=['POST'])
def editar_tarefa(id):

    if 'usuario_id' not in session:
        return redirect(url_for('main.login'))

    nova_descricao = request.form['descricao']

    tarefa = Atividade.query.filter_by(
        id=id,
        usuario_id=session['usuario_id']
    ).first()

    if tarefa:
        tarefa.descricao = nova_descricao
        db.session.commit()

    return redirect(url_for('main.home'))


# =========================
# 👁️ DETALHE DA TAREFA
# =========================
@main.route('/tarefa/<int:id>')
def detalhe_tarefa(id):

    if 'usuario_id' not in session:
        return redirect(url_for('main.login'))

    tarefa = Atividade.query.filter_by(
        id=id,
        usuario_id=session['usuario_id']
    ).first()

    if not tarefa:
        return redirect(url_for('main.home'))

    return render_template('detalhe_tarefa.html', tarefa=tarefa)


# =========================
# LOGOUT
# =========================
@main.route('/logout')
def logout():

    session.clear()

    return redirect(url_for('main.login'))