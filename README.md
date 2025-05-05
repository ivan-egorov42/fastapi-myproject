# 🏀 Basketball Club Stats API

Это веб-приложение для ведения и анализа статистики баскетбольного клуба (например, Dallas Mavericks), построенное с использованием **FastAPI**, **SQLModel**, **PostgreSQL** и **Docker**.

## 📦 Возможности

- 🔐 Аутентификация пользователей (OAuth2 + JWT)
- 📊 CRUD-операции:
  - Игроки (Players)
  - Матчи (Games)
  - Статистика игроков (Player Stats)
  - Командная статистика матчей (Game Stats)
- 🔎 Фильтрация и сортировка данных (по сезону, росту, позиции и др.)
- 📈 Агрегации: средние, максимальные и суммарные показатели игроков


## 🚀 Технологии

- **FastAPI** — современный web-фреймворк на Python
- **SQLModel** (SQLAlchemy + Pydantic)
- **PostgreSQL** — база данных
- **Docker / Docker Compose** — контейнеризация
- **Alembic** — миграции схемы базы данных
- **pytest** — модульные тесты

---

## 🐳 Запуск проекта в Docker

```bash
# Клонируем репозиторий
git clone https://github.com/ivan-egorov42/fastapi-myproject.git
cd fastapi-myproject

# Запускаем контейнеры
docker-compose up --build
```

## Entity-Relationship Diagram

![ER Diagram](docs/diagram.png)