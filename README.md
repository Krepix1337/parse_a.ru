# 🚗 Auto.ru Parser

Парсер автомобилей с auto.ru с возможностью поиска по API или Telegram-боту.

## ✨ Возможности

- 🕵️ **Парсинг данных** с auto.ru с использованием Playwright
- 🌐 **FastAPI REST API** для интеграции с другими системами
- 🤖 **Telegram-бот** для удобного поиска автомобилей
- 🗄 **PostgreSQL база данных** для хранения собранных данных
- 🐳 **Docker-контейнеризация** для простого развертывания

## 🛠 Технологии

- **Python 3.12+**
- **FastAPI** — современный веб-фреймворк
- **Playwright** — автоматизация браузера для парсинга
- **SQLAlchemy 2.0** — ORM для работы с БД
- **PostgreSQL** — реляционная база данных
- **Alembic** — миграции базы данных
- **aiogram** — Telegram бот
- **Docker** — контейнеризация

## 📦 Установка и запуск

### Требования

- Python 3.12+
- PostgreSQL 15+
- Docker и Docker Compose (опционально)

### Шаг 1: Клонирование репозитория

```bash
git clone https://github.com/ваш-username/parse_auto.ru.git
cd parse_auto.ru
```

### Шаг 2: Настройка переменных окружения

Создайте файл `.env` в корне проекта:

```env
# Режим работы
MODE=DEV

# Логирование
LOG_LEVEL=INFO

# Настройки основной базы данных
DB_USER=postgres
DB_PASS=ваш_пароль
DB_HOST=localhost
DB_PORT=5432
DB_NAME=auto_parser

# Настройки тестовой базы данных
TEST_DB_USER=postgres
TEST_DB_PASS=ваш_пароль
TEST_DB_HOST=localhost
TEST_DB_PORT=5432
TEST_DB_NAME=auto_parser_test

# Настройки парсера
PARSER_TIMEOUT=30
PARSER_HEADLESS=True

# Telegram Bot (опционально)
TELEGRAM_TOKEN=ваш_token
TELEGRAM_CHAT_ID=ваш_chat_id
```

Для примера настроек используйте `.env.example`.

### Шаг 3: Запуск через Docker (рекомендуется)

```bash
docker-compose up -d
```

После запуска:
- API доступен по адресу: `http://localhost:8000`
- База данных: `localhost:5432`

### Шаг 4: Запуск локально

```bash
# Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows

# Установка зависимостей
pip install -r requirements.txt

# Применение миграций
alembic upgrade head

# Запуск сервера
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Запуск Telegram-бота

```bash
python -m app.bot.tgbot
```

## 📖 Использование

### API

#### Root endpoint
```
GET /
```

#### Поиск автомобилей
```
POST /search
Content-Type: application/json

{
  "mark": "acura",
  "model": "mdx",
  "generation": "2013—2019"
}
```

Ответ: массив найденных автомобилей с данными.

#### API документация
После запуска сервера документация доступна по адресу:  
`http://localhost:8000/docs`

### Telegram-бот

1. Найдите вашего бота в Telegram
2. Отправьте команду `/start`
3. Следуйте инструкциям: введите марку, модель и год
4. Получите до 3 первых объявлений

## 📊 Структура базы данных

### Таблица `cars`
- `id` — первичный ключ
- `mark` — марка автомобиля
- `model` — модель
- `generation` — поколение
- `title` — заголовок объявления
- `subtitle` — комплектация
- `url` — ссылка на объявление
- `price` — цена в рублях
- `year` — год выпуска
- `mileage` — пробег
- `specs` — характеристики
- `parsed_at` — дата парсинга

### Таблица `Generation`
- `id` — первичный ключ
- `mark` — марка
- `model` — модель
- `generation_name` — название поколения
- `year_start` — год начала производства
- `year_end` — год окончания производства

## 🧪 Тестирование

```bash
# Запуск тестов
pytest

# С покрытием кода
pytest --cov=app --cov-report=html
```

## 🗄 Миграции базы данных

```bash
# Создание новой миграции
alembic revision -m "название миграции"

# Применение миграций
alembic upgrade head

# Откат миграций
alembic downgrade base
```

## 🐳 Docker

### Команды

```bash
# Запуск в фоновом режиме
docker-compose up -d

# Остановка
docker-compose down

# Просмотр логов
docker-compose logs -f

# Пересборка контейнера
docker-compose build --no-cache
```

### Объёмы данных

- PostgreSQL данные хранятся в томпе `postgres_data`

## 📝 Лицензия

Этот проект распространяется под лицензией MIT. Смотрите файл [LICENSE](LICENSE).

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку (`git checkout -b feature/AmazingFeature`)
3. Сделайте коммит (`git commit -m 'Add some AmazingFeature'`)
4. Запушите в ветку (`git push origin feature/AmazingFeature`)
5. Откройте Pull Request

## 📞 Поддержка

Если у вас возникли вопросы или проблемы:
- Откройте issue в репозитории проекта
- Свяжитесь с разработчиком

## ⭐️ Благодарности

- [Playwright](https://playwright.dev/) за отличный инструмент для автоматизации браузера
- [FastAPI](https://fastapi.tiangolo.com/) за великолепный веб-фреймворк

---

**Приятного использования! 🚀**
