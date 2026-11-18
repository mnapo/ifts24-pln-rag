# PLN RAG

Asistente conversacional configurable para un negocio, desarrollado con Python, FastAPI y DeepSeek.

## Requisitos

- Python 3.12 o superior.
- Una clave de API de DeepSeek para generar respuestas.

## Configuración

1. Copiar `.env.example` a `.env`.
2. Crear una clave desde [DeepSeek Platform](https://platform.deepseek.com/) y completar `DEEPSEEK_API_KEY`.
3. Ajustar las variables `BUSINESS_*` según la información disponible del negocio.
4. Instalar dependencias: `pip install -r requirements.txt`.
5. Ejecutar: `uvicorn main:app --reload`.

La API de DeepSeek se factura por tokens y requiere saldo disponible o crédito promocional en la cuenta. El acceso gratuito al chat web de DeepSeek no incluye uso gratuito ilimitado de la API.

## Variables de entorno

La aplicación admite que las variables opcionales estén ausentes o vacías. En ese caso utiliza valores predeterminados seguros y continúa iniciando.

- `DEEPSEEK_API_KEY`: credencial necesaria para generar respuestas. Si no está definida, la aplicación puede iniciar, pero el endpoint de chat responde con un error controlado indicando que falta configurarla.
- `DEEPSEEK_MODEL`: modelo utilizado. Predeterminado: `deepseek-flash`.
- `BUSINESS_*`: datos de identidad, productos, políticas, horarios y tono. Los campos no definidos se omiten del contexto.
- `MAX_HISTORY_MESSAGES` y `MAX_MESSAGE_LENGTH`: límites de solicitudes. Si faltan o contienen valores inválidos, se utilizan los valores predeterminados.

Los valores numéricos inválidos se registran en el log y no impiden el inicio del servidor. El archivo `.env` no debe subirse al repositorio.

## Conversaciones

La aplicación no persiste conversaciones. El historial se mantiene temporalmente en el navegador y se envía con cada solicitud.

## Interfaz web

La aplicación incluye una ventana de chat adaptable a dispositivos móviles, servida desde FastAPI en la ruta raíz. Inicia el servidor y abre `http://localhost:8000`.

El historial se conserva en `sessionStorage` durante la sesión del navegador y se envía junto con cada mensaje. No se almacena en el servidor ni en una base de datos.
