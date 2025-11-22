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

# ==========================================================
# 🔐 VARIABLES DE ENTORNO (CARGAR ANTES DE USAR OPENAI)
# ==========================================================
from dotenv import load_dotenv
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path, override=True)

OPENAI_KEY = os.getenv("OPENAI_API_KEY")
print("API KEY DETECTADA:", OPENAI_KEY)

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


def respond_and_cache(key: str, payload: dict):
    # normalize stored payload and include timestamp
    stored = payload.copy()
    stored.setdefault("sources", [])
    stored.setdefault("confidence", None)
    stored["timestamp"] = int(time.time())
    QA_CACHE[key] = stored
    save_cache(QA_CACHE)
    return jsonify(stored)


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
def procesar_documento(file_path):
    ext = file_path.split(".")[-1].lower()

    if ext == "pdf":
        loader = PyPDFLoader(file_path)
    elif ext == "txt":
        loader = TextLoader(file_path)
    elif ext == "docx":
        loader = Docx2txtLoader(file_path)
    else:
        return None, f"❌ Tipo de archivo no soportado: {ext}"

    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    chunks = splitter.split_documents(docs)

    embeddings = OpenAIEmbeddings(api_key=OPENAI_KEY)
    vector_db = FAISS.from_documents(chunks, embeddings)

    vector_db.save_local(VECTOR_PATH)

    return True, "Documento procesado correctamente."


# ==========================================================
# 🤖 MODELO DE CLÚSTERS
# ==========================================================
app = Flask(__name__)
model, vectorizer = load_model()

if model is None:
    model, vectorizer = build_and_train_model(training_data, n_clusters=6)

RESPUESTAS = {
    0: ["¡Hola! 😊 ¿Cómo estás?", "¡Qué gusto saludarte!", "¿En qué puedo ayudarte hoy?"],
    1: ["Hasta luego 👋", "Nos vemos pronto.", "¡Cuídate! 😊"],
    2: ["Soy un asistente virtual creado para ayudarte 💻", "Pregúntame lo que quieras 😉"],
    3: ["¡Claro! ¿En qué puedo ayudarte?", "Cuéntame tu problema 🤖"],
    4: ["¡Gracias a ti! ❤️", "Me alegra ser de ayuda 😄"],
    5: ["Lamento eso 😔, puedo intentarlo nuevamente.", "Parece que algo no salió bien 😅"],
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
    if "file" not in request.files:
        return jsonify({"message": "❌ No enviaste archivo"})

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"message": "❌ Nombre de archivo vacío"})

    path = os.path.join("uploads", file.filename)
    os.makedirs("uploads", exist_ok=True)
    file.save(path)

    ok, msg = procesar_documento(path)
    # después de procesar, recargar vector DB en memoria para evitar recargas por cada petición
    try:
        load_vector_db_if_needed()
    except Exception as _:
        pass
    return jsonify({"message": msg})


# --- CHAT ---
@app.route("/chat", methods=["POST"])
def chat():
    user_text = request.form.get("message", "").strip()

    if not user_text:
        return jsonify({"response": "Por favor escribe algo 😅"})

    # Detectar peticiones triviales (saludos, agradecimientos) y manejar localmente
    lower = user_text.lower()
    tokens = re.findall(r"\w+", lower)
    greeting_keywords = {"hola", "buenos", "buenas", "hey", "saludos", "gracias", "adios", "adiós", "chao", "hasta", "luego", "nos", "nos vemos"}
    if any(tok in greeting_keywords for tok in tokens) or lower in ("hola", "gracias", "buenas", "buenos días", "buenas tardes", "buenas noches", "adiós", "adios", "chao"):
        # usar el modelo de clústers o respuestas predefinidas para respuestas cortas
        try:
            cluster = predict_cluster(model, vectorizer, user_text)
            response = random.choice(RESPUESTAS.get(cluster, ["¡Hola! ¿En qué puedo ayudarte?"]))
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
            if cache_key in QA_CACHE:
                # devolver respuesta cacheada sin llamar al LLM
                cached = QA_CACHE[cache_key]
                return jsonify(cached)

            # obtener documentos relevantes con score desde FAISS
            # si es una petición de aclaración, aumentar k para recuperar más contexto
            k = 6 if is_clarify else 3
            # results devuelve una lista de tuplas (Document, score)
            results = vector_db.similarity_search_with_score(user_text, k=k)

            contexto = "\n\n".join([d.page_content for d, s in results])

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

            # Prompt mejorado: pedimos una salida JSON estructurada para evitar ambigüedades
            prompt_template = """
Actúa como un asistente legal especializado. Usa EXCLUSIVAMENTE la información dentro del bloque CONTEXTO para responder. No inventes información.

Devuelve SOLO un objeto JSON con las claves:
- answer: cadena (respuesta útil y precisa). Si la información específica no está en el contexto, responde de manera amigable explicando que no encuentras esa información particular en el documento actual, pero sugiere reformular la pregunta o indica qué tipo de información sí está disponible.
- sources: lista de objetos {{text_snippet, source, page, score}} (puede estar vacía).
- confidence: una etiqueta entre "alta", "media" o "baja".
- evidence: lista con 0-2 citas textuales exactas extraídas del CONTEXTO.

El JSON debe ser el único contenido de la respuesta, sin explicaciones adicionales.

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
                if answer and answer.strip().upper() == "NO_ENCONTRADO":
                    answer = "Lo siento, no encuentro información específica sobre esa consulta en el documento actual. ¿Podrías reformular tu pregunta o ser más específico sobre lo que buscas?"
                
                parsed_sources = parsed.get("sources", sources)
                confidence = parsed.get("confidence", None) or derived_confidence
                evidence = parsed.get("evidence", [])
                payload = {"response": answer, "sources": parsed_sources, "confidence": confidence, "evidence": evidence}
                # guardar en cache con clave que incluye corpus_id
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
        RESPUESTAS.get(cluster, ["No estoy seguro de entender 😅, pero puedo intentarlo otra vez."])
    )
    return jsonify({"response": response})


# ==========================================================
# 🚀 EJECUTAR SERVIDOR
# ==========================================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
