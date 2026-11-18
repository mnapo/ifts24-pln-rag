from app.config import Settings


def build_business_instructions(settings: Settings) -> str:
    sections = [
        f"Eres el asistente virtual de {settings.business_name}.",
        "Responde en español neutro, salvo que la persona utilice otro idioma.",
        "Sé útil, claro y honesto. No inventes precios, disponibilidad, políticas ni datos del negocio.",
        "Si no tienes información suficiente, dilo y solicita el dato necesario o deriva al canal de contacto configurado.",
        f"Tono: {settings.business_tone or 'Claro, cordial y profesional'}.",
    ]
    business_data = [
        ("Rubro", settings.business_sector),
        ("Descripción", settings.business_description),
        ("Productos y servicios", settings.business_products),
        ("Políticas", settings.business_policies),
        ("Horarios", settings.business_hours),
        ("Contacto", settings.business_contact),
        ("Instrucciones adicionales", settings.business_instructions),
    ]
    for label, value in business_data:
        if value:
            sections.append(f"{label}: {value}")
    sections.append(
        "Considera los datos anteriores como contexto del negocio. No afirmes haber realizado reservas, compras, pagos ni otras acciones externas."
    )
    return "\n\n".join(sections)
