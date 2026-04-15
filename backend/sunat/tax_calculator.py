"""
TAX CALCULATOR SUNAT - Contador Automático
Calcula TODOS los impuestos y obligaciones SUNAT:
- IGV (18%)
- Impuesto a la Renta (según régimen)
- Detracciones (SPOT)
- Retenciones
- Percepciones
- Libros contables
- PDTs
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class TaxCalculator:
    """
    Calculadora tributaria SUNAT completa
    Actualizada con normativa vigente 2026
    """
    
    # TASAS VIGENTES 2026
    TASAS = {
        "igv": 0.18,
        "renta_rus": [0, 20, 50],  # Categorías 1, 2, 3 (montos fijos)
        "renta_rer": 0.015,  # 1.5%
        "renta_general": 0.295,  # 29.5%
        "renta_dividendos": 0.05  # 5%
    }
    
    # DETRACCIONES (Sistema SPOT)
    # Actualizado con normas vigentes 2026
    DETRACCIONES = {
        "azucar": {"tasa": 0.10, "umbral": 700, "codigo": "001"},
        "arroz": {"tasa": 0.12, "umbral": 700, "codigo": "002"},
        "alcohol": {"tasa": 0.10, "umbral": 700, "codigo": "003"},
        "recursos_hidrobiologicos": {"tasa": 0.09, "umbral": 700, "codigo": "004"},
        "maiz": {"tasa": 0.10, "umbral": 700, "codigo": "005"},
        "algodon": {"tasa": 0.10, "umbral": 700, "codigo": "006"},
        "caña_azucar": {"tasa": 0.10, "umbral": 700, "codigo": "007"},
        "madera": {"tasa": 0.09, "umbral": 700, "codigo": "008"},
        "arena_piedra": {"tasa": 0.10, "umbral": 700, "codigo": "009"},
        "residuos": {"tasa": 0.15, "umbral": 700, "codigo": "010"},
        "bienes_pdj": {"tasa": 0.04, "umbral": 700, "codigo": "011"},
        "intermediacion": {"tasa": 0.12, "umbral": 700, "codigo": "012"},
        "cemento": {"tasa": 0.10, "umbral": 700, "codigo": "014"},
        "otros_bienes": {"tasa": 0.10, "umbral": 700, "codigo": "019"},
        "servicios": {"tasa": 0.12, "umbral": 700, "codigo": "020"},
    }
    
    # RETENCIONES
    RETENCIONES = {
        "porcentaje": 0.03,  # 3%
        "umbral": 700,
        "solo_agentes_retencion": True
    }
    
    # PERCEPCIONES (importaciones)
    PERCEPCIONES = {
        "importacion_definitiva": 0.10,  # 10%
        "importacion_apendice": 0.035,  # 3.5%
        "venta_interna": 0.02  # 2%
    }
    
    def __init__(self):
        self.regimen_actual = "RER"  # Por defecto
    
    def _clasificar_producto_detraccion(self, producto: str) -> Optional[str]:
        """
        Clasificar producto para detracción
        """
        producto_lower = producto.lower()
        
        # Mapeo de productos a categorías de detracción
        mapeo = {
            "azucar": "azucar",
            "arroz": "arroz",
            "maiz": "maiz",
            "trigo": "otros_bienes",
            "cebolla": None,  # No sujeto a detracción
            "papa": None,
            "tomate": None,
            "cemento": "cemento",
            "arena": "arena_piedra",
            "madera": "madera"
        }
        
        return mapeo.get(producto_lower)
    
    async def calculate_all_taxes(
        self,
        tipo: str,  # "compra" o "venta"
        producto: str,
        cantidad: float,
        precio_unitario: float,
        fecha: str,
        regimen: str = "RER"
    ) -> Dict:
        """
        Calcular TODOS los impuestos y obligaciones
        
        Args:
            tipo: "compra" o "venta"
            producto: Nombre del producto
            cantidad: Cantidad
            precio_unitario: Precio por unidad
            fecha: Fecha operación
            regimen: RUS, RER, o GENERAL
        
        Returns:
            Dict completo con todos los cálculos
        """
        try:
            logger.info(f"📋 Calculando impuestos para {tipo} de {producto}...")
            
            # MONTO TOTAL
            monto_total = cantidad * precio_unitario
            
            # ========================================
            # 1. IGV
            # ========================================
            base_imponible = monto_total / 1.18 if tipo == "venta" else monto_total
            igv_monto = base_imponible * self.TASAS["igv"]
            
            igv_data = {
                "base": round(base_imponible, 2),
                "tasa": self.TASAS["igv"],
                "monto": round(igv_monto, 2),
                "tipo": "IGV Ventas" if tipo == "venta" else "IGV Compras",
                "credito_fiscal": round(igv_monto, 2) if tipo == "compra" else 0,
                "debito_fiscal": round(igv_monto, 2) if tipo == "venta" else 0
            }
            
            # ========================================
            # 2. IMPUESTO A LA RENTA
            # ========================================
            renta_data = {}
            
            if regimen == "RUS":
                # Régimen Único Simplificado (cuota fija)
                # Depende de categoría (ingresos + compras mensuales)
                renta_data = {
                    "regimen": "RUS",
                    "tipo": "Cuota fija mensual",
                    "tasa": None,
                    "monto": 20,  # Categoría 1 (ejemplo)
                    "nota": "Cuota mensual según categoría RUS"
                }
            
            elif regimen == "RER":
                # Régimen Especial Renta (1.5% ingresos netos)
                if tipo == "venta":
                    renta_monto = monto_total * self.TASAS["renta_rer"]
                    renta_data = {
                        "regimen": "RER",
                        "tipo": "Sobre ingresos netos",
                        "tasa": self.TASAS["renta_rer"],
                        "monto": round(renta_monto, 2)
                    }
                else:
                    renta_data = {
                        "regimen": "RER",
                        "tipo": "Solo sobre ventas",
                        "monto": 0
                    }
            
            else:  # GENERAL
                # Régimen General (29.5% sobre utilidades)
                # Requiere contabilidad completa
                renta_data = {
                    "regimen": "GENERAL",
                    "tipo": "Sobre utilidades",
                    "tasa": self.TASAS["renta_general"],
                    "monto": 0,  # Se calcula al cierre del año
                    "nota": "29.5% sobre utilidad anual"
                }
            
            # ========================================
            # 3. DETRACCIÓN
            # ========================================
            detraccion_categoria = self._clasificar_producto_detraccion(producto)
            detraccion_data = {"aplica": False}
            
            if detraccion_categoria and tipo == "compra":
                detraccion_config = self.DETRACCIONES[detraccion_categoria]
                
                if monto_total >= detraccion_config["umbral"]:
                    detraccion_monto = monto_total * detraccion_config["tasa"]
                    
                    detraccion_data = {
                        "aplica": True,
                        "categoria": detraccion_categoria,
                        "codigo": detraccion_config["codigo"],
                        "tasa": detraccion_config["tasa"],
                        "monto": round(detraccion_monto, 2),
                        "cuenta_banco_nacion": "00-XXX-XXXXXX",
                        "plazo_deposito": "5 días hábiles",
                        "nota": f"Depositar en Banco de la Nación antes de {self._calcular_plazo_detraccion(fecha)}"
                    }
            
            # ========================================
            # 4. RETENCIÓN
            # ========================================
            retencion_data = {"aplica": False}
            
            # Solo si comprador es agente de retención
            if tipo == "venta" and monto_total >= self.RETENCIONES["umbral"]:
                retencion_data = {
                    "aplica": True,
                    "tasa": self.RETENCIONES["porcentaje"],
                    "monto": round(monto_total * self.RETENCIONES["porcentaje"], 2),
                    "nota": "Solo si comprador es agente de retención designado por SUNAT"
                }
            
            # ========================================
            # 5. PERCEPCIÓN
            # ========================================
            percepcion_data = {"aplica": False}
            
            # Solo en ventas de ciertos productos
            # (Simplificado - requiere lista específica)
            
            # ========================================
            # 6. LIBROS CONTABLES
            # ========================================
            libro_compras = self._generar_asiento_libro_compras(
                fecha, producto, monto_total, igv_monto
            ) if tipo == "compra" else None
            
            libro_ventas = self._generar_asiento_libro_ventas(
                fecha, producto, monto_total, igv_monto
            ) if tipo == "venta" else None
            
            # ========================================
            # 7. DECLARACIONES PDT
            # ========================================
            pdt_601 = self._preparar_pdt_601(igv_data, fecha)  # IGV
            pdt_621 = self._preparar_pdt_621(renta_data, fecha)  # Renta
            
            # ========================================
            # 8. ALERTAS Y RECOMENDACIONES
            # ========================================
            alertas = []
            
            # Vencimientos
            alertas.append(f"📅 Declaración IGV vence: {self._calcular_vencimiento_igv(fecha)}")
            alertas.append(f"📅 Pago Renta mensual vence: {self._calcular_vencimiento_renta(fecha)}")
            
            if detraccion_data["aplica"]:
                alertas.append(f"⚠️ CRÍTICO: Depositar detracción en {detraccion_data['plazo_deposito']}")
            
            # Recomendaciones régimen
            if regimen == "GENERAL" and monto_total < 50000:
                alertas.append("💡 Sugerencia: Podrías beneficiarte en RER (tasa menor)")
            
            # ========================================
            # CONSOLIDAR RESULTADO
            # ========================================
            total_impuestos = igv_data["monto"] + renta_data.get("monto", 0)
            if detraccion_data["aplica"]:
                total_impuestos += detraccion_data["monto"]
            
            neto_final = monto_total - total_impuestos if tipo == "venta" else monto_total + total_impuestos
            
            return {
                "monto_total": round(monto_total, 2),
                "igv": igv_data,
                "renta": renta_data,
                "detraccion": detraccion_data,
                "retencion": retencion_data,
                "percepcion": percepcion_data,
                "total_impuestos": round(total_impuestos, 2),
                "neto_final": round(neto_final, 2),
                "libro_compras": libro_compras,
                "libro_ventas": libro_ventas,
                "pdt_601": pdt_601,
                "pdt_621": pdt_621,
                "alertas": alertas,
                "regimen": regimen
            }
            
        except Exception as e:
            logger.error(f"❌ Error calculando impuestos: {str(e)}")
            return {}
    
    def _generar_asiento_libro_compras(self, fecha, producto, monto, igv) -> Dict:
        """Generar asiento contable libro de compras"""
        return {
            "fecha": fecha,
            "descripcion": f"Compra de {producto}",
            "base_imponible": round(monto / 1.18, 2),
            "igv": round(igv, 2),
            "total": round(monto, 2),
            "tipo_comprobante": "Factura",
            "numero_serie": "F001-00000001"
        }
    
    def _generar_asiento_libro_ventas(self, fecha, producto, monto, igv) -> Dict:
        """Generar asiento contable libro de ventas"""
        return {
            "fecha": fecha,
            "descripcion": f"Venta de {producto}",
            "base_imponible": round(monto / 1.18, 2),
            "igv": round(igv, 2),
            "total": round(monto, 2),
            "tipo_comprobante": "Factura",
            "numero_serie": "F001-00000001"
        }
    
    def _preparar_pdt_601(self, igv_data, fecha) -> Dict:
        """Preparar datos para PDT 601 (IGV)"""
        return {
            "periodo": fecha[:7],  # YYYY-MM
            "ventas_gravadas": igv_data.get("debito_fiscal", 0),
            "compras_gravadas": igv_data.get("credito_fiscal", 0),
            "igv_a_pagar": max(0, igv_data.get("debito_fiscal", 0) - igv_data.get("credito_fiscal", 0))
        }
    
    def _preparar_pdt_621(self, renta_data, fecha) -> Dict:
        """Preparar datos para PDT 621 (Renta Mensual)"""
        return {
            "periodo": fecha[:7],
            "regimen": renta_data.get("regimen"),
            "monto_a_pagar": renta_data.get("monto", 0)
        }
    
    def _calcular_vencimiento_igv(self, fecha) -> str:
        """Calcular fecha vencimiento IGV (según cronograma SUNAT)"""
        # Simplificado - en producción usar cronograma real SUNAT
        mes = int(fecha[5:7])
        año = int(fecha[:4])
        
        # Vencimiento aproximado: día 18 del mes siguiente
        mes_siguiente = mes + 1 if mes < 12 else 1
        año_siguiente = año if mes < 12 else año + 1
        
        return f"{año_siguiente}-{mes_siguiente:02d}-18"
    
    def _calcular_vencimiento_renta(self, fecha) -> str:
        """Calcular vencimiento Renta mensual"""
        # Similar a IGV
        return self._calcular_vencimiento_igv(fecha)
    
    def _calcular_plazo_detraccion(self, fecha) -> str:
        """Calcular fecha límite depósito detracción"""
        from datetime import datetime, timedelta
        fecha_obj = datetime.strptime(fecha, "%Y-%m-%d")
        fecha_limite = fecha_obj + timedelta(days=5)
        return fecha_limite.strftime("%Y-%m-%d")

# Test
if __name__ == "__main__":
    async def test():
        calc = TaxCalculator()
        
        print("🧪 Testing Tax Calculator...\n")
        
        print("1️⃣ Compra arroz (con detracción):")
        result = await calc.calculate_all_taxes(
            tipo="compra",
            producto="arroz",
            cantidad=1000,
            precio_unitario=3.50,
            fecha="2026-04-09",
            regimen="RER"
        )
        print(f"   Monto total: S/ {result['monto_total']}")
        print(f"   IGV: S/ {result['igv']['monto']}")
        print(f"   Detracción: S/ {result['detraccion'].get('monto', 0) if result['detraccion']['aplica'] else 0}")
        print(f"   Total impuestos: S/ {result['total_impuestos']}\n")
        
        print("2️⃣ Venta cebolla (sin detracción):")
        result2 = await calc.calculate_all_taxes(
            tipo="venta",
            producto="cebolla",
            cantidad=500,
            precio_unitario=4.20,
            fecha="2026-04-09",
            regimen="RER"
        )
        print(f"   Monto total: S/ {result2['monto_total']}")
        print(f"   IGV: S/ {result2['igv']['monto']}")
        print(f"   Renta: S/ {result2['renta']['monto']}")
        print(f"   Neto: S/ {result2['neto_final']}")
        
        print("\n✅ Tests completados")
    
    asyncio.run(test())
