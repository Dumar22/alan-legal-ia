# ==========================================================
# main.py — Chatbot con GPT + RAG + FAISS (2025)
# ==========================================================

from flask import Flask, render_template, request, jsonify
import os
import random
import json
import re
import time
import hashlib
from pathlib import Path
import uuid
from datetime import datetime
from supabase import create_client, Client

# ==========================================================
# 🔐 VARIABLES DE ENTORNO (CARGAR ANTES DE USAR OPENAI)
# ==========================================================
from dotenv import load_dotenv
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path, override=True)

OPENAI_KEY = os.getenv("OPENAI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

print("API KEY DETECTADA:", OPENAI_KEY)
print("SUPABASE URL:", SUPABASE_URL[:30] + "..." if SUPABASE_URL else "No configurado")

# Inicializar Supabase
supabase: Client = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Supabase conectado")
    except Exception as e:
        print("⚠ Error conectando Supabase:", e)
else:
    print("⚠ Configuración de Supabase incompleta")

# ==========================================================
# 🔧 OpenAI SDK nuevo (2025)
# ==========================================================
from openai import OpenAI
client = OpenAI(api_key=OPENAI_KEY)

# ==========================================================
# 📦 IMPORTS DEL CHATBOT
# ==========================================================
from chatbot.data import training_data
from chatbot.model import build_and_train_model, load_model, predict_cluster
from chatbot.responses import (get_respuesta_by_tipo, get_respuesta_no_encontrado_inteligente, 
                              RESPUESTAS_CONTEXTUALES, RESPUESTAS_CONFIANZA)

# Procesamiento de documentos
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

VECTOR_PATH = "vector_db"
CACHE_PATH = Path("qa_cache.json")
VECTOR_DB = None


def load_cache():
    if CACHE_PATH.exists():
        try:
            return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_cache(cache):
    try:
        CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        print("⚠ Error saving cache:", e)


def make_key(question: str) -> str:
    norm = " ".join(re.findall(r"\w+", question.lower()))
    return hashlib.sha256(norm.encode("utf-8")).hexdigest()


QA_CACHE = load_cache()
CACHE_TTL = 3600  # 1 hora de cache
MAX_CACHE_SIZE = 100

def clean_expired_cache():
    """Limpia entradas expiradas del cache."""
    now = int(time.time())
    expired_keys = [k for k, v in QA_CACHE.items() 
                   if now - v.get('timestamp', now) > CACHE_TTL]
    for key in expired_keys:
        QA_CACHE.pop(key, None)
    if expired_keys:
        save_cache(QA_CACHE)
        print(f"🧹 Limpiadas {len(expired_keys)} entradas expiradas del cache")

def respond_and_cache(key: str, payload: dict):
    # normalize stored payload and include timestamp
    stored = payload.copy()
    stored.setdefault("sources", [])
    stored.setdefault("confidence", None)
    stored["timestamp"] = int(time.time())
    stored["cached"] = True
    
    # Limpiar cache expirado
    clean_expired_cache()
    
    # Si el cache está lleno, eliminar entradas más antiguas
    if len(QA_CACHE) >= MAX_CACHE_SIZE:
        oldest_key = min(QA_CACHE.keys(), 
                       key=lambda k: QA_CACHE[k].get('timestamp', 0))
        QA_CACHE.pop(oldest_key, None)
        print(f"🗑️ Eliminada entrada antigua del cache")
    
    QA_CACHE[key] = stored
    save_cache(QA_CACHE)
    
    # Remover timestamp antes de enviar al frontend
    response_payload = {k: v for k, v in stored.items() if k not in ['timestamp']}
    return jsonify(response_payload)

def get_cached_response(key: str):
    """Obtiene respuesta del cache si no ha expirado."""
    if key in QA_CACHE:
        cached = QA_CACHE[key]
        now = int(time.time())
        if now - cached.get('timestamp', now) <= CACHE_TTL:
            response = {k: v for k, v in cached.items() if k not in ['timestamp']}
            return response
        else:
            QA_CACHE.pop(key, None)
            save_cache(QA_CACHE)
    return None


def get_corpus_id():
    """Generate a small fingerprint for the current vector DB so cache keys include the corpus state."""
    try:
        p = Path(VECTOR_PATH)
        if not p.exists():
            return "no_vector"
        items = []
        for f in sorted(p.glob("**/*")):
            if f.is_file():
                items.append(f.name + str(int(f.stat().st_mtime)))
        if not items:
            return "no_vector"
        s = "|".join(items)
        return hashlib.sha256(s.encode("utf-8")).hexdigest()
    except Exception:
        return "no_vector"


def load_vector_db_if_needed():
    """Load the FAISS vector DB into the global VECTOR_DB once."""
    global VECTOR_DB
    if VECTOR_DB is not None:
        return VECTOR_DB
    try:
        if os.path.exists(VECTOR_PATH):
            embeddings = OpenAIEmbeddings(api_key=OPENAI_KEY)
            VECTOR_DB = FAISS.load_local(VECTOR_PATH, embeddings, allow_dangerous_deserialization=True)
            print("📂 Vector DB cargado en memoria.")
            return VECTOR_DB
    except Exception as e:
        print("⚠ Error cargando Vector DB en memoria:", e)
        VECTOR_DB = None
    return None


# ==========================================================
# 🗄 FUNCIONES SUPABASE
# ==========================================================
def save_document_to_db(filename: str, file_path: str, corpus_id: str):
    """Guarda información del documento en Supabase."""
    if not supabase:
        return False
    try:
        data = {
            "id": str(uuid.uuid4()),
            "filename": filename,
            "file_path": file_path,
            "corpus_id": corpus_id,
            "created_at": datetime.now().isoformat(),
            "status": "processed"
        }
        result = supabase.table("documents").insert(data).execute()
        print(f"✅ Documento guardado en DB: {filename}")
        return True
    except Exception as e:
        print(f"⚠ Error guardando documento: {e}")
        return False


def save_conversation_to_db(user_question: str, bot_response: str, sources: list, confidence: str, evidence: list, cross_references: list):
    """Guarda la conversación en Supabase."""
    if not supabase:
        return False
    try:
        data = {
            "id": str(uuid.uuid4()),
            "user_question": user_question,
            "bot_response": bot_response,
            "sources": json.dumps(sources) if sources else "[]",
            "confidence": confidence,
            "evidence": json.dumps(evidence) if evidence else "[]",
            "cross_references": json.dumps(cross_references) if cross_references else "[]",
            "created_at": datetime.now().isoformat(),
            "corpus_id": get_corpus_id()
        }
        result = supabase.table("conversations").insert(data).execute()
        return True
    except Exception as e:
        print(f"⚠ Error guardando conversación: {e}")
        return False


def get_conversation_history(limit: int = 10):
    """Obtiene el historial de conversaciones desde Supabase."""
    if not supabase:
        return []
    try:
        result = supabase.table("conversations").select("*").order("created_at", desc=True).limit(limit).execute()
        return result.data
    except Exception as e:
        print(f"⚠ Error obteniendo historial: {e}")
        return []


# ==========================================================
# 🔧 PRUEBA AUTOMÁTICA DE API
# ==========================================================
try:
    test = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Hola, ¿funcionas?"}]
    )
    print("OpenAI funcionando →", test.choices[0].message.content)
except Exception as e:
    print("❌ Error al probar OpenAI:", e)


# ==========================================================
# 📄 CARGAR Y VECTORIZAR DOCUMENTOS
# ==========================================================
def procesar_documento(file_path, filename=""):
    """Procesa un documento optimizado para velocidad y eficiencia."""
    try:
        ext = file_path.split(".")[-1].lower()
        
        # Cargar documento con configuraciones optimizadas
        if ext == "pdf":
            loader = PyPDFLoader(file_path)
        elif ext == "txt":
            loader = TextLoader(file_path, encoding='utf-8', autodetect_encoding=True)
        elif ext == "docx":
            loader = Docx2txtLoader(file_path)
        else:
            return False, f"❌ Tipo de archivo no soportado: {ext}"

        print(f"📄 Cargando {filename or file_path}...")
        docs = loader.load()
        
        # Verificar que se cargó contenido
        if not docs or not any(doc.page_content.strip() for doc in docs):
            return False, "❌ El documento no contiene texto legible"
        
        total_chars = sum(len(doc.page_content) for doc in docs)
        print(f"📊 Documento cargado: {total_chars:,} caracteres")
        
        # Chunking optimizado - tamaño dinámico basado en el documento
        if total_chars < 10000:  # Documento pequeño
            chunk_size = 600
            chunk_overlap = 50
        elif total_chars < 50000:  # Documento mediano
            chunk_size = 800 
            chunk_overlap = 100
        else:  # Documento grande
            chunk_size = 1000
            chunk_overlap = 150
            
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, 
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
        )
        chunks = splitter.split_documents(docs)
        print(f"✂️ Creados {len(chunks)} chunks (tamaño: {chunk_size})")
        
        # Añadir metadatos mejorados a los chunks
        for i, chunk in enumerate(chunks):
            chunk.metadata.update({
                "source": filename or os.path.basename(file_path),
                "chunk_id": i,
                "chunk_size": len(chunk.page_content),
                "file_type": ext,
                "processed_at": datetime.now().isoformat()
            })
        
        print("🔢 Generando embeddings optimizados...")
        embeddings = OpenAIEmbeddings(
            api_key=OPENAI_KEY,
            chunk_size=500,  # Reducir tamaño de lote para mayor velocidad
            max_retries=2,   # Reducir reintentos para mayor velocidad
            request_timeout=10  # Timeout más corto
        )
        
        # Crear o actualizar vector DB
        global VECTOR_DB
        if VECTOR_DB is None:
            VECTOR_DB = FAISS.from_documents(chunks, embeddings)
            print("🏗️ Vector DB creado")
        else:
            # Añadir chunks a DB existente
            new_vectors = FAISS.from_documents(chunks, embeddings)
            VECTOR_DB.merge_from(new_vectors)
            print("➕ Chunks añadidos a Vector DB existente")
        
        VECTOR_DB.save_local(VECTOR_PATH)
        print(f"💾 Vector DB guardado en {VECTOR_PATH}")
        
        return True, f"✅ {filename or 'Documento'} procesado: {len(chunks)} chunks creados"
        
    except Exception as e:
        print(f"❌ Error procesando {filename or file_path}: {e}")
        return False, f"❌ Error procesando archivo: {str(e)[:100]}"


# ==========================================================
# 🤖 MODELO DE CLÚSTERS
# ==========================================================
app = Flask(__name__)

# Configuración para carga de archivos
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB máximo total
app.config['UPLOAD_FOLDER'] = 'uploads'
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB por archivo
MAX_FILES = 3  # máximo 3 archivos
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_corpus_id():
    """Genera o retorna un ID único para el corpus actual"""
    corpus_file = os.path.join("vector_db", "corpus_id.txt")
    try:
        if os.path.exists(corpus_file):
            with open(corpus_file, 'r') as f:
                return f.read().strip()
        else:
            # Crear nuevo ID basado en timestamp
            new_id = f"corpus_{int(time.time())}"
            os.makedirs("vector_db", exist_ok=True)
            with open(corpus_file, 'w') as f:
                f.write(new_id)
            return new_id
    except Exception as e:
        print(f"⚠ Error con corpus_id: {e}")
        return f"corpus_{int(time.time())}"

model, vectorizer = load_model()

if model is None:
    model, vectorizer = build_and_train_model(training_data, n_clusters=6)

# Sistema de respuestas profesionales mejorado
# Las respuestas ahora se manejan desde chatbot/responses.py
# Mapeo de clusters a tipos de respuesta
CLUSTER_TO_RESPONSE_TYPE = {
    0: "saludo",
    1: "despedida", 
    2: "aclaracion_rol",
    3: "carga_documentos",
    4: "despedida",
    5: "no_entiendo"
}

# ==========================================================
# 🌐 RUTAS FLASK
# ==========================================================
@app.route("/")
def home():
    return render_template("index.html")


# --- SUBIR DOCUMENTO ---
@app.route("/upload", methods=["POST"])
def upload():
    try:
        # Verificar que se enviaron archivos
        if 'files' not in request.files:
            return jsonify({"success": False, "message": "❌ No se enviaron archivos"})
        
        files = request.files.getlist('files')
        
        # Validaciones
        if len(files) == 0:
            return jsonify({"success": False, "message": "❌ Selecciona al menos un archivo"})
        
        if len(files) > MAX_FILES:
            return jsonify({"success": False, "message": f"❌ Máximo {MAX_FILES} archivos permitidos"})
        
        # Validar cada archivo
        valid_files = []
        total_size = 0
        
        for file in files:
            if file.filename == "":
                continue
                
            # Validar extensión
            if not allowed_file(file.filename):
                return jsonify({"success": False, "message": f"❌ Tipo no permitido: {file.filename}"})
            
            # Validar tamaño (simular leyendo el archivo)
            file.seek(0, 2)  # ir al final
            file_size = file.tell()
            file.seek(0)  # volver al inicio
            
            if file_size > MAX_FILE_SIZE:
                size_mb = file_size / (1024 * 1024)
                max_mb = MAX_FILE_SIZE / (1024 * 1024)
                return jsonify({"success": False, "message": f"❌ {file.filename} es muy grande ({size_mb:.1f}MB). Máximo: {max_mb}MB"})
            
            total_size += file_size
            valid_files.append((file, file_size))
        
        if not valid_files:
            return jsonify({"success": False, "message": "❌ No hay archivos válidos"})
        
        # Procesar archivos
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        results = []
        processed_files = []
        
        for file, file_size in valid_files:
            # Generar nombre único para evitar conflictos
            timestamp = int(time.time())
            safe_filename = f"{timestamp}_{file.filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
            
            try:
                file.save(file_path)
                size_mb = file_size / (1024 * 1024)
                print(f"💾 Guardado: {file.filename} ({size_mb:.1f}MB)")
                
                # Procesar documento
                success, message = procesar_documento(file_path, file.filename)
                
                if success:
                    processed_files.append(file.filename)
                    # Guardar info en Supabase
                    try:
                        save_document_to_db(file.filename, file_path, get_corpus_id())
                    except Exception as e:
                        print(f"⚠ Error guardando en Supabase: {e}")
                
                results.append({
                    "filename": file.filename,
                    "success": success,
                    "message": message,
                    "size_mb": round(size_mb, 1)
                })
                
            except Exception as e:
                results.append({
                    "filename": file.filename,
                    "success": False,
                    "message": f"❌ Error: {str(e)[:50]}",
                    "size_mb": round(file_size / (1024 * 1024), 1)
                })
        
        # Recargar vector DB en memoria
        try:
            load_vector_db_if_needed()
        except Exception as e:
            print(f"⚠ Error recargando Vector DB: {e}")
        
        # Preparar respuesta
        successful = len(processed_files)
        total = len(results)
        
        if successful == total:
            message = f"✅ {successful} archivo(s) procesado(s) correctamente"
            success = True
        elif successful > 0:
            message = f"⚠ {successful}/{total} archivos procesados. Ver detalles."
            success = True
        else:
            message = "❌ No se pudo procesar ningún archivo"
            success = False
        
        return jsonify({
            "success": success,
            "message": message,
            "processed_files": processed_files,
            "details": results,
            "total_processed": successful,
            "total_files": total
        })
        
    except Exception as e:
        print(f"❌ Error en upload: {e}")
        return jsonify({"success": False, "message": f"❌ Error del servidor: {str(e)[:100]}"})


# --- CHAT ---
@app.route("/chat", methods=["POST"])
def chat():
    start_time = time.time()
    user_text = request.form.get("message", "").strip()

    if not user_text:
        return jsonify({"response": "Por favor escribe algo 😅"})
    
    print(f"🔍 Consulta recibida: {user_text[:100]}...")

    # Detectar peticiones triviales (saludos, agradecimientos) y manejar localmente
    lower = user_text.lower()
    tokens = re.findall(r"\w+", lower)
    greeting_keywords = {"hola", "buenos", "buenas", "hey", "saludos", "gracias", "adios", "adiós", "chao", "hasta", "luego", "nos", "nos vemos"}
    if any(tok in greeting_keywords for tok in tokens) or lower in ("hola", "gracias", "buenas", "buenos días", "buenas tardes", "buenas noches", "adiós", "adios", "chao"):
        # usar el modelo de clústers o respuestas predefinidas para respuestas cortas
        try:
            cluster = predict_cluster(model, vectorizer, user_text)
            # Usar el nuevo sistema de respuestas profesionales
            response_type = CLUSTER_TO_RESPONSE_TYPE.get(cluster, "no_entiendo")
            response = get_respuesta_by_tipo(response_type)
            return jsonify({"response": response})
        except Exception:
            return jsonify({"response": "Hola — ¿en qué puedo ayudarte?"})

    # Detectar si es una petición de aclaración / simplificación
    clarify_keywords = ["explica", "explicame", "sin tecnicismos", "en otras palabras", "no entiendo", "simplifica", "resumen", "resume", "parafrasea", "más simple", "nivel sencillo"]
    is_clarify = any(kw in lower for kw in clarify_keywords)

    # ==========================================================
    # 1️⃣ RAG (si existe base vectorial)
    # ==========================================================
    vector_db = load_vector_db_if_needed()
    if vector_db is not None:
        try:
            # antes de llamar a la API, chequear cache por pregunta+corpus
            corpus_id = get_corpus_id()
            cache_key = make_key(user_text + "|" + corpus_id)
            
            # Verificar cache inteligente
            cached_response = get_cached_response(cache_key)
            if cached_response:
                print(f"🚀 Respuesta desde cache para: {user_text[:50]}...")
                return jsonify(cached_response)

            # obtener documentos relevantes con score optimizado desde FAISS
            # si es una petición de aclaración, aumentar k para recuperar más contexto
            k = 8 if is_clarify else 4
            # results devuelve una lista de tuplas (Document, score)
            results = vector_db.similarity_search_with_score(user_text, k=k)
            
            # Filtrar resultados por score de relevancia (menor score = más relevante)
            filtered_results = [(d, s) for d, s in results if s < 1.0]  # Solo resultados relevantes
            if not filtered_results:
                filtered_results = results[:2]  # Al menos 2 resultados como fallback
            
            # Comprimir contexto eliminando redundancias
            seen_content = set()
            unique_docs = []
            for d, s in filtered_results:
                # Crear hash del contenido para detectar duplicados
                content_hash = hashlib.md5(d.page_content.encode()).hexdigest()
                if content_hash not in seen_content:
                    seen_content.add(content_hash)
                    unique_docs.append((d, s))
            
            contexto = "\n\n--- SECCIÓN ---\n".join([d.page_content for d, s in unique_docs])
            print(f"📋 Contexto optimizado: {len(unique_docs)} secciones únicas")

            # construir lista de fuentes con metadatos para devolver al frontend
            sources = []
            for d, s in results:
                metadata = d.metadata if hasattr(d, 'metadata') else {}
                sources.append({
                    "text_snippet": d.page_content[:500],
                    "source": metadata.get("source", metadata.get("source_id", "unknown")),
                    "page": metadata.get("page", None),
                    "score": float(s)
                })

            # Heurística simple para calcular 'confidence' a partir de las puntuaciones de FAISS
            # Asumimos que FAISS devuelve distancias (valores más bajos => más cercanos/relevantes).
            derived_confidence = None
            try:
                scores = [abs(item.get("score", 0)) for item in sources if item.get("score") is not None]
                if len(scores) > 0:
                    min_score = min(scores)
                    conf_value = 1.0 / (1.0 + min_score)
                    if conf_value > 0.7:
                        derived_confidence = "alta"
                    elif conf_value > 0.4:
                        derived_confidence = "media"
                    else:
                        derived_confidence = "baja"
                else:
                    derived_confidence = "baja"
            except Exception:
                derived_confidence = "baja"

            # Prompt optimizado para respuestas concretas y específicas
            prompt_template = """
Eres un asistente legal experto. Proporciona respuestas CONCRETAS, ESPECÍFICAS y DIRECTAS usando ÚNICAMENTE el CONTEXTO proporcionado.

FORMATO DE RESPUESTA REQUERIDO:
✅ CONCISIÓN: Máximo 3-4 párrafos, directo al punto
✅ ESPECIFICIDAD: Menciona artículos, secciones, números exactos cuando estén disponibles
✅ ESTRUCTURA: Organiza la respuesta con puntos clave numerados si es complejo
✅ EVIDENCIA: Incluye citas textuales exactas entre comillas
✅ CONEXIONES: Si hay información relacionada en diferentes secciones, conéctala claramente

REGLAS ESTRICTAS:
- NO uses frases genéricas como "según el documento" - SÉ ESPECÍFICO
- NO repitas información - SINTETIZA
- SI no hay información suficiente: indica QUÉ información específica falta
- SIEMPRE incluye números de artículo/sección cuando estén disponibles

Devuelve ÚNICAMENTE un objeto JSON válido:
{{
  "answer": "Respuesta directa y específica con números de artículo/sección",
  "key_points": ["Punto clave 1 con referencia específica", "Punto clave 2", "Punto clave 3"],
  "specific_articles": ["Art. X", "Sección Y", "Párrafo Z"],
  "exact_quotes": ["Cita textual exacta 1", "Cita textual exacta 2"],
  "confidence": "alta|media|baja",
  "missing_info": "Qué información específica falta (si aplica)",
  "cross_references": ["Conexión específica entre secciones"]
}}

--- CONTEXTO ---
{contexto}
--- PREGUNTA ---
{user_text}
"""

            # si es clarificación, añadir instrucción para simplificar el lenguaje
            prompt = prompt_template.format(contexto=contexto, user_text=user_text)
            if is_clarify:
                prompt += "\n\nIMPORTANTE: Si la petición es una aclaración o simplificación, responde en lenguaje sencillo, sin tecnicismos, manteniendo la precisión y basándote en el CONTEXTO."

            try:
                ai_response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "Eres un asistente útil y preciso. Responde en JSON según lo solicitado."},
                        {"role": "user", "content": prompt}
                    ]
                )
            except Exception as e:
                # si falla la conexión con OpenAI, intentar devolver cache si existe
                print("⚠ Error en RAG:", e)
                if cache_key in QA_CACHE:
                    return jsonify(QA_CACHE[cache_key])
                return jsonify({"response": "Error: no se pudo conectar al servicio de IA. Intenta de nuevo más tarde.", "error": str(e)})

            respuesta_gpt = ai_response.choices[0].message.content

            # Intentar parsear la respuesta como JSON estructurado.
            # Si no es JSON puro, intentar extraer el primer objeto JSON dentro del texto.
            parsed = None
            try:
                parsed = json.loads(respuesta_gpt)
            except Exception:
                # limpiar fences y buscar primer { ... }
                clean = respuesta_gpt.strip()
                # remover fences ```json ... ``` y ``` ... ```
                clean = re.sub(r"```\w*", "", clean)
                # localizar la primera { y la última }
                start = clean.find('{')
                end = clean.rfind('}')
                if start != -1 and end != -1 and end > start:
                    try:
                        candidate = clean[start:end+1]
                        parsed = json.loads(candidate)
                    except Exception:
                        parsed = None

            if parsed:
                answer = parsed.get("answer", parsed.get("response", None))
                
                # Si el LLM devolvió NO_ENCONTRADO, convertirlo a mensaje más amigable
                if answer and (answer.strip().upper() == "NO_ENCONTRADO" or "no encuentro" in answer.lower()):
                    missing_info = parsed.get("missing_info", "")
                    if missing_info:
                        answer = f"No encuentro información específica sobre esa consulta. Necesitaría más detalles sobre: {missing_info}"
                    else:
                        answer = "Lo siento, no encuentro información específica sobre esa consulta en el documento actual. ¿Podrías ser más específico?"
                
                # Extraer nueva estructura de respuesta
                key_points = parsed.get("key_points", [])
                specific_articles = parsed.get("specific_articles", [])
                exact_quotes = parsed.get("exact_quotes", [])
                missing_info = parsed.get("missing_info", "")
                
                parsed_sources = parsed.get("sources", sources)
                confidence = parsed.get("confidence", None) or derived_confidence
                cross_references = parsed.get("cross_references", [])
                
                # Payload mejorado con nueva estructura
                payload = {
                    "response": answer,
                    "key_points": key_points,
                    "specific_articles": specific_articles,
                    "exact_quotes": exact_quotes,
                    "sources": parsed_sources, 
                    "confidence": confidence, 
                    "cross_references": cross_references,
                    "missing_info": missing_info,
                    "response_time": f"{time.time() - start_time:.2f}s" if 'start_time' in locals() else "N/A"
                }
                
                # guardar en cache y Supabase
                try:
                    save_conversation_to_db(user_text, answer, parsed_sources, confidence, exact_quotes, cross_references)
                except Exception as e:
                    print(f"⚠ Error guardando en Supabase: {e}")
                
                print(f"✅ Respuesta generada: {len(answer)} chars, {len(key_points)} puntos clave")
                return respond_and_cache(cache_key, payload)
            else:
                # fallback: LLM no devolvió JSON; intentar extraer texto plano legible
                text_ans = respuesta_gpt.strip()
                # si el texto es un JSON textual mostrado, intentar extraer answer con regex
                m = re.search(r'"answer"\s*:\s*"([^"]+)"', text_ans)
                if m:
                    text_only = m.group(1)
                    # Convertir NO_ENCONTRADO a mensaje amigable
                    if text_only.strip().upper() == "NO_ENCONTRADO":
                        text_only = "Lo siento, no encuentro información específica sobre esa consulta en el documento actual. ¿Podrías reformular tu pregunta?"
                else:
                    # quitar saltos y limitar longitud
                    text_only = text_ans[:2000]
                    # Si contiene NO_ENCONTRADO, reemplazarlo
                    if "NO_ENCONTRADO" in text_only.upper():
                        text_only = "Lo siento, no encuentro información específica sobre esa consulta en el documento actual. ¿Podrías ser más específico sobre lo que buscas?"

                payload = {"response": text_only, "sources": sources, "confidence": derived_confidence}
                return respond_and_cache(cache_key, payload)

        except Exception as e:
            print("⚠ Error en RAG:", e)

    # ==========================================================
    # 2️⃣ GPT normal si no hay vector DB
    # ==========================================================
    try:
        ai_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Eres un asistente amable y útil."},
                {"role": "user", "content": user_text}
            ]
        )
        respuesta_gpt = ai_response.choices[0].message.content
        return jsonify({"response": respuesta_gpt})

    except Exception as e:
        print("⚠ Error con OpenAI:", e)

    # ==========================================================
    # 3️⃣ Backup con clústers
    # ==========================================================
    cluster = predict_cluster(model, vectorizer, user_text)
    response = random.choice(
        [get_respuesta_by_tipo(CLUSTER_TO_RESPONSE_TYPE.get(cluster, "no_entiendo"))]
    )
    return jsonify({"response": response})


# --- HISTORIAL ---
@app.route("/history", methods=["GET"])
def history():
    """Devuelve el historial de conversaciones."""
    try:
        conversations = get_conversation_history(20)  # últimas 20 conversaciones
        # Limpiar y formatear datos para el frontend
        formatted_history = []
        for conv in conversations:
            formatted_history.append({
                "id": conv.get("id"),
                "question": conv.get("user_question"),
                "response": conv.get("bot_response"),
                "confidence": conv.get("confidence"),
                "timestamp": conv.get("created_at"),
                "has_cross_refs": bool(conv.get("cross_references") and conv.get("cross_references") != "[]")
            })
        return jsonify({"history": formatted_history})
    except Exception as e:
        print(f"⚠ Error obteniendo historial: {e}")
        return jsonify({"history": [], "error": "No se pudo obtener el historial"})


# ==========================================================
# 🚀 EJECUTAR SERVIDOR
# ==========================================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
