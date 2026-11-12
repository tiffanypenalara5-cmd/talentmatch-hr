from modulos.extractor import extraer_informacion, buscar_palabras

CV_COMPLETO = """CANDIDATA FICTICIA 001
Correo: ficticia001@ejemplo.com

FORMACION ACADEMICA
Bachillerato en Administración de Recursos Humanos

EXPERIENCIA
Asistente de Recursos Humanos, 3 años

COMPETENCIAS TECNICAS
Excel avanzado, reclutamiento y selección

IDIOMAS
Inglés nivel B2
"""

CV_INCOMPLETO = """CANDIDATO FICTICIO 002

FORMACION ACADEMICA
Técnico en Gestión Administrativa

COMPETENCIAS TECNICAS
Word, Excel, atención al cliente
"""

CV_CON_RANGOS = """CANDIDATA FICTICIA 003

EXPERIENCIA LABORAL
Auxiliar de personal, 2018 - 2021
Coordinadora de reclutamiento, 2021 - 2023

IDIOMAS
Inglés B1
Francés básico
"""

CV_SIN_DURACION = """CANDIDATO FICTICIO 004

EXPERIENCIA
Apoyo en tareas administrativas y atención de usuarios
"""


def mostrar(nombre, texto):
    info = extraer_informacion(texto)
    print(f"--- {nombre} ---")
    for seccion, contenido in info["secciones"].items():
        estado = "con información" if contenido else "SIN INFORMACIÓN"
        print(f"  {seccion}: {estado}")
    anios = info["anios_experiencia"]
    print("  Años de experiencia:", anios if anios is not None else "SIN EVIDENCIA")
    print("  Idiomas:", info["idiomas"] if info["idiomas"] else "SIN EVIDENCIA")
    print("  Busco 'excel':", buscar_palabras(texto, ["excel"]))
    print()


mostrar("CASO 1: CV completo", CV_COMPLETO)
mostrar("CASO 2: CV incompleto", CV_INCOMPLETO)
mostrar("CASO 3: experiencia con rangos de años", CV_CON_RANGOS)
mostrar("CASO 4: experiencia sin duración", CV_SIN_DURACION)