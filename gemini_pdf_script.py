import google.generativeai as genai
import os
from PyPDF2 import PdfReader
import time
import questionary

# Configura la clave de API de Gemini
os.environ["API_KEY"] = input("Introduce tu clave de API de Gemini: ")
genai.configure(api_key=os.environ["API_KEY"])

def generar_diccionario_preguntas_desde_archivo(ruta_archivo):
    """Lee un archivo .txt, extrae las preguntas separadas por comas y genera un diccionario."""
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
            contenido = archivo.read()  # Lee todo el contenido del archivo
        
        # Divide las preguntas por comas y elimina espacios en blanco adicionales
        preguntas = [pregunta.strip() for pregunta in contenido.split(',') if pregunta.strip()]

        # Genera el diccionario con índices numéricos
        preguntas_dict = {i + 1: pregunta for i, pregunta in enumerate(preguntas)}
        
        return preguntas_dict
    except FileNotFoundError:
        print(f"Error: El archivo en la ruta '{ruta_archivo}' no fue encontrado.")
        return {}
    except Exception as e:
        print(f"Ocurrió un error: {e}")
        return {}

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

def get_citations(segments, question, max_retries=3, wait_time=10):
    """Obtiene citas textuales relevantes para la pregunta de investigación utilizando la API de Gemini."""
    citations = []
    model = genai.GenerativeModel("gemini-1.5-flash")

    for segment in segments:
        prompt = (
            f"Extrae solo las citas textuales exactas del texto proporcionado que respondan directamente a la pregunta de investigación: '{question}'. "
            f"Si no se encuentran citas relevantes, responde con 'NO HAY NADA'.\n\n"
            f"Texto: {segment}\n\n"
            "Formato de respuesta: Proporciona únicamente las citas exactas sin explicaciones o contexto adicional."
        )
        retries = 0
        
        while retries < max_retries:
            try:
                response = model.generate_content(prompt)
                if response.text:
                    if "NO HAY NADA" not in response.text:
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

def save_citations_to_file(citations, question, output_file="citations.txt"):
    """Guarda las citas obtenidas en un archivo de texto."""
    with open(output_file, "w", encoding="utf-8") as file:
        file.write(f"Pregunta: {question}\n")
        for citation in citations:
            file.write(f"- {citation}\n")
        file.write("\n")

def main():
    ruta = 'Preguntas.txt'
    questions_dict = generar_diccionario_preguntas_desde_archivo(ruta)

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
            
            # Mostrar las preguntas para seleccionar
            question = questionary.select(
                "Selecciona una pregunta para la investigación:",
                choices=list(questions_dict.values())
            ).ask()
            
            if question:
                text = extract_text_from_pdf(pdf_path)
                segments = split_text(text)
                citations = get_citations(segments, question)
                save_citations_to_file(citations, question)
                print("Citas guardadas en 'citations.txt'.")
            else:
                print("No se seleccionó ninguna pregunta.")
        else:
            print("No se seleccionó ningún archivo PDF.")

        # Pregunta si el usuario desea continuar o terminar
        continuar = questionary.confirm("¿Deseas realizar otra operación?").ask()
        if not continuar:
            print("Terminando la ejecución.")
            break

if __name__ == "__main__":
    main()
