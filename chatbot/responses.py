# -*- coding: utf-8 -*-
"""
Sistema de respuestas predefinidas para el asistente legal AI
Mantiene el contexto como abogado especializado en documentos legales
"""

# Respuestas base del sistema
RESPUESTAS_BASE = {
    "saludo": [
        "¡Hola! Soy tu asistente legal especializado. Estoy aquí para ayudarte a analizar y comprender documentos legales. ¿En qué puedo asistirte hoy?",
        "Buenos días/tardes. Soy tu abogado virtual especializado en análisis documental. ¿Qué documentos necesitas que revise o qué consulta legal tienes?",
        "Bienvenido/a. Como tu asistente jurídico especializado, puedo ayudarte a interpretar contratos, normativas y otros documentos legales. ¿Cómo puedo ayudarte?"
    ],
    "despedida": [
        "Ha sido un placer asistirte con tus consultas legales. Recuerda que siempre estoy aquí para ayudarte con el análisis de documentos. ¡Hasta pronto!",
        "Gracias por confiar en mi análisis jurídico. Si necesitas revisar más documentos o tienes otras consultas legales, no dudes en contactarme.",
        "Espero haber sido de ayuda en tu consulta legal. Quedo a tu disposición para futuras revisiones documentales. ¡Que tengas un excelente día!"
    ],
    "no_entiendo": [
        "Como abogado especializado, necesito más contexto para brindarte una respuesta precisa. ¿Podrías reformular tu consulta legal o especificar qué tipo de documento necesitas analizar?",
        "Para ofrecerte el mejor análisis jurídico, requiero información más específica. ¿Te refieres a algún tipo particular de contrato, normativa o documento legal?",
        "Mi especialidad es el análisis de documentos legales. ¿Podrías aclarar si tu consulta se refiere a interpretación contractual, compliance normativo o algún otro tema jurídico específico?"
    ]
}

# Respuestas cuando no se encuentra información
RESPUESTAS_NO_ENCONTRADO = {
    "contratos": [
        "📋 **Análisis Contractual**: No encontré información específica sobre este punto en los contratos cargados. Como abogado, te recomiendo:",
        "- Revisar si existe alguna cláusula relacionada en las disposiciones generales",
        "- Verificar los anexos o documentos complementarios",
        "- Considerar la legislación aplicable supletoria",
        "¿Necesitas que analice alguna sección específica del contrato?"
    ],
    "normativa": [
        "⚖️ **Consulta Normativa**: La información solicitada no se encuentra en la documentación legal cargada. Te sugiero:",
        "- Verificar si existe normativa específica actualizada sobre el tema",
        "- Consultar jurisprudencia relevante",
        "- Revisar disposiciones transitorias o complementarias",
        "¿Puedes proporcionar más contexto sobre la normativa que necesitas analizar?"
    ],
    "general": [
        "🔍 **Análisis Documental**: No localicé información específica sobre tu consulta en los documentos actuales. Como tu asistente jurídico, recomiendo:",
        "- Cargar documentos adicionales relacionados con el tema",
        "- Reformular la consulta con términos más específicos",
        "- Verificar si la información está en secciones complementarias",
        "¿Te gustaría que revise algún aspecto particular de los documentos cargados?"
    ],
    "interpretacion": [
        "📖 **Interpretación Legal**: Aunque no encontré referencias directas, puedo ayudarte con el análisis basado en principios jurídicos generales:",
        "- Aplicación de la normativa supletoria",
        "- Interpretación sistemática del documento",
        "- Análisis de la intención de las partes",
        "¿Necesitas que profundice en algún aspecto interpretativo específico?"
    ]
}

# Respuestas para diferentes tipos de consultas legales
RESPUESTAS_CONTEXTUALES = {
    "carga_documentos": [
        "Perfecto, he recibido tu(s) documento(s). Como abogado especializado, procederé a realizar un análisis exhaustivo para poder responder tus consultas legales con precisión.",
        "Documentos cargados exitosamente. Ahora puedo ayudarte con análisis contractual, interpretación de cláusulas, identificación de riesgos legales y cualquier consulta jurídica específica.",
        "Excelente, ya tengo acceso a la documentación. Estoy listo para brindarte asesoría legal especializada sobre el contenido de estos documentos."
    ],
    "analisis_riesgo": [
        "⚠️ **Análisis de Riesgos**: He identificado los siguientes aspectos que requieren atención legal:",
        "🔍 **Evaluación Jurídica**: Basado en mi análisis, estos son los puntos críticos:",
        "📊 **Reporte Legal**: Mi evaluación profesional indica las siguientes consideraciones:"
    ],
    "interpretacion_clausulas": [
        "📋 **Interpretación Contractual**: Según el análisis de la cláusula:",
        "⚖️ **Análisis Jurisprudencial**: La interpretación legal de esta disposición:",
        "📖 **Exégesis Legal**: El sentido jurídico de esta cláusula implica:"
    ],
    "recomendaciones": [
        "💡 **Recomendaciones Legales**: Como tu abogado asesor, sugiero:",
        "🎯 **Estrategia Jurídica**: Mi recomendación profesional es:",
        "📋 **Plan de Acción Legal**: Te aconsejo los siguientes pasos:"
    ]
}

# Respuestas de error manteniendo el contexto profesional
RESPUESTAS_ERROR = {
    "error_procesamiento": [
        "⚠️ Disculpa, como abogado responsable debo informarte que hubo un inconveniente técnico al procesar tu consulta legal. Por favor, inténtalo nuevamente.",
        "🔧 Experimenté una dificultad técnica al analizar tu documento legal. Mi compromiso profesional me obliga a solicitar que reenvíes la consulta.",
        "❌ Se presentó un error en el sistema de análisis jurídico. Para brindarte el servicio legal que mereces, por favor reintenta tu consulta."
    ],
    "documento_no_valido": [
        "📄 El formato del documento no es compatible con mi sistema de análisis legal. Acepto PDF, DOC, DOCX y TXT para garantizar un análisis jurídico preciso.",
        "🚫 Para realizar un análisis legal profesional, necesito documentos en formatos estándar: PDF, Word o texto plano.",
        "⚖️ Como abogado, requiero documentos legibles en formatos PDF, DOC, DOCX o TXT para garantizar un análisis jurídico adecuado."
    ],
    "limite_tamaño": [
        "📏 El documento excede el límite de tamaño para análisis. Como práctica legal estándar, prefiero documentos más manejables para un análisis detallado.",
        "⚡ Para garantizar un análisis jurídico eficiente, el documento debe ser menor a 16MB. ¿Podrías dividirlo en secciones?",
        "📊 El tamaño del archivo supera los límites técnicos. Te recomiendo segmentar el documento para un análisis legal más preciso."
    ]
}

# Respuestas para mantener el rol profesional
RESPUESTAS_ROL = {
    "fuera_contexto": [
        "👔 Como abogado especializado en análisis documental, mi experticia se centra en temas legales. ¿Tienes alguna consulta jurídica o documento legal que necesites revisar?",
        "⚖️ Mi rol profesional es ser tu asistente jurídico especializado. ¿Puedo ayudarte con algún análisis contractual, normativo o de compliance?",
        "📚 Estoy especializado en derecho y análisis de documentos legales. ¿Hay algún tema jurídico en el que pueda asistirte profesionalmente?"
    ],
    "aclaracion_rol": [
        "Soy tu abogado virtual especializado en análisis y interpretación de documentos legales. Mi función es ayudarte con:",
        "• Análisis contractual y cláusulas",
        "• Interpretación de normativas",
        "• Identificación de riesgos legales",
        "• Recomendaciones jurídicas",
        "• Compliance y cumplimiento normativo",
        "¿En cuál de estas áreas necesitas mi asistencia profesional?"
    ]
}

# Respuestas con diferentes niveles de confianza
RESPUESTAS_CONFIANZA = {
    "alta": [
        "✅ **Análisis Jurídico Confirmado**: Basado en la documentación legal revisada, puedo afirmar con certeza que:",
        "🎯 **Dictamen Legal**: Con base en el análisis exhaustivo de los documentos, mi conclusión jurídica es:",
        "⚖️ **Opinión Legal Fundada**: La evidencia documental me permite establecer claramente que:"
    ],
    "media": [
        "📋 **Análisis Legal Preliminar**: Según la información disponible en los documentos, considero que:",
        "🔍 **Evaluación Jurídica**: Con base en la documentación parcial, mi apreciación legal es:",
        "📖 **Interpretación Probable**: Los elementos legales analizados sugieren que:"
    ],
    "baja": [
        "⚠️ **Observación Legal**: Con la información limitada disponible, debo señalar que:",
        "🔍 **Análisis Preliminar**: Aunque la documentación es incompleta, puedo observar que:",
        "📝 **Comentario Jurídico**: Basándome en los elementos parciales, considero importante mencionar que:"
    ]
}

def get_respuesta_by_tipo(tipo, subtipo="general"):
    """
    Obtiene una respuesta aleatoria del tipo especificado
    """
    import random
    
    if tipo in RESPUESTAS_BASE:
        return random.choice(RESPUESTAS_BASE[tipo])
    elif tipo == "no_encontrado":
        if subtipo in RESPUESTAS_NO_ENCONTRADO:
            return "\n".join(RESPUESTAS_NO_ENCONTRADO[subtipo])
        return "\n".join(RESPUESTAS_NO_ENCONTRADO["general"])
    elif tipo in RESPUESTAS_CONTEXTUALES:
        return random.choice(RESPUESTAS_CONTEXTUALES[tipo])
    elif tipo in RESPUESTAS_ERROR:
        return random.choice(RESPUESTAS_ERROR[tipo])
    elif tipo in RESPUESTAS_ROL:
        return random.choice(RESPUESTAS_ROL[tipo])
    elif tipo == "confianza":
        if subtipo in RESPUESTAS_CONFIANZA:
            return random.choice(RESPUESTAS_CONFIANZA[subtipo])
    
    return "Como tu abogado especializado, estoy aquí para ayudarte con cualquier consulta legal o análisis documental que necesites."

def get_respuesta_no_encontrado_inteligente(pregunta):
    """
    Determina el mejor tipo de respuesta NO_ENCONTRADO basado en la pregunta
    """
    pregunta_lower = pregunta.lower()
    
    palabras_contrato = ["contrato", "cláusula", "acuerdo", "convenio", "pacto", "estipulación"]
    palabras_normativa = ["ley", "decreto", "norma", "reglamento", "resolución", "disposición"]
    palabras_interpretacion = ["significa", "interpretación", "sentido", "alcance", "implicación"]
    
    if any(palabra in pregunta_lower for palabra in palabras_contrato):
        return get_respuesta_by_tipo("no_encontrado", "contratos")
    elif any(palabra in pregunta_lower for palabra in palabras_normativa):
        return get_respuesta_by_tipo("no_encontrado", "normativa")
    elif any(palabra in pregunta_lower for palabra in palabras_interpretacion):
        return get_respuesta_by_tipo("no_encontrado", "interpretacion")
    else:
        return get_respuesta_by_tipo("no_encontrado", "general")