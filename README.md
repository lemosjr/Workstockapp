# 🏗️ WorkStock

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14%2B-336791)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Em%20Desenvolvimento-orange)

**WorkStock** é um sistema desktop de gestão de reformas focado na otimização de processos para empresas do setor imobiliário e de construção civil. O sistema centraliza o controle de estoque, ordens de serviço (OS), orçamentos e comunicação entre as partes envolvidas (Empresa, Proprietário e Inquilino).

---

## 📋 Funcionalidades Principais

### 🏢 Módulo Empresa (Administrador)
- **Gestão de OS:** Criação, edição e acompanhamento de Ordens de Serviço.
- **Controle de Estoque:** Cadastro de materiais (SKU, preços, fornecedores) e baixa automática ao vincular materiais a uma OS.
- **Orçamentação:** Cálculo automático de custos de material + inserção de mão de obra.
- **Dashboard:** Visão geral com métricas de faturamento, OSs ativas e alertas de estoque baixo.
- **Gestão de Usuários:** Cadastro de novos perfis (Proprietários, Clientes, Colaboradores).

### 🏠 Módulo Proprietário
- **Aprovação de Orçamentos:** Interface para aprovar ou rejeitar orçamentos enviados pela empresa.
- **Acompanhamento:** Visualização do status das reformas em seus imóveis.
- **Histórico:** Acesso ao chat e detalhes da obra.

### 👤 Módulo Cliente (Inquilino)
- **Solicitações:** Abertura rápida de chamados para reparos.
- **Acompanhamento:** Visualização do status de suas solicitações.

### 💬 Comunicação
- **Chat Integrado:** Histórico de mensagens vinculado a cada Ordem de Serviço, permitindo comunicação transparente entre todos os perfis.

---

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python 3
* **Interface Gráfica (GUI):** CustomTkinter (Design moderno e responsivo)
* **Banco de Dados:** PostgreSQL
* **Driver de Banco:** Psycopg2-binary
* **Segurança:** Bcrypt (Hashing de senhas)
* **Gerenciamento de Configuração:** Python-dotenv
* **Arquitetura:** MVC (Model-View-Controller)

---

## 📂 Estrutura do Projeto (MVC)

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