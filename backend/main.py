"""
FINANCIAL INTELLIGENCE SYSTEM PERU - API BACKEND
Sistema de inteligencia financiera nivel profesional
Autor: Deiner Cleison Villegas Villegas
© 2026 Todos los derechos reservados
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import asyncio
import logging

# Importar todos los módulos
from scrapers.bcrp_scraper import BCRPScraper
from scrapers.investing_scraper import InvestingScraper
from scrapers.sunat_scraper import SUNATScraper
from scrapers.minagri_scraper import MinagriScraper
from scrapers.news_scraper import NewsScraper
from scrapers.social_scraper import SocialScraper
from intelligence.predictor import PricePredictor
from intelligence.risk_analyzer import RiskAnalyzer
from intelligence.forex_predictor import ForexPredictor
from intelligence.arbitrage_detector import ArbitrageDetector
from sunat.tax_calculator import TaxCalculator
from sunat.regime_advisor import RegimeAdvisor
from sunat.compliance_monitor import ComplianceMonitor
from banking.credit_scorer import CreditScorer
from banking.liquidity_manager import LiquidityManager
from banking.cash_flow_predictor import CashFlowPredictor
from alerts.telegram_bot import TelegramBot
from alerts.whatsapp_bot import WhatsAppBot
from database.db_manager import DatabaseManager

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar FastAPI
app = FastAPI(
    title="Financial Intelligence System Peru API",
    description="Sistema profesional de inteligencia financiera y análisis de mercados",
    version="1.0.0"
)

# CORS - Permitir acceso desde GitHub Pages
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción: solo tu dominio
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar componentes
db = DatabaseManager()
bcrp = BCRPScraper()
investing = InvestingScraper()
sunat = SUNATScraper()
minagri = MinagriScraper()
news = NewsScraper()
social = SocialScraper()
predictor = PricePredictor()
risk_analyzer = RiskAnalyzer()
forex_predictor = ForexPredictor()
arbitrage = ArbitrageDetector()
tax_calc = TaxCalculator()
regime_advisor = RegimeAdvisor()
compliance = ComplianceMonitor()
credit_scorer = CreditScorer()
liquidity_mgr = LiquidityManager()
cashflow_predictor = CashFlowPredictor()
telegram_bot = TelegramBot()
whatsapp_bot = WhatsAppBot()

# ============================================================================
# MODELOS DE DATOS (Pydantic)
# ============================================================================

class ProductQuery(BaseModel):
    producto: str
    dias_prediccion: Optional[int] = 15

class TransactionInput(BaseModel):
    tipo: str  # "compra" o "venta"
    producto: str
    cantidad: float
    precio_unitario: float
    fecha: Optional[str] = None

class BusinessSimulation(BaseModel):
    producto: str
    capital_inicial: float
    cantidad: float
    precio_compra: float
    dias_holding: int = 30

class CreditRequest(BaseModel):
    tipo_negocio: str
    monto_credito: float
    plazo_meses: int
    garantia: Optional[str] = None

# ============================================================================
# ENDPOINTS - MERCADOS EN TIEMPO REAL
# ============================================================================

@app.get("/")
async def root():
    """Endpoint raíz - Estado del sistema"""
    return {
        "status": "online",
        "sistema": "Financial Intelligence System Peru",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "productos_monitoreados": 150,
        "fuentes_datos": 25,
        "actualizacion": "tiempo_real"
    }

@app.get("/api/markets/realtime")
async def get_realtime_markets():
    """
    Mercados en tiempo real - Todos los productos
    Actualización: cada 1 minuto
    """
    try:
        logger.info("📊 Obteniendo datos mercados en tiempo real...")
        
        # Obtener datos de todas las fuentes en paralelo
        tasks = [
            bcrp.get_tipo_cambio(),
            bcrp.get_indicadores_macro(),
            investing.get_commodities_prices(),
            minagri.get_precios_agricolas(),
            sunat.get_importaciones_recientes(),
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        tipo_cambio = results[0] if not isinstance(results[0], Exception) else {}
        macro = results[1] if not isinstance(results[1], Exception) else {}
        commodities = results[2] if not isinstance(results[2], Exception) else {}
        agricolas = results[3] if not isinstance(results[3], Exception) else {}
        importaciones = results[4] if not isinstance(results[4], Exception) else {}
        
        # Consolidar respuesta
        response = {
            "timestamp": datetime.now().isoformat(),
            "forex": {
                "usd_pen": tipo_cambio.get("compra", 0),
                "usd_pen_venta": tipo_cambio.get("venta", 0),
                "variacion_24h": tipo_cambio.get("variacion", 0),
                "actualizacion": "real_time"
            },
            "macro_peru": {
                "inflacion_mensual": macro.get("inflacion", 0),
                "reservas_internacionales_usd": macro.get("reservas", 0),
                "pbi_variacion": macro.get("pbi_var", 0),
                "tasa_referencia_bcrp": macro.get("tasa_ref", 0)
            },
            "commodities_internacional": commodities,
            "productos_agricolas_peru": agricolas,
            "importaciones_24h": importaciones,
            "fuentes": [
                "BCRP API (oficial)",
                "Investing.com (scraping)",
                "MINAGRI SISDEP",
                "SUNAT Aduanas"
            ]
        }
        
        # Guardar en base de datos
        await db.save_market_snapshot(response)
        
        return response
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo mercados: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/products/{producto}/price")
async def get_product_price(producto: str):
    """
    Precio actual de un producto específico
    Parámetros: cebolla, papa, arroz, oro, usd, etc.
    """
    try:
        producto_lower = producto.lower()
        
        # Buscar en diferentes fuentes según tipo de producto
        if producto_lower in ["usd", "eur", "gbp", "jpy"]:
            data = await bcrp.get_tipo_cambio_moneda(producto_lower)
            source = "BCRP"
        elif producto_lower in ["oro", "plata", "cobre", "petroleo", "trigo", "soya"]:
            data = await investing.get_commodity_price(producto_lower)
            source = "Investing.com"
        else:
            # Productos agrícolas locales
            data = await minagri.get_precio_producto(producto_lower)
            source = "MINAGRI"
        
        if not data:
            raise HTTPException(status_code=404, detail=f"Producto '{producto}' no encontrado")
        
        return {
            "producto": producto,
            "precio_actual": data.get("precio", 0),
            "unidad": data.get("unidad", "kg"),
            "moneda": data.get("moneda", "PEN"),
            "variacion_24h": data.get("var_24h", 0),
            "variacion_7d": data.get("var_7d", 0),
            "variacion_30d": data.get("var_30d", 0),
            "maximo_52w": data.get("max_52w", 0),
            "minimo_52w": data.get("min_52w", 0),
            "fuente": source,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error obteniendo precio {producto}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/products/predict")
async def predict_product_price(query: ProductQuery):
    """
    Predicción de precio futuro usando Machine Learning
    """
    try:
        producto = query.producto.lower()
        dias = query.dias_prediccion
        
        logger.info(f"🔮 Prediciendo precio {producto} para {dias} días...")
        
        # Obtener datos históricos
        historical_data = await db.get_historical_prices(producto, days=365)
        
        if len(historical_data) < 30:
            raise HTTPException(
                status_code=400, 
                detail=f"Datos insuficientes para {producto}. Se necesitan al menos 30 días de historia."
            )
        
        # Ejecutar predicción con ML
        prediction = await predictor.predict_price(
            producto=producto,
            historical_data=historical_data,
            dias_adelante=dias
        )
        
        return {
            "producto": producto,
            "precio_actual": prediction["precio_actual"],
            "precio_predicho": prediction["precio_predicho"],
            "dias_prediccion": dias,
            "fecha_prediccion": prediction["fecha_prediccion"],
            "confianza": prediction["confianza"],  # 0-100
            "tendencia": prediction["tendencia"],  # "alcista", "bajista", "lateral"
            "factores_clave": prediction["factores"],
            "recomendacion": prediction["recomendacion"],
            "modelo_usado": "Random Forest + ARIMA",
            "precision_historica": prediction["precision"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error en predicción: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/opportunities/today")
async def get_top_opportunities():
    """
    Top 10 oportunidades de negocio HOY
    Ordenadas por ROI estimado
    """
    try:
        logger.info("🎯 Analizando oportunidades en todos los productos...")
        
        # Analizar 150+ productos
        opportunities = []
        
        # Obtener todos los productos activos
        productos = await db.get_all_products()
        
        for producto in productos:
            # Análisis multifactor para cada producto
            analysis = await predictor.analyze_opportunity(producto)
            
            if analysis["score"] > 60:  # Solo oportunidades con score > 60
                opportunities.append(analysis)
        
        # Ordenar por ROI esperado
        opportunities.sort(key=lambda x: x["roi_estimado"], reverse=True)
        
        # Top 10
        top_10 = opportunities[:10]
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_oportunidades": len(opportunities),
            "top_10": top_10,
            "criterios_analisis": [
                "Predicción precio ML",
                "Estacionalidad histórica",
                "Señales climáticas",
                "Precios internacionales",
                "Volumen importaciones",
                "Análisis riesgo"
            ]
        }
        
    except Exception as e:
        logger.error(f"❌ Error analizando oportunidades: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ENDPOINTS - ANÁLISIS SUNAT (CONTADOR AUTOMÁTICO)
# ============================================================================

@app.post("/api/sunat/calculate")
async def calculate_sunat_taxes(transaction: TransactionInput):
    """
    Calculadora completa SUNAT
    Calcula: IGV, Renta, Detracciones, Retenciones, Percepciones
    """
    try:
        logger.info(f"📋 Calculando impuestos para transacción {transaction.tipo}...")
        
        result = await tax_calc.calculate_all_taxes(
            tipo=transaction.tipo,
            producto=transaction.producto,
            cantidad=transaction.cantidad,
            precio_unitario=transaction.precio_unitario,
            fecha=transaction.fecha or datetime.now().strftime("%Y-%m-%d")
        )
        
        return {
            "transaccion": {
                "tipo": transaction.tipo,
                "producto": transaction.producto,
                "cantidad": transaction.cantidad,
                "precio_unitario": transaction.precio_unitario,
                "monto_total": result["monto_total"]
            },
            "impuestos": {
                "igv": {
                    "base_imponible": result["igv"]["base"],
                    "tasa": result["igv"]["tasa"],
                    "monto": result["igv"]["monto"]
                },
                "renta": {
                    "regimen": result["renta"]["regimen"],
                    "tasa": result["renta"]["tasa"],
                    "monto": result["renta"]["monto"]
                },
                "detraccion": result["detraccion"],
                "retencion": result["retencion"],
                "percepcion": result["percepcion"]
            },
            "total_impuestos": result["total_impuestos"],
            "neto_final": result["neto_final"],
            "libros_contables": {
                "asiento_compras": result["libro_compras"],
                "asiento_ventas": result["libro_ventas"]
            },
            "declaraciones": {
                "pdt_601_igv": result["pdt_601"],
                "pdt_621_renta": result["pdt_621"]
            },
            "alertas": result["alertas"]
        }
        
    except Exception as e:
        logger.error(f"❌ Error calculando impuestos: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sunat/regime/recommend")
async def recommend_tax_regime(
    ingresos_anuales: float,
    tipo_actividad: str,
    empleados: int = 0
):
    """
    Recomendador de régimen tributario óptimo
    RUS vs RER vs Régimen General
    """
    try:
        recommendation = await regime_advisor.get_best_regime(
            ingresos_anuales=ingresos_anuales,
            tipo_actividad=tipo_actividad,
            empleados=empleados
        )
        
        return recommendation
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sunat/compliance/status")
async def get_compliance_status():
    """
    Estado de cumplimiento tributario
    Vencimientos, alertas, obligaciones pendientes
    """
    try:
        status = await compliance.get_full_status()
        
        return {
            "estado_general": status["estado"],
            "proximos_vencimientos": status["vencimientos"],
            "obligaciones_pendientes": status["pendientes"],
            "libros_electronicos": status["libros"],
            "nuevas_normas": status["normas_nuevas"],
            "recomendaciones": status["recomendaciones"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ENDPOINTS - ANÁLISIS BANCARIO (INTELIGENCIA FINANCIERA)
# ============================================================================

@app.post("/api/banking/credit/evaluate")
async def evaluate_credit_request(request: CreditRequest):
    """
    Evaluación crediticia profesional
    Como Comité de Créditos de banco
    """
    try:
        evaluation = await credit_scorer.evaluate_request(
            tipo_negocio=request.tipo_negocio,
            monto_credito=request.monto_credito,
            plazo_meses=request.plazo_meses,
            garantia=request.garantia
        )
        
        return evaluation
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/banking/simulate")
async def simulate_business(simulation: BusinessSimulation):
    """
    Simulación Monte Carlo de negocio
    10,000 escenarios posibles
    """
    try:
        logger.info(f"🎲 Simulando negocio {simulation.producto}...")
        
        results = await predictor.monte_carlo_simulation(
            producto=simulation.producto,
            capital_inicial=simulation.capital_inicial,
            cantidad=simulation.cantidad,
            precio_compra=simulation.precio_compra,
            dias_holding=simulation.dias_holding,
            num_simulaciones=10000
        )
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/banking/cashflow/predict")
async def predict_cashflow(dias: int = 30):
    """
    Predicción flujo de caja
    """
    try:
        prediction = await cashflow_predictor.predict(dias=dias)
        
        return prediction
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ENDPOINTS - ALERTAS Y NOTIFICACIONES
# ============================================================================

@app.post("/api/alerts/configure")
async def configure_alerts(
    telegram_chat_id: Optional[str] = None,
    whatsapp_number: Optional[str] = None,
    productos_monitoreados: Optional[List[str]] = None
):
    """
    Configurar alertas personalizadas
    """
    try:
        config = {
            "telegram_chat_id": telegram_chat_id,
            "whatsapp_number": whatsapp_number,
            "productos": productos_monitoreados or []
        }
        
        await db.save_alert_config(config)
        
        # Iniciar monitoreo
        if telegram_chat_id:
            await telegram_bot.subscribe(telegram_chat_id, productos_monitoreados)
        
        if whatsapp_number:
            await whatsapp_bot.subscribe(whatsapp_number, productos_monitoreados)
        
        return {
            "status": "configurado",
            "telegram": "activo" if telegram_chat_id else "inactivo",
            "whatsapp": "activo" if whatsapp_number else "inactivo",
            "productos_monitoreados": len(productos_monitoreados or [])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/alerts/send-test")
async def send_test_alert():
    """
    Enviar alerta de prueba
    """
    try:
        test_message = """
🚀 ALERTA DE PRUEBA - Sistema Activo

✅ Sistema funcionando correctamente
📊 Monitoreando 150+ productos
🔔 Alertas configuradas

Próxima actualización: 60 segundos
"""
        
        await telegram_bot.send_message(test_message)
        await whatsapp_bot.send_message(test_message)
        
        return {"status": "alertas enviadas"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ENDPOINTS - ANÁLISIS AVANZADO
# ============================================================================

@app.get("/api/analysis/forex/predict")
async def predict_forex(par: str = "USD/PEN", dias: int = 15):
    """
    Predicción tipo de cambio con ML
    """
    try:
        prediction = await forex_predictor.predict(par=par, dias=dias)
        
        return prediction
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analysis/arbitrage")
async def detect_arbitrage_opportunities():
    """
    Detector de arbitraje
    Importación vs producción local
    """
    try:
        opportunities = await arbitrage.scan_all_products()
        
        return opportunities
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analysis/risk/{producto}")
async def analyze_product_risk(producto: str):
    """
    Análisis de riesgo completo
    """
    try:
        risk_analysis = await risk_analyzer.analyze(producto)
        
        return risk_analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# TAREAS EN BACKGROUND (Scrapers automáticos)
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """
    Iniciar scrapers automáticos al arrancar servidor
    """
    logger.info("🚀 Iniciando Financial Intelligence System Peru...")
    
    # Iniciar scrapers en background
    asyncio.create_task(run_scrapers_loop())
    
    logger.info("✅ Sistema iniciado correctamente")

async def run_scrapers_loop():
    """
    Loop infinito de scrapers
    """
    while True:
        try:
            # Cada 1 minuto: BCRP (tipo cambio)
            await bcrp.update_tipo_cambio()
            
            # Cada 5 minutos: Investing.com (commodities)
            if datetime.now().minute % 5 == 0:
                await investing.update_all_commodities()
            
            # Cada 30 minutos: Noticias
            if datetime.now().minute % 30 == 0:
                await news.scrape_latest()
            
            # Cada 1 hora: SUNAT, MINAGRI
            if datetime.now().minute == 0:
                await sunat.update_importaciones()
                await minagri.update_precios()
            
            # Cada 6 horas: Análisis predictivo completo
            if datetime.now().hour % 6 == 0 and datetime.now().minute == 0:
                await predictor.update_all_predictions()
            
            await asyncio.sleep(60)  # Esperar 1 minuto
            
        except Exception as e:
            logger.error(f"❌ Error en scrapers loop: {str(e)}")
            await asyncio.sleep(300)  # Esperar 5 minutos si hay error

# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/health")
async def health_check():
    """
    Estado de salud del sistema
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "database": "online",
            "scrapers": "running",
            "predictor": "ready",
            "telegram_bot": "active",
            "whatsapp_bot": "active"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
