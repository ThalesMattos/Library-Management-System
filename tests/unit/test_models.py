"""
Testes unitários para os modelos User, Book e Copy.

Verificam a criação, atributos padrão, relacionamentos e integridade
dos modelos ORM sem depender de rotas ou lógica de negócio da aplicação.
"""

from datetime import datetime

import pytest

from Library_Management_System import db
from Library_Management_System.models import Book, Copy, User


class TestUserModel:
    def test_criacao_usuario_persiste_no_banco(self, app):
        user = User(name="Alice", email="alice@test.com", password="hash_qualquer")
        db.session.add(user)
        db.session.commit()
        assert user.id is not None

    def test_usuario_admin_padrao_e_falso(self, app):
        user = User(name="Bob", email="bob@test.com", password="hash")
        db.session.add(user)
        db.session.commit()
        assert user.admin is False

    def test_usuario_admin_pode_ser_verdadeiro(self, app):
        user = User(name="Admin", email="admin@dominio.com", password="hash", admin=True)
        db.session.add(user)
        db.session.commit()
        assert user.admin is True

    def test_email_usuario_e_unico(self, app):
        u1 = User(name="Carlos", email="carlos@test.com", password="hash")
        u2 = User(name="Carlos2", email="carlos@test.com", password="hash")
        db.session.add(u1)
        db.session.commit()
        db.session.add(u2)
        with pytest.raises(Exception):
            db.session.commit()

    def test_user_mixin_is_active_retorna_verdadeiro(self, app):
        user = User(name="Diana", email="diana@test.com", password="hash")
        db.session.add(user)
        db.session.commit()
        assert user.is_active is True

    def test_user_mixin_get_id_retorna_string(self, app):
        user = User(name="Eva", email="eva@test.com", password="hash")
        db.session.add(user)
        db.session.commit()
        assert user.get_id() == str(user.id)

    def test_usuario_tem_relacionamento_com_copies(self, app):
        user = User(name="Fabio", email="fabio@test.com", password="hash")
        db.session.add(user)
        db.session.commit()
        assert hasattr(user, "book")


class TestBookModel:
    def test_criacao_livro_persiste_no_banco(self, app):
        book = Book(
            name="Flask Web Development",
            author="Miguel Grinberg",
            description="Guia completo de Flask",
            total_copy=3,
            present_copy=3,
            issued_copy=0,
        )
        db.session.add(book)
        db.session.commit()
        assert book.id is not None

    def test_livro_tem_nome_correto(self, app):
        book = Book(
            name="Clean Code",
            author="Robert C. Martin",
            description="Código limpo",
            total_copy=2,
            present_copy=2,
            issued_copy=0,
        )
        db.session.add(book)
        db.session.commit()
        recuperado = Book.query.filter_by(name="Clean Code").first()
        assert recuperado is not None
        assert recuperado.author == "Robert C. Martin"

    def test_livro_total_copies_igual_present_copies_inicial(self, app):
        book = Book(
            name="The Pragmatic Programmer",
            author="Hunt & Thomas",
            description="Programador pragmático",
            total_copy=4,
            present_copy=4,
            issued_copy=0,
        )
        db.session.add(book)
        db.session.commit()
        assert book.total_copy == book.present_copy

    def test_livro_com_copies_relacionadas(self, app):
        book = Book(
            name="Design Patterns",
            author="Gang of Four",
            description="Padrões de projeto",
            total_copy=2,
            present_copy=2,
            issued_copy=0,
        )
        copy1 = Copy(date_added=datetime.now())
        copy2 = Copy(date_added=datetime.now())
        book.copy.append(copy1)
        book.copy.append(copy2)
        db.session.add(book)
        db.session.commit()
        assert len(book.copy) == 2

    def test_livro_nome_unico(self, app):
        b1 = Book(name="Livro X", author="A", description="D", total_copy=1, present_copy=1, issued_copy=0)
        b2 = Book(name="Livro X", author="B", description="D", total_copy=1, present_copy=1, issued_copy=0)
        db.session.add(b1)
        db.session.commit()
        db.session.add(b2)
        with pytest.raises(Exception):
            db.session.commit()


class TestCopyModel:
    def test_criacao_copy_persiste_no_banco(self, app, sample_book):
        copy = Copy(date_added=datetime.now(), book=sample_book.id)
        db.session.add(copy)
        db.session.commit()
        assert copy.id is not None

    def test_copy_issued_by_padrao_none(self, app, sample_book):
        copy = Copy(date_added=datetime.now(), book=sample_book.id)
        db.session.add(copy)
        db.session.commit()
        assert copy.issued_by is None

    def test_copy_date_issued_padrao_none(self, app, sample_book):
        copy = Copy(date_added=datetime.now(), book=sample_book.id)
        db.session.add(copy)
        db.session.commit()
        assert copy.date_issued is None

    def test_copy_referencia_livro_correto(self, app, sample_book):
        copy = Copy(date_added=datetime.now(), book=sample_book.id)
        db.session.add(copy)
        db.session.commit()
        assert copy.book == sample_book.id
