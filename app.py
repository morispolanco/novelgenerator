import streamlit as st
import requests
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from io import BytesIO

# ... (all previous functions remain unchanged)

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

# Botón para generar la novela y contenedor para el botón de descarga
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
                f"Asegúrate de que el capítulo tenga una longitud adecuada y continúe la historia de forma coherente."
            )
            
            # Generar el contenido del capítulo
            chapter_content = generate_novel_content(prompt)
            if chapter_content:
                chapter_content = chapter_content.strip()
            
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

        # Crear y mantener el botón de descarga disponible
        if novel_content:
            chapters_text = [content for _, content, _ in novel_content]
            word_buffer = create_word_document(
                chapters=chapters_text,
                title=title,
                author_name=author_name,
                author_bio=author_bio,
                language=language.lower()
            )
            
            # Botón de descarga que ahora permanece después de la generación
            st.download_button(
                label="Descargar Novela en Word",
                data=word_buffer.getvalue(),
                file_name=f"{title.replace(' ', '_')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
    else:
        st.warning("Por favor, completa todos los campos.")
