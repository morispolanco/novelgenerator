import streamlit as st
import requests
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from io import BytesIO

# Función para llamar a la API de Qwen Turbo
def generate_novel_content(prompt):
    api_key = st.secrets["OPENROUTER_API_KEY"]
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "model": "qwen/qwen-turbo",  # Modelo Qwen Turbo
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        st.error(f"Error al generar el contenido: {response.status_code}")
        return None

# Función para contar el número de palabras en un texto
def count_words(text):
    words = text.split()
    return len(words)

# Función para reemplazar comillas por rayas en diálogos (solo para español)
def replace_quotes_with_dashes(text, language="spanish"):
    if language.lower() == "spanish":
        # Reemplazar comillas dobles por rayas en diálogos
        text = text.replace('“', '—').replace('”', '—')
        text = text.replace('"', '—')
    return text

# Función para agregar numeración de páginas al documento Word
def add_page_numbers(doc):
    for section in doc.sections:
        footer = section.footer
        paragraph = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = paragraph.add_run()
        fldChar = OxmlElement('w:fldChar')
        fldChar.set(qn('w:fldCharType'), 'begin')
        instrText = OxmlElement('w:instrText')
        instrText.set(qn('xml:space'), 'preserve')
        instrText.text = "PAGE"
        fldChar2 = OxmlElement('w:fldChar')
        fldChar2.set(qn('w:fldCharType'), 'end')
        run._r.append(fldChar)
        run._r.append(instrText)
        run._r.append(fldChar2)

# Función para crear un documento Word con formato específico
def create_word_document(chapters, title, author_name="", author_bio="", language="spanish"):
    doc = Document()

    # Configurar el tamaño de página (5.5 x 8.5 pulgadas)
    section = doc.sections[0]
    section.page_width = Inches(5.5)
    section.page_height = Inches(8.5)

    # Configurar márgenes de 0.8 pulgadas en todo
    section.top_margin = Inches(0.8)
    section.bottom_margin = Inches(0.8)
    section.left_margin = Inches(0.8)
    section.right_margin = Inches(0.8)

    # Añadir y formatear el título
    formatted_title = format_title(title, language)
    title_paragraph = doc.add_paragraph()
    title_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_run = title_paragraph.add_run(formatted_title)
    title_run.bold = True
    title_run.font.size = Pt(14)
    title_run.font.name = "Times New Roman"

    # Añadir nombre del autor si está proporcionado
    if author_name:
        author_paragraph = doc.add_paragraph()
        author_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        author_run = author_paragraph.add_run(author_name)
        author_run.font.size = Pt(12)
        author_run.font.name = "Times New Roman"
        doc.add_page_break()

    # Añadir perfil del autor si está proporcionado
    if author_bio:
        bio_paragraph = doc.add_paragraph("Author Information")
        bio_paragraph.style = "Heading 2"
        bio_paragraph.runs[0].font.size = Pt(11)
        bio_paragraph.runs[0].font.name = "Times New Roman"
        doc.add_paragraph(author_bio).style = "Normal"
        doc.add_page_break()

    # Añadir capítulos
    for i, chapter in enumerate(chapters, 1):
        chapter_title_text = f"Chapter {i}" if language.lower() != "spanish" else f"Capítulo {i}"
        formatted_chapter_title = format_title(chapter_title_text, language)
        chapter_title = doc.add_paragraph(formatted_chapter_title)
        chapter_title.style = "Heading 1"
        chapter_title.runs[0].font.size = Pt(12)
        chapter_title.runs[0].font.name = "Times New Roman"

        paragraphs = chapter.split('\n\n')
        for para_text in paragraphs:
            para_text = para_text.replace('\n', ' ').strip()
            # Reemplazar comillas por rayas si el idioma es español
            para_text = replace_quotes_with_dashes(para_text, language)
            paragraph = doc.add_paragraph(para_text)
            paragraph.style = "Normal"
            paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            paragraph.paragraph_format.space_after = Pt(6)  # Changed to 6 pt
            for run in paragraph.runs:
                run.font.size = Pt(11)
                run.font.name = "Times New Roman"

        doc.add_page_break()

    # Agregar numeración de páginas
    add_page_numbers(doc)

    # Guardar el documento en un objeto de bytes
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# Función para formatear el título según el idioma
def format_title(title, language):
    if language.lower() == "spanish":
        return title.upper()
    else:
        return title.title()

# Interfaz de usuario de Streamlit
st.title("Generador de Novelas")

# Entradas del usuario
title = st.text_input("Título de la novela:")
genre = st.selectbox("Género:", [
    "Ciencia Ficción",
    "Fantasía",
    "Romance",
    "Misterio",
    "Drama",
    "Terror",
    "Aventura",
    "Ficción histórica",
    "Comedia",
    "Thriller",
    "Distopía",
    "Realismo Mágico"
])
audience = st.selectbox("Audiencia:", ["Niños", "Adolescentes", "Adultos"])
num_chapters = st.number_input("Número de capítulos:", min_value=1, max_value=50, value=5)

# Solicitar detalles de la trama
st.subheader("Define la trama de tu novela")
planteamiento = st.text_area("Planteamiento:", placeholder="Introduce el escenario y los personajes principales.")
nudo = st.text_area("Nudo:", placeholder="Describe el conflicto o desafío central.")
desenlace = st.text_area("Desenlace:", placeholder="Explica cómo se resuelve la historia.")

instructions = st.text_area("Instrucciones especiales (opcional):", 
                            placeholder="Ejemplo: Incluye un personaje misterioso que aparezca en cada capítulo.")
author_name = st.text_input("Nombre del autor (opcional):")
author_bio = st.text_area("Biografía del autor (opcional):", 
                          placeholder="Escribe algo sobre el autor aquí...")
language = st.selectbox("Idioma:", ["Español", "Inglés"])

# Botón para generar la novela
if st.button("Generar Novela"):
    if title and genre and audience and num_chapters and planteamiento and nudo and desenlace:
        st.write(f"Generando novela: **{title}** ({genre}, para {audience})...")
        
        novel_content = []
        total_word_count = 0
        
        # Barra de progreso
        progress_bar = st.progress(0)
        status_text = st.empty()  # Para mostrar el estado actual
        
        # Contenedor para mostrar los capítulos generados
        chapter_container = st.container()
        
        for chapter in range(1, int(num_chapters) + 1):
            status_text.text(f"Generando capítulo {chapter} de {num_chapters}...")
            
            # Crear el prompt para el capítulo
            prompt = (
                f"Escribe el capítulo {chapter} de una novela titulada '{title}'. "
                f"El género es {genre} y está dirigido a {audience}. "
                f"La trama sigue este planteamiento: {planteamiento}. "
                f"El nudo principal es: {nudo}. "
                f"El desenlace será: {desenlace}. "
                f"{instructions if instructions else ''} "
                f"Asegúrate de que el capítulo tenga una longitud adecuada y continúe la historia de forma coherente. "
                f"El capítulo debe tener al menos 1000 palabras."
            )
            
            # Generar el contenido del capítulo
            chapter_content = ""
            while count_words(chapter_content) < 1000:  # Verificar que el capítulo tenga más de 1000 palabras
                new_content = generate_novel_content(prompt)
                if new_content:
                    chapter_content += " " + new_content.strip()
            
            # Reemplazar comillas por rayas si el idioma es español
            chapter_content = replace_quotes_with_dashes(chapter_content, language)
            
            word_count = count_words(chapter_content)
            total_word_count += word_count
            novel_content.append((f"Capítulo {chapter}", chapter_content, word_count))
            
            # Mostrar el capítulo generado en tiempo real
            with chapter_container.expander(f"Capítulo {chapter} ({word_count} palabras)"):
                st.write(chapter_content)
            
            # Actualizar la barra de progreso
            progress = chapter / num_chapters
            progress_bar.progress(progress)
        
        status_text.text("¡Novela generada con éxito!")
        
        # Mostrar el total de palabras
        st.write(f"**Total de palabras en la novela:** {total_word_count}")

        # Crear y descargar el archivo Word
        if novel_content:
            chapters_text = [content for _, content, _ in novel_content]
            word_buffer = create_word_document(
                chapters=chapters_text,
                title=title,
                author_name=author_name,
                author_bio=author_bio,
                language=language.lower()
            )
            st.download_button(
                label="Descargar Novela en Word",
                data=word_buffer,
                file_name=f"{title.replace(' ', '_')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
    else:
        st.warning("Por favor, completa todos los campos.")
