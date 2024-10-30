# Use uma imagem base do Python
FROM python:3.9

# Instala libGL para o OpenCV funcionar corretamente
RUN apt-get update && apt-get install -y libgl1-mesa-glx

# Define o diretório de trabalho no container
WORKDIR /app

# Copia o arquivo requirements.txt e instala as dependências
COPY parking_lot/requirements.txt .
RUN pip install -r requirements.txt

# Copia todo o código da pasta parking_lot para o diretório de trabalho no container
COPY parking_lot /app/parking_lot

# Define o diretório onde está o main.py como o de trabalho
WORKDIR /app/parking_lot

# Expõe a porta 8000
EXPOSE 8000

# Comando para iniciar a aplicação com Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
