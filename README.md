# ZIP Checker Service

Микросервис для проверки ZIP-архивов, реализованный в рамках тестового задания.

## Описание
Сервис принимает ZIP-архивы, проверяет их целостность, структуру, размер и наличие вредоносного кода (заглушки), и возвращает результаты. Использует FastAPI, PostgreSQL, Keycloak для аутентификации, и Alembic для миграций.

## Требования
- Docker
- Docker Compose
- Python 3.12+

## Установка
1. Склонируйте репозиторий:
   ```bash
   git clone <repository>
   cd zip_checker

2. Запустите сервисы:
    docker-compose up -d

3. Примените миграции:
    docker exec -it zip_checker-app-1 sh
    alembic upgrade head

## Использование
    API: http://localhost:8000/docs (Swagger UI)
    Аутентификация через Keycloak:
        URL: http://localhost:8080
        Realm: zip-checker
        Client: zip-checker-client
        Credentials: test_user / password
        Client Secret: 9QJaYB3lXTghM0fw48EkN1psZeq1JnKm

## API
    POST /upload: Загрузка ZIP-архива (multipart/form-data, возвращает task_id).
    GET /report/{task_id}: Получение результатов проверки (JSON с характеристиками: status, results).

## Тесты
    Базовые unit-тесты в tests/test_api.py (проверка /upload, /report, и невалидных файлов).
    Запуск тестов:
        docker exec -it zip_checker-app-1 sh
        PYTHONPATH=/app pytest tests/

## Ограничения
    Ответ /report использует заглушки (integrity, antivirus, structure, size) вместо sonarque из ТЗ, что допустимо.
    Файлы хранятся в базе (file_content) вместо MinIO из-за сроков.
    Тесты упрощены (без Keycloak-аутентификации).
    Отсутствуют кэширование, контрольные суммы, поддержка Git (низкий приоритет).

## Разработка
    Технологии: FastAPI, SQLAlchemy (asyncpg), PostgreSQL, Keycloak, Alembic, Pytest.
    Миграции: migrations/versions/ (добавлен file_content).
    Логирование: Все операции логируются.

## Примечания
    Проект демонстрирует базовую функциональность, асинхронные запросы, интеграцию с Keycloak, миграции, и тесты.
    Для продакшена рекомендуется:
        Подогнать ответ /report под контракт ТЗ (sonarque).
        Добавить MinIO.
        Расширить тесты (интеграционные, с Keycloak).
        Реализовать кэширование (Redis).