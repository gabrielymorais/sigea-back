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

- Criar migraçoes
```bash
docker compose exec web python manage.py makemigrations
```
- Aplicar migraçoes no banco
```bash
docker compose exec web python manage.py migrate
```

- Criando um novo app no Django:
```bash
docker compose exec web python manage.py startapp nomeApp apps/nomeApp
```
- Depois de criar um novo app:
```bash
docker compose exec web python manage.py makemigrations nomeApp
docker compose exec web python manage.py migrate
```
- Criando um usuario:
```bash
docker compose exec web python manage.py createsuperuser
```

## Para rodar os testes 
- Todos os testes
```bash
docker compose run --rm web python manage.py test apps
```
- Com output detalhado (recomendado)
```bash
docker compose run --rm web python manage.py test apps --verbosity=2
```
- Módulo específico
```bash
docker compose run --rm web python manage.py test apps.users
docker compose run --rm web python manage.py test apps.atas
docker compose run --rm web python manage.py test apps.historico
```
- Parar no primeiro erro
```bash
docker compose run --rm web python manage.py test apps --failfast
```