# Django REST LMS

API для онлайн-обучения на Django REST Framework.

---

## Что нужно для запуска

- Docker Desktop
- Git

---

## Как запустить проект

### 1. Скачать проект

```bash
git clone https://github.com/VikaDavlyatshina/DjangoRest.git
cd DjangoRest
```

### 2. Создать файл с настройками

```bash
cp .env.example .env.docker
```

Откройте .env.docker и замените и заполните его своими данными

### 3. Запустить все сервисы

```bash
docker compose up -d --build
```

### 4. Применить миграции

```bash
docker compose exec backend python manage.py migrate
```

### 5. Создать администратора (опционально)

```bash
docker compose exec backend python manage.py createsuperuser
```

### 6. Открыть сайт

http://localhost:8000

Админка: http://localhost:8000/admin

---

## Как проверить, что всё работает

### Статус контейнеров

```bash
docker compose ps
```

Должно быть 5 сервисов со статусом Up.

### База данных

```bash
docker compose exec postgres psql -U postgres -d djangorest -c "SELECT 1"
```

Ожидаемый ответ: 1

### Redis

```bash
docker compose exec redis redis-cli PING
```

Ожидаемый ответ: PONG

### Celery
```bash
docker compose exec celery celery -A config inspect ping

```

Ожидаемый ответ: OK

---

## Как остановить

```bash
docker compose down
```

Чтобы удалить все данные:

```bash
docker compose down -v

```
