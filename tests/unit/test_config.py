"""
Testes unitários para as classes de configuração do projeto.

Verificam que cada configuração (Test, Production, Development)
tem os valores corretos sem precisar inicializar a aplicação Flask.
"""

from config import Config, DevelopmentConfig, ProductionConfig, StagingConfig, TestConfig


class TestConfigBase:
    def test_csrf_habilitado_por_padrao(self):
        assert Config.CSRF_ENABLED is True

    def test_testing_desabilitado_por_padrao(self):
        assert Config.TESTING is False

    def test_secret_key_existe(self):
        assert Config.SECRET_KEY is not None


class TestTestConfig:
    def test_testing_habilitado(self):
        assert TestConfig.TESTING is True

    def test_debug_habilitado(self):
        assert TestConfig.DEBUG is True

    def test_banco_de_dados_e_sqlite_em_memoria(self):
        assert TestConfig.SQLALCHEMY_DATABASE_URI == "sqlite:///:memory:"

    def test_csrf_desabilitado_para_testes(self):
        assert TestConfig.WTF_CSRF_ENABLED is False


class TestProductionConfig:
    def test_debug_desabilitado(self):
        assert ProductionConfig.DEBUG is False

    def test_testing_desabilitado(self):
        assert ProductionConfig.TESTING is False


class TestDevelopmentConfig:
    def test_debug_habilitado(self):
        assert DevelopmentConfig.DEBUG is True

    def test_development_habilitado(self):
        assert DevelopmentConfig.DEVELOPMENT is True


class TestStagingConfig:
    def test_debug_habilitado(self):
        assert StagingConfig.DEBUG is True

    def test_development_habilitado(self):
        assert StagingConfig.DEVELOPMENT is True
