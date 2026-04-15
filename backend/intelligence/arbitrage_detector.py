"""
ARBITRAGE DETECTOR
Detecta oportunidades de arbitraje:
- Importación vs producción local
- Diferencias de precio entre regiones
- Temporal arbitrage (comprar ahora, vender después)
"""

import asyncio
from datetime import datetime
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class ArbitrageDetector:
    """
    Detector de oportunidades de arbitraje
    """
    
    def __init__(self):
        # Costos típicos de importación Perú
        self.costos_importacion = {
            "flete_maritimo_pct": 0.08,  # 8% del valor FOB
            "seguro_pct": 0.02,  # 2%
            "arancel_pct": 0.06,  # 6% promedio
            "igv_importacion": 0.18,  # 18%
            "gastos_aduaneros": 500,  # USD fijos
            "almacenaje_mes": 300  # USD/mes
        }
    
    async def scan_all_products(self) -> List[Dict]:
        """
        Escanear todos los productos buscando arbitraje
        """
        try:
            logger.info("🔍 Escaneando oportunidades de arbitraje...")
            
            oportunidades = []
            
            # Productos típicos de importación
            productos_importacion = [
                "arroz", "trigo", "maiz", "azucar", "aceite"
            ]
            
            for producto in productos_importacion:
                oportunidad = await self.analizar_arbitraje(producto)
                
                if oportunidad and oportunidad["margen_pct"] > 15:
                    oportunidades.append(oportunidad)
            
            # Ordenar por margen
            oportunidades.sort(
                key=lambda x: x["margen_pct"],
                reverse=True
            )
            
            logger.info(f"✅ {len(oportunidades)} oportunidades de arbitraje detectadas")
            
            return oportunidades
            
        except Exception as e:
            logger.error(f"❌ Error escaneando arbitraje: {str(e)}")
            return []
    
    async def analizar_arbitraje(self, producto: str) -> Dict:
        """
        Analizar oportunidad de arbitraje para un producto
        """
        try:
            # Obtener precio internacional
            from scrapers.investing_scraper import InvestingScraper
            investing = InvestingScraper()
            
            # Mapeo producto → commodity internacional
            mapeo = {
                "arroz": "arroz",
                "trigo": "trigo",
                "maiz": "maiz",
                "azucar": "azucar"
            }
            
            commodity = mapeo.get(producto.lower())
            if not commodity:
                return {}
            
            # Precio internacional (simulado si no está disponible)
            precio_internacional_usd_ton = {
                "arroz": 450,  # USD/ton
                "trigo": 280,
                "maiz": 220,
                "azucar": 420
            }.get(commodity, 0)
            
            if not precio_internacional_usd_ton:
                return {}
            
            # Obtener precio local
            from scrapers.minagri_scraper import MinagriScraper
            minagri = MinagriScraper()
            precio_local_data = await minagri.get_precio_producto(producto)
            
            if not precio_local_data:
                return {}
            
            precio_local_pen_kg = precio_local_data["precio"]
            
            # Tipo de cambio
            from scrapers.bcrp_scraper import BCRPScraper
            bcrp = BCRPScraper()
            tc_data = await bcrp.get_tipo_cambio()
            tc = tc_data["promedio"] if tc_data else 3.75
            
            # ========================================
            # CALCULAR COSTO TOTAL IMPORTACIÓN
            # ========================================
            
            # 1. Precio FOB (USD/ton)
            precio_fob = precio_internacional_usd_ton
            
            # 2. Flete marítimo (% del FOB)
            flete = precio_fob * self.costos_importacion["flete_maritimo_pct"]
            
            # 3. Seguro
            seguro = precio_fob * self.costos_importacion["seguro_pct"]
            
            # 4. Valor CIF (FOB + Flete + Seguro)
            valor_cif = precio_fob + flete + seguro
            
            # 5. Arancel (% del CIF)
            arancel = valor_cif * self.costos_importacion["arancel_pct"]
            
            # 6. IGV (18% de CIF + Arancel)
            base_igv = valor_cif + arancel
            igv = base_igv * self.costos_importacion["igv_importacion"]
            
            # 7. Gastos aduaneros
            gastos_aduana = self.costos_importacion["gastos_aduaneros"] / 20  # Por tonelada (contenedor 20 ton)
            
            # 8. Almacenaje (1 mes)
            almacenaje = self.costos_importacion["almacenaje_mes"] / 20
            
            # COSTO TOTAL USD/ton
            costo_total_usd_ton = valor_cif + arancel + igv + gastos_aduana + almacenaje
            
            # Convertir a PEN/kg
            costo_importacion_pen_kg = (costo_total_usd_ton * tc) / 1000
            
            # ========================================
            # MARGEN DE ARBITRAJE
            # ========================================
            
            margen_pen_kg = precio_local_pen_kg - costo_importacion_pen_kg
            margen_pct = (margen_pen_kg / costo_importacion_pen_kg) * 100
            
            # ========================================
            # EVALUACIÓN
            # ========================================
            
            if margen_pct > 20:
                viabilidad = "MUY_ALTA"
                recomendacion = "IMPORTAR INMEDIATAMENTE"
            elif margen_pct > 10:
                viabilidad = "ALTA"
                recomendacion = "IMPORTAR - Buena oportunidad"
            elif margen_pct > 5:
                viabilidad = "MEDIA"
                recomendacion = "EVALUAR - Margen ajustado"
            else:
                viabilidad = "BAJA"
                recomendacion = "NO VIABLE - Margen insuficiente"
            
            # ========================================
            # RESULTADO
            # ========================================
            
            return {
                "producto": producto,
                "tipo_arbitraje": "IMPORTACION",
                "precios": {
                    "internacional_usd_ton": precio_fob,
                    "local_pen_kg": precio_local_pen_kg,
                    "importacion_pen_kg": round(costo_importacion_pen_kg, 2)
                },
                "margen_pen_kg": round(margen_pen_kg, 2),
                "margen_pct": round(margen_pct, 1),
                "viabilidad": viabilidad,
                "recomendacion": recomendacion,
                "desglose_costos": {
                    "fob_usd": precio_fob,
                    "flete_usd": round(flete, 2),
                    "seguro_usd": round(seguro, 2),
                    "arancel_usd": round(arancel, 2),
                    "igv_usd": round(igv, 2),
                    "otros_usd": round(gastos_aduana + almacenaje, 2),
                    "total_usd_ton": round(costo_total_usd_ton, 2)
                },
                "rentabilidad_estimada": {
                    "inversion_1000kg": round(costo_importacion_pen_kg * 1000, 2),
                    "venta_1000kg": round(precio_local_pen_kg * 1000, 2),
                    "ganancia_1000kg": round(margen_pen_kg * 1000, 2),
                    "roi_pct": round(margen_pct, 1)
                },
                "riesgos": [
                    "Variación tipo de cambio" if tc > 3.70 else None,
                    "Precio internacional volátil" if commodity in ["azucar"] else None,
                    "Tiempo de importación 30-45 días"
                ],
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error analizando arbitraje {producto}: {str(e)}")
            return {}
    
    async def analizar_arbitraje_regional(
        self, 
        producto: str,
        region_origen: str,
        region_destino: str
    ) -> Dict:
        """
        Arbitraje entre regiones de Perú
        Ej: Comprar en Arequipa, vender en Lima
        """
        try:
            # Por ahora simplificado
            # En producción: precios por región de MINAGRI
            
            diferencia_precio = 0.50  # S/ 0.50/kg diferencia típica
            costo_transporte = 0.20  # S/ 0.20/kg
            
            margen = diferencia_precio - costo_transporte
            margen_pct = (margen / diferencia_precio) * 100
            
            return {
                "tipo": "ARBITRAJE_REGIONAL",
                "producto": producto,
                "ruta": f"{region_origen} → {region_destino}",
                "margen_pen_kg": margen,
                "margen_pct": margen_pct
            }
            
        except Exception as e:
            logger.error(f"❌ Error arbitraje regional: {str(e)}")
            return {}

# Test
if __name__ == "__main__":
    async def test():
        detector = ArbitrageDetector()
        
        print("🧪 Testing Arbitrage Detector...\n")
        
        print("1️⃣ Análisis arbitraje arroz:")
        arb = await detector.analizar_arbitraje("arroz")
        
        if arb:
            print(f"   Precio local: S/ {arb['precios']['local_pen_kg']}/kg")
            print(f"   Costo importación: S/ {arb['precios']['importacion_pen_kg']}/kg")
            print(f"   Margen: {arb['margen_pct']:.1f}%")
            print(f"   Viabilidad: {arb['viabilidad']}")
            print(f"   Recomendación: {arb['recomendacion']}")
        
        print("\n2️⃣ Escaneo completo:")
        ops = await detector.scan_all_products()
        print(f"   Oportunidades encontradas: {len(ops)}")
        
        print("\n✅ Tests completados")
    
    asyncio.run(test())
