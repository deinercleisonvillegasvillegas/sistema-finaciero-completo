"""
TELEGRAM BOT - Alertas en tiempo real
Envía notificaciones críticas vía Telegram
"""

import asyncio
import aiohttp
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class TelegramBot:
    """
    Bot de Telegram para alertas
    Configuración: crear bot con @BotFather
    """
    
    def __init__(self, bot_token: Optional[str] = None):
        # Token del bot (obtener de @BotFather en Telegram)
        self.bot_token = bot_token or "TU_BOT_TOKEN_AQUI"
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        
        # IDs de chats suscritos
        self.subscribers = []
        
        self.session = None
    
    async def _get_session(self):
        """Crear sesión HTTP"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def send_message(self, text: str, chat_id: Optional[str] = None):
        """
        Enviar mensaje a Telegram
        
        Args:
            text: Mensaje a enviar
            chat_id: ID del chat (si None, envía a todos los suscritos)
        """
        try:
            if chat_id:
                await self._send_to_chat(chat_id, text)
            else:
                # Enviar a todos los suscritos
                for subscriber_id in self.subscribers:
                    await self._send_to_chat(subscriber_id, text)
                    
        except Exception as e:
            logger.error(f"❌ Error enviando mensaje Telegram: {str(e)}")
    
    async def _send_to_chat(self, chat_id: str, text: str):
        """Enviar mensaje a un chat específico"""
        try:
            session = await self._get_session()
            
            url = f"{self.base_url}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "Markdown"
            }
            
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    logger.info(f"✅ Mensaje enviado a Telegram chat {chat_id}")
                else:
                    logger.error(f"❌ Error Telegram API: {response.status}")
                    
        except Exception as e:
            logger.error(f"❌ Error enviando a chat {chat_id}: {str(e)}")
    
    async def subscribe(self, chat_id: str, productos: List[str]):
        """
        Suscribir un usuario a alertas
        
        Args:
            chat_id: ID del chat de Telegram
            productos: Lista de productos a monitorear
        """
        if chat_id not in self.subscribers:
            self.subscribers.append(chat_id)
            logger.info(f"✅ Usuario {chat_id} suscrito a alertas")
            
            # Mensaje de bienvenida
            welcome_msg = f"""
🎉 *¡Bienvenido al Sistema de Alertas!*

Estás suscrito a notificaciones de:
{chr(10).join(['• ' + p for p in productos])}

Recibirás alertas cuando:
📈 Precios suban >10%
📉 Precios bajen >10%
⚠️ Oportunidades detectadas
📅 Vencimientos SUNAT

_Última actualización: Tiempo real_
"""
            await self.send_message(welcome_msg, chat_id)
    
    async def send_price_alert(self, producto: str, precio_actual: float, variacion: float):
        """
        Alerta de cambio de precio
        """
        emoji = "🔴" if variacion < 0 else "🟢"
        arrow = "📉" if variacion < 0 else "📈"
        
        message = f"""
{emoji} *ALERTA DE PRECIO*

{arrow} *{producto.upper()}*
Precio actual: S/ {precio_actual:.2f}
Variación: {variacion:+.1f}%

{'🔥 OPORTUNIDAD DE COMPRA' if variacion < -10 else '⚠️ PRECIO ALTO' if variacion > 10 else '📊 Precio estable'}

_Actualizado: {self._get_timestamp()}_
"""
        await self.send_message(message)
    
    async def send_opportunity_alert(self, oportunidad: dict):
        """
        Alerta de oportunidad de negocio
        """
        message = f"""
💰 *OPORTUNIDAD DETECTADA*

📦 *{oportunidad['producto'].upper()}*

💵 Inversión: S/ {oportunidad['inversion']:.2f}
📈 ROI estimado: {oportunidad['roi']:+.1f}%
⏱️ Plazo: {oportunidad['dias']} días
🎯 Ganancia esperada: S/ {oportunidad['ganancia']:.2f}

*Acción recomendada:*
{oportunidad['accion']}

_Confianza: {oportunidad['confianza']}%_
"""
        await self.send_message(message)
    
    async def send_sunat_alert(self, alerta: dict):
        """
        Alerta de vencimiento SUNAT
        """
        message = f"""
📅 *RECORDATORIO SUNAT*

{alerta['tipo']}
📝 Monto: S/ {alerta['monto']:.2f}
⏰ Vence: {alerta['fecha_vencimiento']}
⚠️ Faltan {alerta['dias_restantes']} días

{alerta['instrucciones']}
"""
        await self.send_message(message)
    
    def _get_timestamp(self) -> str:
        """Timestamp actual formateado"""
        from datetime import datetime
        return datetime.now().strftime("%d/%m/%Y %H:%M")
    
    async def close(self):
        """Cerrar sesión"""
        if self.session and not self.session.closed:
            await self.session.close()

# Test
if __name__ == "__main__":
    async def test():
        # Para testear:
        # 1. Crear bot con @BotFather en Telegram
        # 2. Obtener token
        # 3. Iniciar chat con el bot
        # 4. Obtener tu chat_id
        
        bot = TelegramBot()
        
        print("🧪 Testing Telegram Bot...")
        print("⚠️ Configurar BOT_TOKEN primero\n")
        
        # Test alerta precio
        await bot.send_price_alert("cebolla", 3.20, -12.5)
        
        await bot.close()
        print("✅ Test completado")
    
    asyncio.run(test())
