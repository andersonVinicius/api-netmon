# Dockerfile
# Imagem mínima para monitoramento de conectividade

FROM python:3.12-slim

# Create non-root user for safety
RUN adduser --disabled-password --gecos "" monitor

# Working directory inside the container
WORKDIR /app

# Copia apenas o requirements para aproveitar cache do Docker
COPY requirements.txt /app/
# Instala dependências
RUN pip install --no-cache-dir -r requirements.txt
# Copia todo o restante do código
COPY . /app/

USER monitor

# Default command (customise via docker-compose if needed)
CMD ["python", "main.py", "-i", "30", "--syslog"]
