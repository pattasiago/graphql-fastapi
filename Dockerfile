# Use uma imagem base do Python
FROM python:3.11-slim

# Defina o diretório de trabalho
WORKDIR /app

# Copie os arquivos do projeto
COPY requirements.txt requirements.txt

# Instale as dependências
RUN pip install -r requirements.txt

COPY . .


# Exponha a porta 8000
EXPOSE 8000

# Comando para rodar a aplicação
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
