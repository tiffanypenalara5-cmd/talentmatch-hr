import os

from modulos.vacantes import Criterio, Vacante
from modulos.lector_pdf import extraer_texto, ErrorLecturaPDF
from modulos.evaluador import evaluar_candidato, generar_ranking

CARPETA = "datos/cvs_ficticios"

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

resultados = []
errores = []

for archivo in sorted(os.listdir(CARPETA)):
    if not archivo.lower().endswith(".pdf") or archivo == "cv_demo.pdf":
        continue
    ruta = os.path.join(CARPETA, archivo)
    try:
        texto = extraer_texto(ruta)["texto"]
        resultados.append(evaluar_candidato(vacante, archivo, texto))
    except ErrorLecturaPDF as error:
        errores.append((archivo, str(error)))

print(f"CV evaluados: {len(resultados)}")
print()
ranking = generar_ranking(resultados)
columnas = ["Posición", "Candidato", "Puntaje confirmado", "Puntaje posible",
            "Cobertura (%)", "Cumplidos", "No cumplidos", "Sin evidencia"]
print(ranking[columnas].to_string(index=False))

print()
print(f"Archivos con error: {len(errores)}")
for archivo, mensaje in errores:
    print("-", archivo, ":", mensaje)