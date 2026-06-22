"""
Testes de aceitação — simulam jornadas completas de usuário.

Abordagem: cliente de teste Flask (sem browser real), cobrindo
os critérios de aceitação do sistema de ponta a ponta.

Cenários cobertos:
  AC-01  Usuário se registra e acessa o dashboard imediatamente
  AC-02  Administrador faz login, adiciona um livro e o remove com sucesso
  AC-03  Usuário não autenticado não consegue acessar área restrita
  AC-04  Mensagem correta exibida ao tentar registrar e-mail já existente
"""

from Library_Management_System import db
from Library_Management_System.models import Book


class TestJornadaUsuario:
    """AC-01 — Registro, acesso ao dashboard e logout."""

    def test_registro_completo_e_acesso_ao_dashboard(self, client):
        # 1. Usuário visita a página inicial e ela carrega corretamente
        resposta = client.get("/")
        assert resposta.status_code == 200
        assert b"Library Management System" in resposta.data

        # 2. Usuário acessa o formulário de registro
        resposta = client.get("/register")
        assert resposta.status_code == 200

        # 3. Usuário preenche e envia o formulário de registro
        resposta = client.post(
            "/register",
            data=dict(
                name="Maria Oliveira",
                email="maria@biblioteca.com",
                password="MariaSegura123!",
            ),
            follow_redirects=False,
        )
        # Sistema redireciona para o dashboard após registro bem-sucedido
        assert resposta.status_code == 302
        assert "/dashboard" in resposta.headers.get("Location", "")

        # 4. Seguindo o redirecionamento, o dashboard carrega com sucesso
        resposta = client.get("/dashboard", follow_redirects=True)
        assert resposta.status_code == 200

        # 5. Usuário faz logout
        resposta = client.get("/logout", follow_redirects=True)
        assert resposta.status_code == 200

        # 6. Após logout, tentar acessar dashboard redireciona para login
        resposta = client.get("/dashboard", follow_redirects=False)
        assert resposta.status_code == 302


class TestJornadaAdministrador:
    """AC-02 — Administrador gerencia o acervo da biblioteca."""

    def test_admin_gerencia_catalogo_completo(self, client, admin_user):
        # 1. Admin acessa a página de login de administrador
        resposta = client.get("/admin")
        assert resposta.status_code == 200

        # 2. Admin faz login com credenciais válidas
        resposta = client.post(
            "/admin",
            data=dict(email="admin@test.com", password="AdminPass123!"),
            follow_redirects=False,
        )
        assert resposta.status_code == 302

        # 3. Admin visualiza o painel administrativo
        resposta = client.get("/admin/dashboard", follow_redirects=True)
        assert resposta.status_code == 200

        # 4. Admin adiciona um novo livro ao acervo
        resposta = client.post(
            "/add/book",
            data=dict(
                name="The Pragmatic Programmer",
                author="Andrew Hunt e David Thomas",
                description="Do aprendiz ao mestre",
                number=4,
            ),
            follow_redirects=True,
        )
        assert resposta.status_code == 200
        assert b"Book added successfully" in resposta.data

        # 5. O livro aparece no painel administrativo
        resposta = client.get("/admin/dashboard")
        assert b"The Pragmatic Programmer" in resposta.data

        # 6. O livro também aparece na página inicial para visitantes
        resposta = client.get("/")
        assert b"The Pragmatic Programmer" in resposta.data

        # 7. Admin remove o livro (sem exemplares emprestados)
        livro = Book.query.filter_by(name="The Pragmatic Programmer").first()
        assert livro is not None
        resposta = client.post(
            "/remove/book",
            data=dict(book=livro.id),
            follow_redirects=True,
        )
        assert resposta.status_code == 200
        assert b"Book removed successfully" in resposta.data


class TestControleAcesso:
    """AC-03 — Área restrita inacessível sem autenticação."""

    def test_usuario_anonimo_nao_acessa_areas_restritas(self, client):
        rotas_restritas = [
            "/dashboard",
            "/admin/dashboard",
            "/add/book",
            "/remove/book",
            "/return/book",
            "/issue/book",
        ]
        for rota in rotas_restritas:
            resposta = client.get(rota, follow_redirects=False)
            assert resposta.status_code == 302, (
                f"Rota {rota} deveria redirecionar usuário anônimo, "
                f"mas retornou {resposta.status_code}"
            )


class TestValidacaoCadastro:
    """AC-04 — Validação de e-mail duplicado no registro."""

    def test_email_duplicado_exibe_mensagem_de_erro(self, client, regular_user):
        # Tenta registrar com o mesmo e-mail do usuário já existente
        resposta = client.post(
            "/register",
            data=dict(
                name="Outro Nome",
                email="usuario@test.com",
                password="OutraSenha123!",
            ),
            follow_redirects=True,
        )
        assert resposta.status_code == 200
        assert b"User already exists" in resposta.data
