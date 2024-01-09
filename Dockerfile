# Docker-команда FROM вказує базовий образ контейнера
# Наш базовий образ - це Linux з попередньо встановленим python-3.10
FROM python:3.10

# Встановимо змінну середовища
ENV APP_HOME /app

# Встановимо робочу директорію всередині контейнера
WORKDIR $APP_HOME

# Встановимо залежності всередині контейнера
COPY pyproject.toml $APP_HOME/pyproject.toml

RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --only main

# Скопіюємо інші файли в робочу директорію контейнера
COPY .. .

# Позначимо порт, де працює застосунок всередині контейнера
EXPOSE 8080

# Запустимо наш застосунок всередині контейнера
ENTRYPOINT ["python", "main.py"]