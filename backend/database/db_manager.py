"""
DATABASE MANAGER
Gestor de base de datos para almacenar:
- Precios históricos
- Predicciones
- Configuración usuarios
- Alertas enviadas
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Gestor de base de datos
    Por ahora usa JSON en memoria (simple)
    En producción: PostgreSQL/Redis
    """
    
    def __init__(self):
        # Almacenamiento en memoria (temporal)
        self.products = {}
        self.historical_prices = {}
        self.predictions = {}
        self.users = {}
        self.alerts_sent = []
        
        # Inicializar productos
        self._init_products()
    
    def _init_products(self):
        """Inicializar lista de productos monitoreados"""
        self.products = [
            # Agrícolas
            "cebolla", "papa", "tomate", "zanahoria", "camote",
            "palta", "mango", "platano", "limon", "maracuya",
            "arroz", "maiz", "quinua", "frijol",
            
            # Commodities internacionales
            "oro", "plata", "cobre", "petroleo_brent", "petroleo_wti",
            "trigo", "soya", "azucar", "cafe"
        ]
    
    async def get_all_products(self) -> List[str]:
        """Obtener lista de todos los productos"""
        return self.products
    
    async def save_product_price(self, producto: str, data: Dict):
        """
        Guardar precio de producto
        """
        try:
            if producto not in self.historical_prices:
                self.historical_prices[producto] = []
            
            # Agregar punto de datos
            price_point = {
                "fecha": datetime.now().strftime("%Y-%m-%d"),
                "precio": data.get("precio", 0),
                "timestamp": datetime.now().isoformat()
            }
            
            self.historical_prices[producto].append(price_point)
            
            # Mantener solo últimos 365 días
            if len(self.historical_prices[producto]) > 365:
                self.historical_prices[producto] = self.historical_prices[producto][-365:]
            
            logger.debug(f"💾 Precio {producto} guardado: {price_point['precio']}")
            
        except Exception as e:
            logger.error(f"❌ Error guardando precio: {str(e)}")
    
    async def get_historical_prices(
        self,
        producto: str,
        days: int = 30
    ) -> List[Dict]:
        """
        Obtener precios históricos
        """
        try:
            if producto not in self.historical_prices:
                return []
            
            # Retornar últimos N días
            all_prices = self.historical_prices[producto]
            return all_prices[-days:] if len(all_prices) >= days else all_prices
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo históricos: {str(e)}")
            return []
    
    async def save_forex_data(self, par: str, data: Dict):
        """Guardar datos de tipo de cambio"""
        await self.save_product_price(par.replace("/", "_"), data)
    
    async def save_commodity_data(self, commodity: str, data: Dict):
        """Guardar datos de commodity"""
        await self.save_product_price(commodity, data)
    
    async def save_prediction(self, producto: str, prediction: Dict):
        """Guardar predicción"""
        try:
            self.predictions[producto] = {
                "prediction": prediction,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.debug(f"💾 Predicción {producto} guardada")
            
        except Exception as e:
            logger.error(f"❌ Error guardando predicción: {str(e)}")
    
    async def get_prediction(self, producto: str) -> Optional[Dict]:
        """Obtener predicción de producto"""
        return self.predictions.get(producto, {}).get("prediction")
    
    async def save_alert_config(self, config: Dict):
        """Guardar configuración de alertas"""
        try:
            user_id = config.get("telegram_chat_id") or config.get("whatsapp_number")
            
            if user_id:
                self.users[user_id] = config
                logger.info(f"✅ Configuración alertas guardada para {user_id}")
                
        except Exception as e:
            logger.error(f"❌ Error guardando config: {str(e)}")
    
    async def save_market_snapshot(self, data: Dict):
        """Guardar snapshot de mercados"""
        # Por ahora solo log
        logger.debug(f"📸 Snapshot mercados guardado")
    
    async def log_alert_sent(self, tipo: str, destinatario: str, mensaje: str):
        """Registrar alerta enviada"""
        self.alerts_sent.append({
            "tipo": tipo,
            "destinatario": destinatario,
            "mensaje": mensaje,
            "timestamp": datetime.now().isoformat()
        })
        
        # Mantener solo últimas 1000 alertas
        if len(self.alerts_sent) > 1000:
            self.alerts_sent = self.alerts_sent[-1000:]

# Test
if __name__ == "__main__":
    async def test():
        db = DatabaseManager()
        
        print("🧪 Testing Database Manager...\n")
        
        # Test guardar precio
        await db.save_product_price("cebolla", {"precio": 3.20})
        
        # Test obtener históricos
        historical = await db.get_historical_prices("cebolla")
        print(f"Históricos cebolla: {len(historical)} registros")
        
        # Test productos
        products = await db.get_all_products()
        print(f"Total productos: {len(products)}")
        
        print("\n✅ Tests completados")
    
    asyncio.run(test())
