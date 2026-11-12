"""Conversiones entre la tabla editable de la pantalla y los objetos Vacante."""

import pandas as pd

from modulos.vacantes import Criterio, Vacante

COLUMNAS = ["Criterio", "Categoría", "Peso (%)", "Palabras clave", "Años mínimos"]


def vacante_ejemplo():
    """Vacante de ejemplo para que el programa arranque con datos."""
    return Vacante(
        nombre="Analista de Recursos Humanos",
        descripcion="Apoyo en reclutamiento, selección y administración de personal.",
        criterios=[
            Criterio("Carrera afín", "Formación académica", 20,
                     ["administración de recursos humanos", "psicología"]),
            Criterio("Experiencia en RR.HH.", "Experiencia", 25, minimo=2),
            Criterio("Manejo de Excel", "Competencias técnicas", 25, ["excel"]),
            Criterio("Inglés", "Idiomas", 15, ["inglés"]),
            Criterio("Código de Trabajo", "Conocimientos específicos", 15,
                     ["código de trabajo", "reclutamiento"]),
        ],
    )


def vacante_a_tabla(vacante):
    """Convierte una Vacante en la tabla que se muestra en pantalla."""
    filas = [{
        "Criterio": c.nombre,
        "Categoría": c.categoria,
        "Peso (%)": float(c.peso),
        "Palabras clave": ", ".join(c.palabras_clave),
        "Años mínimos": float(c.minimo),
    } for c in vacante.criterios]
    return pd.DataFrame(filas, columns=COLUMNAS)


def _texto(valor):
    return "" if pd.isna(valor) else str(valor).strip()


def _numero(valor):
    if pd.isna(valor):
        return 0.0
    try:
        return float(valor)
    except (TypeError, ValueError):
        return 0.0


def tabla_a_vacante(nombre, descripcion, tabla):
    """Convierte la tabla editada en una Vacante. Ignora las filas totalmente vacías."""
    criterios = []
    for _, fila in tabla.iterrows():
        nombre_c = _texto(fila.get("Criterio"))
        categoria = _texto(fila.get("Categoría"))
        peso = _numero(fila.get("Peso (%)"))
        palabras = [p.strip() for p in _texto(fila.get("Palabras clave")).split(",")
                    if p.strip()]
        minimo = _numero(fila.get("Años mínimos"))

        if not nombre_c and not categoria and peso == 0 and not palabras and minimo == 0:
            continue  # fila vacía: se ignora
        criterios.append(Criterio(nombre_c, categoria, peso, palabras, minimo))

    return Vacante(nombre=(nombre or ""), descripcion=(descripcion or ""),
                   criterios=criterios)