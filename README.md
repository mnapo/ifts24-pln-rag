# PLN RAG

Asistente conversacional configurable para un negocio, desarrollado con Python y FastAPI. Utiliza proveedores de modelos de lenguaje mediante APIs compatibles con OpenAI.

## Requisitos

- Python 3.12 o superior.
- Una clave de API del proveedor seleccionado.

## Configuración

1. Copiar `.env.example` a `.env`.
2. Crear una clave de API en [Google AI Studio](https://aistudio.google.com/) y completar `AI_API_KEY`.
3. Ajustar las variables `BUSINESS_*` según la información disponible del negocio.
4. Instalar dependencias: `pip install -r requirements.txt`.
5. Ejecutar: `uvicorn main:app --reload`.

La configuración predeterminada utiliza Gemini 3.8 Flash. Google ofrece un nivel gratuito con límites de uso. En el nivel gratuito, Google puede utilizar el contenido enviado para mejorar sus productos; no envíes datos sensibles o confidenciales. Consulta los [precios y límites vigentes](https://ai.google.dev/gemini-api/docs/pricing).

## Proveedores compatibles

El proveedor se selecciona mediante variables de entorno, sin modificar el frontend ni el flujo de chat.

| Proveedor | `AI_PROVIDER` | URL base predeterminada |
|---|---|---|
| Google Gemini | `gemini` | `https://generativelanguage.googleapis.com/v1beta/openai/` |
| Groq | `groq` | `https://api.groq.com/openai/v1` |
| OpenRouter | `openrouter` | `https://openrouter.ai/api/v1` |
| DeepSeek | `deepseek` | `https://api.deepseek.com` |
| OpenAI | `openai` | `https://api.openai.com/v1` |

Para cambiar de proveedor, actualizar `AI_PROVIDER`, `AI_API_KEY` y `AI_MODEL`. También se puede definir `AI_BASE_URL` para utilizar cualquier endpoint compatible con la API de chat de OpenAI.

## Variables de entorno

- `AI_PROVIDER`: proveedor de IA. Predeterminado: `gemini`.
- `AI_API_KEY`: clave de API del proveedor seleccionado.
- `AI_MODEL`: identificador del modelo. Predeterminado: `gemini-3.8-flash`.
- `AI_BASE_URL`: URL base personalizada opcional.
- `BUSINESS_*`: datos de identidad, productos, políticas, horarios y tono. Los campos no definidos se omiten del contexto.
- `MAX_HISTORY_MESSAGES` y `MAX_MESSAGE_LENGTH`: límites de solicitudes. Si faltan o contienen valores inválidos, se utilizan los valores predeterminados.

Las variables opcionales pueden estar ausentes o vacías. Los valores numéricos inválidos se registran en el log y no impiden el inicio del servidor. El archivo `.env` no debe subirse al repositorio.

## Conversaciones

La aplicación no persiste conversaciones. El historial se mantiene temporalmente en el navegador y se envía con cada solicitud.

## Interfaz web

La aplicación incluye una ventana de chat adaptable a dispositivos móviles, servida desde FastAPI en la ruta raíz. Inicia el servidor y abre `http://localhost:8000`.

El historial se conserva en `sessionStorage` durante la sesión del navegador y se envía junto con cada mensaje. No se almacena en el servidor ni en una base de datos.
