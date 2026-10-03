FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ src/
COPY configs/ configs/
COPY models/ models/
CMD ["python", "-c", "import joblib; joblib.load('models/modelo_ventas.joblib'); print('Modelo cargado')"]