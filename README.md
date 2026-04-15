# 🏦 FINANCIAL INTELLIGENCE SYSTEM PERU

Sistema profesional de inteligencia financiera y análisis de mercados para Perú.

## 🎯 CARACTERÍSTICAS

### ✅ Monitoreo en Tiempo Real
- **150+ productos** monitoreados 24/7
- **Tipo de cambio** USD/PEN actualizado cada minuto
- **Commodities internacionales** (oro, petróleo, granos)
- **Precios agrícolas** peruanos (cebolla, papa, arroz, etc.)

### 🤖 Inteligencia Artificial
- **Predicciones ML** con Random Forest + ARIMA
- **Simulación Monte Carlo** (10,000 escenarios)
- **Análisis de riesgo** multifactorial
- **Detector de arbitraje** (importación vs local)

### 📊 Análisis SUNAT
- **Contador automático** (IGV, Renta, Detracciones)
- **Recomendador de régimen** tributario
- **Cronograma de vencimientos**
- **Monitor de cumplimiento**

### 🔔 Alertas Inteligentes
- **Telegram Bot** (alertas instantáneas)
- **WhatsApp Bot** (notificaciones críticas)
- Alertas de:
  - Cambios de precio >10%
  - Oportunidades de negocio
  - Vencimientos SUNAT
  - Noticias financieras relevantes

## 🚀 TECNOLOGÍAS

**Backend:**
- Python 3.11
- FastAPI (API REST)
- aiohttp (scraping asíncrono)
- BeautifulSoup4 (parsing HTML)

**Frontend:**
- HTML5 + JavaScript vanilla
- Chart.js (gráficos)
- Diseño responsive

**Deployment:**
- Render.com (backend - GRATIS)
- GitHub Pages (frontend - GRATIS)

## 📁 ESTRUCTURA DEL PROYECTO

```
financial-system/
├── backend/
│   ├── main.py                 # API FastAPI principal
│   ├── requirements.txt        # Dependencias Python
│   ├── render.yaml            # Config Render.com
│   │
│   ├── scrapers/              # Scrapers de datos
│   │   ├── bcrp_scraper.py    # Tipo cambio BCRP
│   │   ├── investing_scraper.py # Commodities
│   │   ├── minagri_scraper.py  # Precios agrícolas
│   │   ├── sunat_scraper.py    # Importaciones SUNAT
│   │   └── news_scraper.py     # Noticias financieras
│   │
│   ├── intelligence/          # Machine Learning
│   │   ├── predictor.py       # Predicción precios
│   │   ├── risk_analyzer.py   # Análisis riesgo
│   │   ├── forex_predictor.py # Predicción TC
│   │   └── arbitrage_detector.py # Arbitraje
│   │
│   ├── sunat/                 # Compliance tributario
│   │   └── tax_calculator.py  # Calculadora impuestos
│   │
│   ├── alerts/                # Sistema de alertas
│   │   ├── telegram_bot.py    # Bot Telegram
│   │   └── whatsapp_bot.py    # Bot WhatsApp
│   │
│   └── database/              # Base de datos
│       └── db_manager.py      # Gestor DB
│
└── frontend/
    └── index.html             # Dashboard web

```

## 🔧 INSTALACIÓN

### Opción A: Desde Celular (Android)

1. **Instalar Termux:**
   ```
   Descargar desde Play Store o F-Droid
   ```

2. **Configurar Git:**
   ```bash
   pkg install git
   git config --global user.name "Tu Nombre"
   git config --global user.email "tu@email.com"
   ```

3. **Clonar repositorio:**
   ```bash
   git clone https://github.com/TU_USUARIO/financial-system.git
   cd financial-system/backend
   ```

4. **Deploy en Render.com:**
   - Ir a https://render.com
   - Sign Up con GitHub
   - New Web Service → Conectar repo
   - Deploy automático

### Opción B: Desde PC

1. **Clonar:**
   ```bash
   git clone https://github.com/TU_USUARIO/financial-system.git
   cd financial-system
   ```

2. **Backend local:**
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn main:app --reload
   ```

3. **Frontend local:**
   ```bash
   cd frontend
   python -m http.server 8080
   ```

## 📊 ENDPOINTS API

### Mercados
```
GET  /api/markets/realtime           # Mercados en tiempo real
GET  /api/products/{producto}/price  # Precio producto
POST /api/products/predict           # Predicción ML
GET  /api/opportunities/today        # Top oportunidades
```

### SUNAT
```
POST /api/sunat/calculate            # Calcular impuestos
GET  /api/sunat/regime/recommend     # Recomendar régimen
GET  /api/sunat/compliance/status    # Estado cumplimiento
```

### Análisis
```
POST /api/banking/simulate           # Simulación Monte Carlo
GET  /api/analysis/forex/predict     # Predicción TC
GET  /api/analysis/arbitrage         # Detectar arbitraje
GET  /api/analysis/risk/{producto}   # Análisis riesgo
```

## 🔑 CONFIGURACIÓN

### Variables de Entorno (.env)

```bash
# Telegram Bot
TELEGRAM_BOT_TOKEN=tu_token_aqui
TELEGRAM_CHAT_ID=tu_chat_id

# WhatsApp (Twilio)
TWILIO_ACCOUNT_SID=tu_sid
TWILIO_AUTH_TOKEN=tu_token
TWILIO_WHATSAPP_NUMBER=+14155238886

# Base de datos (opcional)
DATABASE_URL=postgresql://...
```

## 📱 CONFIGURAR ALERTAS

### Telegram

1. Crear bot con @BotFather
2. Obtener token
3. Configurar en `alerts/telegram_bot.py`

### WhatsApp

1. Cuenta Twilio (gratis)
2. Activar Sandbox WhatsApp
3. Configurar en `alerts/whatsapp_bot.py`

## 🧪 TESTING

```bash
# Test scrapers
python -m scrapers.bcrp_scraper
python -m scrapers.investing_scraper

# Test predictor
python -m intelligence.predictor

# Test SUNAT
python -m sunat.tax_calculator
```

## 📈 ROADMAP

- [x] Backend API completo
- [x] Scrapers tiempo real
- [x] Predicciones ML
- [x] Calculadora SUNAT
- [x] Alertas Telegram/WhatsApp
- [x] Dashboard web
- [ ] App móvil (React Native)
- [ ] Base de datos PostgreSQL
- [ ] Sistema de usuarios
- [ ] Backtesting predicciones
- [ ] API pública

## 📄 LICENCIA

© 2026 Financial Intelligence System Peru  
Todos los derechos reservados.

**Desarrollado por:** Deiner Cleison Villegas Villegas  
**Consultor Financiero-Tributario**

## ⚠️ DISCLAIMER

Este sistema utiliza modelos predictivos basados en datos públicos.  
**NO constituye asesoría financiera.**  
El usuario asume toda responsabilidad de sus decisiones de inversión.

Cumplimiento SUNAT: Información actualizada al 09/04/2026 - Verificar vigencia normativa.

## 📞 SOPORTE

- Email: contacto@ejemplo.com
- GitHub Issues: https://github.com/TU_USUARIO/financial-system/issues
- Telegram: @tu_usuario

---

**⭐ Si te sirvió este proyecto, dale una estrella en GitHub!**
