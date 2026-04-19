# Dockerfile для LMS проекта с Poetry

# Берём образ Python 3.13 (облегчённая версия)
FROM python:3.13-slim

# Отключаем создание файлов .pyc (экономит место)
ENV PYTHONDONTWRITEBYTECODE=1

# Отключаем буферизацию вывода (логи видно сразу)
ENV PYTHONUNBUFFERED=1

# Создаём рабочую папку внутри контейнера
WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Poetry
RUN pip install --no-cache-dir poetry

# Копируем файлы с зависимостями (отдельно от кода для оптимизации)
COPY pyproject.toml poetry.lock ./

# Устанавливаем зависимости проекта
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Устанавливаем pip-зависимости (которые не работают через Poetry)
RUN pip install --no-cache-dir \
    django-celery-beat==2.9.0 \
    django-timezone-field==7.2.1 \
    python-crontab==3.3.0 \
    cron-descriptor==1.4.5

# Копируем весь код проекта
COPY . .

# Порт, который будет использовать приложение
EXPOSE 8000

# Запускаем сервер Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]