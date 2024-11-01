FROM python:3.9

RUN apt-get update && apt-get install -y libgl1-mesa-glx

WORKDIR /app

COPY parking_lot/requirements.txt .
RUN pip install -r requirements.txt

COPY parking_lot /app/parking_lot

WORKDIR /app/parking_lot

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
