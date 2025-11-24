# WorkStock

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14%2B-336791)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Em%20Desenvolvimento-orange)

**WorkStock** é um sistema desktop de gestão de reformas focado na otimização de processos para empresas do setor imobiliário e de construção civil. O sistema centraliza o controle de estoque, ordens de serviço (OS), orçamentos e comunicação entre as partes envolvidas (Empresa, Proprietário e Inquilino).

---

## Funcionalidades Principais

### Módulo Empresa (Administrador)
- **Gestão de OS:** Criação, edição e acompanhamento de Ordens de Serviço.
- **Controle de Estoque:** Cadastro de materiais (SKU, preços, fornecedores) e baixa automática ao vincular materiais a uma OS.
- **Orçamentação:** Cálculo automático de custos de material + inserção de mão de obra.
- **Dashboard:** Visão geral com métricas de faturamento, OSs ativas e alertas de estoque baixo.
- **Gestão de Usuários:** Cadastro de novos perfis (Proprietários, Clientes, Colaboradores).

### Módulo Proprietário
- **Aprovação de Orçamentos:** Interface para aprovar ou rejeitar orçamentos enviados pela empresa.
- **Acompanhamento:** Visualização do status das reformas em seus imóveis.
- **Histórico:** Acesso ao chat e detalhes da obra.

### Módulo Cliente (Inquilino)
- **Solicitações:** Abertura rápida de chamados para reparos.
- **Acompanhamento:** Visualização do status de suas solicitações.

### Comunicação
- **Chat Integrado:** Histórico de mensagens vinculado a cada Ordem de Serviço, permitindo comunicação transparente entre todos os perfis.

---

## Tecnologias Utilizadas

* **Linguagem:** Python 3
* **Interface Gráfica (GUI):** CustomTkinter (Design moderno e responsivo)
* **Banco de Dados:** PostgreSQL
* **Driver de Banco:** Psycopg2-binary
* **Segurança:** Bcrypt (Hashing de senhas)
* **Gerenciamento de Configuração:** Python-dotenv
* **Arquitetura:** MVC (Model-View-Controller)

---

## Estrutura do Projeto (MVC)

```text
workstockapp/
├── app/
│   ├── controllers/   # Lógica de Negócio e Validação
│   ├── models/        # Acesso ao Banco de Dados (SQL)
│   ├── views/         # Telas e Interface (CustomTkinter)
│   └── utils/         # Conexão com DB e utilitários
├── config/            # Carregamento de variáveis de ambiente
├── main.py            # Ponto de entrada da aplicação
├── database_setup.sql # Script para criar o banco do zero
└── requirements.txt   # Dependências do projeto
````

-----

## Como Executar o Projeto

### Pré-requisitos

  * Python 3.10 ou superior instalado.
  * PostgreSQL instalado e rodando.

### Passo a Passo

1.  **Clone o repositório:**

    ```bash
    git clone [https://github.com/seu-usuario/workstockapp.git](https://github.com/seu-usuario/workstockapp.git)
    cd workstockapp
    ```

2.  **Crie e ative um ambiente virtual (recomendado):**

    ```bash
    python -m venv venv
    # Windows:
    .\venv\Scripts\activate
    # Linux/Mac:
    source venv/bin/activate
    ```

3.  **Instale as dependências:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure o Banco de Dados:**

      * Crie um banco de dados no PostgreSQL chamado `workstock_db`.
      * Execute o script `database_setup.sql` (localizado na raiz) na sua ferramenta de banco de dados para criar as tabelas.

5.  **Configure as Variáveis de Ambiente:**

      * Crie um arquivo `.env` na raiz do projeto.
      * Preencha com suas credenciais locais:

    <!-- end list -->

    ```env
    DB_HOST=localhost
    DB_PORT=5432
    DB_NAME=workstock_db
    DB_USER=postgres
    DB_PASSWORD=sua_senha_aqui
    ```

6.  **Crie os Usuários de Teste (Seed):**

      * Execute o script auxiliar para criar os perfis iniciais (Empresa, Proprietário, Cliente):

    <!-- end list -->

    ```bash
    python criar_usuarios_teste.py
    ```

7.  **Execute a Aplicação:**

    ```bash
    python main.py
    ```

-----

## Usuários de Teste (Padrão)

Após rodar o script de criação, use estas credenciais para testar os diferentes perfis:

| Perfil | E-mail | Senha |
| :--- | :--- | :--- |
| **Empresa (Admin)** | `empresa@gmail.com` | `123456` |
| **Proprietário** | `proprietario@gmail.com` | `123456` |
| **Cliente** | `cliente@gmail.com` | `123456` |

-----

## Roadmap (Próximos Passos)

Este projeto está em evolução constante para se tornar um produto comercial viável.

  - [x] Arquitetura MVC Base
  - [x] CRUD Estoque e OS
  - [x] Sistema de Login e Permissões
  - [x] Fluxo de Aprovação de Orçamento
  - [ ] **Migração para ORM (SQLAlchemy)** 
  - [ ] **Criação de API REST (FastAPI)** 
  - [ ] **Interface Web/Mobile para Clientes**

-----

## 📄 Licença

Este projeto está sob a licença MIT.

```
```
