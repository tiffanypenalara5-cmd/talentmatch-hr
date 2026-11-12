from modulos.vacantes import Criterio, Vacante
from modulos.evaluador import evaluar_candidato, generar_ranking

vacante = Vacante(
    nombre="Analista de Recursos Humanos",
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

CV1 = """CANDIDATA FICTICIA 001

FORMACION ACADEMICA
Bachillerato en Administración de Recursos Humanos

EXPERIENCIA
Asistente de Recursos Humanos, 3 años

COMPETENCIAS TECNICAS
Excel avanzado, reclutamiento y selección

IDIOMAS
Inglés nivel B2
"""

CV2 = """CANDIDATO FICTICIO 002

FORMACION ACADEMICA
Técnico en Gestión Administrativa

COMPETENCIAS TECNICAS
Word, Excel, atención al cliente
"""

CV3 = """CANDIDATA FICTICIA 003

EXPERIENCIA LABORAL
Auxiliar de personal, 2018 - 2021
Coordinadora de reclutamiento, 2021 - 2023

IDIOMAS
Inglés B1
Francés básico
"""

CV4 = """CANDIDATO FICTICIO 004

EXPERIENCIA
Apoyo en tareas administrativas y atención de usuarios
"""

resultados = [
    evaluar_candidato(vacante, "CV 1 completo", CV1),
    evaluar_candidato(vacante, "CV 2 incompleto", CV2),
    evaluar_candidato(vacante, "CV 3 rangos", CV3),
    evaluar_candidato(vacante, "CV 4 sin duración", CV4),
]

print("=== RANKING ===")
ranking = generar_ranking(resultados)
columnas = ["Posición", "Candidato", "Puntaje confirmado",
            "Puntaje posible", "Cobertura (%)"]
print(ranking[columnas].to_string(index=False))

print()
print("=== DETALLE: CV 2 incompleto ===")
for d in resultados[1]["detalle"]:
    puntos = "sin calificar" if d["Puntos"] is None else f"{d['Puntos']:g} pts"
    print(f"- {d['Criterio']}: {d['Estado']} ({puntos})")
    print(f"    {d['Explicación']}")