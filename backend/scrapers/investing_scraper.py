"""
INVESTING.COM SCRAPER
Obtiene precios de commodities internacionales:
- Metales (oro, plata, cobre)
- Energía (petróleo, gas)
- Granos (trigo, maíz, soya)
- Alimentos (azúcar, café, cacao)

Técnicas anti-bloqueo:
- User-Agent rotativo
- Proxies (opcional)
- Rate limiting
- Caché agresivo
"""

import aiohttp
import asyncio
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import Dict, List
import random
import logging
import json

logger = logging.getLogger(__name__)

class InvestingScraper:
    """
    Scraper Investing.com con protección anti-bloqueo
    """
    
    BASE_URL = "https://www.investing.com"
    
    # Productos y sus URLs
    COMMODITIES = {
        # Metales
        "oro": "/commodities/gold",
        "plata": "/commodities/silver",
        "cobre": "/commodities/copper",
        "zinc": "/commodities/zinc",
        "plomo": "/commodities/lead",
        "platino": "/commodities/platinum",
        
        # Energía
        "petroleo_brent": "/commodities/brent-oil",
        "petroleo_wti": "/commodities/crude-oil",
        "gas_natural": "/commodities/natural-gas",
        "gasolina": "/commodities/gasoline-rbob",
        
        # Granos
        "trigo": "/commodities/us-wheat",
        "maiz": "/commodities/us-corn",
        "soya": "/commodities/us-soybeans",
        "arroz": "/commodities/rough-rice",
        "avena": "/commodities/us-oats",
        
        # Alimentos
        "azucar": "/commodities/us-sugar-no11",
        "cafe": "/commodities/us-coffee-c",
        "cacao": "/commodities/us-cocoa",
        "algodon": "/commodities/us-cotton",
        "jugo_naranja": "/commodities/orange-juice",
        
        # Ganado
        "ganado_vivo": "/commodities/live-cattle",
        "cerdo": "/commodities/lean-hogs"
    }
    
    # User-Agents rotativos (simular navegadores reales)
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ]
    
    def __init__(self):
        self.session = None
        self.cache = {}
        self.cache_expiry = {}
        self.last_request_time = {}
    
    def _get_random_user_agent(self) -> str:
        """Seleccionar User-Agent aleatorio"""
        return random.choice(self.USER_AGENTS)
    
    def _get_headers(self) -> Dict:
        """Headers para simular navegador real"""
        return {
            "User-Agent": self._get_random_user_agent(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "es-PE,es;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Cache-Control": "max-age=0"
        }
    
    async def _get_session(self):
        """Crear sesión HTTP reutilizable"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(
                headers=self._get_headers(),
                timeout=timeout
            )
        return self.session
    
    async def _rate_limit(self, url: str):
        """
        Rate limiting: esperar entre requests
        Mínimo 5 segundos entre requests al mismo recurso
        """
        last_time = self.last_request_time.get(url, 0)
        elapsed = datetime.now().timestamp() - last_time
        
        if elapsed < 5:
            wait_time = 5 - elapsed + random.uniform(1, 3)  # +1-3 seg aleatorio
            logger.debug(f"⏳ Rate limit: esperando {wait_time:.1f} segundos...")
            await asyncio.sleep(wait_time)
        
        self.last_request_time[url] = datetime.now().timestamp()
    
    async def _fetch_page(self, url: str) -> str:
        """
        Obtener HTML de una página con protección anti-bloqueo
        """
        try:
            # Verificar caché
            if url in self.cache:
                if datetime.now() < self.cache_expiry.get(url, datetime.min):
                    logger.debug(f"📦 Usando caché para {url}")
                    return self.cache[url]
            
            # Rate limiting
            await self._rate_limit(url)
            
            session = await self._get_session()
            
            async with session.get(url, ssl=False) as response:
                if response.status == 200:
                    html = await response.text()
                    
                    # Guardar en caché (válido 1 hora)
                    self.cache[url] = html
                    self.cache_expiry[url] = datetime.now() + timedelta(hours=1)
                    
                    logger.info(f"✅ Página obtenida: {url}")
                    return html
                    
                elif response.status == 429:  # Too Many Requests
                    logger.warning(f"⚠️ Rate limited por Investing.com - esperando 60 seg")
                    await asyncio.sleep(60)
                    return await self._fetch_page(url)  # Reintentar
                    
                else:
                    logger.error(f"❌ Error HTTP {response.status}: {url}")
                    return ""
                    
        except Exception as e:
            logger.error(f"❌ Error fetching {url}: {str(e)}")
            return ""
    
    def _parse_commodity_page(self, html: str, commodity_name: str) -> Dict:
        """
        Parsear página de commodity y extraer datos
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Precio actual (varía según diseño de Investing.com)
            price = 0
            price_elem = soup.find('div', {'data-test': 'instrument-price-last'})
            if not price_elem:
                price_elem = soup.find('span', {'class': 'text-2xl'})
            if price_elem:
                price_text = price_elem.text.strip().replace(',', '')
                price = float(price_text)
            
            # Variación
            variacion = 0
            var_elem = soup.find('div', {'data-test': 'instrument-price-change-percent'})
            if var_elem:
                var_text = var_elem.text.strip().replace('%', '').replace('+', '')
                variacion = float(var_text)
            
            # Máximo y mínimo del día
            high_52w = 0
            low_52w = 0
            
            # Buscar tabla de datos
            tabla = soup.find('div', {'class': 'instrument-metadata'})
            if tabla:
                rows = tabla.find_all('div', {'class': 'text-sm'})
                for row in rows:
                    text = row.text.lower()
                    if '52' in text and 'high' in text:
                        val = row.find_next('div')
                        if val:
                            high_52w = float(val.text.strip().replace(',', ''))
                    elif '52' in text and 'low' in text:
                        val = row.find_next('div')
                        if val:
                            low_52w = float(val.text.strip().replace(',', ''))
            
            return {
                "producto": commodity_name,
                "precio": price,
                "variacion_pct": variacion,
                "max_52w": high_52w,
                "min_52w": low_52w,
                "moneda": "USD",
                "unidad": self._get_unidad(commodity_name),
                "timestamp": datetime.now().isoformat(),
                "fuente": "Investing.com"
            }
            
        except Exception as e:
            logger.error(f"❌ Error parseando commodity {commodity_name}: {str(e)}")
            return {}
    
    def _get_unidad(self, commodity: str) -> str:
        """Unidad de medida según commodity"""
        unidades = {
            "oro": "oz",
            "plata": "oz",
            "cobre": "lb",
            "petroleo_brent": "barril",
            "petroleo_wti": "barril",
            "gas_natural": "MMBtu",
            "trigo": "bushel",
            "maiz": "bushel",
            "soya": "bushel",
            "arroz": "cwt",
            "azucar": "lb",
            "cafe": "lb",
            "cacao": "ton"
        }
        return unidades.get(commodity, "unidad")
    
    async def get_commodity_price(self, commodity: str) -> Dict:
        """
        Obtener precio actual de un commodity
        
        Args:
            commodity: Nombre del commodity (ej: 'oro', 'petroleo_brent')
        
        Returns:
            Dict con precio y datos
        """
        try:
            commodity_lower = commodity.lower()
            
            if commodity_lower not in self.COMMODITIES:
                logger.error(f"❌ Commodity '{commodity}' no encontrado")
                return {}
            
            url = self.BASE_URL + self.COMMODITIES[commodity_lower]
            
            logger.info(f"🔍 Obteniendo precio {commodity}...")
            
            html = await self._fetch_page(url)
            
            if not html:
                return {}
            
            data = self._parse_commodity_page(html, commodity)
            
            logger.info(f"✅ {commodity}: ${data.get('precio', 0)} ({data.get('variacion_pct', 0):+.2f}%)")
            
            return data
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo {commodity}: {str(e)}")
            return {}
    
    async def get_commodities_prices(self) -> Dict:
        """
        Obtener precios de TODOS los commodities
        (Solo los más importantes para no saturar)
        """
        try:
            logger.info("📊 Obteniendo precios de commodities principales...")
            
            # Commodities críticos (para no hacer 25 requests)
            criticos = [
                "oro", "plata", "cobre",
                "petroleo_brent", "petroleo_wti",
                "trigo", "maiz", "soya", "arroz",
                "azucar", "cafe"
            ]
            
            # Obtener en paralelo con límite de concurrencia
            semaphore = asyncio.Semaphore(3)  # Máximo 3 requests simultáneos
            
            async def fetch_with_semaphore(commodity):
                async with semaphore:
                    return await self.get_commodity_price(commodity)
            
            tasks = [fetch_with_semaphore(c) for c in criticos]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Consolidar resultados
            commodities_data = {}
            for i, commodity in enumerate(criticos):
                if not isinstance(results[i], Exception) and results[i]:
                    commodities_data[commodity] = results[i]
            
            logger.info(f"✅ Obtenidos {len(commodities_data)} commodities")
            
            return commodities_data
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo commodities: {str(e)}")
            return {}
    
    async def update_all_commodities(self):
        """
        Actualizar todos los commodities en base de datos
        (Llamado por scraper loop cada 5 minutos)
        """
        try:
            commodities = await self.get_commodities_prices()
            
            if commodities:
                # Guardar en DB
                from database.db_manager import DatabaseManager
                db = DatabaseManager()
                
                for commodity, data in commodities.items():
                    await db.save_commodity_data(commodity, data)
                
                logger.info(f"💾 {len(commodities)} commodities guardados en DB")
                
        except Exception as e:
            logger.error(f"❌ Error actualizando commodities: {str(e)}")
    
    async def close(self):
        """Cerrar sesión HTTP"""
        if self.session and not self.session.closed:
            await self.session.close()

# Test del módulo
if __name__ == "__main__":
    async def test():
        scraper = InvestingScraper()
        
        print("🧪 Testing Investing.com Scraper...\n")
        
        # Test 1: Un commodity
        print("1️⃣ Precio ORO:")
        oro = await scraper.get_commodity_price("oro")
        print(f"   Precio: ${oro.get('precio', 0)}/oz")
        print(f"   Variación: {oro.get('variacion_pct', 0):+.2f}%\n")
        
        # Test 2: Múltiples commodities
        print("2️⃣ Commodities principales:")
        all_commodities = await scraper.get_commodities_prices()
        for name, data in all_commodities.items():
            print(f"   {name.upper()}: ${data.get('precio', 0)} ({data.get('variacion_pct', 0):+.2f}%)")
        
        await scraper.close()
        print("\n✅ Tests completados")
    
    asyncio.run(test())
