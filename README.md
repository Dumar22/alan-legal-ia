# 🏛️ Alana Legal Sense - Asistente Jurídico Inteligente con IA

## 📋 Descripción

**Alana Legal Sense** es un asistente jurídico inteligente de última generación que utiliza IA avanzada para analizar documentos legales y proporcionar respuestas precisas. Integra tecnologías RAG (Retrieval-Augmented Generation) con FAISS, razonamiento cruzado entre documentos, y persistencia de datos con Supabase.

## 🚀 **¡LISTO PARA DESPLEGAR EN PRODUCCIÓN!**

### 🌐 Despliegue Recomendado: [Render.com](https://render.com)
- ✅ **Gratis** para proyectos públicos  
- ✅ **Integración directa con GitHub**
- ✅ **Despliegue automático** en cada push
- ✅ **HTTPS incluido** automáticamente
- ✅ **Variables de entorno seguras**

### 📋 Pasos Rápidos de Despliegue:
1. **Fork** este repositorio en GitHub
2. **Crear cuenta** en [render.com](https://render.com)  
3. **Nuevo Web Service** → Conectar repositorio
4. **Configurar variables de entorno**:
   ```
   OPENAI_API_KEY=tu_clave_aqui
   SUPABASE_URL=tu_url_supabase
   SUPABASE_ANON_KEY=tu_clave_supabase
   FLASK_ENV=production
   ```
5. **¡Desplegar!** Tu app estará en: `https://alana-legal-sense.onrender.com`

### 📁 Archivos de Despliegue Incluidos:
- ✅ `Procfile` - Comando de inicio
- ✅ `build.sh` - Script de construcción  
- ✅ `runtime.txt` - Python 3.11
- ✅ `DEPLOYMENT.md` - Guía completa

## ✨ Características Principales

### 🔍 Procesamiento Avanzado
- **RAG (Retrieval-Augmented Generation)** con FAISS para búsqueda semántica
- **Razonamiento cruzado** - conecta información de múltiples secciones
- **Chunking inteligente** con solapamiento para preservar contexto
- **Múltiples formatos** - PDF, TXT, DOCX

### 💾 Persistencia de Datos
- **Base de datos Supabase** para almacenar conversaciones y documentos
- **Caché inteligente** - evita llamadas innecesarias a la API
- **Historial de conversaciones** accesible desde la interfaz

### 🎯 Respuestas Precisas
- **Citación de fuentes** con fragmentos exactos del documento
- **Indicador de confianza** basado en scores de similitud
- **Cross-references** - muestra conexiones entre diferentes secciones
- **Respuestas amigables** - no devuelve "NO_ENCONTRADO" sino explicaciones útiles

### 🌐 Interfaz Responsiva
- **Diseño adaptativo** para móviles y escritorio
- **Chat interactivo** con feedback visual
- **Visualización de fuentes** y referencias cruzadas
- **Modal de historial** para revisar conversaciones previas

## 🛠️ Tecnologías Utilizadas

- **Backend**: Flask, Python 3.8+
- **IA/ML**: OpenAI GPT-4o, LangChain, FAISS
- **Base de datos**: Supabase (PostgreSQL)
- **Frontend**: HTML5, CSS3, JavaScript Vanilla
- **Vectorización**: OpenAI Embeddings

## 🚀 Instalación y Configuración

### 1. Clonar el repositorio
```bash
git clone https://github.com/Dumar22/alan-legal-ia.git
cd alan-legal-ia
```

### 2. Configurar entorno virtual
```bash
python -m venv env
# Windows
env\\Scripts\\activate
# Linux/Mac
source env/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env con tus credenciales:
OPENAI_API_KEY=sk-tu-api-key-aqui
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_ANON_KEY=tu-anon-key-aqui
```

### 5. Configurar Base de Datos Supabase

1. Crear cuenta en [Supabase](https://supabase.com)
2. Crear nuevo proyecto
3. Ejecutar el script SQL en el Editor SQL de Supabase:
```sql
-- Copiar y ejecutar el contenido de supabase_schema.sql
```
4. Obtener URL y Anon Key desde Project Settings > API

### 6. Ejecutar la aplicación
```bash
python main.py
```

La aplicación estará disponible en `http://localhost:5000`

## 📚 Uso del Sistema

### 1. Subir Documento
- Click en "Seleccionar archivo" y elegir PDF, TXT o DOCX
- Click "Subir" - el documento se procesará automáticamente
- Una vez procesado, estará listo para consultas

### 2. Hacer Consultas
- Escribe tu pregunta en el chat
- El sistema buscará en el documento y generará una respuesta
- Verás la respuesta junto con:
  - **Fuentes**: fragmentos específicos del documento
  - **Confianza**: nivel de certeza de la respuesta
  - **Cross-references**: conexiones con otras secciones

### 3. Ver Historial
- Click en "📋 Historial" para ver conversaciones previas
- Las respuestas con referencias cruzadas se marcan con 🔗

## 🔧 Ejemplos de Consultas

### Consultas Básicas
```
- "¿Cuál es el valor del contrato?"
- "¿Quiénes son las partes?"
- "¿Cuáles son las obligaciones del contratista?"
```

### Consultas con Razonamiento Cruzado
```
- "¿Qué relación hay entre el artículo 5 y las penalidades?"
- "¿Cómo se conectan los plazos con las garantías?"
- "¿Qué dice sobre pagos en diferentes secciones?"
```

### Consultas de Aclaración
```
- "No entiendo, explícalo sin tecnicismos"
- "¿Puedes simplificar la respuesta anterior?"
- "Resume la información más importante"
```

## 📁 Estructura del Proyecto

```
alan-legal-ia/
├── main.py                 # Aplicación principal Flask
├── requirements.txt        # Dependencias Python
├── .env.example           # Plantilla de configuración
├── supabase_schema.sql    # Schema de base de datos
├── chatbot/               # Módulos del chatbot
│   ├── __init__.py
│   ├── data.py           # Datos de entrenamiento
│   └── model.py          # Modelo de clustering
├── static/               # Archivos estáticos
│   ├── css/
│   │   └── style.css     # Estilos CSS
│   └── js/
│       └── app.js        # JavaScript frontend
├── templates/            # Plantillas HTML
│   └── index.html        # Interfaz principal
├── uploads/              # Documentos subidos (generado)
├── vector_db/           # Base vectorial FAISS (generado)
├── models/              # Modelos ML (generado)
└── qa_cache.json        # Caché de preguntas (generado)
```

## 🛡️ Seguridad y Privacidad

- **Datos locales**: Los documentos se procesan y almacenan localmente
- **API Keys**: Nunca se exponen en el frontend
- **Supabase RLS**: Políticas de seguridad configuradas
- **Caché**: Incluye timestamp para invalidación automática

## 🔄 API Endpoints

### POST /upload
- **Descripción**: Sube y procesa un documento
- **Formato**: multipart/form-data
- **Response**: `{"message": "status"}`

### POST /chat
- **Descripción**: Procesa una consulta
- **Body**: `message=tu-pregunta`
- **Response**: 
```json
{
  "response": "respuesta del asistente",
  "sources": [{"text_snippet": "...", "source": "...", "page": 1, "score": 0.95}],
  "confidence": "alta",
  "evidence": ["cita1", "cita2"],
  "cross_references": ["conexión1", "conexión2"]
}
```

### GET /history
- **Descripción**: Obtiene historial de conversaciones
- **Response**: `{"history": [...]}`

## 🚀 Despliegue en Producción

### Variables de Entorno Adicionales
```bash
FLASK_ENV=production
FLASK_DEBUG=False
```

### Consideraciones
- Usar servidor WSGI como Gunicorn
- Configurar HTTPS
- Establecer límites de carga de archivos
- Configurar políticas de RLS más restrictivas en Supabase

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama: `git checkout -b feature/nueva-caracteristica`
3. Commit: `git commit -m 'Añadir nueva característica'`
4. Push: `git push origin feature/nueva-caracteristica`
5. Abrir Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 📞 Soporte

Para soporte técnico o consultas:
- Crear un issue en GitHub
- Contactar al equipo de desarrollo

---

**¿Listo para comenzar?** 🚀

1. Configura tu `.env` con las API keys
2. Ejecuta `python main.py`
3. Sube tu primer documento legal
4. ¡Comienza a hacer preguntas!

El asistente analizará el documento y te dará respuestas precisas basadas únicamente en su contenido, mostrando las fuentes exactas y conexiones entre diferentes secciones.
