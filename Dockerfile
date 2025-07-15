FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y bash && rm -rf /var/lib/apt/lists/*

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["bash", "-c", "./wait-for-it.sh db:5432 --timeout=30 -- python manage.py runserver 0.0.0.0:8000"]