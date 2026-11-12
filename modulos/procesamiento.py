"""Procesamiento por lotes: lee varios CV, los evalúa y separa los que dieron error."""

import os

from modulos.lector_pdf import extraer_texto, ErrorLecturaPDF
from modulos.evaluador import evaluar_candidato

MAX_BYTES = 5 * 1024 * 1024  # 5 MB por archivo


def evaluar_lote(vacante, archivos):
    """Recibe una lista de (nombre_archivo, contenido_en_bytes).
    Devuelve (resultados, errores). Un archivo con problemas no detiene a los demás."""
    resultados = []
    errores = []
    for nombre, contenido in archivos:
        try:
            if len(contenido) > MAX_BYTES:
                raise ErrorLecturaPDF("El archivo pesa más de 5 MB.")
            texto = extraer_texto(contenido)["texto"]
            nombre_corto = os.path.splitext(nombre)[0]
            resultados.append(evaluar_candidato(vacante, nombre_corto, texto))
        except ErrorLecturaPDF as error:
            errores.append({"Archivo": nombre, "Motivo": str(error)})
    return resultados, errores


def leer_carpeta(carpeta):
    """Lee los PDF de una carpeta y devuelve una lista de (nombre, bytes)."""
    if not os.path.isdir(carpeta):
        return []
    lote = []
    for nombre in sorted(os.listdir(carpeta)):
        if nombre.lower().endswith(".pdf") and nombre != "cv_demo.pdf":
            with open(os.path.join(carpeta, nombre), "rb") as f:
                lote.append((nombre, f.read()))
    return lote