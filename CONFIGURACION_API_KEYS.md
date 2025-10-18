# 🔑 Configuración de Claves API para EvalAI

Para que las funcionalidades de IA (transcripción de audio con OpenAI Whisper y generación de rúbricas con Google Gemini) funcionen correctamente, necesitas configurar tus claves API.

## Pasos para configurar las claves API:

1. **Crear un archivo `.env`**:
   En el directorio `C:\Users\ramid\EvalAI\backend_django\`, crea un nuevo archivo llamado `.env` (asegúrate de que el nombre sea exactamente `.env`, sin ningún prefijo ni sufijo).

2. **Agregar las claves API**:
   Abre el archivo `.env` que acabas de crear y añade las siguientes líneas, reemplazando `tu-clave-openai-aqui` y `tu-clave-gemini-aqui` con tus claves reales:

   ```env
   OPENAI_API_KEY=tu-clave-openai-aqui
   GEMINI_API_KEY=tu-clave-gemini-aqui
   ```

   - **`OPENAI_API_KEY`**: Obtén esta clave desde tu cuenta de OpenAI (https://platform.openai.com/account/api-keys). Es necesaria para la transcripción de audio con Whisper.
   - **`GEMINI_API_KEY`**: Obtén esta clave desde Google AI Studio (https://aistudio.google.com/app/apikey). Es necesaria para la generación de rúbricas con Gemini.

3. **Guardar el archivo**:
   Guarda el archivo `.env`.

4. **Reiniciar el servidor**:
   Para que los cambios en las variables de entorno surtan efecto, debes reiniciar el servidor de EvalAI. Puedes hacerlo ejecutando el script de inicio:

   ```bash
   powershell -ExecutionPolicy Bypass -File .\INICIAR_EVALAI.ps1
   ```

Una vez que hayas seguido estos pasos, las funcionalidades de IA deberían operar sin problemas.