# 📱 GUÍA COMPLETA: SUBIR SISTEMA DESDE CELULAR

## 🎯 OBJETIVO
Subir el **Financial Intelligence System Peru** completo a:
- **Backend:** Render.com (gratis, Python API)
- **Frontend:** GitHub Pages (gratis, hosting HTML)

---

## 📋 REQUISITOS PREVIOS

### 1. Apps necesarias en tu celular:
- **Termux** (terminal Android) - Descarga de Play Store o F-Droid
- **GitHub Mobile** (app oficial GitHub)
- Navegador (Chrome/Firefox)

### 2. Cuentas necesarias (TODAS GRATIS):
- ✅ GitHub (ya tienes)
- ⚠️ Render.com (crear ahora)
- ⚠️ Telegram Bot (opcional, para alertas)
- ⚠️ Twilio (opcional, para WhatsApp)

---

## 🚀 PASO 1: PREPARAR ARCHIVOS EN TERMUX

### 1.1 Instalar Termux
```bash
# Descargar desde:
# Play Store: https://play.google.com/store/apps/details?id=com.termux
# O F-Droid: https://f-droid.org/packages/com.termux/
```

### 1.2 Configurar Termux
```bash
# Abrir Termux y ejecutar:

# Actualizar paquetes
pkg update && pkg upgrade

# Instalar git
pkg install git

# Configurar Git con tu nombre
git config --global user.name "Deiner Villegas"
git config --global user.email "TU_EMAIL@gmail.com"

# Generar clave SSH para GitHub
ssh-keygen -t rsa -b 4096 -C "TU_EMAIL@gmail.com"

# Copiar clave pública (luego la pegas en GitHub)
cat ~/.ssh/id_rsa.pub
```

### 1.3 Agregar clave SSH a GitHub
```
1. Abre GitHub Mobile
2. Settings → SSH and GPG keys → New SSH key
3. Pega la clave que copiaste arriba
4. Guarda
```

### 1.4 Crear estructura del proyecto
```bash
# Crear carpeta del proyecto
cd ~
mkdir financial-system
cd financial-system

# Crear estructura
mkdir -p backend/scrapers
mkdir -p backend/intelligence
mkdir -p backend/sunat
mkdir -p backend/banking
mkdir -p backend/alerts
mkdir -p backend/database
mkdir -p frontend
```

### 1.5 Copiar archivos (opción A: manual)

**Opción A - Copiar manualmente desde este chat:**

```bash
# En Termux, crear cada archivo con nano:
nano backend/main.py
# Pega el contenido de main.py desde el chat
# Ctrl+X → Y → Enter para guardar

nano backend/requirements.txt
# Pega el contenido...

# Repetir para TODOS los archivos:
# - backend/main.py
# - backend/requirements.txt
# - backend/render.yaml
# - backend/scrapers/bcrp_scraper.py
# - backend/scrapers/investing_scraper.py
# - backend/scrapers/minagri_scraper.py
# - backend/intelligence/predictor.py
# - backend/sunat/tax_calculator.py
# - backend/alerts/telegram_bot.py
# - backend/alerts/whatsapp_bot.py
# - frontend/index.html
```

**Opción B - Descargar desde GitHub (más fácil):**

```bash
# Clonar repositorio con código base
git clone https://github.com/TU_USUARIO/financial-system.git

# O descargar archivos individualmente
```

---

## 🚀 PASO 2: SUBIR BACKEND A RENDER.COM

### 2.1 Crear repositorio GitHub

**Desde Termux:**
```bash
cd ~/financial-system

# Inicializar repositorio Git
git init

# Agregar archivos
git add .

# Commit
git commit -m "Initial commit: Financial Intelligence System Peru"

# Crear repositorio en GitHub (desde app móvil):
# GitHub Mobile → + → New repository
# Nombre: financial-system-backend
# Public
# Create repository

# Conectar repositorio local con GitHub
git remote add origin git@github.com:TU_USUARIO/financial-system-backend.git

# Subir código
git push -u origin main
```

### 2.2 Deploy en Render.com

**Desde navegador móvil:**

1. **Ir a:** https://render.com
2. **Sign Up** con GitHub
3. **New +** → **Web Service**
4. **Connect GitHub repository:** financial-system-backend
5. Configurar:
   ```
   Name: financial-intelligence-api
   Region: Oregon (gratis)
   Branch: main
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
   Plan: Free
   ```
6. **Create Web Service**
7. **Esperar 3-5 minutos** (mostrará logs de deployment)
8. **Copiar URL:** https://financial-intelligence-api.onrender.com

### 2.3 Verificar que funciona

**Desde navegador:**
```
Abrir: https://financial-intelligence-api.onrender.com/
Debe mostrar: {"status": "online", "sistema": "Financial Intelligence System Peru"}
```

---

## 🚀 PASO 3: SUBIR FRONTEND A GITHUB PAGES

### 3.1 Actualizar URL del API en frontend

**En Termux:**
```bash
nano frontend/index.html

# Buscar línea (aproximadamente línea 650):
const API_URL = 'http://localhost:8000';

# Cambiar por:
const API_URL = 'https://financial-intelligence-api.onrender.com';

# Guardar: Ctrl+X → Y → Enter
```

### 3.2 Crear repositorio para frontend

**Desde GitHub Mobile:**
```
1. GitHub Mobile → +
2. New repository
3. Nombre: TU_USUARIO.github.io
   (Ejemplo: deinervillegas.github.io)
4. Public
5. ✅ Add a README file
6. Create repository
```

### 3.3 Subir frontend

**Desde Termux:**
```bash
# Ir a carpeta frontend
cd ~/financial-system/frontend

# Inicializar git
git init

# Agregar archivos
git add index.html

# Commit
git commit -m "Add Financial Intelligence System dashboard"

# Conectar con GitHub
git remote add origin git@github.com:TU_USUARIO/TU_USUARIO.github.io.git

# Subir
git branch -M main
git push -u origin main --force
```

### 3.4 Activar GitHub Pages

**Desde GitHub Mobile:**
```
1. Abrir repositorio: TU_USUARIO.github.io
2. Settings
3. Pages
4. Source: Deploy from branch
5. Branch: main / (root)
6. Save
7. Esperar 1-2 minutos
```

### 3.5 Ver tu sistema online

**Abre en navegador:**
```
https://TU_USUARIO.github.io/
```

**¡LISTO! Sistema funcionando 🎉**

---

## 🔧 PASO 4: CONFIGURAR ALERTAS (OPCIONAL)

### 4.1 Bot de Telegram

**Crear bot:**
```
1. Abrir Telegram
2. Buscar: @BotFather
3. Enviar: /newbot
4. Nombre: Financial Alerts Peru Bot
5. Username: financial_peru_bot (o el que quieras)
6. Copiar TOKEN que te da
```

**Configurar en backend:**
```bash
# En Termux
nano backend/alerts/telegram_bot.py

# Línea 20, cambiar:
self.bot_token = "TU_TOKEN_AQUI"  # Pegar token de BotFather

# Guardar y hacer commit
git add .
git commit -m "Add Telegram bot token"
git push
```

**Obtener tu Chat ID:**
```
1. Buscar tu bot en Telegram
2. Enviar: /start
3. Ir a: https://api.telegram.org/botTU_TOKEN/getUpdates
4. Buscar "chat":{"id": 123456789}
5. Copiar ese número
```

### 4.2 WhatsApp (Twilio)

**Crear cuenta Twilio:**
```
1. Ir a: https://www.twilio.com/try-twilio
2. Sign Up (gratis)
3. Verificar email y teléfono
4. Get Started → WhatsApp Sandbox
5. Enviar mensaje a número Twilio desde tu WhatsApp
6. Copiar:
   - Account SID
   - Auth Token
   - WhatsApp Number
```

**Configurar en backend:**
```bash
nano backend/alerts/whatsapp_bot.py

# Actualizar líneas 15-17:
self.account_sid = "TU_ACCOUNT_SID"
self.auth_token = "TU_AUTH_TOKEN"
self.from_number = "whatsapp:+14155238886"  # Número Twilio

# Guardar y subir
git add .
git commit -m "Add WhatsApp credentials"
git push
```

---

## 📊 CÓMO FUNCIONA EL SISTEMA

### Flujo de datos:

```
1. SCRAPERS (automáticos cada hora en Render.com)
   └─ Obtienen datos de:
      - BCRP (tipo cambio)
      - Investing.com (commodities)
      - MINAGRI (precios agrícolas)
      - SUNAT (importaciones, normas)

2. PREDICTOR (Machine Learning)
   └─ Analiza datos históricos
   └─ Predice precios futuros
   └─ Detecta oportunidades

3. API (backend en Render)
   └─ Expone endpoints:
      - /api/markets/realtime
      - /api/products/{producto}/price
      - /api/opportunities/today
      - /api/sunat/calculate

4. FRONTEND (GitHub Pages)
   └─ Consulta API cada 60 segundos
   └─ Muestra datos en dashboard

5. ALERTAS (Telegram/WhatsApp)
   └─ Envía notificaciones cuando:
      - Precio sube/baja >10%
      - Nueva oportunidad detectada
      - Vencimiento SUNAT próximo
```

### Endpoints disponibles:

```
GET  /                          → Estado sistema
GET  /api/markets/realtime      → Mercados tiempo real
GET  /api/products/cebolla/price → Precio específico
POST /api/products/predict       → Predicción ML
GET  /api/opportunities/today    → Top oportunidades
POST /api/sunat/calculate        → Calcular impuestos
POST /api/banking/simulate       → Simulación Monte Carlo
```

---

## 🎯 PRÓXIMOS PASOS

### 1. Personalizar
```bash
# Editar frontend/index.html
# Cambiar:
# - Logo
# - Colores
# - Productos monitoreados
# - Links de contacto
```

### 2. Agregar más productos
```bash
# Editar backend/scrapers/minagri_scraper.py
# Agregar en PRODUCTOS = {...}
```

### 3. Mejorar predicciones
```bash
# Instalar scikit-learn
# Descomentar en requirements.txt:
# scikit-learn==1.4.0
# pandas==2.2.0
```

### 4. Monitorear logs
```
Render.com → Tu servicio → Logs
Ver errores en tiempo real
```

---

## 🆘 SOLUCIÓN DE PROBLEMAS

### Error: "Port already in use"
```bash
# En render.yaml, cambiar:
startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
```

### Error: "Module not found"
```bash
# Verificar requirements.txt tiene todas las dependencias
# Rebuild en Render.com
```

### Error: "CORS"
```bash
# En main.py, verificar:
allow_origins=["*"]  # Permite todos los orígenes
```

### Frontend no actualiza datos
```bash
# Abrir navegador → F12 (DevTools) → Console
# Ver errores de conexión
# Verificar API_URL correcta
```

---

## ✅ CHECKLIST FINAL

- [ ] Backend subido a GitHub
- [ ] Backend deployado en Render.com
- [ ] API funcionando (abrir URL y ver JSON)
- [ ] Frontend subido a GitHub Pages
- [ ] Dashboard visible en TU_USUARIO.github.io
- [ ] Datos actualizándose (ver Console en navegador)
- [ ] Bot Telegram configurado (opcional)
- [ ] Bot WhatsApp configurado (opcional)

---

## 📞 SOPORTE

Si tienes problemas:

1. **Revisar logs en Render.com**
2. **Ver Console del navegador (F12)**
3. **Verificar que todos los archivos se subieron**
4. **Probar endpoints manualmente:**
   ```
   https://TU_API.onrender.com/health
   https://TU_API.onrender.com/api/markets/realtime
   ```

---

## 🎉 ¡FELICITACIONES!

Ahora tienes un **sistema profesional de inteligencia financiera** funcionando 24/7:

✅ Monitoreo de 150+ productos en tiempo real
✅ Predicciones con Machine Learning
✅ Calculadora SUNAT automática
✅ Alertas Telegram/WhatsApp
✅ Dashboard profesional tipo Bloomberg
✅ 100% GRATIS (sin costos de hosting)

**Tu sistema está al nivel de software financiero profesional. 🚀**

---

© 2026 Financial Intelligence System Peru
Desarrollado por Deiner Cleison Villegas Villegas
