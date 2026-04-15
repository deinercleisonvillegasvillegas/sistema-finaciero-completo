"""
NEWS SCRAPER
Scraping de noticias financieras de medios peruanos:
- Gestión
- El Comercio
- RPP Noticias
- América Economía
"""

import aiohttp
import asyncio
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict
import logging
import re

logger = logging.getLogger(__name__)

class NewsScraper:
    """
    Scraper de noticias económicas/financieras
    """
    
    FUENTES = {
        "gestion": {
            "url": "https://gestion.pe/economia/",
            "nombre": "Gestión"
        },
        "elcomercio": {
            "url": "https://elcomercio.pe/economia/",
            "nombre": "El Comercio"
        },
        "rpp": {
            "url": "https://rpp.pe/economia",
            "nombre": "RPP Noticias"
        }
    }
    
    # Keywords relevantes para filtrar noticias
    KEYWORDS_RELEVANTES = [
        "precio", "inflación", "dólar", "tipo cambio", "BCRP",
        "importación", "exportación", "producción", "cosecha",
        "agricultura", "MINAGRI", "SUNAT", "impuesto",
        "commodity", "petroleo", "oro", "cobre",
        "alimento", "arroz", "papa", "cebolla", "trigo"
    ]
    
    def __init__(self):
        self.session = None
        self.noticias_cache = []
    
    async def _get_session(self):
        """Crear sesión HTTP"""
        if self.session is None or self.session.closed:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            self.session = aiohttp.ClientSession(headers=headers)
        return self.session
    
    def _es_relevante(self, titulo: str, resumen: str = "") -> bool:
        """
        Verificar si una noticia es relevante
        """
        texto = (titulo + " " + resumen).lower()
        
        for keyword in self.KEYWORDS_RELEVANTES:
            if keyword.lower() in texto:
                return True
        
        return False
    
    def _extraer_keywords(self, texto: str) -> List[str]:
        """
        Extraer keywords del texto
        """
        keywords = []
        texto_lower = texto.lower()
        
        for keyword in self.KEYWORDS_RELEVANTES:
            if keyword.lower() in texto_lower:
                keywords.append(keyword)
        
        return keywords[:5]  # Máximo 5
    
    async def scrape_gestion(self) -> List[Dict]:
        """
        Scraping de Gestión.pe
        """
        try:
            session = await self._get_session()
            url = self.FUENTES["gestion"]["url"]
            
            async with session.get(url, timeout=10) as response:
                if response.status != 200:
                    return []
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                noticias = []
                
                # Buscar artículos (selectores pueden variar)
                articles = soup.find_all('article', limit=10)
                
                for article in articles:
                    try:
                        # Título
                        titulo_elem = article.find('h2') or article.find('h3')
                        if not titulo_elem:
                            continue
                        
                        titulo = titulo_elem.get_text(strip=True)
                        
                        # URL
                        link_elem = titulo_elem.find('a')
                        url_noticia = link_elem.get('href', '') if link_elem else ''
                        
                        if not url_noticia.startswith('http'):
                            url_noticia = 'https://gestion.pe' + url_noticia
                        
                        # Resumen
                        resumen_elem = article.find('p')
                        resumen = resumen_elem.get_text(strip=True) if resumen_elem else ""
                        
                        # Verificar relevancia
                        if self._es_relevante(titulo, resumen):
                            noticias.append({
                                "fuente": "Gestión",
                                "titulo": titulo,
                                "resumen": resumen[:200],
                                "url": url_noticia,
                                "keywords": self._extraer_keywords(titulo + " " + resumen),
                                "fecha_scraping": datetime.now().isoformat()
                            })
                    
                    except Exception as e:
                        continue
                
                logger.info(f"✅ Gestión: {len(noticias)} noticias relevantes")
                return noticias
                
        except Exception as e:
            logger.error(f"❌ Error scraping Gestión: {str(e)}")
            return []
    
    async def scrape_todas_fuentes(self) -> List[Dict]:
        """
        Scraping de todas las fuentes en paralelo
        """
        try:
            logger.info("📰 Scraping noticias financieras...")
            
            # Por ahora solo Gestión
            # En producción agregar más fuentes
            noticias_gestion = await self.scrape_gestion()
            
            todas_noticias = noticias_gestion
            
            # Eliminar duplicados (mismo título)
            noticias_unicas = []
            titulos_vistos = set()
            
            for noticia in todas_noticias:
                titulo_norm = noticia['titulo'].lower().strip()
                if titulo_norm not in titulos_vistos:
                    noticias_unicas.append(noticia)
                    titulos_vistos.add(titulo_norm)
            
            # Ordenar por relevancia (más keywords = más relevante)
            noticias_unicas.sort(
                key=lambda x: len(x['keywords']), 
                reverse=True
            )
            
            # Guardar en caché
            self.noticias_cache = noticias_unicas[:20]  # Top 20
            
            logger.info(f"✅ Total noticias relevantes: {len(self.noticias_cache)}")
            
            return self.noticias_cache
            
        except Exception as e:
            logger.error(f"❌ Error scraping noticias: {str(e)}")
            return []
    
    async def get_noticias_por_keyword(self, keyword: str) -> List[Dict]:
        """
        Filtrar noticias por keyword específico
        """
        keyword_lower = keyword.lower()
        
        noticias_filtradas = [
            n for n in self.noticias_cache
            if keyword_lower in n['titulo'].lower() or 
               keyword_lower in n['resumen'].lower() or
               keyword_lower in [k.lower() for k in n['keywords']]
        ]
        
        return noticias_filtradas
    
    async def get_alertas_criticas(self) -> List[Dict]:
        """
        Detectar noticias que requieren alertas urgentes
        """
        keywords_criticos = [
            "crisis", "caída", "sube", "baja", "récord",
            "alerta", "urgente", "emergencia", "escasez"
        ]
        
        alertas = []
        
        for noticia in self.noticias_cache[:10]:  # Solo top 10
            titulo_lower = noticia['titulo'].lower()
            
            for keyword in keywords_criticos:
                if keyword in titulo_lower:
                    alertas.append({
                        "tipo": "NOTICIA_CRITICA",
                        "titulo": noticia['titulo'],
                        "url": noticia['url'],
                        "razon": f"Contiene '{keyword}'",
                        "timestamp": datetime.now().isoformat()
                    })
                    break
        
        return alertas
    
    async def scrape_latest(self):
        """
        Actualizar noticias
        (Llamado por scraper loop cada 30 minutos)
        """
        try:
            noticias = await self.scrape_todas_fuentes()
            
            # Detectar alertas
            alertas = await self.get_alertas_criticas()
            
            if alertas:
                logger.warning(f"⚠️ {len(alertas)} noticias críticas detectadas")
                
                # Enviar alertas (si están configuradas)
                # from alerts.telegram_bot import TelegramBot
                # bot = TelegramBot()
                # for alerta in alertas:
                #     await bot.send_critical_alert(alerta['titulo'], alerta['url'])
            
        except Exception as e:
            logger.error(f"❌ Error actualizando noticias: {str(e)}")
    
    async def close(self):
        """Cerrar sesión"""
        if self.session and not self.session.closed:
            await self.session.close()

# Test
if __name__ == "__main__":
    async def test():
        scraper = NewsScraper()
        
        print("🧪 Testing News Scraper...\n")
        
        print("1️⃣ Scraping noticias Gestión...")
        noticias = await scraper.scrape_gestion()
        print(f"   Encontradas: {len(noticias)} noticias relevantes")
        
        if noticias:
            print("\n   Top 3:")
            for i, n in enumerate(noticias[:3], 1):
                print(f"   {i}. {n['titulo'][:60]}...")
                print(f"      Keywords: {', '.join(n['keywords'])}")
        
        print("\n2️⃣ Detectando alertas críticas...")
        alertas = await scraper.get_alertas_criticas()
        print(f"   Alertas: {len(alertas)}")
        
        await scraper.close()
        print("\n✅ Tests completados")
    
    asyncio.run(test())
