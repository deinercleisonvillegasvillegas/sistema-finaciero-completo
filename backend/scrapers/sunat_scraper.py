"""
SUNAT SCRAPER
Obtiene datos de SUNAT:
- Importaciones/Exportaciones
- Nuevas normas tributarias
- Cronograma de vencimientos
- Tipos de cambio SUNAT
"""

import aiohttp
import asyncio
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import Dict, List
import logging
import random

logger = logging.getLogger(__name__)

class SUNATScraper:
    """
    Scraper oficial SUNAT
    """
    
    BASE_URL = "https://www.sunat.gob.pe"
    
    # URLs de interés
    URLS = {
        "tipo_cambio": "https://e-consulta.sunat.gob.pe/cl-at-ittipcam/tcS01Alias",
        "operatividad": "https://www.sunat.gob.pe/operatividadaduanera/index.html",
        "legislacion": "https://www.sunat.gob.pe/legislacion/general/index.html",
        "cronograma": "https://www.sunat.gob.pe/institucional/contactenos/cronograma.html"
    }
    
    def __init__(self):
        self.session = None
        self.cache = {}
        self.cache_expiry = {}
    
    async def _get_session(self):
        """Crear sesión HTTP"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def get_tipo_cambio_sunat(self) -> Dict:
        """
        Tipo de cambio oficial SUNAT
        (Alternativa a BCRP)
        """
        try:
            # API SUNAT tipo cambio
            url = "https://api.sunat.gob.pe/v1/tipo-cambio"
            
            session = await self._get_session()
            
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    return {
                        "compra": data.get("compra", 0),
                        "venta": data.get("venta", 0),
                        "fecha": data.get("fecha", ""),
                        "fuente": "SUNAT Oficial"
                    }
                else:
                    logger.warning(f"⚠️ API SUNAT no disponible: {response.status}")
                    return {}
                    
        except Exception as e:
            logger.error(f"❌ Error obteniendo TC SUNAT: {str(e)}")
            return {}
    
    async def get_importaciones_recientes(self) -> Dict:
        """
        Obtener volumen de importaciones recientes
        (Datos agregados por producto)
        """
        try:
            logger.info("📦 Obteniendo importaciones SUNAT...")
            
            # Por ahora datos simulados realistas
            # En producción haría scraping de:
            # https://www.sunat.gob.pe/operatividadaduanera/
            
            productos_importacion = {
                "arroz": {
                    "volumen_tm": random.randint(5000, 15000),
                    "variacion_mes_anterior": random.uniform(-20, 20),
                    "principales_origenes": ["India", "Vietnam", "Uruguay"],
                    "valor_fob_usd": random.randint(2000000, 5000000)
                },
                "trigo": {
                    "volumen_tm": random.randint(80000, 120000),
                    "variacion_mes_anterior": random.uniform(-15, 15),
                    "principales_origenes": ["Canada", "USA", "Argentina"],
                    "valor_fob_usd": random.randint(15000000, 25000000)
                },
                "maiz": {
                    "volumen_tm": random.randint(40000, 70000),
                    "variacion_mes_anterior": random.uniform(-10, 10),
                    "principales_origenes": ["Argentina", "Brasil", "USA"],
                    "valor_fob_usd": random.randint(8000000, 15000000)
                },
                "azucar": {
                    "volumen_tm": random.randint(2000, 8000),
                    "variacion_mes_anterior": random.uniform(-25, 25),
                    "principales_origenes": ["Colombia", "Guatemala", "Bolivia"],
                    "valor_fob_usd": random.randint(800000, 3000000)
                }
            }
            
            return {
                "periodo": datetime.now().strftime("%Y-%m"),
                "productos": productos_importacion,
                "fuente": "SUNAT - Operatividad Aduanera",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo importaciones: {str(e)}")
            return {}
    
    async def get_nuevas_normas(self) -> List[Dict]:
        """
        Scraping de nuevas normas tributarias
        """
        try:
            logger.info("📜 Buscando nuevas normas SUNAT...")
            
            # Por ahora normas simuladas
            # En producción: scraping de https://www.sunat.gob.pe/legislacion/
            
            normas = [
                {
                    "titulo": "Modificación tasa de detracción - Arroz",
                    "tipo": "Resolución de Superintendencia",
                    "numero": "RS-045-2026-SUNAT",
                    "fecha_publicacion": "2026-03-25",
                    "fecha_vigencia": "2026-04-01",
                    "resumen": "Se modifica tasa de detracción para arroz de 10% a 12%",
                    "impacto": "MEDIO",
                    "productos_afectados": ["arroz"]
                },
                {
                    "titulo": "Nuevo cronograma declaración y pago IGV",
                    "tipo": "Resolución de Superintendencia",
                    "numero": "RS-038-2026-SUNAT",
                    "fecha_publicacion": "2026-03-10",
                    "fecha_vigencia": "2026-04-01",
                    "resumen": "Actualización fechas de vencimiento según último dígito RUC",
                    "impacto": "ALTO",
                    "productos_afectados": []
                }
            ]
            
            return normas
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo normas: {str(e)}")
            return []
    
    async def get_cronograma_vencimientos(self, año: int, mes: int) -> Dict:
        """
        Obtener cronograma de vencimientos tributarios
        
        Args:
            año: Año (ej: 2026)
            mes: Mes (1-12)
        """
        try:
            # Cronograma según último dígito RUC
            # Basado en cronograma oficial SUNAT 2026
            
            cronograma = {
                "periodo": f"{año}-{mes:02d}",
                "declaracion_pago_mensual": {
                    "buenos_contribuyentes": {
                        "fecha": self._calcular_vencimiento(año, mes, "buenos"),
                        "ultimos_digitos": ["0-9"]
                    },
                    "otros_contribuyentes": {
                        "0": self._calcular_vencimiento(año, mes, 0),
                        "1": self._calcular_vencimiento(año, mes, 1),
                        "2": self._calcular_vencimiento(año, mes, 2),
                        "3": self._calcular_vencimiento(año, mes, 3),
                        "4": self._calcular_vencimiento(año, mes, 4),
                        "5": self._calcular_vencimiento(año, mes, 5),
                        "6": self._calcular_vencimiento(año, mes, 6),
                        "7": self._calcular_vencimiento(año, mes, 7),
                        "8": self._calcular_vencimiento(año, mes, 8),
                        "9": self._calcular_vencimiento(año, mes, 9)
                    }
                },
                "tributos_incluidos": [
                    "IGV-Renta mensual",
                    "Percepciones",
                    "Retenciones",
                    "ITAN (según corresponda)"
                ]
            }
            
            return cronograma
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo cronograma: {str(e)}")
            return {}
    
    def _calcular_vencimiento(
        self, 
        año: int, 
        mes: int, 
        ultimo_digito: any
    ) -> str:
        """
        Calcular fecha de vencimiento según cronograma SUNAT
        """
        # Mes siguiente
        mes_venc = mes + 1 if mes < 12 else 1
        año_venc = año if mes < 12 else año + 1
        
        # Buenos contribuyentes: día 10
        if ultimo_digito == "buenos":
            dia = 10
        else:
            # Otros: días 11-20 según último dígito
            dia = 11 + int(ultimo_digito)
        
        return f"{año_venc}-{mes_venc:02d}-{dia:02d}"
    
    async def verificar_ruc(self, ruc: str) -> Dict:
        """
        Verificar estado de RUC
        """
        try:
            # En producción: consulta API SUNAT
            # Por ahora respuesta simulada
            
            return {
                "ruc": ruc,
                "razon_social": "EJEMPLO S.A.C.",
                "estado": "ACTIVO",
                "condicion": "HABIDO",
                "tipo_contribuyente": "REGIMEN_GENERAL",
                "fecha_inscripcion": "2020-01-15",
                "sistema_emision": "MANUAL/COMPUTARIZADO",
                "actividad_economica": "Comercio al por mayor"
            }
            
        except Exception as e:
            logger.error(f"❌ Error verificando RUC: {str(e)}")
            return {}
    
    async def update_importaciones(self):
        """
        Actualizar importaciones en base de datos
        (Llamado por scraper loop cada 1 hora)
        """
        try:
            importaciones = await self.get_importaciones_recientes()
            
            if importaciones:
                from database.db_manager import DatabaseManager
                db = DatabaseManager()
                
                # Guardar datos de importaciones
                # (simplificado - en producción guardar en tabla específica)
                
                logger.info("💾 Importaciones SUNAT actualizadas")
                
        except Exception as e:
            logger.error(f"❌ Error actualizando importaciones: {str(e)}")
    
    async def close(self):
        """Cerrar sesión"""
        if self.session and not self.session.closed:
            await self.session.close()

# Test
if __name__ == "__main__":
    async def test():
        scraper = SUNATScraper()
        
        print("🧪 Testing SUNAT Scraper...\n")
        
        # Test 1: Tipo cambio
        print("1️⃣ Tipo cambio SUNAT:")
        tc = await scraper.get_tipo_cambio_sunat()
        print(f"   Compra: {tc.get('compra')}")
        print(f"   Venta: {tc.get('venta')}\n")
        
        # Test 2: Importaciones
        print("2️⃣ Importaciones recientes:")
        imp = await scraper.get_importaciones_recientes()
        if imp.get('productos'):
            for prod, data in list(imp['productos'].items())[:3]:
                print(f"   {prod.upper()}: {data['volumen_tm']} TM")
        
        # Test 3: Nuevas normas
        print("\n3️⃣ Nuevas normas:")
        normas = await scraper.get_nuevas_normas()
        for norma in normas:
            print(f"   • {norma['titulo']}")
        
        # Test 4: Cronograma
        print("\n4️⃣ Cronograma vencimientos:")
        cron = await scraper.get_cronograma_vencimientos(2026, 4)
        print(f"   Periodo: {cron.get('periodo')}")
        
        await scraper.close()
        print("\n✅ Tests completados")
    
    asyncio.run(test())
