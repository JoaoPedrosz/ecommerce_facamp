from app import db


class Categoria(db.Model):
    __tablename__ = "categorias"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    nome = db.Column(
        db.String(80),
        nullable=False,
        unique=True,
    )

    produtos = db.relationship(
        "Produto",
        back_populates="categoria",
    )


class Cliente(db.Model):
    __tablename__ = "clientes"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    nome = db.Column(
        db.String(120),
        nullable=False,
    )

    email = db.Column(
        db.String(160),
        nullable=False,
        unique=True,
    )

    senha_hash = db.Column(
        db.String(255),
        nullable=False,
    )

    pedidos = db.relationship(
        "Pedido",
        back_populates="cliente",
    )


class Produto(db.Model):
    __tablename__ = "produtos"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    nome = db.Column(
        db.String(140),
        nullable=False,
    )

    descricao = db.Column(
        db.Text,
    )

    preco = db.Column(
        db.Numeric(10, 2),
        nullable=False,
    )

    estoque = db.Column(
        db.Integer,
        nullable=False,
        server_default=db.text("0"),
    )

    categoria_id = db.Column(
        db.Integer,
        db.ForeignKey("categorias.id"),
        nullable=False,
    )

    categoria = db.relationship(
        "Categoria",
        back_populates="produtos",
    )

    itens_pedido = db.relationship(
        "ItemPedido",
        back_populates="produto",
    )

    __table_args__ = (
        db.CheckConstraint(
            "preco >= 0"
        ),
        db.CheckConstraint(
            "estoque >= 0"
        ),
        db.Index(
            "idx_produtos_nome",
            "nome",
        ),
    )


class Pedido(db.Model):
    __tablename__ = "pedidos"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    status = db.Column(
        db.String(30),
        nullable=False,
        server_default=db.text(
            "'CRIADO'"
        ),
    )

    total = db.Column(
        db.Numeric(10, 2),
        nullable=False,
        server_default=db.text("0"),
    )

    cliente_id = db.Column(
        db.Integer,
        db.ForeignKey("clientes.id"),
        nullable=False,
    )

    criado_em = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=db.func.now(),
    )

    cliente = db.relationship(
        "Cliente",
        back_populates="pedidos",
    )

    itens = db.relationship(
        "ItemPedido",
        back_populates="pedido",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    __table_args__ = (
        db.Index(
            "idx_pedidos_cliente",
            "cliente_id",
        ),
    )


class ItemPedido(db.Model):
    __tablename__ = "itens_pedido"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    quantidade = db.Column(
        db.Integer,
        nullable=False,
    )

    preco_unitario = db.Column(
        db.Numeric(10, 2),
        nullable=False,
    )

    pedido_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "pedidos.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    produto_id = db.Column(
        db.Integer,
        db.ForeignKey("produtos.id"),
        nullable=False,
    )

    pedido = db.relationship(
        "Pedido",
        back_populates="itens",
    )

    produto = db.relationship(
        "Produto",
        back_populates="itens_pedido",
    )

    __table_args__ = (
        db.CheckConstraint(
            "quantidade > 0"
        ),
        db.Index(
            "idx_itens_pedido",
            "pedido_id",
        ),
    )