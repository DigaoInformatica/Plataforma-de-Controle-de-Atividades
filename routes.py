from flask import Blueprint, render_template, request, redirect, url_for, session
from models import db, Usuario, Atividade, Tarefa

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
# HOME
# =========================
@main.route('/home')
def home():

    if 'usuario_id' not in session:
        return redirect(url_for('main.login'))

    atividades = Atividade.query.filter_by(
        usuario_id=session['usuario_id']
    ).all()

    atividades_com_status = []

    for atividade in atividades:
        tarefas = Tarefa.query.filter_by(
            atividade_id=atividade.id
        ).all()

        total = len(tarefas)
        concluidas = len([t for t in tarefas if t.concluida])

        concluida = False
        if total > 0 and total == concluidas:
            concluida = True

        atividades_com_status.append({
            'atividade': atividade,
            'concluida': concluida
        })

    return render_template(
        'home.html',
        usuario=session['usuario_nome'],
        tarefas=atividades_com_status
    )


# =========================
# CRIAR ATIVIDADE
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
# EXCLUIR ATIVIDADE (SEM ERRO)
# =========================
@main.route('/excluir-tarefa/<int:id>')
def excluir_tarefa(id):

    if 'usuario_id' not in session:
        return redirect(url_for('main.login'))

    atividade = Atividade.query.filter_by(
        id=id,
        usuario_id=session['usuario_id']
    ).first()

    if not atividade:
        return redirect(url_for('main.home'))

    try:
        # 🔥 DELETA TODAS AS SUBTAREFAS (sem carregar na memória)
        Tarefa.query.filter_by(
            atividade_id=atividade.id
        ).delete(synchronize_session=False)

        # 🔥 DEPOIS DELETA A ATIVIDADE
        db.session.delete(atividade)

        db.session.commit()

    except Exception as e:
        db.session.rollback()
        print("ERRO AO EXCLUIR:", e)

    return redirect(url_for('main.home'))


# =========================
# EDITAR ATIVIDADE
# =========================
@main.route('/editar-tarefa/<int:id>', methods=['POST'])
def editar_tarefa(id):

    if 'usuario_id' not in session:
        return redirect(url_for('main.login'))

    nova_descricao = request.form['descricao']

    atividade = Atividade.query.filter_by(
        id=id,
        usuario_id=session['usuario_id']
    ).first()

    if atividade:
        atividade.descricao = nova_descricao
        db.session.commit()

    return redirect(url_for('main.home'))


# =========================
# DETALHE DA ATIVIDADE
# =========================
@main.route('/tarefa/<int:id>')
def detalhe_tarefa(id):

    if 'usuario_id' not in session:
        return redirect(url_for('main.login'))

    atividade = Atividade.query.filter_by(
        id=id,
        usuario_id=session['usuario_id']
    ).first()

    if not atividade:
        return redirect(url_for('main.home'))

    tarefas = Tarefa.query.filter_by(
        atividade_id=atividade.id
    ).all()

    total = len(tarefas)
    concluidas = len([t for t in tarefas if t.concluida])

    porcentagem = 0
    if total > 0:
        porcentagem = int((concluidas / total) * 100)

    return render_template(
        'detalhe_tarefa.html',
        atividade=atividade,
        tarefas=tarefas,
        porcentagem=porcentagem
    )


# =========================
# CRIAR SUBTAREFA
# =========================
@main.route('/criar-subtarefa/<int:atividade_id>', methods=['POST'])
def criar_subtarefa(atividade_id):

    if 'usuario_id' not in session:
        return redirect(url_for('main.login'))

    descricao = request.form['descricao']

    nova = Tarefa(
        descricao=descricao,
        atividade_id=atividade_id
    )

    db.session.add(nova)
    db.session.commit()

    return redirect(url_for('main.detalhe_tarefa', id=atividade_id))


# =========================
# EXCLUIR SUBTAREFA
# =========================
@main.route('/excluir-subtarefa/<int:id>')
def excluir_subtarefa(id):

    if 'usuario_id' not in session:
        return redirect(url_for('main.login'))

    tarefa = Tarefa.query.get(id)

    if tarefa:
        atividade_id = tarefa.atividade_id
        db.session.delete(tarefa)
        db.session.commit()
        return redirect(url_for('main.detalhe_tarefa', id=atividade_id))

    return redirect(url_for('main.home'))


# =========================
# CONCLUIR SUBTAREFA
# =========================
@main.route('/concluir-subtarefa/<int:id>')
def concluir_subtarefa(id):

    if 'usuario_id' not in session:
        return redirect(url_for('main.login'))

    tarefa = Tarefa.query.get(id)

    if tarefa:
        tarefa.concluida = not tarefa.concluida
        db.session.commit()
        return redirect(url_for('main.detalhe_tarefa', id=tarefa.atividade_id))

    return redirect(url_for('main.home'))


# =========================
# LOGOUT
# =========================
@main.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.login'))