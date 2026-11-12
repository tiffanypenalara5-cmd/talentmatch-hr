from modulos.vacantes import Criterio, Vacante, validar_vacante

# CASO 1: vacante correcta (los pesos suman 100)
vacante_ok = Vacante(
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

# CASO 2: vacante con errores a propósito
vacante_mala = Vacante(
    nombre="Vacante con errores",
    criterios=[
        Criterio("Carrera afín", "Formación académica", 30, []),
        Criterio("Experiencia", "Experiencia", 40, minimo=0),
    ],
)

print("--- CASO 1 (debería ser válida) ---")
errores = validar_vacante(vacante_ok)
print("Sin errores" if not errores else errores)

print()
print("--- CASO 2 (debería mostrar errores) ---")
for e in validar_vacante(vacante_mala):
    print("-", e)
