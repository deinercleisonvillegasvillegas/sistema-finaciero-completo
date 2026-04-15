"""
RISK ANALYZER
Análisis de riesgo completo para inversiones:
- Riesgo de mercado (volatilidad)
- Riesgo político/regulatorio
- Riesgo cambiario
- Riesgo operacional
- Scoring de riesgo 0-100
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List
import logging
import statistics

logger = logging.getLogger(__name__)

class RiskAnalyzer:
    """
    Analizador de riesgo profesional
    """
    
    # Factores de riesgo por categoría de producto
    RIESGOS_BASE = {
        # Agrícolas peruanos - Alta volatilidad
        "cebolla": {"volatilidad": 0.12, "estacional": 0.8, "regulatorio": 0.2},
        "papa": {"volatilidad": 0.10, "estacional": 0.7, "regulatorio": 0.1},
        "tomate": {"volatilidad": 0.15, "estacional": 0.9, "regulatorio": 0.1},
        "arroz": {"volatilidad": 0.06, "estacional": 0.5, "regulatorio": 0.4},
        
        # Commodities internacionales - Volatilidad media
        "oro": {"volatilidad": 0.02, "estacional": 0.1, "regulatorio": 0.1},
        "petroleo_brent": {"volatilidad": 0.03, "estacional": 0.3, "regulatorio": 0.5},
        "cobre": {"volatilidad": 0.025, "estacional": 0.2, "regulatorio": 0.3},
        
        # Forex - Volatilidad baja
        "usd": {"volatilidad": 0.01, "estacional": 0.1, "regulatorio": 0.4}
    }
    
    # Eventos de riesgo político/regulatorio Perú
    EVENTOS_RIESGO = [
        {"tipo": "politico", "nivel": "medio", "descripcion": "Año electoral próximo"},
        {"tipo": "regulatorio", "nivel": "bajo", "descripcion": "Cambios normativos SUNAT"},
        {"tipo": "economico", "nivel": "bajo", "descripcion": "Inflación controlada"}
    ]
    
    def __init__(self):
        self.riesgo_pais_peru = 1.85  # Spread sobre bonos USA (%)
    
    async def analyze(self, producto: str) -> Dict:
        """
        Análisis de riesgo completo
        
        Args:
            producto: Nombre del producto
        
        Returns:
            Dict con análisis completo de riesgo
        """
        try:
            logger.info(f"🎯 Analizando riesgo: {producto}")
            
            producto_lower = producto.lower()
            
            # Obtener factores base
            factores = self.RIESGOS_BASE.get(
                producto_lower,
                {"volatilidad": 0.08, "estacional": 0.5, "regulatorio": 0.3}
            )
            
            # ========================================
            # 1. RIESGO DE MERCADO (Volatilidad)
            # ========================================
            volatilidad = factores["volatilidad"]
            
            if volatilidad < 0.03:
                riesgo_mercado = "BAJO"
                score_mercado = 20
            elif volatilidad < 0.08:
                riesgo_mercado = "MEDIO"
                score_mercado = 50
            else:
                riesgo_mercado = "ALTO"
                score_mercado = 80
            
            # ========================================
            # 2. RIESGO ESTACIONAL
            # ========================================
            estacionalidad = factores["estacional"]
            mes_actual = datetime.now().month
            
            # Meses de alta estacionalidad para productos agrícolas
            meses_riesgo = [5, 6, 7]  # Mayo-Julio (invierno, baja producción)
            
            if mes_actual in meses_riesgo and estacionalidad > 0.6:
                riesgo_estacional = "ALTO"
                score_estacional = 70
            else:
                riesgo_estacional = "BAJO"
                score_estacional = 20
            
            # ========================================
            # 3. RIESGO CAMBIARIO
            # ========================================
            # Para productos importados
            if producto_lower in ["trigo", "maiz", "petroleo_brent"]:
                # Alta exposición USD
                riesgo_cambiario = "ALTO"
                score_cambiario = 60
                exposicion_usd = 0.8
            elif producto_lower in ["arroz", "azucar"]:
                # Media exposición USD
                riesgo_cambiario = "MEDIO"
                score_cambiario = 40
                exposicion_usd = 0.5
            else:
                # Baja exposición USD (producción local)
                riesgo_cambiario = "BAJO"
                score_cambiario = 20
                exposicion_usd = 0.2
            
            # ========================================
            # 4. RIESGO REGULATORIO
            # ========================================
            reg_factor = factores["regulatorio"]
            
            if reg_factor > 0.5:
                riesgo_regulatorio = "ALTO"
                score_regulatorio = 70
            elif reg_factor > 0.3:
                riesgo_regulatorio = "MEDIO"
                score_regulatorio = 40
            else:
                riesgo_regulatorio = "BAJO"
                score_regulatorio = 20
            
            # ========================================
            # 5. RIESGO PAÍS (Perú)
            # ========================================
            if self.riesgo_pais_peru < 1.5:
                riesgo_pais = "BAJO"
                score_pais = 20
            elif self.riesgo_pais_peru < 2.5:
                riesgo_pais = "MEDIO"
                score_pais = 40
            else:
                riesgo_pais = "ALTO"
                score_pais = 70
            
            # ========================================
            # 6. SCORE TOTAL DE RIESGO (0-100)
            # ========================================
            # Ponderación de factores
            pesos = {
                "mercado": 0.35,
                "estacional": 0.20,
                "cambiario": 0.20,
                "regulatorio": 0.15,
                "pais": 0.10
            }
            
            score_total = (
                score_mercado * pesos["mercado"] +
                score_estacional * pesos["estacional"] +
                score_cambiario * pesos["cambiario"] +
                score_regulatorio * pesos["regulatorio"] +
                score_pais * pesos["pais"]
            )
            
            # Clasificación final
            if score_total < 30:
                clasificacion = "RIESGO BAJO"
                color = "verde"
            elif score_total < 60:
                clasificacion = "RIESGO MEDIO"
                color = "amarillo"
            else:
                clasificacion = "RIESGO ALTO"
                color = "rojo"
            
            # ========================================
            # 7. RECOMENDACIONES
            # ========================================
            recomendaciones = []
            
            if riesgo_mercado == "ALTO":
                recomendaciones.append("Diversificar posición - alta volatilidad")
            
            if riesgo_cambiario == "ALTO":
                recomendaciones.append("Cobertura cambiaria recomendada (forward/opciones)")
            
            if riesgo_estacional == "ALTO":
                recomendaciones.append("Comprar ahora antes de pico estacional")
            
            if exposicion_usd > 0.5:
                recomendaciones.append(f"Monitorear USD/PEN (exposición {exposicion_usd*100:.0f}%)")
            
            # ========================================
            # RESULTADO CONSOLIDADO
            # ========================================
            return {
                "producto": producto,
                "score_riesgo_total": round(score_total, 1),
                "clasificacion": clasificacion,
                "color_semaforo": color,
                "factores": {
                    "mercado": {
                        "nivel": riesgo_mercado,
                        "score": score_mercado,
                        "volatilidad_diaria": f"{volatilidad*100:.1f}%",
                        "descripcion": "Variabilidad histórica de precios"
                    },
                    "estacional": {
                        "nivel": riesgo_estacional,
                        "score": score_estacional,
                        "factor": estacionalidad,
                        "descripcion": "Riesgo por temporada/clima"
                    },
                    "cambiario": {
                        "nivel": riesgo_cambiario,
                        "score": score_cambiario,
                        "exposicion_usd": f"{exposicion_usd*100:.0f}%",
                        "descripcion": "Exposición a variación USD/PEN"
                    },
                    "regulatorio": {
                        "nivel": riesgo_regulatorio,
                        "score": score_regulatorio,
                        "descripcion": "Cambios normativos/aranceles"
                    },
                    "pais": {
                        "nivel": riesgo_pais,
                        "score": score_pais,
                        "spread_peru": f"{self.riesgo_pais_peru}%",
                        "descripcion": "Riesgo macroeconómico Perú"
                    }
                },
                "eventos_actuales": self.EVENTOS_RIESGO,
                "recomendaciones": recomendaciones,
                "var_estimado_30d": self._calcular_var(volatilidad, 30),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error analizando riesgo: {str(e)}")
            return {}
    
    def _calcular_var(self, volatilidad: float, dias: int) -> Dict:
        """
        Calcular Value at Risk (VaR)
        Pérdida máxima esperada con 95% confianza
        """
        import math
        
        # VaR al 95% = -1.65 * volatilidad * sqrt(dias)
        var_95 = 1.65 * volatilidad * math.sqrt(dias)
        
        # VaR al 99% = -2.33 * volatilidad * sqrt(dias)
        var_99 = 2.33 * volatilidad * math.sqrt(dias)
        
        return {
            "var_95_pct": round(var_95 * 100, 2),
            "var_99_pct": round(var_99 * 100, 2),
            "interpretacion": f"95% confianza: pérdida máxima {var_95*100:.1f}% en {dias} días"
        }
    
    async def comparar_riesgos(self, productos: List[str]) -> Dict:
        """
        Comparar riesgo entre múltiples productos
        """
        try:
            analisis = []
            
            for producto in productos:
                risk = await self.analyze(producto)
                if risk:
                    analisis.append({
                        "producto": producto,
                        "score": risk["score_riesgo_total"],
                        "clasificacion": risk["clasificacion"]
                    })
            
            # Ordenar por menor riesgo
            analisis.sort(key=lambda x: x["score"])
            
            return {
                "productos_analizados": len(analisis),
                "ranking": analisis,
                "menor_riesgo": analisis[0] if analisis else None,
                "mayor_riesgo": analisis[-1] if analisis else None
            }
            
        except Exception as e:
            logger.error(f"❌ Error comparando riesgos: {str(e)}")
            return {}

# Test
if __name__ == "__main__":
    async def test():
        analyzer = RiskAnalyzer()
        
        print("🧪 Testing Risk Analyzer...\n")
        
        # Test 1: Análisis individual
        print("1️⃣ Análisis riesgo cebolla:")
        risk = await analyzer.analyze("cebolla")
        print(f"   Score total: {risk['score_riesgo_total']}")
        print(f"   Clasificación: {risk['clasificacion']}")
        print(f"   Volatilidad: {risk['factores']['mercado']['volatilidad_diaria']}")
        
        # Test 2: Comparación
        print("\n2️⃣ Comparación riesgos:")
        comp = await analyzer.comparar_riesgos(["cebolla", "arroz", "oro", "usd"])
        print("   Ranking (menor a mayor riesgo):")
        for i, p in enumerate(comp['ranking'], 1):
            print(f"   {i}. {p['producto'].upper()}: {p['score']:.1f} - {p['clasificacion']}")
        
        print("\n✅ Tests completados")
    
    asyncio.run(test())
