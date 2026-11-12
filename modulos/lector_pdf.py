"""Módulo lector de PDF: extrae el texto de un currículum y valida el archivo."""

import os
import pymupdf

MIN_CARACTERES = 30


class ErrorLecturaPDF(Exception):
    """Se usa cuando un PDF no se puede leer. El mensaje es apto para mostrarlo al usuario."""


def extraer_texto(origen):
    """Recibe una ruta (texto) o el contenido del archivo (bytes).
    Devuelve un diccionario con el texto y el número de páginas."""

    if isinstance(origen, (bytes, bytearray)):
        if len(origen) == 0:
            raise ErrorLecturaPDF("El archivo está vacío.")
        abrir = lambda: pymupdf.open(stream=bytes(origen), filetype="pdf")
    else:
        ruta = str(origen)
        if not ruta.lower().endswith(".pdf"):
            raise ErrorLecturaPDF("El archivo no tiene extensión .pdf.")
        if not os.path.isfile(ruta):
            raise ErrorLecturaPDF("No se encontró el archivo.")
        abrir = lambda: pymupdf.open(ruta)

    try:
        doc = abrir()
    except Exception:
        raise ErrorLecturaPDF("El archivo no es un PDF válido o está dañado.") from None

    try:
        if doc.needs_pass:
            raise ErrorLecturaPDF("El PDF está protegido con contraseña.")
        paginas = [pagina.get_text() for pagina in doc]
    finally:
        doc.close()

    texto = "\n".join(paginas).strip()
    if len(texto) < MIN_CARACTERES:
        raise ErrorLecturaPDF(
            "El PDF no contiene texto legible (puede ser una imagen escaneada). "
            "No se puede evaluar automáticamente: revise este CV manualmente."
        )

    return {"texto": texto, "paginas": len(paginas)}