"""
WHATSAPP BOT - Alertas vía WhatsApp
Usa Twilio API (trial gratuito disponible)
"""

import asyncio
import aiohttp
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class WhatsAppBot:
    """
    Bot de WhatsApp usando Twilio
    Configuración: cuenta Twilio + sandbox
    """
    
    def __init__(
        self,
        account_sid: Optional[str] = None,
        auth_token: Optional[str] = None,
        from_number: Optional[str] = None
    ):
        # Credenciales Twilio (obtener en twilio.com)
        self.account_sid = account_sid or "TU_ACCOUNT_SID"
        self.auth_token = auth_token or "TU_AUTH_TOKEN"
        self.from_number = from_number or "whatsapp:+14155238886"  # Sandbox Twilio
        
        self.base_url = f"https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}/Messages.json"
        
        self.subscribers = []
        self.session = None
    
    async def _get_session(self):
        """Crear sesión HTTP con auth"""
        if self.session is None or self.session.closed:
            auth = aiohttp.BasicAuth(self.account_sid, self.auth_token)
            self.session = aiohttp.ClientSession(auth=auth)
        return self.session
    
    async def send_message(self, text: str, to_number: Optional[str] = None):
        """
        Enviar mensaje WhatsApp
        
        Args:
            text: Mensaje a enviar
            to_number: Número destino (formato: whatsapp:+51999999999)
        """
        try:
            if to_number:
                await self._send_to_number(to_number, text)
            else:
                # Enviar a todos los suscritos
                for subscriber in self.subscribers:
                    await self._send_to_number(subscriber, text)
                    
        except Exception as e:
            logger.error(f"❌ Error enviando WhatsApp: {str(e)}")
    
    async def _send_to_number(self, to_number: str, text: str):
        """Enviar mensaje a un número específico"""
        try:
            session = await self._get_session()
            
            payload = {
                "From": self.from_number,
                "To": to_number,
                "Body": text
            }
            
            async with session.post(self.base_url, data=payload) as response:
                if response.status == 201:
                    logger.info(f"✅ WhatsApp enviado a {to_number}")
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Error Twilio: {response.status} - {error_text}")
                    
        except Exception as e:
            logger.error(f"❌ Error enviando a {to_number}: {str(e)}")
    
    async def subscribe(self, phone_number: str, productos: list):
        """
        Suscribir número a alertas
        
        Args:
            phone_number: Número WhatsApp (formato: whatsapp:+51999999999)
            productos: Lista de productos
        """
        if phone_number not in self.subscribers:
            self.subscribers.append(phone_number)
            logger.info(f"✅ {phone_number} suscrito a WhatsApp")
            
            welcome_msg = f"""
🎉 *Bienvenido al Sistema de Alertas Financieras Peru*

Estás suscrito a:
{chr(10).join(['• ' + p for p in productos])}

Recibirás alertas de:
📈 Cambios de precio >10%
💰 Oportunidades de negocio
📅 Vencimientos SUNAT
⚠️ Eventos críticos

_Sistema activo 24/7_
"""
            await self.send_message(welcome_msg, phone_number)
    
    async def send_critical_alert(self, titulo: str, mensaje: str):
        """
        Alerta crítica urgente
        """
        alert_text = f"""
🚨 *ALERTA CRÍTICA*

{titulo}

{mensaje}

⏰ {self._get_timestamp()}
"""
        await self.send_message(alert_text)
    
    async def send_opportunity(self, oportunidad: dict):
        """
        Notificación de oportunidad
        """
        msg = f"""
💰 *OPORTUNIDAD DETECTADA*

📦 {oportunidad['producto'].upper()}

Inversión: S/ {oportunidad['inversion']:.2f}
ROI: {oportunidad['roi']:+.1f}%
Plazo: {oportunidad['dias']} días
Ganancia: S/ {oportunidad['ganancia']:.2f}

*{oportunidad['accion']}*

Confianza: {oportunidad['confianza']}%
"""
        await self.send_message(msg)
    
    def _get_timestamp(self) -> str:
        """Timestamp actual"""
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
        # 1. Crear cuenta Twilio (trial gratis)
        # 2. Obtener Account SID y Auth Token
        # 3. Activar sandbox WhatsApp
        # 4. Enviar mensaje "join <sandbox-code>" a número Twilio
        
        bot = WhatsAppBot()
        
        print("🧪 Testing WhatsApp Bot...")
        print("⚠️ Configurar credenciales Twilio primero\n")
        
        # Test mensaje
        await bot.send_critical_alert(
            "Prueba Sistema",
            "Sistema de alertas activo ✅"
        )
        
        await bot.close()
        print("✅ Test completado")
    
    asyncio.run(test())
