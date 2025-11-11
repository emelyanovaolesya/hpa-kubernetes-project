# API Gateway Service

API Gateway для микросервисов Users и Orders с JWT аутентификацией и полной документацией.

## Архитектура

```
service_gateway/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── users.py          # Endpoints для users
│   │       │   └── orders.py         # Endpoints для orders
│   │       └── router.py             # Главный роутер v1
│   ├── core/
│   │   ├── dependencies.py           # JWT валидация и dependencies
│   │   ├── proxy.py                  # Proxy client для микросервисов
│   │   └── security.py               # JWT декодирование
│   ├── schemas/
│   │   ├── user.py                   # Pydantic схемы пользователей
│   │   ├── order.py                  # Pydantic схемы заказов
│   │   └── response.py               # Схемы ответов
│   ├── config.py                     # Настройки приложения
│   └── main.py                       # Главный файл приложения
├── run.py                            # Точка входа
└── requirements.txt                  # Зависимости
```

## Требования

- Python 3.10+
- Запущенные сервисы: service_users (порт 8002) и service_orders (порт 8001)

## Установка и запуск

### 1. Установка зависимостей

```bash
cd service_gateway
pip install -r requirements.txt
```

### 2. Настройка переменных окружения

Убедитесь, что файл `.env` в корне проекта содержит:

```env
# JWT Configuration (должны совпадать с другими сервисами)
JWT_SECRET_KEY=your-secret-key-change-this-in-production
JWT_ALGORITHM=HS256

# Application Configuration
SERVICE_GATEWAY_HOST=localhost
SERVICE_GATEWAY_PORT=8000

SERVICE_USERS_URL=http://localhost:8002
SERVICE_ORDERS_URL=http://localhost:8001
```

### 3. Запуск сервиса

```bash
python run.py
```

Сервис будет доступен по адресу: `http://localhost:8000`

- **Swagger документация**: http://localhost:8000/docs
- **ReDoc документация**: http://localhost:8000/redoc

## Аутентификация

API Gateway проверяет JWT токены на защищенных endpoints.

**Незащищенные endpoints:**
- `POST /v1/auth/register` - регистрация
- `POST /v1/auth/login` - авторизация

**Защищенные endpoints:**
- Все остальные endpoints требуют Bearer токен в заголовке `Authorization`

### Процесс работы:

1. **Регистрация/Авторизация** - gateway проксирует запрос к service_users
2. **Получение токена** - service_users возвращает JWT токен
3. **Использование токена** - при запросе к защищенным endpoints:
   - Gateway валидирует JWT токен
   - Если токен валидный, gateway проксирует запрос к соответствующему сервису
   - Токен передается в заголовке Authorization к микросервису

## 📡 API Endpoints

Все endpoints возвращают ответы в едином формате:

```json
{
  "success": boolean,
  "data": object | null,
  "error": {
    "code": string,
    "message": string
  } | null
}
```

### Примеры использования

#### 1. Регистрация пользователя

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

#### 2. Авторизация

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

#### 3. Получить текущий профиль

```bash
TOKEN="your-jwt-token"

curl -X GET "http://localhost:8000/v1/users/me" \
  -H "Authorization: Bearer $TOKEN"
```

#### 4. Создать заказ

```bash
curl -X POST "http://localhost:8000/v1/orders/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {
        "name": "Laptop",
        "amount": 2,
        "description": "High-performance laptop",
        "price": 1200.50
      }
    ]
  }'
```

#### 5. Получить список заказов

```bash
curl -X GET "http://localhost:8000/v1/orders/?page=1&size=10&sort_by=created_at&sort_order=desc" \
  -H "Authorization: Bearer $TOKEN"
```

## Безопасность

### JWT Валидация

Gateway валидирует JWT токены перед проксированием запросов:
- Проверяет подпись токена
- Проверяет срок действия токена
- Извлекает информацию о пользователе

### Обработка ошибок

Gateway возвращает понятные ошибки:

- **401 Unauthorized** - невалидный или отсутствующий токен
- **403 Forbidden** - недостаточно прав (например, не admin)
- **404 Not Found** - ресурс не найден
- **422 Unprocessable Entity** - ошибка валидации данных
- **503 Service Unavailable** - микросервис недоступен
- **504 Gateway Timeout** - превышено время ожидания ответа

## Технологии

- **FastAPI** - веб-фреймворк
- **httpx** - асинхронный HTTP клиент для проксирования
- **python-jose** - JWT токены
- **Pydantic** - валидация данных
- **uvicorn** - ASGI сервер

## Преимущества использования API Gateway

1. **Единая точка входа** - все запросы идут через один endpoint
2. **Централизованная аутентификация** - JWT проверяется один раз в gateway
3. **Упрощенная интеграция** - клиент работает с одним API
4. **Полная документация** - вся документация в одном месте (Swagger UI)
5. **Маршрутизация** - гибкий маппинг путей между gateway и микросервисами
6. **Обработка ошибок** - единообразная обработка ошибок от всех сервисов

## Мониторинг

Health check endpoint:

```bash
curl http://localhost:8000/health
```

**Ответ:**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "services": {
      "users": "http://localhost:8002",
      "orders": "http://localhost:8001"
    }
  },
  "error": null
}
```

## Тестирование

Используйте Swagger UI для тестирования всех endpoints:
- http://localhost:8000/docs

Swagger UI предоставляет:
- Полную документацию всех endpoints
- Возможность тестировать запросы прямо из браузера
- Схемы запросов и ответов
- Примеры данных

В моем проекте тестирование выполнено в POSTMAN
