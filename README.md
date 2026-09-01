# 🛒 E-commerce FACAMP — Flask + PostgreSQL

Projeto de e-commerce desenvolvido para a disciplina de TAI da FACAMP.

A aplicação foi construída utilizando Python, Flask, SQLAlchemy e PostgreSQL e demonstra o ciclo completo entre aplicação e banco de dados, incluindo:

- catálogo de produtos;
- carrinho de compras;
- cadastro de clientes;
- autenticação;
- criação de pedidos;
- itens de pedido;
- atualização de estoque;
- histórico de pedidos;
- transações com COMMIT e ROLLBACK;
- constraints e índices no PostgreSQL;
- configuração segura por variáveis de ambiente.

---

# 📌 Objetivo do projeto

O objetivo é desenvolver uma aplicação de e-commerce integrada a um banco de dados PostgreSQL, aplicando conceitos de:

- modelagem de dados;
- banco de dados relacional;
- integridade referencial;
- SQL;
- ORM;
- aplicações web com Flask;
- transações;
- controle de estoque;
- autenticação;
- segurança básica;
- testes;
- versionamento com Git/GitHub;
- deploy em cloud.

O projeto utiliza a seguinte arquitetura:

```text
Navegador
    ↓
Flask
    ↓
SQLAlchemy
    ↓
psycopg
    ↓
PostgreSQL
```

---

# 🛠 Tecnologias utilizadas

## Back-end

- Python
- Flask
- Flask-SQLAlchemy
- SQLAlchemy
- Psycopg

## Banco de dados

- PostgreSQL
- pgAdmin

## Front-end

- HTML5
- CSS3
- Jinja2

## Versionamento e deploy

- Git
- GitHub
- GitHub Desktop
- Gunicorn
- Render

---

# 📋 Requisitos funcionais

Os requisitos funcionais implementados são:

| ID | Requisito | Situação |
|---|---|---|
| RF01 | Listar produtos disponíveis | ✅ Implementado |
| RF02 | Adicionar produto ao carrinho | ✅ Implementado |
| RF03 | Visualizar carrinho e total | ✅ Implementado |
| RF04 | Finalizar pedido | ✅ Implementado |
| RF05 | Atualizar estoque | ✅ Implementado |
| RF06 | Registrar cliente e histórico de pedidos | ✅ Implementado |

---

# 🔒 Requisitos não funcionais

## Integridade

O banco impede estados inválidos por meio de constraints.

Exemplos:

- preço não pode ser negativo;
- estoque não pode ser negativo;
- quantidade de um item deve ser maior que zero;
- produto deve possuir categoria;
- pedido deve possuir cliente;
- item deve possuir pedido e produto;
- e-mail de cliente deve ser único;
- nome de categoria deve ser único.

## Segurança

As seguintes práticas foram adotadas:

- senhas não são armazenadas em texto puro;
- senhas são armazenadas utilizando hash;
- credenciais do PostgreSQL não ficam no código;
- `DATABASE_URL` é utilizada como variável de ambiente;
- `SECRET_KEY` é utilizada como variável de ambiente;
- `.env` é ignorado pelo Git;
- `.env.example` contém somente valores de exemplo;
- erros de conexão não exibem a string de conexão para o usuário.

## Desempenho

Foram criados índices para consultas utilizadas frequentemente:

- produtos por nome;
- pedidos por cliente;
- itens por pedido.

## Manutenibilidade

A aplicação foi dividida entre:

- configuração;
- modelos;
- rotas;
- templates;
- arquivos estáticos;
- banco de dados.

## Portabilidade

A configuração por `DATABASE_URL` permite utilizar PostgreSQL localmente ou em um provedor cloud sem alterar o código principal da aplicação.

---

# 🗃 Modelagem do banco de dados

O projeto possui cinco entidades persistentes principais:

```text
Cliente
Categoria
Produto
Pedido
ItemPedido
```

O carrinho não é armazenado como uma tabela.

Ele é mantido temporariamente na sessão do Flask.

---

# 🔗 Relacionamentos

```text
Categoria 1 ───── N Produto

Cliente   1 ───── N Pedido

Pedido    1 ───── N ItemPedido

Produto   1 ───── N ItemPedido
```

Em outras palavras:

- uma categoria pode possuir vários produtos;
- cada produto pertence a uma categoria;
- um cliente pode realizar vários pedidos;
- cada pedido pertence a um cliente;
- um pedido pode conter vários itens;
- cada item pertence a um pedido;
- um produto pode aparecer em vários itens de pedidos.

---

# 🧱 Estrutura física do banco

## Tabela `categorias`

```sql
CREATE TABLE categorias (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(80) NOT NULL UNIQUE
);
```

## Tabela `clientes`

```sql
CREATE TABLE clientes (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(120) NOT NULL,
    email VARCHAR(160) NOT NULL UNIQUE,
    senha_hash VARCHAR(255) NOT NULL
);
```

## Tabela `produtos`

```sql
CREATE TABLE produtos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(140) NOT NULL,
    descricao TEXT,
    preco NUMERIC(10,2) NOT NULL CHECK (preco >= 0),
    estoque INTEGER NOT NULL DEFAULT 0 CHECK (estoque >= 0),
    categoria_id INTEGER NOT NULL REFERENCES categorias(id)
);
```

## Tabela `pedidos`

```sql
CREATE TABLE pedidos (
    id SERIAL PRIMARY KEY,
    status VARCHAR(30) NOT NULL DEFAULT 'CRIADO',
    total NUMERIC(10,2) NOT NULL DEFAULT 0,
    cliente_id INTEGER NOT NULL REFERENCES clientes(id),
    criado_em TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

## Tabela `itens_pedido`

```sql
CREATE TABLE itens_pedido (
    id SERIAL PRIMARY KEY,
    quantidade INTEGER NOT NULL CHECK (quantidade > 0),
    preco_unitario NUMERIC(10,2) NOT NULL,
    pedido_id INTEGER NOT NULL
        REFERENCES pedidos(id)
        ON DELETE CASCADE,
    produto_id INTEGER NOT NULL
        REFERENCES produtos(id)
);
```

---

# 🛡 Constraints utilizadas

O banco utiliza diferentes tipos de constraints para manter a integridade dos dados.

## PRIMARY KEY

Identifica unicamente cada registro.

Exemplo:

```sql
id SERIAL PRIMARY KEY
```

## FOREIGN KEY

Mantém os relacionamentos entre as tabelas.

Exemplo:

```sql
cliente_id INTEGER NOT NULL
    REFERENCES clientes(id)
```

## UNIQUE

Evita valores duplicados.

Utilizado em:

```text
clientes.email
categorias.nome
```

## NOT NULL

Impede que informações obrigatórias sejam gravadas sem valor.

## CHECK

Impede valores inválidos.

Exemplos:

```sql
CHECK (preco >= 0)
CHECK (estoque >= 0)
CHECK (quantidade > 0)
```

## ON DELETE CASCADE

Os itens de um pedido estão relacionados ao pedido utilizando:

```sql
ON DELETE CASCADE
```

Assim, caso um pedido seja removido diretamente do banco, seus itens associados também são removidos.

---

# ⚡ Índices

Foram criados os seguintes índices:

```sql
CREATE INDEX idx_produtos_nome
ON produtos(nome);
```

Utilizado para facilitar busca e ordenação dos produtos.

```sql
CREATE INDEX idx_pedidos_cliente
ON pedidos(cliente_id);
```

Utilizado principalmente no histórico de pedidos do cliente.

```sql
CREATE INDEX idx_itens_pedido
ON itens_pedido(pedido_id);
```

Utilizado para localizar rapidamente os itens pertencentes a determinado pedido.

Além desses índices, o PostgreSQL cria índices automaticamente para os campos definidos como `UNIQUE`, como:

```text
clientes.email
categorias.nome
```

---

# 🌱 Dados iniciais

Durante a inicialização do banco é criada a categoria:

```text
Tecnologia
```

E três produtos iniciais:

| Produto | Descrição | Preço | Estoque |
|---|---|---:|---:|
| Teclado Mecânico | Switches táteis | R$ 299,90 | 20 |
| Mouse Sem Fio | Sensor óptico | R$ 149,90 | 35 |
| Monitor 24 polegadas | Painel IPS | R$ 999,00 | 12 |

Os valores monetários são manipulados no Python utilizando `Decimal`, evitando o uso de `float` para dinheiro.

---

# 🏗 Estrutura do projeto

```text
ecommerce_facamp/
│
├── SQL/
│   └── schema.sql
│
├── static/
│   └── style.css
│
├── templates/
│   ├── admin/
│   │   ├── produto_form.html
│   │   └── produtos.html
│   │
│   ├── base.html
│   ├── carrinho.html
│   ├── catalogo.html
│   ├── checkout.html
│   ├── checkout_sucesso.html
│   ├── login.html
│   └── meus_pedidos.html
│
├── .env.example
├── .gitattributes
├── .gitignore
├── .python-version
│
├── app.py
├── config.py
├── models.py
├── routes.py
│
├── requirements.txt
├── Procfile
├── render.yaml
└── README.md
```

---

# 📂 Responsabilidade dos arquivos

## `app.py`

Responsável por:

- criar a aplicação Flask;
- inicializar o SQLAlchemy;
- carregar as configurações;
- registrar as rotas;
- disponibilizar o comando `init-db`;
- testar a conexão com PostgreSQL.

---

## `config.py`

Responsável pela configuração da aplicação.

As informações sensíveis são carregadas pelas variáveis:

```text
DATABASE_URL
SECRET_KEY
```

Nenhuma senha do PostgreSQL é escrita diretamente no arquivo.

---

## `models.py`

Contém o mapeamento ORM das tabelas PostgreSQL:

```text
Categoria
Cliente
Produto
Pedido
ItemPedido
```

Também contém:

- relacionamentos;
- constraints;
- índices;
- valores padrão do banco.

---

## `routes.py`

Contém a lógica da aplicação, incluindo:

- catálogo;
- carrinho;
- remoção do carrinho;
- checkout;
- criação de cliente;
- login;
- logout;
- histórico de pedidos;
- controle de sessão;
- validação de estoque;
- transação de compra.

---

## `templates/`

Contém as páginas HTML renderizadas pelo Flask utilizando Jinja2.

---

## `static/style.css`

Contém a estilização visual da aplicação.

---

## `SQL/schema.sql`

Contém o script SQL utilizado para representar e criar a estrutura física do banco de dados.

---

# 🛍 Fluxo da aplicação

## 1. Catálogo

A rota principal:

```text
/
```

consulta os produtos cadastrados e os exibe no catálogo.

São apresentados:

- nome;
- descrição;
- categoria;
- preço;
- quantidade em estoque.

O usuário pode escolher a quantidade e adicionar o produto ao carrinho.

---

# 🛒 Carrinho

O carrinho é mantido na sessão Flask.

Exemplo conceitual:

```python
{
    "1": 2,
    "3": 1
}
```

Isso representa:

```text
Produto 1 → quantidade 2
Produto 3 → quantidade 1
```

O carrinho não é persistido em uma tabela PostgreSQL.

A página calcula:

```text
subtotal = preço × quantidade
```

e:

```text
total = soma dos subtotais
```

Também é possível remover um produto do carrinho antes da finalização.

---

# 👤 Cliente

Durante o primeiro checkout, caso o cliente ainda não exista, são solicitados:

```text
nome
e-mail
senha
```

O e-mail é convertido para letras minúsculas antes da consulta.

O banco possui:

```sql
UNIQUE(email)
```

evitando clientes duplicados com o mesmo e-mail.

---

# 🔐 Armazenamento da senha

A aplicação não armazena a senha original.

É utilizado:

```python
generate_password_hash()
```

para criar o hash.

Para verificar a senha durante o login é utilizado:

```python
check_password_hash()
```

Dessa forma, a coluna:

```text
senha_hash
```

armazena somente o resultado do hash.

---

# 🔑 Login

A aplicação possui uma página de login em:

```text
/login
```

O usuário informa:

```text
e-mail
senha
```

O sistema procura o cliente pelo e-mail e verifica o hash da senha.

Se os dados forem válidos, o identificador do cliente é armazenado na sessão:

```python
session["cliente_id"]
```

---

# 🚪 Logout

O logout remove o identificador do cliente da sessão:

```python
session.pop("cliente_id", None)
```

Depois disso o usuário deixa de estar autenticado.

---

# 🧾 Meus pedidos

Clientes autenticados podem acessar:

```text
/meus-pedidos
```

A consulta utiliza o identificador da sessão para retornar somente os pedidos pertencentes ao cliente atualmente autenticado.

Os pedidos são exibidos do mais recente para o mais antigo.

---

# 🔄 Login durante o checkout

Caso o usuário chegue ao checkout sem estar autenticado, ele pode:

```text
criar uma nova conta
```

ou:

```text
entrar em uma conta existente
```

Ao selecionar a opção de login pelo checkout, a aplicação utiliza:

```text
proximo=checkout
```

Após autenticação bem-sucedida, o cliente retorna para o checkout.

O login não cria automaticamente um pedido.

O pedido somente é criado quando o usuário confirma o checkout.

---

# 💳 Checkout

O checkout é uma das partes mais importantes do projeto.

O fluxo é:

```text
Carrinho
   ↓
Identificar/Cadastrar cliente
   ↓
Criar pedido
   ↓
Validar produtos
   ↓
Validar estoque
   ↓
Criar ItemPedido
   ↓
Reduzir estoque
   ↓
Calcular total
   ↓
COMMIT
```

---

# 🔄 Transação e atomicidade

A criação do pedido é realizada como uma única unidade lógica.

Dentro da mesma transação são realizadas as operações:

```text
1. identificação/criação do cliente;
2. criação do pedido;
3. consulta dos produtos;
4. validação do estoque;
5. redução do estoque;
6. criação dos itens do pedido;
7. cálculo do valor total;
8. persistência das alterações.
```

Somente se todas as etapas forem concluídas corretamente é executado:

```python
db.session.commit()
```

---

# ↩️ ROLLBACK

Caso qualquer erro aconteça durante a criação do pedido é executado:

```python
db.session.rollback()
```

Isso evita que apenas uma parte da operação seja gravada.

Por exemplo:

```text
Produto A possui estoque suficiente
Produto B não possui estoque suficiente
```

Mesmo que o Produto A já tenha sido processado no código, se o Produto B causar uma falha antes do `commit`, toda a transação é desfeita.

Assim:

```text
pedido não é criado;
itens não são persistidos;
estoque não fica parcialmente alterado.
```

---

# 📦 Validação de estoque

Antes de reduzir a quantidade de um produto, a aplicação verifica:

```python
if produto.estoque < quantidade:
```

Caso não exista estoque suficiente:

```text
Estoque insuficiente para <produto>.
```

é informado ao usuário.

Nenhuma alteração referente ao pedido é confirmada no banco.

---

# 💰 Valores monetários

No PostgreSQL, valores monetários são armazenados utilizando:

```sql
NUMERIC(10,2)
```

No Python é utilizado:

```python
Decimal
```

Exemplo:

```python
Decimal("299.90")
```

Isso evita problemas de precisão associados ao tipo `float`.

---

# 🧪 Teste da conexão com o banco

Existe a rota:

```text
/teste-banco
```

Ela executa:

```sql
SELECT 1
```

Quando a conexão funciona, retorna:

```text
Conexão com PostgreSQL funcionando!
```

Caso exista uma falha:

```text
Erro ao conectar com PostgreSQL.
```

O erro completo do driver não é exibido ao usuário para evitar exposição de informações da conexão.

---

# 🧪 Testes realizados

## Catálogo

Verificado se os produtos cadastrados aparecem contendo:

- nome;
- descrição;
- preço;
- estoque;
- categoria.

Resultado:

```text
✅ Funcionando
```

---

## Carrinho

Foram adicionados produtos com diferentes quantidades.

Foram verificados:

- quantidade;
- preço unitário;
- subtotal;
- total.

Resultado:

```text
✅ Funcionando
```

---

## Remoção do carrinho

Foi implementada opção de remover um produto antes da compra.

Resultado:

```text
✅ Funcionando
```

---

## Checkout

Foi realizado pedido completo e verificada a criação dos registros no PostgreSQL.

Resultado:

```text
✅ Funcionando
```

---

## Atualização do estoque

Após a confirmação de uma compra, a quantidade comprada é subtraída do estoque.

Resultado:

```text
✅ Funcionando
```

---

## Estoque insuficiente

Foi testada uma quantidade maior do que a disponível.

Exemplo:

```text
Estoque disponível: 12
Quantidade solicitada: maior que 12
```

A aplicação retorna erro de estoque insuficiente.

A transação sofre `ROLLBACK`.

Resultado:

```text
✅ Funcionando
```

---

## Cadastro de cliente

Ao realizar a primeira compra com um novo e-mail, o cliente é cadastrado.

A senha é armazenada utilizando hash.

Resultado:

```text
✅ Funcionando
```

---

## Cliente existente

Ao utilizar um e-mail já cadastrado, a aplicação verifica a senha correspondente.

Uma senha incorreta impede a operação.

Resultado:

```text
✅ Funcionando
```

---

## Login

Login com cliente existente foi implementado utilizando e-mail e senha.

Resultado:

```text
✅ Funcionando
```

---

## Logout

O cliente pode encerrar a sessão.

Resultado:

```text
✅ Funcionando
```

---

## Histórico

A página `Meus Pedidos` apresenta apenas os pedidos do cliente autenticado.

Resultado:

```text
✅ Funcionando
```

---

# 🔎 Consultas SQL para validação

## Visualizar pedidos

```sql
SELECT *
FROM pedidos
ORDER BY id DESC;
```

---

## Pedido e cliente

```sql
SELECT
    p.id,
    c.nome,
    p.status,
    p.total
FROM pedidos p
JOIN clientes c
    ON c.id = p.cliente_id;
```

---

## Itens do pedido

```sql
SELECT
    ip.pedido_id,
    pr.nome,
    ip.quantidade,
    ip.preco_unitario
FROM itens_pedido ip
JOIN produtos pr
    ON pr.id = ip.produto_id;
```

---

## Consulta completa

```sql
SELECT
    p.id AS pedido_id,
    c.nome AS cliente,
    pr.nome AS produto,
    ip.quantidade,
    ip.preco_unitario,
    p.total,
    p.status,
    p.criado_em
FROM pedidos p
JOIN clientes c
    ON c.id = p.cliente_id
JOIN itens_pedido ip
    ON ip.pedido_id = p.id
JOIN produtos pr
    ON pr.id = ip.produto_id
ORDER BY p.id DESC;
```

---

# 🔍 Verificação dos valores DEFAULT

Foi verificado diretamente no catálogo do PostgreSQL se os valores padrão estavam corretamente configurados.

Consulta utilizada:

```sql
SELECT
    table_name,
    column_name,
    column_default
FROM information_schema.columns
WHERE table_schema = 'public'
AND (
    (
        table_name = 'produtos'
        AND column_name = 'estoque'
    )
    OR
    (
        table_name = 'pedidos'
        AND column_name IN (
            'status',
            'total',
            'criado_em'
        )
    )
)
ORDER BY
    table_name,
    column_name;
```

Resultado esperado e obtido:

```text
pedidos.criado_em → now()
pedidos.status     → 'CRIADO'
pedidos.total      → 0
produtos.estoque   → 0
```

Durante a validação foi identificado que alguns `DEFAULT`s ainda não estavam configurados fisicamente no PostgreSQL.

Foram corrigidos com:

```sql
ALTER TABLE produtos
ALTER COLUMN estoque
SET DEFAULT 0;
```

```sql
ALTER TABLE pedidos
ALTER COLUMN status
SET DEFAULT 'CRIADO';
```

```sql
ALTER TABLE pedidos
ALTER COLUMN total
SET DEFAULT 0;
```

Após a correção, os valores foram novamente consultados e validados.

---

# 🚀 Desafio de extensão escolhido

Foi escolhido o desafio:

## Desafio 2 — Autenticação e histórico do cliente

O MVP foi expandido para possuir:

- autenticação;
- login;
- logout;
- controle de sessão;
- senha armazenada em hash;
- e-mail único;
- identificação do cliente logado;
- página `Meus Pedidos`;
- histórico filtrado pelo cliente autenticado;
- integração entre login e checkout.

---

# 👤 Identificação do cliente autenticado

O cliente logado é identificado através de:

```python
session.get("cliente_id")
```

Um `context_processor` disponibiliza o cliente autenticado para os templates.

Isso permite apresentar no catálogo informações como:

```text
Olá, <nome do cliente>
Meus Pedidos
Sair
```

---

# 🔐 Proteção do histórico

A rota:

```text
/meus-pedidos
```

verifica primeiro se existe:

```python
session["cliente_id"]
```

Caso não exista, o usuário é redirecionado para:

```text
/login
```

Depois, os pedidos são consultados utilizando:

```text
Pedido.cliente_id == cliente_id
```

impedindo que o histórico geral seja apresentado.

---

# 🔧 Configuração do ambiente

## 1. Criar ambiente virtual

No Windows:

```powershell
python -m venv .venv
```

Ativar:

```powershell
.venv\Scripts\Activate.ps1
```

Caso o PowerShell bloqueie a execução do script, pode ser utilizada temporariamente:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

E depois:

```powershell
.venv\Scripts\Activate.ps1
```

---

# 📦 Instalação das dependências

Com o ambiente virtual ativado:

```powershell
pip install -r requirements.txt
```

Principais dependências utilizadas:

```text
Flask
Flask-SQLAlchemy
SQLAlchemy
psycopg
gunicorn
```

---

# 🐘 PostgreSQL local

Criar no PostgreSQL um banco chamado:

```text
ecommerce
```

Exemplo de configuração de desenvolvimento:

```text
Banco: ecommerce
SGBD: PostgreSQL
```

O banco pode ser administrado utilizando o pgAdmin.

---

# 🔑 Variáveis de ambiente

A aplicação necessita das seguintes variáveis:

```text
DATABASE_URL
SECRET_KEY
```

Exemplo de `DATABASE_URL`:

```text
postgresql+psycopg://usuario:senha@host:5432/ecommerce
```

A senha real não deve ser escrita no repositório.

---

# 📄 `.env.example`

O repositório possui o arquivo:

```text
.env.example
```

com:

```env
DATABASE_URL=postgresql+psycopg://usuario:senha@host:5432/ecommerce
SECRET_KEY=troque-esta-chave
```

Esse arquivo serve apenas como exemplo.

Nenhuma credencial real deve ser colocada nele.

---

# 🚫 `.gitignore`

O projeto utiliza `.gitignore` para impedir o versionamento de arquivos desnecessários ou sensíveis.

Exemplo:

```gitignore
# Ambiente virtual
.venv/

# Variáveis de ambiente / senhas
.env

# Cache do Python
__pycache__/
*.pyc

# VS Code
.vscode/

# Sistema
.DS_Store
Thumbs.db
```

---

# ⚙️ Inicialização do banco

Após configurar `DATABASE_URL`:

```powershell
flask --app app init-db
```

O comando utiliza:

```python
db.create_all()
```

e insere os dados iniciais caso a categoria inicial ainda não exista.

---

# ▶️ Executando localmente

Com o ambiente virtual ativado e as variáveis de ambiente configuradas:

```powershell
flask --app app run --debug
```

Depois abrir:

```text
http://127.0.0.1:5000
```

Para testar somente a conexão:

```text
http://127.0.0.1:5000/teste-banco
```

---

# 🌐 Principais rotas

| Rota | Método | Função |
|---|---|---|
| `/` | GET | Catálogo |
| `/carrinho` | GET | Visualizar carrinho |
| `/carrinho/adicionar/<produto_id>` | POST | Adicionar ao carrinho |
| `/carrinho/remover/<produto_id>` | POST | Remover do carrinho |
| `/checkout` | GET / POST | Finalizar pedido |
| `/login` | GET / POST | Autenticar cliente |
| `/logout` | POST | Encerrar sessão |
| `/meus-pedidos` | GET | Histórico do cliente |
| `/teste-banco` | GET | Testar conexão PostgreSQL |

---

# 🔒 Segurança do repositório

Antes da publicação no GitHub foram adotadas as seguintes medidas:

```text
✅ senha removida do código;
✅ DATABASE_URL configurada externamente;
✅ SECRET_KEY configurada externamente;
✅ .env ignorado;
✅ .venv ignorado;
✅ __pycache__ ignorado;
✅ .env.example sem credenciais reais;
✅ mensagens de erro não mostram string de conexão.
```

---

# 📤 Git e GitHub

O código será versionado em um repositório Git.

Arquivos sensíveis não devem ser enviados.

Antes do commit deve ser verificado se não aparecem:

```text
.env
.venv/
__pycache__/
```

Arquivos como estes podem ser versionados:

```text
.env.example
.gitignore
app.py
config.py
models.py
routes.py
requirements.txt
Procfile
render.yaml
SQL/schema.sql
static/
templates/
README.md
```

---

# 🚀 Preparação para deploy

Foram criados os arquivos necessários para preparar a aplicação para execução em produção.

## `Procfile`

```text
web: gunicorn app:app
```

O comando inicia a aplicação através do Gunicorn.

---

## `render.yaml`

Arquivo responsável pela definição do serviço web.

Exemplo:

```yaml
services:
  - type: web
    name: ecommerce-facamp
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app:app

    envVars:
      - key: DATABASE_URL
        sync: false

      - key: SECRET_KEY
        sync: false
```

Os valores reais de:

```text
DATABASE_URL
SECRET_KEY
```

não são incluídos nesse arquivo.

---

# ☁️ Estado do deploy

No momento desta documentação:

```text
Aplicação local          ✅
PostgreSQL local         ✅
Modelagem                ✅
DDL                       ✅
Constraints               ✅
Índices                   ✅
Catálogo                  ✅
Carrinho                  ✅
Checkout                  ✅
Controle de estoque       ✅
Transação / rollback      ✅
Cadastro de cliente       ✅
Hash de senha             ✅
Login                     ✅
Logout                    ✅
Histórico de pedidos      ✅
.env.example              ✅
.gitignore                ✅
Procfile                  ✅
render.yaml               ✅
GitHub                    ⏳ Em publicação
PostgreSQL cloud          ⏳ Pendente
Deploy web                ⏳ Pendente
Testes da aplicação cloud ⏳ Pendente
```

Esta seção deverá ser atualizada após a conclusão do deploy.

---

# 📈 Fluxo completo do sistema

```text
                ┌───────────────────┐
                │     Catálogo      │
                └─────────┬─────────┘
                          │
                          ▼
                ┌───────────────────┐
                │     Carrinho      │
                │  Sessão do Flask  │
                └─────────┬─────────┘
                          │
                          ▼
                ┌───────────────────┐
                │     Checkout      │
                └─────────┬─────────┘
                          │
                 Cliente autenticado?
                    │             │
                   SIM           NÃO
                    │             │
                    │       ┌─────▼─────┐
                    │       │Login ou   │
                    │       │Cadastro   │
                    │       └─────┬─────┘
                    │             │
                    └──────┬──────┘
                           │
                           ▼
                ┌───────────────────┐
                │ Criar Pedido      │
                └─────────┬─────────┘
                          │
                          ▼
                ┌───────────────────┐
                │ Validar estoque   │
                └─────────┬─────────┘
                          │
                    ┌─────┴──────┐
                    │            │
               Suficiente    Insuficiente
                    │            │
                    ▼            ▼
             Criar itens       ROLLBACK
                    │
                    ▼
             Reduzir estoque
                    │
                    ▼
             Calcular total
                    │
                    ▼
                  COMMIT
                    │
                    ▼
             Pedido concluído
```

---

# 📚 Conceitos aplicados

Durante o desenvolvimento foram aplicados os seguintes conceitos:

```text
Modelagem relacional
Chaves primárias
Chaves estrangeiras
Cardinalidade
Constraints
Índices
ORM
Sessões web
Hash de senha
Autenticação
SQL
JOIN
Transações ACID
COMMIT
ROLLBACK
Controle de estoque
Variáveis de ambiente
Separação de responsabilidades
Git
Deploy
```

---

# ⚠️ Limitações atuais

O projeto possui finalidade acadêmica e funciona como um MVP.

Não foram implementados:

- pagamento real;
- gateway de pagamento;
- cálculo de frete;
- transportadora;
- rastreamento;
- recuperação de senha por e-mail;
- confirmação de e-mail;
- painel administrativo completo;
- cadastro de endereço;
- cupons de desconto;
- integração logística.

Essas funcionalidades podem ser adicionadas em futuras evoluções.

---

# 🔮 Melhorias futuras

Possíveis evoluções:

- painel administrativo completo;
- CRUD de produtos;
- CRUD de categorias;
- gerenciamento de estoque;
- imagens dos produtos;
- busca de produtos;
- filtros por categoria;
- paginação;
- recuperação de senha;
- endereços de entrega;
- pagamento;
- frete;
- cancelamento de pedidos;
- devolução de estoque em cancelamentos;
- migrations;
- testes automatizados;
- proteção CSRF;
- concorrência avançada de estoque;
- logs estruturados;
- interface responsiva mais completa.

---

# ✅ Conclusão

O projeto demonstra a integração entre uma aplicação web Flask e um banco PostgreSQL, cobrindo desde a modelagem até a persistência dos dados.

O fluxo principal implementado é:

```text
Catálogo
→ Carrinho
→ Cliente
→ Checkout
→ Pedido
→ Itens
→ Atualização de estoque
→ Histórico
```

O banco utiliza constraints e relacionamentos para preservar a integridade dos dados, enquanto o checkout utiliza transações para garantir que pedido, itens e estoque sejam atualizados de forma consistente.

Além do MVP, foi implementada a extensão de autenticação e histórico do cliente, incluindo login, logout, senha armazenada em hash, sessão autenticada e consulta dos pedidos pertencentes ao usuário logado.

A aplicação também foi preparada para versionamento e posterior implantação em cloud, mantendo credenciais fora do código através de variáveis de ambiente.