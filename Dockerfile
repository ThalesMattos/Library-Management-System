FROM python:3.12-slim

# Evita arquivos .pyc e saída bufferizada no log do container
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instala dependências antes de copiar o código para aproveitar cache de camadas
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do projeto
COPY . .

EXPOSE 8000

# Gunicorn serve a aplicação via wsgi.py:application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "wsgi:application"]
