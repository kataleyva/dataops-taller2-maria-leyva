# Carga la configuración del modelo desde YAML.

import yaml

RUTA_CONFIG = "configs/modelo.yaml"


def cargar_config(ruta=RUTA_CONFIG):
    # Devuelve la configuración como diccionario.
    with open(ruta, encoding="utf-8") as archivo:
        return yaml.safe_load(archivo)
