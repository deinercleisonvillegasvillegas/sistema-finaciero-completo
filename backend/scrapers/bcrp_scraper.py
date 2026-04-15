"""
BCRP SCRAPER - Banco Central de Reserva del Perú
Obtiene datos oficiales en tiempo real:
- Tipo de cambio USD/PEN
- Indicadores macroeconómicos
- Series históricas
"""

import aiohttp
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class BCRPScraper:
    """
    Scraper oficial API BCRP
    100% legal, sin límites, datos oficiales
    """
    
    BASE_URL = "https://estadisticas.bcrp.gob.pe/estadisticas/series/api"
    
    # Series importantes BCRP
    SERIES = {
        "tipo_cambio_compra": "PD04638PD",
        "tipo_cambio_venta": "PD04639PD",
        "tipo_cambio_promedio": "PD04637PD",
        "inflacion_mensual": "PN01270PM",
        "inflacion_acumulada": "PN01270AM",
        "reservas_internacionales": "PN01288PM",
        "pbi_real": "PN01773AM",
        "tasa_referencia": "PN07810PM",
        "liquidez_total": "PN01289MM",
        "credito_sector_privado": "PN01291MM",
        "depositos_sector_privado": "PN01298MM"
    }
    
    def __init__(self):
        self.session = None
        self.cache = {}
        self.cache_expiry = {}
    
    async def _get_session(self):
        """Crear sesión HTTP reutilizable"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def _fetch_serie(self, codigo_serie: str, periodo: str = "today") -> Dict:
        """
        Obtener datos de una serie BCRP
        
        Args:
            codigo_serie: Código de serie BCRP
            periodo: 'today', 'month', 'year', o fechas específicas
        """
        try:
            # Verificar caché
            cache_key = f"{codigo_serie}_{periodo}"
            if cache_key in self.cache:
                if datetime.now() < self.cache_expiry.get(cache_key, datetime.min):
                    logger.debug(f"📦 Usando caché para {codigo_serie}")
                    return self.cache[cache_key]
            
            # Construir URL
            if periodo == "today":
                # Solo dato más reciente
                url = f"{self.BASE_URL}/{codigo_serie}/json"
            else:
                # Rango de fechas
                url = f"{self.BASE_URL}/{codigo_serie}/json/{periodo}"
            
            session = await self._get_session()
            
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Guardar en caché (válido 5 minutos)
                    self.cache[cache_key] = data
                    self.cache_expiry[cache_key] = datetime.now() + timedelta(minutes=5)
                    
                    logger.info(f"✅ Serie {codigo_serie} obtenida correctamente")
                    return data
                else:
                    logger.error(f"❌ Error BCRP API: {response.status}")
                    return {}
                    
        except Exception as e:
            logger.error(f"❌ Error obteniendo serie BCRP {codigo_serie}: {str(e)}")
            return {}
    
    async def get_tipo_cambio(self) -> Dict:
        """
        Tipo de cambio USD/PEN actual (oficial BCRP)
        Actualización: cada 5 minutos
        """
        try:
            # Obtener compra y venta en paralelo
            compra_data = await self._fetch_serie(self.SERIES["tipo_cambio_compra"])
            venta_data = await self._fetch_serie(self.SERIES["tipo_cambio_venta"])
            promedio_data = await self._fetch_serie(self.SERIES["tipo_cambio_promedio"])
            
            if not compra_data or not venta_data:
                return {}
            
            # Extraer valores más recientes
            compra_serie = compra_data.get("periods", [])
            venta_serie = venta_data.get("periods", [])
            promedio_serie = promedio_data.get("periods", [])
            
            if not compra_serie or not venta_serie:
                return {}
            
            # Último valor
            ultimo_compra = float(compra_serie[-1]["values"][0])
            ultimo_venta = float(venta_serie[-1]["values"][0])
            ultimo_promedio = float(promedio_serie[-1]["values"][0]) if promedio_serie else (ultimo_compra + ultimo_venta) / 2
            fecha = compra_serie[-1]["name"]
            
            # Calcular variaciones
            variacion_24h = 0
            if len(compra_serie) > 1:
                anterior = float(compra_serie[-2]["values"][0])
                variacion_24h = ((ultimo_compra - anterior) / anterior) * 100
            
            variacion_7d = 0
            if len(compra_serie) >= 7:
                hace_7d = float(compra_serie[-7]["values"][0])
                variacion_7d = ((ultimo_compra - hace_7d) / hace_7d) * 100
            
            return {
                "compra": ultimo_compra,
                "venta": ultimo_venta,
                "promedio": ultimo_promedio,
                "fecha": fecha,
                "variacion_24h": round(variacion_24h, 2),
                "variacion_7d": round(variacion_7d, 2),
                "fuente": "BCRP Oficial",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo tipo cambio: {str(e)}")
            return {}
    
    async def get_indicadores_macro(self) -> Dict:
        """
        Indicadores macroeconómicos principales
        """
        try:
            logger.info("📊 Obteniendo indicadores macro BCRP...")
            
            # Obtener todas las series en paralelo
            tasks = [
                self._fetch_serie(self.SERIES["inflacion_mensual"]),
                self._fetch_serie(self.SERIES["reservas_internacionales"]),
                self._fetch_serie(self.SERIES["tasa_referencia"]),
                self._fetch_serie(self.SERIES["pbi_real"]),
                self._fetch_serie(self.SERIES["liquidez_total"]),
                self._fetch_serie(self.SERIES["credito_sector_privado"])
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Procesar resultados
            inflacion_data = results[0] if not isinstance(results[0], Exception) else {}
            reservas_data = results[1] if not isinstance(results[1], Exception) else {}
            tasa_data = results[2] if not isinstance(results[2], Exception) else {}
            pbi_data = results[3] if not isinstance(results[3], Exception) else {}
            liquidez_data = results[4] if not isinstance(results[4], Exception) else {}
            credito_data = results[5] if not isinstance(results[5], Exception) else {}
            
            # Extraer últimos valores
            macro = {}
            
            if inflacion_data.get("periods"):
                ultimo = inflacion_data["periods"][-1]
                macro["inflacion_mensual"] = float(ultimo["values"][0])
                macro["inflacion_fecha"] = ultimo["name"]
            
            if reservas_data.get("periods"):
                ultimo = reservas_data["periods"][-1]
                macro["reservas_usd_millones"] = float(ultimo["values"][0])
            
            if tasa_data.get("periods"):
                ultimo = tasa_data["periods"][-1]
                macro["tasa_referencia_bcrp"] = float(ultimo["values"][0])
            
            if pbi_data.get("periods"):
                ultimo = pbi_data["periods"][-1]
                anterior = pbi_data["periods"][-2] if len(pbi_data["periods"]) > 1 else None
                macro["pbi_var_anual"] = float(ultimo["values"][0])
                if anterior:
                    macro["pbi_var_trimestral"] = float(ultimo["values"][0]) - float(anterior["values"][0])
            
            if liquidez_data.get("periods"):
                ultimo = liquidez_data["periods"][-1]
                macro["liquidez_total_millones"] = float(ultimo["values"][0])
            
            if credito_data.get("periods"):
                ultimo = credito_data["periods"][-1]
                macro["credito_privado_millones"] = float(ultimo["values"][0])
            
            macro["timestamp"] = datetime.now().isoformat()
            macro["fuente"] = "BCRP API Oficial"
            
            logger.info("✅ Indicadores macro obtenidos")
            return macro
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo indicadores macro: {str(e)}")
            return {}
    
    async def get_tipo_cambio_moneda(self, moneda: str) -> Dict:
        """
        Tipo de cambio para otras monedas vs PEN
        
        Args:
            moneda: 'eur', 'gbp', 'jpy', 'cny', etc.
        """
        # BCRP solo tiene USD/PEN oficial
        # Para otras monedas, calcular cruce con USD
        
        if moneda.lower() == "usd":
            return await self.get_tipo_cambio()
        
        # TODO: Implementar cruces con otras monedas
        # Requeriría API adicional o cálculo cruzado
        
        return {}
    
    async def get_serie_historica(
        self, 
        codigo_serie: str, 
        fecha_inicio: str, 
        fecha_fin: str
    ) -> List[Dict]:
        """
        Obtener serie histórica entre dos fechas
        
        Args:
            codigo_serie: Código BCRP
            fecha_inicio: 'YYYY-MM-DD'
            fecha_fin: 'YYYY-MM-DD'
        
        Returns:
            Lista de puntos de datos
        """
        try:
            periodo = f"{fecha_inicio}/{fecha_fin}"
            data = await self._fetch_serie(codigo_serie, periodo)
            
            if not data.get("periods"):
                return []
            
            # Convertir a formato uniforme
            series = []
            for period in data["periods"]:
                series.append({
                    "fecha": period["name"],
                    "valor": float(period["values"][0])
                })
            
            return series
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo serie histórica: {str(e)}")
            return []
    
    async def update_tipo_cambio(self):
        """
        Actualizar tipo de cambio en base de datos
        (Llamado por scraper loop cada 1 minuto)
        """
        try:
            tc = await self.get_tipo_cambio()
            
            if tc:
                # Guardar en DB
                from database.db_manager import DatabaseManager
                db = DatabaseManager()
                await db.save_forex_data("USD/PEN", tc)
                
                logger.info(f"💹 Tipo cambio actualizado: {tc['compra']}")
                
        except Exception as e:
            logger.error(f"❌ Error actualizando tipo cambio: {str(e)}")
    
    async def close(self):
        """Cerrar sesión HTTP"""
        if self.session and not self.session.closed:
            await self.session.close()

# Test del módulo
if __name__ == "__main__":
    async def test():
        scraper = BCRPScraper()
        
        print("🧪 Testing BCRP Scraper...\n")
        
        # Test 1: Tipo de cambio
        print("1️⃣ Tipo de cambio USD/PEN:")
        tc = await scraper.get_tipo_cambio()
        print(f"   Compra: {tc.get('compra')}")
        print(f"   Venta: {tc.get('venta')}")
        print(f"   Variación 24h: {tc.get('variacion_24h')}%\n")
        
        # Test 2: Indicadores macro
        print("2️⃣ Indicadores macro:")
        macro = await scraper.get_indicadores_macro()
        print(f"   Inflación: {macro.get('inflacion_mensual')}%")
        print(f"   Reservas: ${macro.get('reservas_usd_millones')}M")
        print(f"   Tasa BCRP: {macro.get('tasa_referencia_bcrp')}%\n")
        
        await scraper.close()
        print("✅ Tests completados")
    
    asyncio.run(test())
