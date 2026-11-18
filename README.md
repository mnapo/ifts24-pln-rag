# PLN RAG

Asistente conversacional configurable para un negocio, desarrollado con Python, FastAPI y OpenAI.

## Requisitos

- Python 3.12 o superior.
- Una clave de API de OpenAI para generar respuestas.

## Configuración

1. Copiar `.env.example` a `.env`.
2. Completar `OPENAI_API_KEY`.
3. Ajustar las variables `BUSINESS_*` según la información disponible del negocio.
4. Instalar dependencias: `pip install -r requirements.txt`.
5. Ejecutar: `uvicorn app.main:app --reload`.

## Variables de entorno

La aplicación admite que las variables opcionales estén ausentes o vacías. En ese caso utiliza valores predeterminados seguros y continúa iniciando.

- `OPENAI_API_KEY`: credencial necesaria para generar respuestas. Si no está definida, la aplicación puede iniciar, pero el endpoint de chat responde con un error controlado indicando que falta configurarla.
- `OPENAI_MODEL`: modelo utilizado. Predeterminado: `gpt-4.1-mini`.
- `BUSINESS_*`: datos de identidad, productos, políticas, horarios y tono. Los campos no definidos se omiten del contexto.
- `MAX_HISTORY_MESSAGES` y `MAX_MESSAGE_LENGTH`: límites de solicitudes. Si faltan o contienen valores inválidos, se utilizan los valores predeterminados.

Los valores numéricos inválidos se registran en el log y no impiden el inicio del servidor. El archivo `.env` no debe subirse al repositorio.

## Conversaciones

La aplicación no persiste conversaciones. El historial se mantiene temporalmente en el navegador y se envía con cada solicitud.
