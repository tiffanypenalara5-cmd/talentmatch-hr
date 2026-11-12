
import pymupdf
from modulos.lector_pdf import extraer_texto, ErrorLecturaPDF

RUTA_DEMO = "datos/cvs_ficticios/cv_demo.pdf"

TEXTO_CV = """CANDIDATA FICTICIA 001
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

# Crear el CV ficticio en PDF
doc = pymupdf.open()
pagina = doc.new_page()
pagina.insert_text((72, 72), TEXTO_CV, fontsize=11)
doc.save(RUTA_DEMO)
doc.close()

# Un PDF en blanco (simula una imagen escaneada sin texto)
doc_blanco = pymupdf.open()
doc_blanco.new_page()
bytes_blanco = doc_blanco.tobytes()
doc_blanco.close()


def intentar(nombre, origen):
    print(f"--- {nombre} ---")
    try:
        resultado = extraer_texto(origen)
        print("OK:", resultado["paginas"], "página(s),",
              len(resultado["texto"]), "caracteres")
        print(resultado["texto"][:60].replace("\n", " | "))
    except ErrorLecturaPDF as error:
        print("ERROR CONTROLADO:", error)
    print()


intentar("CASO 1: CV válido", RUTA_DEMO)
intentar("CASO 2: archivo que no es PDF", b"esto no es un pdf")
intentar("CASO 3: archivo que no existe", "datos/no_existe.pdf")
intentar("CASO 4: PDF sin texto", bytes_blanco)