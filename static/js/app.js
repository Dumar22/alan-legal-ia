const form = document.getElementById("chatForm");
const input = document.getElementById("userInput");
const messages = document.getElementById("messages");
const sourcesList = document.getElementById("sourcesList");
const confidenceBadge = document.getElementById("confidenceBadge");
const micBtn = document.getElementById('micBtn');

// Speech Recognition setup (browser)
let recognition = null;
let recognizing = false;
if (window.SpeechRecognition || window.webkitSpeechRecognition) {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  recognition = new SR();
  recognition.lang = 'es-ES';
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    input.value = transcript;
    // submit automatically
    form.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
  };

  recognition.onend = () => {
    recognizing = false;
    if (micBtn) micBtn.classList.remove('listening');
  };
}

if (micBtn) {
  micBtn.addEventListener('click', () => {
    if (!recognition) {
      alert('Tu navegador no soporta reconocimiento por voz.');
      return;
    }

    if (recognizing) {
      recognition.stop();
      micBtn.classList.remove('listening');
      recognizing = false;
    } else {
      recognition.start();
      micBtn.classList.add('listening');
      recognizing = true;
    }
  });
}

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
  
  // Detectar si la respuesta viene del cache
  const isCached = data.cached === true;

  // Mostrar respuesta principal con indicador de cache si aplica
  const cacheIcon = isCached ? " 🚀" : "";
  appendMessage("Bot", data.response || "(sin respuesta)", "bot", cacheIcon);

  // Reproducir respuesta en audio (SpeechSynthesis)
  if (data.response && 'speechSynthesis' in window) {
    try {
      const utter = new SpeechSynthesisUtterance(data.response);
      utter.lang = 'es-ES';
      // elegir voz preferida si existe
      const voices = window.speechSynthesis.getVoices();
      if (voices && voices.length) {
        // preferir voces que incluyan 'Spanish' o 'es'
        const v = voices.find(v => /es|spanish/i.test(v.name) || /es/i.test(v.lang));
        if (v) utter.voice = v;
      }
      window.speechSynthesis.cancel();
      window.speechSynthesis.speak(utter);
    } catch (e) {
      console.warn('Error en síntesis de voz:', e);
    }
  }

  // Mostrar tiempo de respuesta si está disponible
  if (data.response_time) {
    const timeDiv = document.createElement("div");
    timeDiv.className = "response-time";
    timeDiv.innerHTML = `⚡ Tiempo de respuesta: ${data.response_time}`;
    messages.appendChild(timeDiv);
  }

  // mostrar confianza
  if (data.confidence) {
    confidenceBadge.textContent = `Confianza: ${data.confidence}`;
    confidenceBadge.className = `badge ${data.confidence}`;
  } else {
    confidenceBadge.textContent = `Confianza: —`;
    confidenceBadge.className = `badge unknown`;
  }

  // Mostrar información estructurada
  sourcesList.innerHTML = "";
  
  // Mostrar puntos clave si existen
  if (Array.isArray(data.key_points) && data.key_points.length > 0) {
    const keyPointsDiv = document.createElement("div");
    keyPointsDiv.className = "key-points";
    keyPointsDiv.innerHTML = `
      <h5>🎯 Puntos clave:</h5>
      <ul class="key-points-list">
        ${data.key_points.map(point => `<li>${escapeHtml(point)}</li>`).join('')}
      </ul>
    `;
    sourcesList.appendChild(keyPointsDiv);
  }
  
  // Mostrar artículos específicos si existen
  if (Array.isArray(data.specific_articles) && data.specific_articles.length > 0) {
    const articlesDiv = document.createElement("div");
    articlesDiv.className = "specific-articles";
    articlesDiv.innerHTML = `
      <h5>📋 Referencias específicas:</h5>
      <div class="articles-list">
        ${data.specific_articles.map(art => `<span class="article-tag">${escapeHtml(art)}</span>`).join('')}
      </div>
    `;
    sourcesList.appendChild(articlesDiv);
  }
  
  // Mostrar citas exactas si existen
  if (Array.isArray(data.exact_quotes) && data.exact_quotes.length > 0) {
    const quotesDiv = document.createElement("div");
    quotesDiv.className = "exact-quotes";
    quotesDiv.innerHTML = `
      <h5>💬 Citas exactas:</h5>
      <div class="quotes-list">
        ${data.exact_quotes.map(quote => `<blockquote>"${escapeHtml(quote)}"</blockquote>`).join('')}
      </div>
    `;
    sourcesList.appendChild(quotesDiv);
  }
  
  // Mostrar información faltante si existe
  if (data.missing_info && data.missing_info.trim()) {
    const missingDiv = document.createElement("div");
    missingDiv.className = "missing-info";
    missingDiv.innerHTML = `
      <h5>⚠️ Información adicional necesaria:</h5>
      <p>${escapeHtml(data.missing_info)}</p>
    `;
    sourcesList.appendChild(missingDiv);
  }

  // mostrar fuentes
  if (Array.isArray(data.sources) && data.sources.length > 0) {
    const sourcesDiv = document.createElement("div");
    sourcesDiv.className = "sources-section";
    sourcesDiv.innerHTML = `<h5>📚 Fuentes:</h5>`;
    
    data.sources.forEach((s, idx) => {
      const div = document.createElement("div");
      div.className = "source-item";
      const src = s.source || s.source_id || "unknown";
      const page = s.page !== undefined && s.page !== null ? ` (p. ${s.page})` : "";
      const score = s.score !== undefined ? ` — relevancia: ${(1/(1+s.score)*100).toFixed(0)}%` : "";
      div.innerHTML = `
        <div class="source-header">Fuente ${idx+1}: <strong>${escapeHtml(src)}</strong>${page}${score}</div>
        <div class="source-snippet">${escapeHtml(s.text_snippet || '')}</div>
      `;
      sourcesDiv.appendChild(div);
    });
    sourcesList.appendChild(sourcesDiv);
    
    // mostrar cross-references si existen
    if (Array.isArray(data.cross_references) && data.cross_references.length > 0) {
      const crossRefDiv = document.createElement("div");
      crossRefDiv.className = "cross-references";
      crossRefDiv.innerHTML = `
        <h5>🔗 Conexiones encontradas:</h5>
        <ul>
          ${data.cross_references.map(ref => `<li>${escapeHtml(ref)}</li>`).join('')}
        </ul>
      `;
      sourcesList.appendChild(crossRefDiv);
    }
  } else {
    sourcesList.innerHTML = `<div class="no-sources">No se encontraron fuentes relevantes.</div>`;
  }

  messages.scrollTop = messages.scrollHeight;
});

function appendMessage(who, text, cls, isCached = false) {
  const el = document.createElement("div");
  el.className = `msg ${cls}`;

  const cacheIndicator = isCached ? ' 🚀' : '';

  // If this is a loading message, build structured content with typing animation
  if (cls && cls.indexOf('loading') !== -1) {
    el.innerHTML = `
      <strong>${escapeHtml(who)}${cacheIndicator}:</strong>
      <div class="content">
        <div class="typing-dots">
          <span></span><span></span><span></span>
        </div>
      </div>
    `;
  } else {
    el.innerHTML = `<strong>${escapeHtml(who)}${cacheIndicator}:</strong> <div class="content">${escapeHtml(text)}</div>`;
  }

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


// Multi-file upload handler
const uploadForm = document.getElementById("uploadForm");
const uploadStatus = document.getElementById("uploadStatus");
const fileInput = document.getElementById("fileInput");
const filesList = document.getElementById("filesList");
const uploadBtn = document.getElementById("uploadBtn");
const uploadProgress = document.getElementById("uploadProgress");
const progressFill = document.querySelector(".progress-fill");
const progressText = document.querySelector(".progress-text");

let selectedFiles = [];

// Constantes de validación
const MAX_FILES = 3;
const MAX_FILE_SIZE = 16 * 1024 * 1024; // 16MB
const ALLOWED_EXTENSIONS = ['pdf', 'txt', 'docx'];

function formatFileSize(bytes) {
  if (bytes === 0) return '0 bytes';
  const k = 1024;
  const sizes = ['bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

function isValidFile(file) {
  const extension = file.name.split('.').pop().toLowerCase();
  return ALLOWED_EXTENSIONS.includes(extension);
}

function updateFilesList() {
  filesList.innerHTML = '';
  
  selectedFiles.forEach((file, index) => {
    const div = document.createElement('div');
    div.className = 'file-item';
    
    const isValid = isValidFile(file);
    const isTooLarge = file.size > MAX_FILE_SIZE;
    const hasError = !isValid || isTooLarge;
    
    let errorText = '';
    if (!isValid) errorText = 'Tipo no permitido';
    else if (isTooLarge) errorText = 'Muy grande (máx. 16MB)';
    
    div.innerHTML = `
      <div class="file-info">
        <span>📄 ${escapeHtml(file.name)}</span>
        <span class="file-size">${formatFileSize(file.size)}</span>
        ${errorText ? `<span class="file-error">${errorText}</span>` : ''}
      </div>
      <button type="button" class="file-remove" data-index="${index}">✕</button>
    `;
    
    if (hasError) {
      div.style.backgroundColor = '#fef2f2';
      div.style.borderColor = '#fca5a5';
    }
    
    filesList.appendChild(div);
  });
  
  // Actualizar estado del botón
  const validFiles = selectedFiles.filter(f => isValidFile(f) && f.size <= MAX_FILE_SIZE);
  uploadBtn.disabled = validFiles.length === 0;
  uploadBtn.textContent = `Subir ${validFiles.length} archivo(s)`;
}

fileInput.addEventListener('change', (e) => {
  const newFiles = Array.from(e.target.files);
  
  // Limitar número de archivos
  if (selectedFiles.length + newFiles.length > MAX_FILES) {
    uploadStatus.innerHTML = `⚠️ Máximo ${MAX_FILES} archivos permitidos`;
    uploadStatus.className = 'status warning';
    return;
  }
  
  // Agregar nuevos archivos evitando duplicados
  newFiles.forEach(file => {
    const isDuplicate = selectedFiles.some(f => f.name === file.name && f.size === file.size);
    if (!isDuplicate) {
      selectedFiles.push(file);
    }
  });
  
  updateFilesList();
  uploadStatus.innerHTML = '';
  uploadStatus.className = 'status';
  
  // Limpiar input
  e.target.value = '';
});

// Manejar remoción de archivos
filesList.addEventListener('click', (e) => {
  if (e.target.classList.contains('file-remove')) {
    const index = parseInt(e.target.dataset.index);
    selectedFiles.splice(index, 1);
    updateFilesList();
  }
});

uploadForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  
  const validFiles = selectedFiles.filter(f => isValidFile(f) && f.size <= MAX_FILE_SIZE);
  
  if (validFiles.length === 0) {
    uploadStatus.innerHTML = "❌ No hay archivos válidos para subir";
    uploadStatus.className = 'status error';
    return;
  }
  
  // Preparar FormData
  const formData = new FormData();
  validFiles.forEach(file => {
    formData.append('files', file);
  });
  
  // Mostrar progreso
  uploadBtn.disabled = true;
  uploadProgress.style.display = 'block';
  uploadStatus.innerHTML = '';
  progressFill.style.width = '0%';
  progressText.textContent = 'Iniciando...';
  
  try {
    // Simular progreso durante la subida
    const progressInterval = setInterval(() => {
      const currentWidth = parseFloat(progressFill.style.width) || 0;
      if (currentWidth < 90) {
        progressFill.style.width = (currentWidth + 10) + '%';
        progressText.textContent = `Procesando archivos... ${Math.round(currentWidth + 10)}%`;
      }
    }, 200);
    
    const response = await fetch("/upload", {
      method: "POST",
      body: formData
    });
    
    clearInterval(progressInterval);
    progressFill.style.width = '100%';
    progressText.textContent = 'Completado';
    
    const data = await response.json();
    
    // Mostrar resultados
    setTimeout(() => {
      uploadProgress.style.display = 'none';
      
      if (data.success) {
        uploadStatus.innerHTML = `✅ ${data.message}`;
        uploadStatus.className = 'status success';
        
        // Mostrar detalles si hay múltiples archivos
        if (data.details && data.details.length > 1) {
          let detailsHtml = '<br><small>';
          data.details.forEach(detail => {
            const icon = detail.success ? '✅' : '❌';
            detailsHtml += `${icon} ${detail.filename} (${detail.size_mb}MB)<br>`;
          });
          detailsHtml += '</small>';
          uploadStatus.innerHTML += detailsHtml;
        }
        
        // Limpiar archivos seleccionados
        selectedFiles = [];
        updateFilesList();
      } else {
        uploadStatus.innerHTML = `❌ ${data.message}`;
        uploadStatus.className = 'status error';
      }
      
      uploadBtn.disabled = false;
    }, 500);
    
  } catch (err) {
    clearInterval(progressInterval);
    uploadProgress.style.display = 'none';
    uploadStatus.innerHTML = "❌ Error de conexión al subir archivos";
    uploadStatus.className = 'status error';
    uploadBtn.disabled = false;
  }
});

// Funcionalidad de historial
const historyBtn = document.getElementById("historyBtn");
const historyModal = document.getElementById("historyModal");
const closeModal = document.querySelector(".close");
const historyList = document.getElementById("historyList");

historyBtn.addEventListener("click", async () => {
  try {
    const response = await fetch("/history");
    const data = await response.json();
    
    historyList.innerHTML = "";
    if (data.history && data.history.length > 0) {
      data.history.forEach(conv => {
        const div = document.createElement("div");
        div.className = "history-item";
        const date = new Date(conv.timestamp).toLocaleString();
        const crossRefIndicator = conv.has_cross_refs ? " 🔗" : "";
        div.innerHTML = `
          <div class="history-question">${escapeHtml(conv.question)}${crossRefIndicator}</div>
          <div class="history-response">${escapeHtml(conv.response)}</div>
          <div class="history-meta">${date} - Confianza: ${conv.confidence || 'N/A'}</div>
        `;
        historyList.appendChild(div);
      });
    } else {
      historyList.innerHTML = "<p>No hay conversaciones previas.</p>";
    }
    
    historyModal.style.display = "block";
  } catch (err) {
    console.error("Error cargando historial:", err);
    historyList.innerHTML = "<p>Error cargando historial.</p>";
    historyModal.style.display = "block";
  }
});

closeModal.addEventListener("click", () => {
  historyModal.style.display = "none";
});

window.addEventListener("click", (event) => {
  if (event.target === historyModal) {
    historyModal.style.display = "none";
  }
});
