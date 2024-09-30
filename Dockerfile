# Use uma imagem base Python
FROM python:3.9-slim

# Defina o diretório de trabalho dentro do container
WORKDIR /app

# Copie os arquivos requirements.txt para o diretório de trabalho
COPY requirements.txt .

# Instale as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Copie o código do aplicativo para o diretório de trabalho
COPY . .

# Exponha a porta que será usada pelo Flask
EXPOSE 5000

# Defina o comando para rodar o aplicativo Flask
CMD ["python", "app.py"]