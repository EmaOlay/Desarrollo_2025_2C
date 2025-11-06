FROM python:3.11-slim

WORKDIR /app

# Instalamos herramientas mínimas y la librería 'rich' para el TUI
RUN apt-get update && apt-get install -y \
    curl \
    # CORRECCIÓN: Usar el paquete compatible que proporciona el cliente 'mysql'
    default-mysql-client \
    netcat-openbsd \
    vim \
    wget \
    gnupg \
    # -------------------------------------------------------------------
    # 1. SETUP DE MONGOSH
    # -------------------------------------------------------------------
    && curl -fsSL https://pgp.mongodb.com/server-8.0.asc | gpg --dearmor -o /usr/share/keyrings/mongodb-server-8.0.gpg \
    && echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-8.0.gpg ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/8.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-8.0.list \
    && apt-get update \
    && apt-get install -y mongodb-mongosh \
    \
    && rm -rf /var/lib/apt/lists/*

# Instalación de clientes de BD (cqlsh requiere pip)
RUN pip install cqlsh

# Instalación de la librería Rich (para TUI básico y formatting)
RUN pip install rich

# Copiamos el script principal de la TUI
# COPY cli.py /app/cli.py

CMD ["python", "cli.py"]