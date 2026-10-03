# Genera datos sintéticos de ventas para DEV y CI (nunca datos reales).

import os

import numpy as np
import pandas as pd

RUTA_SALIDA = "data/ventas.csv"


def generar_ventas(n_filas=1000, porcentaje_nulos=0.0, semilla=42):
    # Crea ventas semanales sintéticas con una relación lineal conocida.
    rng = np.random.default_rng(semilla)
    datos = pd.DataFrame(
        {
            "semana": rng.integers(1, 53, n_filas),
            "precio_promedio": rng.uniform(5_000, 50_000, n_filas).round(0),
            "promocion": rng.integers(0, 2, n_filas),
            "id_tienda": rng.integers(1, 21, n_filas),
        }
    )
    datos["ventas"] = (
        2_000
        - 0.02 * datos["precio_promedio"]
        + 300 * datos["promocion"]
        + 10 * datos["semana"]
        + rng.normal(0, 50, n_filas)
    ).round(0)
    if porcentaje_nulos > 0:
        filas = rng.choice(n_filas, int(n_filas * porcentaje_nulos), replace=False)
        datos.loc[filas, "precio_promedio"] = np.nan
    return datos


def main():
    # Genera el archivo de ventas con el porcentaje de nulos indicado.
    nulos = float(os.getenv("PORCENTAJE_NULOS", "0"))
    os.makedirs("data", exist_ok=True)
    generar_ventas(porcentaje_nulos=nulos).to_csv(RUTA_SALIDA, index=False)
    print(f"Datos sintéticos generados en {RUTA_SALIDA} (nulos: {nulos:.0%})")


if __name__ == "__main__":
    main()
