FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Railway ожидает, что приложение слушает порт из переменной PORT
ENV PORT=5000

# Для production используем Gunicorn вместо flask run
RUN pip install gunicorn

EXPOSE $PORT

# Запускаем через Gunicorn (более стабильно для Railway)
CMD gunicorn --bind 0.0.0.0:$PORT app:app
