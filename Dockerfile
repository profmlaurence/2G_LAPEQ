FROM python:3.11-slim

# Define o diretório de trabalho
WORKDIR /app

# Copia o arquivo de requisitos e instala as dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código da aplicação
COPY . .

# Expõe a porta que o Streamlit usa (o Cloud Run espera a porta definida na env PORT, padrão 8080)
EXPOSE 8080

# Comando para iniciar a aplicação
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]

