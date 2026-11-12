"""Genera 20 currículums FICTICIOS en PDF y 2 archivos defectuosos para pruebas de error.

Todos los datos son inventados: no corresponden a personas reales.
Ejecutar desde la carpeta del proyecto:  python -m datos.generar_cvs
"""

import os

CARPETA = "datos/cvs_ficticios"


def cv(formacion=None, experiencia=None, competencias=None,
       idiomas=None, conocimientos=None, personales=None):
    """Crea la ficha de un candidato. Lo que se deja en None NO aparece en el CV."""
    return {
        "formacion": formacion,
        "experiencia": experiencia,
        "competencias": competencias,
        "idiomas": idiomas,
        "conocimientos": conocimientos,
        "personales": personales,
    }


CANDIDATOS = [
    # 001: perfil fuerte y completo
    cv("Bachillerato en Administración de Recursos Humanos",
       ["Asistente de Recursos Humanos, 2019 - 2023"],
       "Excel avanzado, reclutamiento y selección",
       ["Inglés C1"],
       "Código de Trabajo, legislación laboral",
       (24, "Soltera")),
    # 002: perfil fuerte, otra carrera afín
    cv("Licenciatura en Psicología",
       ["Psicóloga organizacional, 2018 - 2024"],
       "Excel intermedio, evaluación de personal",
       ["Inglés B2"],
       "Código de Trabajo, clima organizacional"),
    # 003: carrera no afín
    cv("Bachillerato en Administración de Empresas",
       ["Auxiliar administrativo, 2021 - 2023"],
       "Word, Excel",
       ["Inglés A2"],
       "Atención al cliente"),
    # 004: perfil débil
    cv("Técnico en Gestión Administrativa",
       ["Recepcionista, 1 año"],
       "Word, correo electrónico"),
    # 005: experiencia hasta la actualidad
    cv("Licenciatura en Administración de Recursos Humanos",
       ["Reclutadora, 2022 - actualidad"],
       "Excel avanzado, entrevistas por competencias",
       ["Inglés B1", "Francés A2"],
       "Reclutamiento y selección, Código de Trabajo"),
    # 006: CV muy incompleto (sin experiencia, idiomas ni conocimientos)
    cv("Bachillerato en Psicología",
       None,
       "Excel básico"),
    # 007: experiencia sin indicar duración
    cv("Diplomado en Recursos Humanos",
       ["Apoyo en tareas administrativas y atención de usuarios"],
       "Excel, Word",
       ["Inglés B2"]),
    # 008: recién graduada, sin experiencia
    cv("Bachillerato en Administración de Recursos Humanos",
       None,
       "Excel intermedio",
       ["Inglés B1"],
       "Código de Trabajo (curso universitario)"),
    # 009: sin sección de formación
    cv(None,
       ["Asistente de planillas, 2017 - 2022"],
       "Excel avanzado",
       ["Inglés B2"],
       "Código de Trabajo, planillas"),
    # 010: mucha experiencia, sin Excel
    cv("Licenciatura en Psicología",
       ["Psicóloga en consultorio privado, 6 años"],
       "Evaluación psicométrica",
       None,
       "Código de Trabajo"),
    # 011: otros idiomas, sin inglés
    cv("Bachillerato en Administración de Recursos Humanos",
       ["Asistente de personal, 2020 - 2022"],
       "Excel avanzado",
       ["Francés B2", "Portugués A2"],
       "Reclutamiento"),
    # 012: IGUAL a 001, solo cambian los datos personales (prueba de no discriminación)
    cv("Bachillerato en Administración de Recursos Humanos",
       ["Asistente de Recursos Humanos, 2019 - 2023"],
       "Excel avanzado, reclutamiento y selección",
       ["Inglés C1"],
       "Código de Trabajo, legislación laboral",
       (52, "Casado")),
    # 013: experiencia insuficiente
    cv("Bachillerato en Psicología",
       ["Asistente de selección de personal, 2023 - 2024"],
       "Excel básico",
       ["Inglés A2"],
       "Selección y reclutamiento"),
    # 014: mucha experiencia en RR.HH.
    cv("Licenciatura en Administración de Recursos Humanos",
       ["Analista de Recursos Humanos, 2015 - 2024"],
       "Excel avanzado, nómina",
       ["Inglés C1"],
       "Código de Trabajo, relaciones laborales"),
    # 015: carrera no afín, buena experiencia
    cv("Técnico en Contabilidad",
       ["Asistente contable, 2019 - 2024"],
       "Excel avanzado, contabilidad",
       ["Inglés B1"],
       "NIIF"),
    # 016: CV casi vacío
    cv("Bachillerato en Administración de Recursos Humanos"),
    # 017: perfil medio
    cv("Licenciatura en Psicología",
       ["Orientadora vocacional, 2021 - 2024"],
       "Excel intermedio",
       ["Inglés B2"],
       "Reclutamiento"),
    # 018: sin conocimientos específicos
    cv("Bachillerato en Administración de Recursos Humanos",
       ["Asistente administrativa, 2022 - 2024"],
       "Excel avanzado",
       ["Inglés B1"]),
    # 019: sin idiomas
    cv("Licenciatura en Administración de Recursos Humanos",
       ["Coordinadora de personal, 2016 - 2022"],
       "Excel avanzado, reclutamiento",
       None,
       "Código de Trabajo"),
    # 020: carrera no afín, buena experiencia técnica
    cv("Técnico en Informática",
       ["Soporte técnico, 2020 - 2024"],
       "Excel avanzado, bases de datos",
       ["Inglés B2"],
       "Redes"),
]


def construir_texto(numero, c):
    """Arma el texto del CV de un candidato."""
    lineas = [
        f"CANDIDATO FICTICIO {numero:03d}",
        f"Correo: ficticio{numero:03d}@ejemplo.com",
        "",
    ]
    if c["personales"]:
        edad, estado_civil = c["personales"]
        lineas += ["DATOS PERSONALES", f"Edad: {edad} años",
                   f"Estado civil: {estado_civil}", ""]
    if c["formacion"]:
        lineas += ["FORMACION ACADEMICA", c["formacion"], ""]
    if c["experiencia"]:
        lineas += ["EXPERIENCIA LABORAL"] + c["experiencia"] + [""]
    if c["competencias"]:
        lineas += ["COMPETENCIAS TECNICAS", c["competencias"], ""]
    if c["idiomas"]:
        lineas += ["IDIOMAS"] + c["idiomas"] + [""]
    if c["conocimientos"]:
        lineas += ["CONOCIMIENTOS ESPECIFICOS", c["conocimientos"], ""]
    return "\n".join(lineas)


def generar():
    import pymupdf  # se importa aquí para poder reutilizar CANDIDATOS sin PyMuPDF

    os.makedirs(CARPETA, exist_ok=True)

    for numero, c in enumerate(CANDIDATOS, start=1):
        doc = pymupdf.open()
        pagina = doc.new_page()
        pagina.insert_text((72, 72), construir_texto(numero, c), fontsize=11)
        doc.save(os.path.join(CARPETA, f"cv_{numero:03d}.pdf"))
        doc.close()

    # Archivo defectuoso 1: PDF sin texto (simula una imagen escaneada)
    doc = pymupdf.open()
    doc.new_page()
    doc.save(os.path.join(CARPETA, "cv_error_sin_texto.pdf"))
    doc.close()

    # Archivo defectuoso 2: archivo dañado que no es un PDF real
    with open(os.path.join(CARPETA, "cv_error_danado.pdf"), "wb") as f:
        f.write(b"Este archivo no es un PDF real.")

    print(f"Listo: {len(CANDIDATOS)} CV ficticios + 2 archivos defectuosos "
          f"en {CARPETA}")


if __name__ == "__main__":
    generar()