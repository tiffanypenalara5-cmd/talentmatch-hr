"""Informes en Word (individual y comparativo) y exportación de resultados (Excel y CSV)."""

import io
from datetime import date

import pandas as pd
from docx import Document
from docx.shared import Pt

from modulos.evaluador import generar_ranking, CUMPLE, NO_CUMPLE, SIN_EVIDENCIA

NOTA_METODOLOGICA = (
    "TalentMatch HR compara el texto de cada currículum con los criterios definidos para la "
    "vacante. Cada criterio se clasifica como «Cumple» (hay evidencia en el CV), «No cumple» "
    "(el CV tiene la sección correspondiente pero no menciona lo solicitado) o «Sin evidencia» "
    "(el CV no trae esa información). La ausencia de información NO se interpreta como falta de "
    "competencia: esos criterios requieren verificación manual. El puntaje confirmado suma los "
    "pesos de los criterios cumplidos; el puntaje posible es el máximo que alcanzaría si se "
    "cumplieran también los criterios sin evidencia. La herramienta no utiliza edad, sexo, "
    "estado civil, nacionalidad ni otras características personales para puntuar. Es un apoyo "
    "para la preselección: la decisión final corresponde siempre al profesional de Recursos "
    "Humanos. Este proyecto trabaja únicamente con datos ficticios (Ley 8968)."
)


def _fecha():
    return date.today().strftime("%d/%m/%Y")


def _g(numero):
    """Número sin decimales innecesarios (100.0 -> 100)."""
    return f"{numero:g}"


def _tabla(doc, encabezados, filas, tamano=9):
    tabla = doc.add_table(rows=1, cols=len(encabezados))
    tabla.style = "Light Grid Accent 1"
    for i, texto in enumerate(encabezados):
        celda = tabla.rows[0].cells[i]
        celda.text = ""
        run = celda.paragraphs[0].add_run(str(texto))
        run.bold = True
        run.font.size = Pt(tamano)
    for fila in filas:
        celdas = tabla.add_row().cells
        for i, valor in enumerate(fila):
            celdas[i].text = ""
            texto = "" if valor is None else str(valor)
            celdas[i].paragraphs[0].add_run(texto).font.size = Pt(tamano)
    return tabla


def _a_bytes(doc):
    salida = io.BytesIO()
    doc.save(salida)
    return salida.getvalue()


def _condicion(criterio):
    if criterio.categoria == "Experiencia":
        return f"Mínimo {_g(criterio.minimo)} años"
    return ", ".join(criterio.palabras_clave)


def informe_individual(vacante, r):
    """Informe en Word de un candidato. Devuelve el archivo como bytes."""
    doc = Document()
    doc.add_heading("Informe individual de evaluación", level=0)
    doc.add_paragraph(f"Vacante: {vacante.nombre}")
    doc.add_paragraph(f"Candidato: {r['candidato']}")
    doc.add_paragraph(f"Fecha del informe: {_fecha()}")

    doc.add_heading("Resumen", level=1)
    _tabla(doc, ["Indicador", "Resultado"], [
        ["Puntaje confirmado", f"{_g(r['puntaje_confirmado'])} de 100"],
        ["Puntaje posible", f"{_g(r['puntaje_posible'])} de 100"],
        ["Cobertura de la evaluación", f"{_g(r['cobertura'])}%"],
        ["Criterios cumplidos", r["cumplidos"]],
        ["Criterios no cumplidos", r["no_cumplidos"]],
        ["Criterios sin evidencia", r["sin_evidencia"]],
        ["Observación", r["observacion"]],
    ], tamano=10)

    doc.add_heading("Detalle por criterio", level=1)
    _tabla(doc, ["Criterio", "Categoría", "Peso (%)", "Estado", "Puntos", "Explicación"], [
        [d["Criterio"], d["Categoría"], _g(d["Peso"]), d["Estado"],
         "sin calificar" if d["Puntos"] is None else _g(d["Puntos"]), d["Explicación"]]
        for d in r["detalle"]
    ])

    doc.add_heading("Interpretación", level=1)
    for estado, titulo in [(CUMPLE, "Criterios cumplidos"),
                           (NO_CUMPLE, "Criterios no cumplidos"),
                           (SIN_EVIDENCIA, "Criterios sin evidencia")]:
        nombres = [d["Criterio"] for d in r["detalle"] if d["Estado"] == estado]
        doc.add_paragraph(f"{titulo}: {', '.join(nombres) if nombres else 'ninguno'}.",
                          style="List Bullet")
    if r["sin_evidencia"] > 0:
        doc.add_paragraph(
            "Los criterios sin evidencia no se consideran incumplimientos. Se recomienda "
            "verificarlos en una entrevista o solicitando información adicional al candidato.")

    doc.add_heading("Nota metodológica", level=1)
    doc.add_paragraph(NOTA_METODOLOGICA)
    return _a_bytes(doc)


def informe_comparativo(vacante, resultados, errores=None):
    """Informe en Word que compara a todos los candidatos. Devuelve bytes."""
    ranking = generar_ranking(resultados)
    por_nombre = {r["candidato"]: r for r in resultados}

    doc = Document()
    doc.add_heading("Informe comparativo de candidatos", level=0)
    doc.add_paragraph(f"Vacante: {vacante.nombre}")
    if vacante.descripcion:
        doc.add_paragraph(vacante.descripcion)
    doc.add_paragraph(f"Fecha del informe: {_fecha()}")
    doc.add_paragraph(f"Candidatos evaluados: {len(resultados)}")

    doc.add_heading("Criterios de la vacante", level=1)
    _tabla(doc, ["Criterio", "Categoría", "Peso (%)", "Condición"],
           [[c.nombre, c.categoria, _g(c.peso), _condicion(c)] for c in vacante.criterios])

    doc.add_heading("Ranking", level=1)
    _tabla(doc, ["Pos.", "Candidato", "Confirmado", "Posible", "Cobertura (%)", "Observación"],
           [[f["Posición"], f["Candidato"], _g(f["Puntaje confirmado"]),
             _g(f["Puntaje posible"]), _g(f["Cobertura (%)"]), f["Observación"]]
            for _, f in ranking.iterrows()])

    mejor = ranking["Puntaje confirmado"].max()
    empatados = int((ranking["Puntaje confirmado"] == mejor).sum())
    if empatados > 1:
        doc.add_paragraph(
            f"Nota: {empatados} candidatos comparten el puntaje confirmado más alto "
            f"({_g(mejor)}). Su orden en la tabla no implica diferencia entre ellos.")

    doc.add_heading("Comparación por criterio", level=1)
    nombres_criterios = [c.nombre for c in vacante.criterios]
    filas = []
    for _, f in ranking.iterrows():
        detalle = por_nombre[f["Candidato"]]["detalle"]
        filas.append([f["Candidato"]] + [d["Estado"] for d in detalle])
    _tabla(doc, ["Candidato"] + nombres_criterios, filas, tamano=8)

    pendientes = [r["candidato"] for r in resultados if r["sin_evidencia"] > 0]
    doc.add_heading("Candidatos que requieren revisión manual", level=1)
    if pendientes:
        doc.add_paragraph(
            f"{len(pendientes)} candidato(s) tienen criterios sin evidencia: "
            + ", ".join(pendientes) + ".")
    else:
        doc.add_paragraph("Todas las evaluaciones están completas.")

    if errores:
        doc.add_heading("Archivos que no se pudieron evaluar", level=1)
        _tabla(doc, ["Archivo", "Motivo"], [[e["Archivo"], e["Motivo"]] for e in errores])

    doc.add_heading("Nota metodológica", level=1)
    doc.add_paragraph(NOTA_METODOLOGICA)
    return _a_bytes(doc)


def ranking_csv(resultados):
    """Ranking en CSV (con codificación que Excel abre bien con tildes)."""
    return generar_ranking(resultados).to_csv(index=False).encode("utf-8-sig")


def exportar_excel(vacante, resultados, errores=None):
    """Libro de Excel con cuatro hojas: Ranking, Detalle, Vacante y Archivos con error."""
    ranking = generar_ranking(resultados)
    detalle = pd.DataFrame([{
        "Candidato": r["candidato"],
        "Criterio": d["Criterio"],
        "Categoría": d["Categoría"],
        "Peso (%)": d["Peso"],
        "Estado": d["Estado"],
        "Puntos": d["Puntos"],
        "Explicación": d["Explicación"],
    } for r in resultados for d in r["detalle"]])
    criterios = pd.DataFrame([{
        "Criterio": c.nombre, "Categoría": c.categoria, "Peso (%)": c.peso,
        "Condición": _condicion(c),
    } for c in vacante.criterios])
    fallidos = pd.DataFrame(errores or [], columns=["Archivo", "Motivo"])

    salida = io.BytesIO()
    with pd.ExcelWriter(salida, engine="openpyxl") as escritor:
        ranking.to_excel(escritor, sheet_name="Ranking", index=False)
        detalle.to_excel(escritor, sheet_name="Detalle por criterio", index=False)
        criterios.to_excel(escritor, sheet_name="Vacante", index=False)
        fallidos.to_excel(escritor, sheet_name="Archivos con error", index=False)
        for hoja in escritor.sheets.values():
            for columna in hoja.columns:
                ancho = max(len(str(c.value)) if c.value is not None else 0 for c in columna)
                hoja.column_dimensions[columna[0].column_letter].width = min(60, ancho + 2)
    return salida.getvalue()