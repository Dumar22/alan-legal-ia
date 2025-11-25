# 🔧 Instrucciones para Configurar Render

## Problema Resuelto
El error `ModuleNotFoundError: No module named 'app'` se debe a que Render estaba buscando un archivo `app.py` pero la aplicación está en `main.py`.

## ✅ Soluciones Implementadas

### 1. Procfile Actualizado
```
web: gunicorn main:app
```

### 2. Archivo app.py Creado
- Punto de entrada alternativo que importa desde `main.py`
- Compatible con servidores WSGI estándar

### 3. Configuración de Gunicorn
- `gunicorn.conf.py` para optimización de producción
- Configuración de workers, timeouts, y logging

## 🚀 Configuración en Render

### Start Command (Elige UNA opción):

**Opción 1 (Recomendada - Simple):**
```
gunicorn main:app
```

**Opción 2 (Con configuración):**
```
gunicorn main:app --config gunicorn.conf.py
```

**Opción 3 (Manual con parámetros):**
```
gunicorn main:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120
```

**Opción 4 (Con app.py):**
```
gunicorn app:app
```

### Variables de Entorno Necesarias:
```
OPENAI_API_KEY=tu_api_key_aqui
SUPABASE_URL=https://...
SUPABASE_ANON_KEY=eyJ...
FLASK_ENV=production
```

## 🔍 Verificación
Después del deploy exitoso, la aplicación debería estar disponible en:
- https://tu-app.onrender.com/

## 🆘 Si Sigue Fallando
1. Usar Start Command: `python main.py`
2. Verificar que todas las variables de entorno están configuradas
3. Revisar logs en Render dashboard para errores específicos

## ✨ Beneficios de Gunicorn vs Python directo
- Mejor manejo de concurrencia
- Más estable bajo carga
- Mejor para producción
- Auto-restart en caso de errores