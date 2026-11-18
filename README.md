# PLN RAG

Asistente conversacional configurable para un negocio, desarrollado con Python, FastAPI y OpenAI.

## Estado

Base inicial en desarrollo.

## Requisitos

- Python 3.12+
- Una clave de API de OpenAI

## Configuración

1. Copiar `.env.example` a `.env`.
2. Completar `OPENAI_API_KEY` y las variables `BUSINESS_*`.
3. Instalar dependencias: `pip install -r requirements.txt`.
4. Ejecutar: `uvicorn app.main:app --reload`.

La aplicación no persiste conversaciones. El historial se mantiene en el navegador y se envía con cada solicitud.
