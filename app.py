from decimal import Decimal

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

from config import Config


db = SQLAlchemy()


def create_app():
    app = Flask(__name__)

    # =========================
    # CONFIGURAÇÃO
    # =========================

    app.config.from_object(Config)

    db.init_app(app)

    # Importar modelos somente depois
    # da criação do objeto db
    from models import (
        Cliente,
        Categoria,
        Produto,
        Pedido,
        ItemPedido,
    )

    from routes import registrar_rotas

    registrar_rotas(app)

    # =========================
    # INICIALIZAR BANCO
    # =========================

    @app.cli.command("init-db")
    def init_db():
        db.create_all()

        # Só insere os dados iniciais
        # se não existir nenhuma categoria
        if Categoria.query.first() is None:

            tecnologia = Categoria(
                nome="Tecnologia"
            )

            db.session.add(tecnologia)

            # Gera o ID da categoria
            # antes do commit
            db.session.flush()

            produtos = [
                Produto(
                    nome="Teclado Mecânico",
                    descricao="Switches táteis",
                    preco=Decimal("299.90"),
                    estoque=20,
                    categoria_id=tecnologia.id,
                ),

                Produto(
                    nome="Mouse Sem Fio",
                    descricao="Sensor óptico",
                    preco=Decimal("149.90"),
                    estoque=35,
                    categoria_id=tecnologia.id,
                ),

                Produto(
                    nome="Monitor 24 polegadas",
                    descricao="Painel IPS",
                    preco=Decimal("999.00"),
                    estoque=12,
                    categoria_id=tecnologia.id,
                ),
            ]

            db.session.add_all(
                produtos
            )

        db.session.commit()

        print(
            "Banco de dados inicializado com sucesso!"
        )

    # =========================
    # TESTE DO BANCO
    # =========================

    @app.route("/teste-banco")
    def teste_banco():

        try:

            db.session.execute(
                text("SELECT 1")
            )

            return (
                "Conexão com PostgreSQL funcionando!",
                200,
            )

        except Exception:

            db.session.rollback()

            return (
                "Erro ao conectar com PostgreSQL.",
                500,
            )

    return app


# =========================
# CRIAR A APLICAÇÃO
# =========================

app = create_app()