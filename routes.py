from decimal import Decimal

from flask import (
    render_template,
    session,
    redirect,
    url_for,
    request,
)

from sqlalchemy import select

from werkzeug.security import (
    generate_password_hash,
    check_password_hash,
)

from app import db
from models import Cliente, Produto, Pedido, ItemPedido


def registrar_rotas(app):

    # =========================
    # CLIENTE LOGADO
    # DISPONÍVEL NOS TEMPLATES
    # =========================

    @app.context_processor
    def disponibilizar_cliente_logado():
        cliente_id = session.get("cliente_id")

        cliente = None

        if cliente_id is not None:
            cliente = db.session.get(
                Cliente,
                cliente_id,
            )

        return {
            "cliente_logado": cliente
        }

    # =========================
    # CATÁLOGO
    # =========================

    @app.route("/")
    def catalogo():

        produtos = db.session.scalars(
            select(Produto).order_by(
                Produto.nome
            )
        ).all()

        erro = session.pop(
            "erro_catalogo",
            None,
        )

        return render_template(
            "catalogo.html",
            produtos=produtos,
            erro=erro,
        )

    # =========================
    # ADICIONAR AO CARRINHO
    # =========================

    @app.post(
        "/carrinho/adicionar/<int:produto_id>"
    )
    def adicionar_carrinho(produto_id):

        produto = db.session.get(
            Produto,
            produto_id,
        )

        if produto is None:

            session["erro_catalogo"] = (
                "Produto não encontrado."
            )

            return redirect(
                url_for("catalogo")
            )

        try:
            quantidade = int(
                request.form.get(
                    "quantidade",
                    1,
                )
            )

        except ValueError:
            quantidade = 1

        if quantidade < 1:

            session["erro_catalogo"] = (
                "A quantidade deve ser maior que zero."
            )

            return redirect(
                url_for("catalogo")
            )

        carrinho = session.get(
            "carrinho",
            {},
        )

        quantidade_atual = carrinho.get(
            str(produto_id),
            0,
        )

        nova_quantidade = (
            quantidade_atual
            + quantidade
        )

        # O estoque será validado
        # somente no checkout.
        carrinho[str(produto_id)] = (
            nova_quantidade
        )

        session["carrinho"] = carrinho

        return redirect(
            url_for("catalogo")
        )

    # =========================
    # CARRINHO
    # =========================

    @app.route("/carrinho")
    def carrinho():

        carrinho_sessao = session.get(
            "carrinho",
            {},
        )

        itens = []
        total = Decimal("0.00")

        for (
            produto_id,
            quantidade,
        ) in carrinho_sessao.items():

            produto = db.session.get(
                Produto,
                int(produto_id),
            )

            if produto is None:
                continue

            subtotal = (
                produto.preco
                * quantidade
            )

            itens.append(
                {
                    "produto": produto,
                    "quantidade": quantidade,
                    "subtotal": subtotal,
                }
            )

            total += subtotal

        return render_template(
            "carrinho.html",
            itens=itens,
            total=total,
        )

    # =========================
    # REMOVER DO CARRINHO
    # =========================

    @app.post(
        "/carrinho/remover/<int:produto_id>"
    )
    def remover_carrinho(produto_id):

        carrinho = session.get(
            "carrinho",
            {},
        )

        carrinho.pop(
            str(produto_id),
            None,
        )

        session["carrinho"] = carrinho

        return redirect(
            url_for("carrinho")
        )

    # =========================
    # CHECKOUT
    # =========================

    @app.route(
        "/checkout",
        methods=["GET", "POST"],
    )
    def checkout():

        carrinho_sessao = session.get(
            "carrinho",
            {},
        )

        if not carrinho_sessao:

            return redirect(
                url_for("carrinho")
            )

        erro = None

        # =========================
        # VERIFICAR LOGIN
        # =========================

        cliente_id = session.get(
            "cliente_id"
        )

        cliente_atual = None

        if cliente_id is not None:

            cliente_atual = db.session.get(
                Cliente,
                cliente_id,
            )

            # Caso a sessão tenha um ID inválido
            if cliente_atual is None:

                session.pop(
                    "cliente_id",
                    None,
                )

        # =========================
        # CONFIRMAR PEDIDO
        # =========================

        if request.method == "POST":

            # =========================
            # CLIENTE LOGADO
            # =========================

            if cliente_atual is not None:

                cliente = cliente_atual

            # =========================
            # CLIENTE NÃO LOGADO
            # =========================

            else:

                nome = request.form.get(
                    "nome",
                    "",
                ).strip()

                email = request.form.get(
                    "email",
                    "",
                ).strip().lower()

                senha = request.form.get(
                    "senha",
                    "",
                )

                if (
                    not nome
                    or not email
                    or not senha
                ):

                    erro = (
                        "Preencha todos os campos."
                    )

                elif len(senha) < 6:

                    erro = (
                        "A senha deve possuir "
                        "pelo menos 6 caracteres."
                    )

                # =========================
                # BUSCAR CLIENTE
                # =========================

                if erro is None:

                    cliente = db.session.scalar(
                        select(Cliente).where(
                            Cliente.email == email
                        )
                    )

                    # Cliente já cadastrado
                    if cliente is not None:

                        if not check_password_hash(
                            cliente.senha_hash,
                            senha,
                        ):

                            erro = (
                                "Senha incorreta "
                                "para este e-mail."
                            )

                    # Cliente novo
                    else:

                        cliente = Cliente(
                            nome=nome,
                            email=email,
                            senha_hash=(
                                generate_password_hash(
                                    senha
                                )
                            ),
                        )

                        db.session.add(
                            cliente
                        )

            # =========================
            # CRIAR PEDIDO
            # =========================

            if erro is None:

                try:

                    db.session.flush()

                    pedido = Pedido(
                        cliente=cliente,
                        status="CRIADO",
                        total=Decimal("0.00"),
                    )

                    db.session.add(
                        pedido
                    )

                    total_pedido = Decimal(
                        "0.00"
                    )

                    # =========================
                    # ITENS DO CARRINHO
                    # =========================

                    for (
                        produto_id,
                        quantidade,
                    ) in carrinho_sessao.items():

                        produto = db.session.get(
                            Produto,
                            int(produto_id),
                        )

                        # =========================
                        # PRODUTO EXISTE?
                        # =========================

                        if produto is None:

                            raise ValueError(
                                "Produto inexistente."
                            )

                        # =========================
                        # VALIDAR ESTOQUE
                        # =========================

                        if (
                            produto.estoque
                            < quantidade
                        ):

                            raise ValueError(
                                f"Estoque insuficiente "
                                f"para {produto.nome}."
                            )

                        # =========================
                        # DIMINUIR ESTOQUE
                        # =========================

                        produto.estoque -= (
                            quantidade
                        )

                        # =========================
                        # SUBTOTAL
                        # =========================

                        subtotal = (
                            produto.preco
                            * quantidade
                        )

                        total_pedido += (
                            subtotal
                        )

                        # =========================
                        # ITEM DO PEDIDO
                        # =========================

                        item = ItemPedido(
                            pedido=pedido,
                            produto=produto,
                            quantidade=quantidade,
                            preco_unitario=(
                                produto.preco
                            ),
                        )

                        db.session.add(
                            item
                        )

                    # =========================
                    # TOTAL DO PEDIDO
                    # =========================

                    pedido.total = (
                        total_pedido
                    )

                    # =========================
                    # COMMIT
                    # =========================

                    db.session.commit()

                    # Limpar carrinho
                    session.pop(
                        "carrinho",
                        None,
                    )

                    # Cliente permanece logado
                    session["cliente_id"] = (
                        cliente.id
                    )

                    return render_template(
                        "checkout_sucesso.html",
                        pedido=pedido,
                    )

                # =========================
                # ROLLBACK
                # =========================

                except ValueError as e:

                    db.session.rollback()

                    erro = str(e)

                except Exception:

                    db.session.rollback()

                    erro = (
                        "Não foi possível "
                        "finalizar o pedido. "
                        "Tente novamente."
                    )

        return render_template(
            "checkout.html",
            erro=erro,
            cliente_logado=cliente_atual,
        )

    # =========================
    # LOGIN
    # =========================

    @app.route(
        "/login",
        methods=["GET", "POST"],
    )
    def login():

        # Pode ser:
        # ""
        # ou "checkout"
        proximo = request.values.get(
            "proximo",
            "",
        )

        # Só aceitamos o destino checkout
        if proximo != "checkout":
            proximo = ""

        # =========================
        # JÁ ESTÁ LOGADO
        # =========================

        if (
            session.get("cliente_id")
            is not None
        ):

            if proximo == "checkout":

                return redirect(
                    url_for("checkout")
                )

            return redirect(
                url_for("meus_pedidos")
            )

        erro = None

        # =========================
        # ENVIAR LOGIN
        # =========================

        if request.method == "POST":

            email = request.form.get(
                "email",
                "",
            ).strip().lower()

            senha = request.form.get(
                "senha",
                "",
            )

            proximo = request.form.get(
                "proximo",
                "",
            )

            if proximo != "checkout":
                proximo = ""

            if not email or not senha:

                erro = (
                    "Preencha e-mail e senha."
                )

            else:

                cliente = db.session.scalar(
                    select(Cliente).where(
                        Cliente.email == email
                    )
                )

                # =========================
                # LOGIN INVÁLIDO
                # =========================

                if cliente is None:

                    erro = (
                        "E-mail ou senha inválidos."
                    )

                elif not check_password_hash(
                    cliente.senha_hash,
                    senha,
                ):

                    erro = (
                        "E-mail ou senha inválidos."
                    )

                # =========================
                # LOGIN CORRETO
                # =========================

                else:

                    session["cliente_id"] = (
                        cliente.id
                    )

                    # Se entrou pelo checkout,
                    # retorna ao checkout.
                    if proximo == "checkout":

                        return redirect(
                            url_for("checkout")
                        )

                    # Login normal
                    return redirect(
                        url_for("meus_pedidos")
                    )

        return render_template(
            "login.html",
            erro=erro,
            proximo=proximo,
        )

    # =========================
    # LOGOUT
    # =========================

    @app.post("/logout")
    def logout():

        session.pop(
            "cliente_id",
            None,
        )

        return redirect(
            url_for("catalogo")
        )

    # =========================
    # MEUS PEDIDOS
    # =========================

    @app.route("/meus-pedidos")
    def meus_pedidos():

        cliente_id = session.get(
            "cliente_id"
        )

        # Não está logado
        if cliente_id is None:

            return redirect(
                url_for("login")
            )

        cliente = db.session.get(
            Cliente,
            cliente_id,
        )

        # Sessão inválida
        if cliente is None:

            session.pop(
                "cliente_id",
                None,
            )

            return redirect(
                url_for("login")
            )

        # =========================
        # PEDIDOS DO CLIENTE LOGADO
        # =========================

        pedidos = db.session.scalars(
            select(Pedido)
            .where(
                Pedido.cliente_id
                == cliente_id
            )
            .order_by(
                Pedido.criado_em.desc()
            )
        ).all()

        return render_template(
            "meus_pedidos.html",
            cliente=cliente,
            pedidos=pedidos,
        )