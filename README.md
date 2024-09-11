# Instrucciones para Usar el Script de Extracción de Citas

Este script permite extraer citas textuales relevantes de archivos PDF utilizando la API de Gemini. A continuación, se detallan los pasos necesarios para configurar y ejecutar el script correctamente.

## Requisitos Previos

**Python**: Asegúrate de tener Python 3.6 o superior instalado en tu sistema. Puedes descargarlo desde [python.org](https://www.python.org/).

**Instalar Dependencias**: El script requiere las siguientes bibliotecas:
- `google-generativeai` para interactuar con la API de Gemini.
- `PyPDF2` para la extracción de texto desde archivos PDF.
- `questionary` para la interacción con el usuario en la línea de comandos.

Puedes instalar estas dependencias usando `pip`. Abre una terminal y ejecuta el siguiente comando:

```bash
pip install google-generativeai PyPDF2 questionary
```
## Configuración

### Archivo de Preguntas

1. Crea un archivo de texto llamado `Preguntas.txt`.
2. En este archivo, escribe las preguntas de investigación que deseas utilizar, separadas por comas.

**Ejemplo de contenido de Preguntas.txt:**

```text
¿PREGUNTA#1?, ¿PREGUNTA#N?
```
### Directorios

- Asegúrate de tener un directorio llamado `pdf` en el mismo lugar donde se encuentra el script.
- Coloca todos los archivos PDF que deseas analizar dentro de este directorio.

## Ejecución del Script

### Configurar la API

Cuando ejecutes el script por primera vez, se te pedirá que ingreses tu clave de API de Gemini. Asegúrate de tener una clave válida para utilizar el servicio.

### Ejecutar el Script

1. Abre una terminal y navega al directorio donde se encuentra el script.
2. Ejecuta el script utilizando el siguiente comando:

```bash
python gemini_pdf_script.py
```

### Instrucciones en la Consola

1. Selecciona el archivo PDF que deseas analizar.
2. Elige una pregunta de la lista proporcionada.
3. El script extraerá citas relevantes del archivo PDF basado en la pregunta seleccionada y las guardará en un archivo llamado `citations.txt`.

### Continuar o Terminar

- Después de guardar las citas en el archivo, el script te preguntará si deseas realizar otra operación.
- Si eliges continuar, podrás seleccionar otro archivo PDF y otra pregunta.
- Si eliges terminar, el script finalizará su ejecución.

## Notas

- Asegúrate de que los archivos PDF no estén protegidos por contraseña o en un formato que no sea compatible con `PyPDF2`.
- Verifica que la clave de API de Gemini esté activa y válida para evitar errores de autenticación.

