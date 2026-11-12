"""Pantalla 'Informes y exportación'."""

import re

import streamlit as st

from modulos.estilos import encabezado
from modulos.informes import (informe_individual, informe_comparativo,
                              ranking_csv, exportar_excel)

MIME_DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
MIME_XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def pagina_informes():
    encabezado("Informes y exportación",
               "Descarga informes en Word y los resultados en Excel o CSV.")

    resultados = st.session_state.get("resultados")
    if not resultados:
        st.info("Primero evalúe candidatos en la sección «Candidatos y ranking».")
        return

    errores = st.session_state["errores"]
    vacante = st.session_state["vacante_evaluada"]

    if st.session_state["vacante"] != vacante:
        st.warning("La vacante cambió después de la evaluación. Los informes usan la "
                   "vacante con la que se evaluó; vuelva a evaluar para actualizarlos.")
    st.caption(f"Vacante evaluada: {vacante.nombre} · {len(resultados)} candidatos evaluados")

    st.subheader("Exportar resultados")
    c1, c2 = st.columns(2)
    c1.download_button("Descargar Excel (.xlsx)",
                       data=exportar_excel(vacante, resultados, errores),
                       file_name="resultados_talentmatch.xlsx", mime=MIME_XLSX)
    c2.download_button("Descargar ranking (.csv)",
                       data=ranking_csv(resultados),
                       file_name="ranking_talentmatch.csv", mime="text/csv")
    st.caption("El Excel incluye cuatro hojas: Ranking, Detalle por criterio, Vacante "
               "y Archivos con error.")

    st.subheader("Informe comparativo")
    st.caption("Compara a todos los candidatos: ranking, estado de cada criterio y "
               "quiénes requieren revisión manual.")
    st.download_button("Descargar informe comparativo (.docx)",
                       data=informe_comparativo(vacante, resultados, errores),
                       file_name="informe_comparativo.docx", mime=MIME_DOCX)

    st.subheader("Informe individual")
    elegido = st.selectbox("Candidato", [r["candidato"] for r in resultados])
    r = next(x for x in resultados if x["candidato"] == elegido)
    nombre_seguro = re.sub(r"[^\w\-]", "_", elegido)
    st.download_button("Descargar informe individual (.docx)",
                       data=informe_individual(vacante, r),
                       file_name=f"informe_{nombre_seguro}.docx", mime=MIME_DOCX)