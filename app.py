import streamlit as st
import pandas as pd

from modulos.estilos import aplicar_estilos, encabezado, tarjeta
from modulos.vacantes import CATEGORIAS, validar_vacante
from modulos.conversiones import vacante_ejemplo, vacante_a_tabla, tabla_a_vacante
from modulos.pagina_candidatos import pagina_candidatos
from modulos.pagina_informes import pagina_informes
st.set_page_config(page_title="TalentMatch HR", page_icon="🎯", layout="wide")
aplicar_estilos()

# Memoria de la sesión: la primera vez se carga una vacante de ejemplo
if "vacante" not in st.session_state:
    ejemplo = vacante_ejemplo()
    st.session_state["vacante"] = ejemplo
    st.session_state["tabla_inicial"] = vacante_a_tabla(ejemplo)
    st.session_state["nombre_vacante"] = ejemplo.nombre
    st.session_state["descripcion_vacante"] = ejemplo.descripcion


def pagina_inicio():
    encabezado("TalentMatch HR",
               "Preselección objetiva de candidatos, con criterios claros y decisión humana.")

    c1, c2, c3 = st.columns(3)
    with c1:
        tarjeta("1. Configura la vacante",
                "Define los criterios de evaluación y cuánto pesa cada uno. Los pesos deben sumar 100%.")
    with c2:
        tarjeta("2. Carga los currículums",
                "Sube varios CV en PDF. El programa extrae formación, experiencia, competencias e idiomas.")
    with c3:
        tarjeta("3. Revisa los resultados",
                "Consulta el ranking, el detalle de cada candidato y qué criterios no tienen evidencia.")

    st.write("")
    vacante = st.session_state["vacante"]
    st.success(f"Vacante activa: {vacante.nombre} ({len(vacante.criterios)} criterios)")
    st.info("TalentMatch HR apoya la decisión del reclutador, no la sustituye. "
            "No usa edad, sexo, estado civil ni otras características personales para puntuar. "
            "Este proyecto trabaja únicamente con datos ficticios (Ley 8968).")


def pagina_vacante():
    encabezado("Configuración de la vacante",
               "Define qué se busca y cuánto pesa cada criterio.")

    col1, col2 = st.columns([1, 2])
    nombre = col1.text_input("Nombre del puesto", key="nombre_vacante")
    descripcion = col2.text_input("Descripción breve (opcional)", key="descripcion_vacante")

    st.subheader("Criterios de evaluación")
    st.caption("Edita la tabla directamente. Para agregar un criterio usa la última fila vacía. "
               "Las palabras clave se separan con comas. "
               "En Experiencia solo se usan los años mínimos.")

    tabla = st.data_editor(
        st.session_state["tabla_inicial"],
        key="editor_criterios",
        num_rows="dynamic",
        hide_index=True,
        column_config={
            "Criterio": st.column_config.TextColumn("Criterio", required=True),
            "Categoría": st.column_config.SelectboxColumn("Categoría", options=CATEGORIAS, required=True),
            "Peso (%)": st.column_config.NumberColumn("Peso (%)", min_value=0, max_value=100,
                                                      step=1, format="%g"),
            "Palabras clave": st.column_config.TextColumn("Palabras clave",
                                                          help="Separadas por comas"),
            "Años mínimos": st.column_config.NumberColumn("Años mínimos", min_value=0,
                                                          step=0.5, format="%g"),
        },
    )

    vacante = tabla_a_vacante(nombre, descripcion, tabla)
    errores = validar_vacante(vacante)
    suma = sum(c.peso for c in vacante.criterios)

    m1, m2, m3 = st.columns(3)
    m1.metric("Criterios", len(vacante.criterios))
    m2.metric("Suma de pesos", f"{suma:g}%")
    m3.metric("Estado", "Válida" if not errores else "Con errores")
    st.progress(int(min(max(suma, 0), 100)))

    if errores:
        st.error("Corrige lo siguiente para poder usar esta vacante:")
        for e in errores:
            st.write("•", e)
        st.info("Mientras tanto se sigue usando la última versión válida.")
    else:
        st.session_state["vacante"] = vacante
        st.success("Vacante válida. Quedó guardada para la evaluación.")

    if vacante.criterios:
        st.subheader("Distribución de pesos")
        grafico = pd.DataFrame({
            "Criterio": [c.nombre or "(sin nombre)" for c in vacante.criterios],
            "Peso (%)": [c.peso for c in vacante.criterios],
        }).set_index("Criterio")
        st.bar_chart(grafico)


def pagina_pendiente(titulo, texto):
    encabezado(titulo, texto)
    st.info("Esta sección se construye en la siguiente parte del proyecto.")


PAGINAS = {
    "Inicio": pagina_inicio,
    "Vacante": pagina_vacante,
    "Candidatos y ranking": pagina_candidatos,
    "informes y exportacion": pagina_informes,
}

with st.sidebar:
    st.markdown("### 🎯 TalentMatch HR")
    st.caption("Preselección de candidatos")
    seleccion = st.radio("Menú", list(PAGINAS), label_visibility="collapsed")
    st.divider()
    st.caption("Datos 100% ficticios. La decisión final es siempre del reclutador.")

PAGINAS[seleccion]()