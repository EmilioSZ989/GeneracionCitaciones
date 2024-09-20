import google.generativeai as genai
import os
from PyPDF2 import PdfReader
import time
import questionary

# Configura la clave de API de Gemini
os.environ["API_KEY"] = input("Introduce tu clave de API de Gemini: ")
genai.configure(api_key=os.environ["API_KEY"])

def cargar_preguntas_como_str(ruta_archivo):
    """Lee un archivo .txt y devuelve todas las preguntas en una sola cadena."""
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
            contenido = archivo.read()  # Lee todo el contenido del archivo
        
        # Devuelve las preguntas como una sola cadena, eliminando espacios en blanco adicionales
        preguntas = ', '.join([pregunta.strip() for pregunta in contenido.split(',') if pregunta.strip()])
        
        return preguntas
    except FileNotFoundError:
        print(f"Error: El archivo en la ruta '{ruta_archivo}' no fue encontrado.")
        return ""
    except Exception as e:
        print(f"Ocurrió un error: {e}")
        return ""

def extract_text_from_pdf(pdf_path):
    """Extrae texto de un archivo PDF."""
    try:
        reader = PdfReader(pdf_path)
        text = ''
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:  # Verifica si se extrajo texto
                text += page_text
        if not text:
            raise ValueError("No se pudo extraer texto del PDF.")
        return text
    except Exception as e:
        print(f"Error al leer el PDF: {e}")
        exit(1)

def split_text(text, max_tokens=2000):
    """Divide el texto en segmentos de un máximo de 'max_tokens' palabras."""
    words = text.split()
    segments = []
    current_segment = ""

    for word in words:
        if len(current_segment.split()) + len(word.split()) <= max_tokens:
            current_segment += f" {word}"
        else:
            segments.append(current_segment.strip())
            current_segment = word

    if current_segment:
        segments.append(current_segment.strip())

    return segments

def get_citations(segments, questions, max_retries=3, wait_time=10):
    """Obtiene citas textuales relevantes para las preguntas de investigación utilizando la API de Gemini."""
    citations = []
    model = genai.GenerativeModel("gemini-1.5-flash")

    for segment in segments:
        prompt = (
            f"Extrae citas textuales exactas que respondan directamente a las siguientes preguntas de investigación: '{questions}'. "
            f"No incluyas texto adicional. Si no hay citas relevantes, omite esa pregunta.\n\n"
            f"Texto: {segment}\n\n"
            "Responde en el formato: \n"
            "- [Pregunta 1]: [Cita relevante]\n"
            "- [Pregunta 2]: [Cita relevante]\n"
            "...etc."
        )

        retries = 0
        
        while retries < max_retries:
            try:
                response = model.generate_content(prompt)
                if response.text:
                    citations.append(response.text.strip())
                    break  # Salir del bucle si la solicitud tiene éxito
            except Exception as e:
                print(f"Error durante la solicitud a la API: {e}")
                if "Resource has been exhausted" in str(e):
                    retries += 1
                    print(f"Esperando {wait_time} segundos antes de reintentar... ({retries}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    break  # Si el error no es de cuota, salimos
    return citations

def save_citations_to_file(citations, questions, output_file="citations.txt"):
    """Guarda solo las citas relevantes en un archivo de texto, excluyendo las que contienen 'NO HAY NADA'."""
    with open(output_file, "w", encoding="utf-8") as file:
        file.write(f"Preguntas: {questions}\n")
        # Filtrar citas que no contienen 'NO HAY NADA'
        citas_relevantes = [citation for citation in citations if 'NO HAY NADA' not in citation]
        if citas_relevantes:
            for citation in citas_relevantes:
                file.write(f"- {citation}\n")
        else:
            file.write("No se encontraron citas relevantes.\n")
        file.write("\n")

def main():
    ruta = 'Preguntas.txt'
    questions = cargar_preguntas_como_str(ruta)

    if not questions:
        print("No se encontraron preguntas válidas en el archivo.")
        return

    # Directorio donde están los archivos PDF
    pdf_directory = "pdf"

    while True:
        # Obtén la lista de archivos PDF en el directorio
        pdf_files = [f for f in os.listdir(pdf_directory) if f.endswith('.pdf')]

        if not pdf_files:
            print("No se encontraron archivos PDF en el directorio.")
            return

        # Mostrar los archivos PDF para seleccionar
        pdf_file = questionary.select(
            "Selecciona un archivo PDF para analizar:",
            choices=pdf_files
        ).ask()

        if pdf_file:
            pdf_path = os.path.join(pdf_directory, pdf_file)
            
            text = extract_text_from_pdf(pdf_path)
            segments = split_text(text)
            citations = get_citations(segments, questions)
            save_citations_to_file(citations, questions)
            print("Citas guardadas en 'citations.txt'.")
        else:
            print("No se seleccionó ningún archivo PDF.")

        # Pregunta si el usuario desea continuar o terminar
        continuar = questionary.confirm("¿Deseas realizar otra operación?").ask()
        if not continuar:
            print("Terminando la ejecución.")
            break

if __name__ == "__main__":
    main()
