# Framework Practice 2 - Microservices Architecture

Проект микросервисной архитектуры на FastAPI с API Gateway, JWT аутентификацией и единым форматом ответов.

## 🐳 Быстрый старт с Docker (Рекомендуется)

```bash
# 1. Убедитесь, что .env файл настроен
cp .env.example .env
# Отредактируйте .env и установите JWT_SECRET_KEY

# 2. Запустите все сервисы
docker-compose up -d

# 3. Проверьте статус
docker-compose ps

# 4. Откройте Swagger UI
# http://localhost:8000/docs
```


## Архитектура проекта

```
framework_prac_2/
├── .env                      # Переменные окружения (общие для всех сервисов)
├── .env.example              # Пример переменных окружения
├── service_gateway/          # API Gateway (порт 8000)
│   ├── app/
│   ├── run.py
│   └── requirements.txt
├── service_users/            # Сервис управления пользователями (порт 8002)
│   ├── app/
│   ├── run.py
│   └── requirements.txt
└── service_orders/           # Сервис управления заказами (порт 8001)
    ├── app/
    ├── run.py
    └── requirements.txt
```

## Сервисы

### 1. **service_gateway** (порт 8000) 🌐
API Gateway - единая точка входа для всех клиентов.

**Функционал:**
- Проксирование запросов к микросервисам
- Централизованная проверка JWT токенов
- Единая документация API (Swagger)
- Маппинг и трансформация путей
- Обработка ошибок от микросервисов

**Основные endpoints:**
- `/v1/auth/*` - аутентификация (proxy к service_users)
- `/v1/users/*` - управление пользователями (proxy к service_users)
- `/v1/orders/*` - управление заказами (proxy к service_orders)

### 2. **service_users** (порт 8002) 👥
Сервис управления пользователями с аутентификацией.

**Функционал:**
- Регистрация пользователей с валидацией
- Авторизация и выдача JWT токенов
- Управление профилем
- Список пользователей для администраторов

**Endpoints:**
- `POST /v1/auth/register` - Регистрация
- `POST /v1/auth/login` - Авторизация
- `GET /v1/users/me` - Текущий профиль
- `PUT /v1/users/me` - Обновление профиля
- `GET /v1/users/all` - Список пользователей (admin)

### 3. **service_orders** (порт 8001)
Сервис управления заказами.

**Функционал:**
- Создание заказов с валидацией
- Получение заказа по ID
- Список заказов пользователя
- Обновление статуса заказа
- Отмена заказа

**Endpoints:**
- `POST /v1/orders/create` - Создание заказа
- `GET /v1/orders/my` - Список заказов
- `GET /v1/orders/{id}` - Заказ по ID
- `PUT /v1/orders/{id}/status` - Обновление статуса
- `DELETE /v1/orders/{id}` - Отмена заказа

## Быстрый старт

### 1. Установка зависимостей

```bash
# Для service_users
cd service_users
pip install -r requirements.txt

# Для service_orders
cd ../service_orders
pip install -r requirements.txt

# Для service_gateway
cd ../service_gateway
pip install -r requirements.txt
```

### 2. Настройка окружения

Скопируйте `.env.example` в `.env` и настройте параметры:

```bash
cp .env.example .env
```

Пример `.env`:
```env
# Database Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=FrameworkPrak2Bd

# JWT Configuration
JWT_SECRET_KEY=your-secret-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application Configuration
SERVICE_GATEWAY_HOST=localhost
SERVICE_GATEWAY_PORT=8000

SERVICE_USERS_HOST=localhost
SERVICE_USERS_PORT=8002
SERVICE_USERS_URL=http://localhost:8002

SERVICE_ORDERS_HOST=localhost
SERVICE_ORDERS_PORT=8001
SERVICE_ORDERS_URL=http://localhost:8001
```

### 3. Создание базы данных

```sql
CREATE DATABASE "FrameworkPrak2Bd";
```

### 4. Запуск сервисов

**Важно: запускайте сервисы в следующем порядке!**

**Терминал 1 - service_users:**
```bash
cd service_users
python run.py
```

**Терминал 2 - service_orders:**
```bash
cd service_orders
python run.py
```

**Терминал 3 - service_gateway:**
```bash
cd service_gateway
python run.py
```
# Запустить все сервисы через Docker
docker-compose up -d

## Документация API

### Основная точка входа - API Gateway

**Все запросы должны идти через API Gateway:**
- **Swagger UI**: http://localhost:8000/docs

### Документация отдельных сервисов (для разработки)

- **service_users**: http://localhost:8002/docs
- **service_orders**: http://localhost:8001/docs

## Единый формат ответов

Все API endpoints возвращают ответы в едином формате:

**Успешный ответ:**
```json
{
  "success": true,
  "data": { ... },
  "error": null
}
```

**Ответ с ошибкой:**
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "ERROR_CODE",
    "message": "Описание ошибки"
  }
}
```

## Аутентификация

### Workflow

1. **Регистрация пользователя:**
```bash
curl -X POST "http://localhost:8000/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123",
    "name": "John Doe",
    "roles": ["client"]
  }'
```

2. **Авторизация и получение токена:**
```bash
curl -X POST "http://localhost:8000/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

**Ответ:**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
  },
  "error": null
}
```

3. **Использование токена в запросах:**
```bash
TOKEN="your-token-here"

# Получить профиль
curl -X GET "http://localhost:8000/v1/users/me" \
  -H "Authorization: Bearer $TOKEN"

# Создать заказ
curl -X POST "http://localhost:8000/v1/orders/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {
        "name": "Laptop",
        "amount": 1,
        "description": "High-performance laptop",
        "price": 1200.00
      }
    ]
  }'
```

## База данных

Все сервисы используют единую базу данных PostgreSQL `FrameworkPrak2Bd`.

**Таблицы:**
- `users` - пользователи (service_users)
- `orders` - заказы (service_orders)

## Безопасность

- Пароли хэшируются с использованием bcrypt
- JWT токены с настраиваемым временем жизни
- Проверка JWT на уровне API Gateway
- Проверка прав доступа на уровне сервисов
- Валидация всех входных данных
- Единообразная обработка ошибок

## Технологии

- **FastAPI** - веб-фреймворк
- **SQLAlchemy** - ORM для работы с БД
- **PostgreSQL** - база данных
- **Pydantic** - валидация данных
- **python-jose** - JWT токены
- **bcrypt** - хэширование паролей
- **httpx** - асинхронный HTTP клиент (для gateway)
- **uvicorn** - ASGI сервер

## Архитектурные особенности

### API Gateway Pattern

**Преимущества:**
- Единая точка входа для клиентов
- Централизованная аутентификация
- Единая документация API
- Гибкая маршрутизация запросов
- Изоляция внутренних сервисов


## Роли пользователей

- **client** - обычный пользователь (по умолчанию)
  - Может создавать и управлять своими заказами
  - Может редактировать свой профиль
  
- **admin** - администратор
  - Все права client
  - Может просматривать список всех пользователей

## Статусы заказов

- **CREATED** - заказ создан (по умолчанию)
- **IN_PROGRESS** - заказ в обработке
- **COMPLETED** - заказ выполнен
- **CANCELLED** - заказ отменен

## Тестирование

### Через Swagger UI

1. Откройте http://localhost:8000/docs
2. Зарегистрируйте пользователя через `/v1/auth/register`
3. Авторизуйтесь через `/v1/auth/login` и скопируйте токен
4. Нажмите кнопку "Authorize" в правом верхнем углу
5. Вставьте токен в формате: `Bearer your-token-here`
6. Тестируйте все защищенные endpoints

### Через curl

Примеры команд приведены выше в разделе "Аутентификация"

## Дополнительная документация

- [service_gateway README](./service_gateway/README.md) - детальная документация API Gateway
- [service_users README](./service_users/README.md) - детальная документация сервиса пользователей (если существует)
- [service_orders README](./service_orders/README.md) - детальная документация сервиса заказов
