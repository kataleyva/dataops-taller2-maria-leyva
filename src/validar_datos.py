# Test de datos: valida la calidad de los datos antes de entrenar.

import sys

import pandas as pd

from config import cargar_config


def validar(datos, columnas, max_nulos):
    # Devuelve la lista de errores encontrados (vacía si los datos son válidos).
    errores = []
    faltantes = set(columnas) - set(datos.columns)
    if faltantes:
        errores.append(f"Columnas faltantes: {sorted(faltantes)}")
    for columna, porcentaje in datos.isna().mean().items():
        if porcentaje > max_nulos:
            errores.append(
                f"Columna '{columna}' con {porcentaje:.0%} de nulos "
                f"(máximo permitido: {max_nulos:.0%})"
            )
    if "ventas" in datos.columns and (datos["ventas"] < 0).any():
        errores.append("Hay ventas negativas")
    return errores


def main():
    # Detiene el pipeline si los datos no cumplen las reglas de calidad.
    config = cargar_config()["datos"]
    datos = pd.read_csv(config["ruta"])
    errores = validar(datos, config["columnas"], config["max_porcentaje_nulos"])
    if errores:
        for error in errores:
            print(f"[Test de datos] ERROR: {error}")
        print("[Test de datos] Pipeline detenido: el modelo NO se entrena.")
        sys.exit(1)
    print(f"[Test de datos] OK: {len(datos)} filas válidas.")


if __name__ == "__main__":
    main()
