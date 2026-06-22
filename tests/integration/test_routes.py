"""
Testes de integração para as rotas da aplicação.

Utilizam o cliente de teste do Flask para exercitar a pilha completa:
rota → view → banco de dados (SQLite em memória).
"""

import pytest

from Library_Management_System import db
from Library_Management_System.models import Book, User


class TestRotasPublicas:
    """Rotas acessíveis sem autenticação."""

    def test_pagina_inicial_retorna_200(self, client):
        response = client.get("/")
        assert response.status_code == 200

    def test_pagina_inicial_contem_titulo_sistema(self, client):
        response = client.get("/")
        assert b"Library Management System" in response.data

    def test_pagina_login_retorna_200(self, client):
        response = client.get("/login")
        assert response.status_code == 200

    def test_pagina_login_contem_formulario(self, client):
        response = client.get("/login")
        assert b"Login" in response.data

    def test_pagina_registro_retorna_200(self, client):
        response = client.get("/register")
        assert response.status_code == 200

    def test_pagina_admin_login_retorna_200(self, client):
        response = client.get("/admin")
        assert response.status_code == 200


class TestRotasProtegidas:
    """Rotas que exigem autenticação redirecionam usuários anônimos."""

    def test_dashboard_redireciona_sem_login(self, client):
        response = client.get("/dashboard")
        assert response.status_code == 302

    def test_admin_dashboard_redireciona_sem_login(self, client):
        response = client.get("/admin/dashboard")
        assert response.status_code == 302

    def test_adicionar_livro_redireciona_sem_login(self, client):
        response = client.get("/add/book")
        assert response.status_code == 302

    def test_remover_livro_redireciona_sem_login(self, client):
        response = client.get("/remove/book")
        assert response.status_code == 302

    def test_devolver_livro_redireciona_sem_login(self, client):
        response = client.get("/return/book")
        assert response.status_code == 302

    def test_emitir_livro_redireciona_sem_login(self, client):
        response = client.get("/issue/book")
        assert response.status_code == 302


class TestAutenticacao:
    """Testes de POST para login, registro e validações de credenciais."""

    def test_registro_usuario_novo_redireciona_para_dashboard(self, client, app):
        response = client.post(
            "/register",
            data=dict(name="João Silva", email="joao@test.com", password="Senha123!"),
        )
        assert response.status_code == 302
        assert "/dashboard" in response.headers.get("Location", "")

    def test_registro_email_duplicado_exibe_mensagem(self, client, regular_user):
        response = client.post(
            "/register",
            data=dict(name="Outro", email="usuario@test.com", password="Qualquer1!"),
            follow_redirects=True,
        )
        assert b"User already exists" in response.data

    def test_login_admin_credenciais_corretas_redireciona(self, client, admin_user):
        response = client.post(
            "/admin",
            data=dict(email="admin@test.com", password="AdminPass123!"),
        )
        assert response.status_code == 302

    def test_login_admin_senha_errada_redireciona_com_erro(self, client, admin_user):
        response = client.post(
            "/admin",
            data=dict(email="admin@test.com", password="SenhaErrada!"),
            follow_redirects=True,
        )
        assert b"Invalid Credentials" in response.data

    def test_login_usuario_credenciais_corretas(self, client, regular_user):
        response = client.post(
            "/login",
            data=dict(email="usuario@test.com", password="UserPass123!"),
        )
        assert response.status_code == 302

    def test_login_usuario_senha_errada(self, client, regular_user):
        response = client.post(
            "/login",
            data=dict(email="usuario@test.com", password="SenhaIncorreta!"),
            follow_redirects=True,
        )
        assert b"Invalid Credentials" in response.data

    def test_logout_redireciona_para_pagina_inicial(self, client, regular_user):
        client.post("/login", data=dict(email="usuario@test.com", password="UserPass123!"))
        response = client.get("/logout", follow_redirects=True)
        assert response.status_code == 200


class TestOperacoesLivro:
    """Testes de CRUD de livros como administrador autenticado."""

    def _login_admin(self, client):
        client.post("/admin", data=dict(email="admin@test.com", password="AdminPass123!"))

    def test_admin_pode_adicionar_livro(self, client, admin_user):
        self._login_admin(client)
        response = client.post(
            "/add/book",
            data=dict(
                name="The Clean Coder",
                author="Robert C. Martin",
                description="Conduta profissional",
                number=3,
            ),
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Book added successfully" in response.data

    def test_adicionar_livro_duplicado_exibe_mensagem(self, client, admin_user, sample_book):
        self._login_admin(client)
        response = client.post(
            "/add/book",
            data=dict(
                name="Python para Todos",
                author="Qualquer Autor",
                description="Desc",
                number=1,
            ),
            follow_redirects=True,
        )
        assert b"Book already exists" in response.data

    def test_admin_pode_remover_livro_sem_emprestimo(self, client, admin_user, sample_book):
        self._login_admin(client)
        response = client.post(
            "/remove/book",
            data=dict(book=sample_book.id),
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Book removed successfully" in response.data

    def test_livro_aparece_no_admin_dashboard(self, client, admin_user, sample_book):
        self._login_admin(client)
        response = client.get("/admin/dashboard")
        assert b"Python para Todos" in response.data

    def test_livro_aparece_na_pagina_inicial(self, client, sample_book):
        response = client.get("/")
        assert b"Python para Todos" in response.data
