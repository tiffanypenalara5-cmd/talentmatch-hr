"""Módulo extractor: convierte el texto de un CV en datos organizados.

IMPORTANTE (Ley 8968 y no discriminación): este módulo NO extrae edad, sexo,
estado civil, nacionalidad, religión, foto ni otros datos personales protegidos.
Solo busca información relacionada con la idoneidad para el puesto.
"""

import re
import unicodedata
from datetime import date

SINONIMOS_SECCIONES = {
    "Formación académica": ["formacion academica", "formacion", "educacion",
                            "estudios", "estudios realizados"],
    "Experiencia": ["experiencia", "experiencia laboral",
                    "experiencia profesional", "historial laboral"],
    "Competencias técnicas": ["competencias tecnicas", "competencias",
                              "habilidades", "habilidades tecnicas", "herramientas"],
    "Idiomas": ["idiomas", "lenguas"],
    "Conocimientos específicos": ["conocimientos", "conocimientos especificos",
                                  "cursos", "capacitaciones", "certificaciones"],
}

# Encabezados que no se evalúan, pero sirven para cerrar la sección anterior
ENCABEZADOS_IGNORADOS = ["perfil", "perfil profesional", "resumen", "objetivo",
                         "datos personales", "informacion personal",
                         "referencias", "contacto"]

IDIOMAS_CONOCIDOS = {
    "ingles": "Inglés", "frances": "Francés", "portugues": "Portugués",
    "aleman": "Alemán", "italiano": "Italiano", "mandarin": "Mandarín",
    "japones": "Japonés",
}


def normalizar(texto):
    """Pasa a minúsculas y quita tildes, para comparar sin problemas."""
    texto = unicodedata.normalize("NFD", texto.lower())
    return "".join(c for c in texto if unicodedata.category(c) != "Mn")


def _identificar_encabezado(linea):
    """Devuelve (nombre_de_seccion, es_encabezado)."""
    limpia = re.sub(r"[^a-z\s]", "", normalizar(linea)).strip()
    if not limpia or len(limpia) > 40:
        return None, False
    for nombre, sinonimos in SINONIMOS_SECCIONES.items():
        if limpia in sinonimos:
            return nombre, True
    if limpia in ENCABEZADOS_IGNORADOS:
        return None, True
    return None, False


def separar_secciones(texto):
    """Devuelve un diccionario: sección -> texto. Si la sección no existe
    o está vacía, el valor es None (SIN INFORMACIÓN)."""
    partes = {nombre: [] for nombre in SINONIMOS_SECCIONES}
    actual = None
    for linea in texto.splitlines():
        seccion, es_encabezado = _identificar_encabezado(linea)
        if es_encabezado:
            actual = seccion
            continue
        if actual is not None and linea.strip():
            partes[actual].append(linea.strip())
    return {nombre: ("\n".join(lineas) if lineas else None)
            for nombre, lineas in partes.items()}


def calcular_anios_experiencia(texto_experiencia):
    """Suma los años de rangos como '2018 - 2021' y también lee frases como
    '3 años'. Devuelve None si no hay forma de saber la duración."""
    if not texto_experiencia:
        return None
    t = normalizar(texto_experiencia)
    anio_actual = date.today().year

    encontro_algo = False
    total_rangos = 0
    patron = (r"\b((?:19|20)\d{2})[ \t]*(?:-|–|a|al|hasta)[ \t]*"
              r"((?:19|20)\d{2}|actualidad|presente|actual)\b")
    for inicio, fin in re.findall(patron, t):
        fin_num = int(fin) if fin.isdigit() else anio_actual
        if fin_num >= int(inicio):
            total_rangos += fin_num - int(inicio)
            encontro_algo = True

    declarados = [int(n) for n in re.findall(r"(\d{1,2})\s*anos?\b", t)]
    if declarados:
        encontro_algo = True

    if not encontro_algo:
        return None
    return float(max(total_rangos, max(declarados, default=0)))


def extraer_idiomas(texto_idiomas):
    """Devuelve {idioma: nivel}. Si no hay sección de idiomas, devuelve {}."""
    resultado = {}
    if not texto_idiomas:
        return resultado
    for linea in texto_idiomas.splitlines():
        t = normalizar(linea)
        for clave, nombre in IDIOMAS_CONOCIDOS.items():
            if clave in t:
                nivel = re.search(r"\b([abc][12])\b", t)
                resultado[nombre] = nivel.group(1).upper() if nivel else "nivel no indicado"
    return resultado


def buscar_palabras(texto, palabras):
    """Devuelve cuáles de las palabras clave aparecen en el texto."""
    t = normalizar(texto)
    encontradas = []
    for palabra in palabras:
        patron = r"\b" + re.escape(normalizar(palabra)) + r"\b"
        if re.search(patron, t):
            encontradas.append(palabra)
    return encontradas


def extraer_informacion(texto):
    """Función principal: organiza todo lo que se puede saber del CV."""
    secciones = separar_secciones(texto)
    return {
        "secciones": secciones,
        "anios_experiencia": calcular_anios_experiencia(secciones["Experiencia"]),
        "idiomas": extraer_idiomas(secciones["Idiomas"]),
    }