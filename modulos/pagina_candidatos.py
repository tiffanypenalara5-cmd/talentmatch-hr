"""Pantalla 'Candidatos y ranking': carga de CV, evaluación, dashboard y detalle."""

import pandas as pd
import streamlit as st

from modulos.estilos import encabezado
from modulos.evaluador import generar_ranking, CUMPLE, NO_CUMPLE, SIN_EVIDENCIA
from modulos.procesamiento import evaluar_lote, leer_carpeta

CARPETA_EJEMPLO = "datos/cvs_ficticios"

ICONOS = {CUMPLE: "✅ Cumple", NO_CUMPLE: "❌ No cumple", SIN_EVIDENCIA: "⚠️ Sin evidencia"}


def _evaluar_y_guardar(vacante, lote):
    with st.spinner("Evaluando currículums..."):
        resultados, errores = evaluar_lote(vacante, lote)
    st.session_state["resultados"] = resultados
    st.session_state["errores"] = errores
    st.session_state["vacante_evaluada"] = vacante


def _pestana_ranking(resultados, errores):
    ranking = generar_ranking(resultados)

    f1, f2 = st.columns([2, 3])
    minimo = f1.slider("Puntaje confirmado mínimo", 0, 100, 0, step=5)
    solo_completos = f2.checkbox(
        "Mostrar solo evaluaciones completas (sin criterios sin evidencia)")

    filtrado = ranking[ranking["Puntaje confirmado"] >= minimo]
    if solo_completos:
        filtrado = filtrado[filtrado["Sin evidencia"] == 0]
    st.caption(f"Mostrando {len(filtrado)} de {len(ranking)} candidatos.")

    st.dataframe(
        filtrado,
        hide_index=True,
        column_config={
            "Puntaje confirmado": st.column_config.ProgressColumn(
                "Puntaje confirmado", min_value=0, max_value=100, format="%g"),
            "Puntaje posible": st.column_config.ProgressColumn(
                "Puntaje posible", min_value=0, max_value=100, format="%g"),
        },
    )
    st.caption("El ranking ordena por puntaje confirmado (criterios con evidencia). "
               "El puntaje posible es el máximo que alcanzaría si se cumplieran los criterios "
               "sin evidencia. Un criterio sin evidencia NO se cuenta como incumplimiento: "
               "requiere revisión manual del reclutador. Ojo: filtrar por puntaje confirmado "
               "puede ocultar candidatos con criterios sin evidencia.")

    if errores:
        st.subheader("Archivos que no se pudieron leer")
        st.warning("Estos archivos no fueron evaluados. Revíselos manualmente.")
        st.dataframe(pd.DataFrame(errores), hide_index=True)


def _pestana_dashboard(resultados):
    ranking = generar_ranking(resultados)

    m1, m2, m3 = st.columns(3)
    m1.metric("Puntaje confirmado promedio", f"{ranking['Puntaje confirmado'].mean():.1f}")
    m2.metric("Puntaje confirmado más alto", f"{ranking['Puntaje confirmado'].max():g}")
    m3.metric("Cobertura promedio", f"{ranking['Cobertura (%)'].mean():.1f}%")

    st.subheader("Puntaje confirmado por candidato")
    st.bar_chart(ranking.set_index("Candidato")[["Puntaje confirmado"]],
                 color="#0F766E")

    st.subheader("Estado de cada criterio en todos los candidatos")
    filas = {}
    for r in resultados:
        for d in r["detalle"]:
            fila = filas.setdefault(d["Criterio"],
                                    {CUMPLE: 0, NO_CUMPLE: 0, SIN_EVIDENCIA: 0})
            fila[d["Estado"]] += 1
    estados = pd.DataFrame.from_dict(filas, orient="index")[
        [CUMPLE, NO_CUMPLE, SIN_EVIDENCIA]]
    st.bar_chart(estados, color=["#0F766E", "#DC2626", "#F59E0B"])
    st.caption("Muestra cuántos candidatos cumplen, no cumplen o no tienen evidencia "
               "para cada criterio. Un criterio con muchos «sin evidencia» indica que "
               "los CV no traen esa información.")


def _pestana_detalle(resultados):
    nombres = [r["candidato"] for r in resultados]
    elegido = st.selectbox("Candidato", nombres)
    r = next(x for x in resultados if x["candidato"] == elegido)

    m1, m2, m3 = st.columns(3)
    m1.metric("Puntaje confirmado", f"{r['puntaje_confirmado']:g}")
    m2.metric("Puntaje posible", f"{r['puntaje_posible']:g}")
    m3.metric("Cobertura", f"{r['cobertura']:g}%")

    if r["sin_evidencia"] > 0:
        st.warning(r["observacion"] + ". La ausencia de información no equivale a "
                   "falta de competencia: verifique estos puntos con el candidato.")
    else:
        st.success(r["observacion"])

    tabla = pd.DataFrame([{
        "Criterio": d["Criterio"],
        "Categoría": d["Categoría"],
        "Peso (%)": d["Peso"],
        "Estado": ICONOS[d["Estado"]],
        "Puntos": d["Puntos"] if d["Puntos"] is not None else None,
        "Explicación": d["Explicación"],
    } for d in r["detalle"]])
    st.dataframe(tabla, hide_index=True)

    c1, c2, c3 = st.columns(3)
    for columna, estado, titulo in [(c1, CUMPLE, "Criterios cumplidos"),
                                    (c2, NO_CUMPLE, "Criterios no cumplidos"),
                                    (c3, SIN_EVIDENCIA, "Criterios sin evidencia")]:
        nombres_criterios = [d["Criterio"] for d in r["detalle"] if d["Estado"] == estado]
        columna.markdown(f"**{titulo} ({len(nombres_criterios)})**")
        for n in nombres_criterios:
            columna.markdown(f"- {n}")
        if not nombres_criterios:
            columna.markdown("- Ninguno")


def pagina_candidatos():
    encabezado("Candidatos y ranking",
               "Carga los currículums en PDF y revisa los resultados.")

    vacante = st.session_state["vacante"]
    st.caption(f"Vacante activa: {vacante.nombre}")

    archivos = st.file_uploader("Currículums en PDF", type=["pdf"],
                                accept_multiple_files=True)

    b1, b2 = st.columns(2)
    evaluar = b1.button("Evaluar candidatos", type="primary", disabled=not archivos)
    ejemplo = b2.button("Usar los CV ficticios de ejemplo")

    if evaluar:
        lote = [(a.name, a.getvalue()) for a in archivos]
        _evaluar_y_guardar(vacante, lote)
    elif ejemplo:
        lote = leer_carpeta(CARPETA_EJEMPLO)
        if lote:
            _evaluar_y_guardar(vacante, lote)
        else:
            st.error(f"No se encontraron PDF en la carpeta {CARPETA_EJEMPLO}. "
                     "Ejecute primero: python -m datos.generar_cvs")

    if "resultados" not in st.session_state:
        st.info("Cargue uno o más PDF y presione «Evaluar candidatos», "
                "o use los CV ficticios de ejemplo.")
        return

    resultados = st.session_state["resultados"]
    errores = st.session_state["errores"]

    if st.session_state["vacante_evaluada"] != vacante:
        st.warning("La vacante cambió después de esta evaluación. "
                   "Vuelva a evaluar para actualizar el ranking.")

    revision = sum(1 for r in resultados if r["sin_evidencia"] > 0)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("CV cargados", len(resultados) + len(errores))
    m2.metric("Evaluados", len(resultados))
    m3.metric("Con error", len(errores))
    m4.metric("Requieren revisión manual", revision)

    if not resultados:
        st.warning("Ningún archivo pudo evaluarse.")
        if errores:
            st.dataframe(pd.DataFrame(errores), hide_index=True)
        return

    tab_ranking, tab_dashboard, tab_detalle = st.tabs(
        ["Ranking", "Dashboard", "Detalle por candidato"])
    with tab_ranking:
        _pestana_ranking(resultados, errores)
    with tab_dashboard:
        _pestana_dashboard(resultados)
    with tab_detalle:
        _pestana_detalle(resultados)