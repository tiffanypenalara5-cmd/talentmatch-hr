"""Módulo de vacantes: define qué se busca y valida la configuración."""

from dataclasses import dataclass, field

CATEGORIAS = [
    "Formación académica",
    "Experiencia",
    "Competencias técnicas",
    "Idiomas",
    "Conocimientos específicos",
]


@dataclass
class Criterio:
    nombre: str
    categoria: str
    peso: float  # porcentaje, de 0 a 100
    palabras_clave: list = field(default_factory=list)  # lo que buscaremos en el CV
    minimo: float = 0  # solo para Experiencia: años mínimos


@dataclass
class Vacante:
    nombre: str
    descripcion: str = ""
    criterios: list = field(default_factory=list)


def validar_vacante(vacante):
    """Devuelve una lista de errores. Lista vacía = la vacante es válida."""
    errores = []

    if not vacante.nombre.strip():
        errores.append("La vacante debe tener un nombre.")

    if len(vacante.criterios) == 0:
        errores.append("La vacante debe tener al menos un criterio.")
        return errores

    for c in vacante.criterios:
        if not c.nombre.strip():
            errores.append("Hay un criterio sin nombre.")
        if c.categoria not in CATEGORIAS:
            errores.append(f"'{c.nombre}': la categoría '{c.categoria}' no existe.")
        if c.peso <= 0 or c.peso > 100:
            errores.append(f"'{c.nombre}': el peso debe ser mayor que 0 y máximo 100.")
        if c.categoria == "Experiencia":
            if c.minimo <= 0:
                errores.append(f"'{c.nombre}': indique los años mínimos de experiencia.")
        elif len(c.palabras_clave) == 0:
            errores.append(f"'{c.nombre}': agregue al menos una palabra clave.")

    suma = sum(c.peso for c in vacante.criterios)
    if abs(suma - 100) > 0.01:
        errores.append(f"Los pesos suman {suma:g}% y deben sumar exactamente 100%.")

    return errores