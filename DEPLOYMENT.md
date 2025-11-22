# Alana Legal Sense - Despliegue en Render.com

## 🚀 Pasos para Desplegar

### 1. Preparar el repositorio en GitHub

Asegúrate de que tu repositorio esté actualizado:

```bash
git add .
git commit -m "Preparar para despliegue - Alana Legal Sense"
git push origin main
```

### 2. Configurar en Render.com

1. **Crear cuenta**: Ve a [render.com](https://render.com) y crea una cuenta
2. **Conectar GitHub**: Autoriza el acceso a tu repositorio
3. **Crear Web Service**: 
   - New → Web Service
   - Conectar tu repositorio `alan-legal-ia`
   - Configuración:
     - **Name**: `alana-legal-sense`
     - **Environment**: `Python 3`
     - **Build Command**: `./build.sh`
     - **Start Command**: `python main.py`

### 3. Variables de Entorno

En Render, configura estas variables de entorno:

```
OPENAI_API_KEY=tu_clave_openai_aqui
SUPABASE_URL=tu_url_supabase_aqui  
SUPABASE_ANON_KEY=tu_clave_supabase_aqui
FLASK_ENV=production
PORT=10000
```

### 4. Configuración de Dominio

- Render te dará un dominio gratuito: `alana-legal-sense.onrender.com`
- Opcional: Puedes conectar tu propio dominio personalizado

### 5. Monitoreo y Logs

- Render proporciona logs en tiempo real
- Métricas de rendimiento incluidas
- Reinicio automático en caso de fallos

## 🔧 Configuraciones Adicionales

### Configuración de Puerto
El archivo `main.py` ya está configurado para usar el puerto de la variable de entorno.

### Archivos de Despliegue Incluidos:
- ✅ `Procfile` - Comando de inicio
- ✅ `runtime.txt` - Versión de Python
- ✅ `build.sh` - Script de construcción
- ✅ `requirements.txt` - Dependencias

### Optimizaciones para Producción:
- Variables de entorno configuradas
- Manejo de errores mejorado
- Logs estructurados
- Cache optimizado

## 📱 Acceso a la Aplicación

Una vez desplegado, tu aplicación estará disponible en:
- **URL Principal**: https://alana-legal-sense.onrender.com
- **Estado de Despliegue**: Visible en el dashboard de Render

## 🛡️ Seguridad

- Variables de entorno protegidas
- HTTPS habilitado automáticamente
- Conexiones seguras a APIs externas

## 📊 Alternativas de Despliegue

Si prefieres otra plataforma:

### Railway.app:
```bash
# Instalar Railway CLI
npm install -g @railway/cli

# Desplegar
railway login
railway init
railway up
```

### Vercel (Serverless):
```bash
# Instalar Vercel CLI
npm install -g vercel

# Desplegar
vercel
```

## 🔄 Despliegue Continuo

Con GitHub conectado:
- ✅ **Auto-deploy** en cada push a `main`
- ✅ **Preview deployments** para pull requests
- ✅ **Rollback** automático en caso de errores

## 📝 Notas Importantes

1. **Primer despliegue**: Puede tomar 5-10 minutos
2. **Variables de entorno**: Deben configurarse antes del primer despliegue
3. **Archivos grandes**: Los modelos se descargan automáticamente
4. **Base de datos**: Supabase funciona perfectamente en producción

¡Tu asistente legal Alana estará disponible 24/7 una vez desplegado! 🎉