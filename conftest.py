"""
Fixtures compartilhadas para todos os testes pytest.

O app é inicializado em Library_Management_System/__init__.py com ProductionConfig.
Cada fixture de teste sobrescreve com TestConfig (SQLite em memória) antes da
primeira operação de banco de dados, garantindo isolamento total entre testes.
"""

import pytest
from werkzeug.security import generate_password_hash

from Library_Management_System import app as flask_app, db
from Library_Management_System.models import Book, Copy, User
from Library_Management_System.views import main

# Registra o blueprint uma única vez — wsgi.py também faz isso,
# mas aqui protegemos contra duplo registro quando o módulo já foi importado.
if "main" not in flask_app.blueprints:
    flask_app.register_blueprint(main)


@pytest.fixture(scope="function")
def app():
    """Cria um contexto de aplicação isolado com banco SQLite em memória."""
    flask_app.config.from_object("config.TestConfig")
    ctx = flask_app.app_context()
    ctx.push()
    db.create_all()
    yield flask_app
    db.session.remove()
    db.drop_all()
    ctx.pop()


@pytest.fixture(scope="function")
def client(app):
    """Retorna o cliente de teste Flask para simular requisições HTTP."""
    return app.test_client()


@pytest.fixture(scope="function")
def admin_user(app):
    """Cria e persiste um usuário administrador no banco de testes."""
    user = User(
        name="Admin Teste",
        email="admin@test.com",
        password=generate_password_hash("AdminPass123!", method="pbkdf2:sha256"),
        admin=True,
    )
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture(scope="function")
def regular_user(app):
    """Cria e persiste um usuário comum no banco de testes."""
    user = User(
        name="Usuario Teste",
        email="usuario@test.com",
        password=generate_password_hash("UserPass123!", method="pbkdf2:sha256"),
        admin=False,
    )
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture(scope="function")
def sample_book(app):
    """Cria e persiste um livro de exemplo com 5 cópias no banco de testes."""
    book = Book(
        name="Python para Todos",
        author="Charles Severance",
        description="Introdução à programação com Python",
        total_copy=5,
        present_copy=5,
        issued_copy=0,
    )
    db.session.add(book)
    db.session.commit()
    return book
