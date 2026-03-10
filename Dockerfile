FROM python:3.14-slim

# Define o diretório de trabalho
WORKDIR /app

# Copia o arquivo de requisitos e instala as dependências
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copia o restante do código da aplicação
COPY . .

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]

gcloud run deploy lapeq-app \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars FIREBASE_API_KEY="AIzaSyCOuUX0VmdtwpYDSTXq2R3tiD3Y9n1SglM" \
  --set-env-vars FIREBASE_STORAGE_BUCKET="optimize-lapeq.firebasestorage.app" \
  --set-env-vars GOOGLE_CLIENT_ID="624820735308-ln85200ausvt4pj5fnu2l6hr402g4eu7.apps.googleusercontent.com" \
  --set-env-vars GOOGLE_CLIENT_SECRET="AIzaSyCOuUX0VmdtwpYDSTXq2R3tiD3Y9n1SglM" \
  --set-env-vars GOOGLE_REDIRECT_URI="https://lapeq2g-624820735308.southamerica-east1.run.app/login"