# SIGEA — Backend (Django + Docker)

Este repositório contém o **backend do SIGEA (Sistema de Gerenciamento de Arquivos)**, desenvolvido em **Django**, utilizando **Docker e Docker Compose** para padronizar o ambiente de execução e **banco de dados relacional** (ex.: PostgreSQL).

---

## 📌 Pré-requisitos

Antes de iniciar, certifique-se de ter instalado:

- Docker
- Docker Compose

---

## 📂 Estrutura do Projeto

Estrutura típica do repositório:

- `manage.py`
- `config/` — configurações principais do Django (settings, urls, wsgi, asgi)
- `apps/` — aplicações do sistema (ex.: users, documents, core)
- `docker-compose.yml`
- `Dockerfile` (se aplicável)
- `.env.example` — modelo de variáveis de ambiente
- `.env` — arquivo local com segredos (**não versionado**)

---

## 🔐 Variáveis de Ambiente (.env)

Este projeto **não versiona informações sensíveis**.  
Você deve criar um arquivo `.env` localmente, baseado no `.env.example`.


## 🐳 Subindo o Ambiente com Docker
```bash
docker compose up -d --build
```
**Derrubando container**
```bash
docker compose down
```
**Derrubar e remover volumes (apaga os dados do banco) **
```bash
docker compose donw -v
```
## 🧱 Migrations (quando e como rodar)
**Quando rodar migrations?**
**As migrations devem ser executadas nas seguintes situações:**
- Primeira execução do projeto (ambiente novo)
- Após atualizar o código (git pull) com novas migrations
- Após alterações nos arquivos models.py

- Executa todas as migrations pendentes no banco(este comando deve ser executado sempre após subir o container pela primeira vez).
```bash
docker compose exec backend python manage.py migrate
```
- Se você modificou algum models.py, gere novas migrations:
```bash
docker compose exec backend python manage.py makemigrations
```
- Em seguida, aplique no banco:
```bash
docker compose exec backend python manage.py migrate
```




