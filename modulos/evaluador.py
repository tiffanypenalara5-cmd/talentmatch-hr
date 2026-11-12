"""Módulo evaluador: compara los CV con una vacante y calcula los puntajes.

Regla central: la AUSENCIA de información en un CV NO se interpreta como falta
de competencia. Se marca "Sin evidencia" y se recomienda revisión manual.
El resultado apoya la decisión del reclutador; no la sustituye.
"""

import pandas as pd

from modulos.extractor import extraer_informacion, buscar_palabras
from modulos.vacantes import validar_vacante

CUMPLE = "Cumple"
NO_CUMPLE = "No cumple"
SIN_EVIDENCIA = "Sin evidencia"


def evaluar_criterio(criterio, texto, info):
    """Devuelve (estado, explicación) para un criterio."""
    seccion = info["secciones"].get(criterio.categoria)

    if criterio.categoria == "Experiencia":
        anios = info["anios_experiencia"]
        if anios is None:
            return SIN_EVIDENCIA, "El CV no indica la duración de la experiencia."
        detalle = f"Acredita {anios:g} años (mínimo {criterio.minimo:g})."
        if anios >= criterio.minimo:
            return CUMPLE, detalle
        return NO_CUMPLE, detalle

    encontradas = buscar_palabras(texto, criterio.palabras_clave)
    if encontradas:
        return CUMPLE, "Evidencia encontrada: " + ", ".join(encontradas) + "."
    if seccion:
        return NO_CUMPLE, (f"La sección '{criterio.categoria}' existe, "
                           "pero no menciona lo solicitado.")
    return SIN_EVIDENCIA, (f"El CV no tiene sección de '{criterio.categoria}' "
                           "ni menciona lo solicitado.")


def evaluar_candidato(vacante, nombre, texto):
    """Evalúa un CV contra la vacante y devuelve un diccionario con el resultado."""
    errores = validar_vacante(vacante)
    if errores:
        raise ValueError("La vacante no es válida: " + " ".join(errores))

    info = extraer_informacion(texto)
    total_pesos = sum(c.peso for c in vacante.criterios)
    confirmado = posible = verificable = 0.0
    detalle = []

    for c in vacante.criterios:
        estado, explicacion = evaluar_criterio(c, texto, info)
        peso = float(c.peso)
        if estado == CUMPLE:
            puntos = peso
            confirmado += peso
            posible += peso
            verificable += peso
        elif estado == NO_CUMPLE:
            puntos = 0.0
            verificable += peso
        else:
            puntos = None  # no se sabe
            posible += peso
        detalle.append({
            "Criterio": c.nombre,
            "Categoría": c.categoria,
            "Peso": peso,
            "Estado": estado,
            "Puntos": puntos,
            "Explicación": explicacion,
        })

    n_sin = sum(1 for d in detalle if d["Estado"] == SIN_EVIDENCIA)
    return {
        "candidato": nombre,
        "puntaje_confirmado": round(confirmado, 1),
        "puntaje_posible": round(posible, 1),
        "cobertura": round(verificable / total_pesos * 100, 1),
        "cumplidos": sum(1 for d in detalle if d["Estado"] == CUMPLE),
        "no_cumplidos": sum(1 for d in detalle if d["Estado"] == NO_CUMPLE),
        "sin_evidencia": n_sin,
        "observacion": ("Evaluación completa" if n_sin == 0
                        else f"Revisión manual: {n_sin} criterio(s) sin evidencia"),
        "detalle": detalle,
    }


def generar_ranking(resultados):
    """Recibe una lista de resultados y devuelve una tabla ordenada (pandas)."""
    filas = [{
        "Candidato": r["candidato"],
        "Puntaje confirmado": r["puntaje_confirmado"],
        "Puntaje posible": r["puntaje_posible"],
        "Cobertura (%)": r["cobertura"],
        "Cumplidos": r["cumplidos"],
        "No cumplidos": r["no_cumplidos"],
        "Sin evidencia": r["sin_evidencia"],
        "Observación": r["observacion"],
    } for r in resultados]

    tabla = pd.DataFrame(filas)
    tabla = tabla.sort_values(
        by=["Puntaje confirmado", "Puntaje posible"], ascending=False
    ).reset_index(drop=True)
    tabla.insert(0, "Posición", tabla.index + 1)
    return tabla