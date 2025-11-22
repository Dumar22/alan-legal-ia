const form = document.getElementById("chatForm");
const input = document.getElementById("userInput");
const messages = document.getElementById("messages");
const sourcesList = document.getElementById("sourcesList");
const confidenceBadge = document.getElementById("confidenceBadge");

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const text = input.value.trim();
  if (!text) return;

  appendMessage("Tú", text, "user");
  input.value = "";

  appendMessage("Bot", "…procesando", "bot loading");
  const response = await fetch("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: `message=${encodeURIComponent(text)}`
  });

  const data = await response.json();
  // quitar el mensaje de loading anterior
  removeLoadingMessages();

  appendMessage("Bot", data.response || "(sin respuesta)", "bot");

  // mostrar confianza
  if (data.confidence) {
    confidenceBadge.textContent = `Confianza: ${data.confidence}`;
    confidenceBadge.className = `badge ${data.confidence}`;
  } else {
    confidenceBadge.textContent = `Confianza: —`;
    confidenceBadge.className = `badge unknown`;
  }

  // mostrar fuentes
  sourcesList.innerHTML = "";
  if (Array.isArray(data.sources) && data.sources.length > 0) {
    data.sources.forEach((s, idx) => {
      const div = document.createElement("div");
      div.className = "source-item";
      const src = s.source || s.source_id || "unknown";
      const page = s.page !== undefined && s.page !== null ? ` (p. ${s.page})` : "";
      const score = s.score !== undefined ? ` — score: ${Number(s.score).toFixed(3)}` : "";
      div.innerHTML = `
        <div class=\"source-header\">Fuente ${idx+1}: <strong>${escapeHtml(src)}</strong>${page}${score}</div>
        <div class=\"source-snippet\">${escapeHtml(s.text_snippet || '')}</div>
      `;
      sourcesList.appendChild(div);
    });
  } else {
    sourcesList.innerHTML = `<div class=\"no-sources\">No se encontraron fuentes relevantes.</div>`;
  }

  messages.scrollTop = messages.scrollHeight;
});

function appendMessage(who, text, cls) {
  const el = document.createElement("div");
  el.className = `msg ${cls}`;
  el.textContent = `${who}: ${text}`;
  messages.appendChild(el);
  messages.scrollTop = messages.scrollHeight;
}

function removeLoadingMessages() {
  const loading = document.querySelectorAll('.loading');
  loading.forEach(n => n.remove());
}

function escapeHtml(unsafe) {
  return unsafe
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\"/g, "&quot;")
    .replace(/'/g, "&#039;");
}


// Subir documento
const uploadForm = document.getElementById("uploadForm");
const uploadStatus = document.getElementById("uploadStatus");

uploadForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const file = document.getElementById("fileInput").files[0];
  if (!file) {
    uploadStatus.innerHTML = "❌ Selecciona un archivo.";
    return;
  }

  uploadStatus.innerHTML = "⬆️ Subiendo...";
  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await fetch("/upload", {
      method: "POST",
      body: formData
    });
    const data = await response.json();
    uploadStatus.innerHTML = "📌 " + data.message;
  } catch (err) {
    uploadStatus.innerHTML = "❌ Error al subir archivo.";
  }
});
