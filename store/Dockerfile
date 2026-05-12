# Використовуємо стабільну версію Python
FROM python:3.11-slim

# Встановлюємо системні залежності для збірки psycopg2 та інших бібліотек
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

# Оновлюємо pip перед інсталяцією
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]