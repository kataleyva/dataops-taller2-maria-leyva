# Train & Validate: entrena el modelo de ventas y calcula su MAPE.

import json
import os

import joblib
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_percentage_error
from sklearn.model_selection import train_test_split

from config import cargar_config


def entrenar(datos, objetivo):
    # Entrena una regresión lineal y devuelve el modelo y su MAPE (%).
    caracteristicas = datos.drop(columns=[objetivo])
    etiquetas = datos[objetivo]
    x_train, x_test, y_train, y_test = train_test_split(
        caracteristicas, etiquetas, test_size=0.2, random_state=42
    )
    modelo = LinearRegression().fit(x_train, y_train)
    mape = mean_absolute_percentage_error(y_test, modelo.predict(x_test)) * 100
    return modelo, round(mape, 2)


def main():
    # Entrena el modelo y guarda el modelo y sus métricas.
    config = cargar_config()
    datos = pd.read_csv(config["datos"]["ruta"]).dropna()
    modelo, mape = entrenar(datos, config["modelo"]["objetivo"])
    os.makedirs("models", exist_ok=True)
    os.makedirs("metrics", exist_ok=True)
    joblib.dump(modelo, config["modelo"]["ruta_salida"])
    metricas = {
        "mape_candidato": mape,
        "mape_produccion": config["modelo"]["mape_modelo_produccion"],
    }
    with open("metrics/qa_metrics.json", "w", encoding="utf-8") as archivo:
        json.dump(metricas, archivo, indent=2)
    print(f"[Train] Modelo entrenado. MAPE = {mape} %")


if __name__ == "__main__":
    main()
