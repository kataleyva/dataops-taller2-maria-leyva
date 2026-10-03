# Valida el modelo candidato antes de promoverlo a producción.

import json
import sys

from config import cargar_config


def es_valido(mape_candidato, mape_produccion, umbral):
    # El candidato pasa si no supera el umbral y no es peor que producción.
    return mape_candidato <= umbral and mape_candidato <= mape_produccion


def main():
    # Lee las métricas y detiene el pipeline si el modelo no es válido.
    umbral = cargar_config()["modelo"]["umbral_mape"]
    with open("metrics/qa_metrics.json", encoding="utf-8") as archivo:
        metricas = json.load(archivo)
    print(f"[Validate] Candidato: MAPE = {metricas['mape_candidato']} %")
    print(f"[Validate] Producción: MAPE = {metricas['mape_produccion']} %")
    print(f"[Validate] Umbral máximo: MAPE = {umbral} %")
    if not es_valido(metricas["mape_candidato"], metricas["mape_produccion"], umbral):
        print("[Validate] ERROR: el modelo no supera el umbral. NO se promueve.")
        sys.exit(1)
    print("[Validate] OK: el modelo puede promoverse.")


if __name__ == "__main__":
    main()
