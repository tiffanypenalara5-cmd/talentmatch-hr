"""Identidad visual de TalentMatch HR: colores, estilos y componentes de pantalla."""

import streamlit as st

CSS = """
<style>
[data-testid="stSidebar"] { background-color: #0F3D3A; }
[data-testid="stSidebar"] * { color: #E6F2F1 !important; }
.block-container { padding-top: 2rem; }
.tm-banner { background: linear-gradient(90deg, #0F766E, #14B8A6); padding: 1.4rem 1.8rem; border-radius: 14px; margin-bottom: 1.2rem; }
.tm-banner h1 { color: #FFFFFF; margin: 0; padding: 0; font-size: 1.9rem; }
.tm-banner p { color: #E6FFFB; margin: 0.3rem 0 0 0; font-size: 1rem; }
.tm-tarjeta { background: #FFFFFF; border: 1px solid #D5E3E1; border-radius: 12px; padding: 1rem 1.2rem; height: 100%; }
.tm-tarjeta h4 { margin: 0 0 0.4rem 0; color: #0F766E; }
.tm-tarjeta p { margin: 0; color: #334155; font-size: 0.95rem; }
[data-testid="stMetric"] { background: #FFFFFF; border: 1px solid #D5E3E1; border-radius: 12px; padding: 0.8rem 1rem; }
</style>
"""


def aplicar_estilos():
    """Aplica los estilos propios de TalentMatch HR a toda la aplicación."""
    st.markdown(CSS, unsafe_allow_html=True)


def encabezado(titulo, subtitulo=""):
    """Banner de color que va al inicio de cada pantalla."""
    st.markdown(
        f'<div class="tm-banner"><h1>{titulo}</h1><p>{subtitulo}</p></div>',
        unsafe_allow_html=True,
    )


def tarjeta(titulo, texto):
    """Cuadro blanco con título y texto corto."""
    st.markdown(
        f'<div class="tm-tarjeta"><h4>{titulo}</h4><p>{texto}</p></div>',
        unsafe_allow_html=True,
    )