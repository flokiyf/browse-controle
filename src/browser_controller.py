"""
Contrôleur de navigateur utilisant Playwright
Gère l'instance du navigateur Chrome et les interactions
"""

import asyncio
from playwright.async_api import async_playwright
from typing import Tuple, Optional
import logging
from .config import BROWSER_CONFIG, START_URL

logger = logging.getLogger(__name__)

# Script JS pour injecter le curseur rouge
INJECT_CURSOR_JS = '''
(function() {
    if (!document.getElementById('ai-cursor')) {
        var cursor = document.createElement('div');
        cursor.id = 'ai-cursor';
        cursor.style.position = 'fixed';
        cursor.style.width = '18px';
        cursor.style.height = '18px';
        cursor.style.background = 'red';
        cursor.style.borderRadius = '50%';
        cursor.style.zIndex = '999999';
        cursor.style.pointerEvents = 'none';
        cursor.style.boxShadow = '0 0 8px 2px rgba(255,0,0,0.5)';
        cursor.style.transition = 'left 0.04s linear, top 0.04s linear';
        cursor.style.left = '0px';
        cursor.style.top = '0px';
        document.body.appendChild(cursor);
    }
    document.body.style.cursor = 'none';
})();
'''

UPDATE_CURSOR_JS = '''
(x, y) => {
    var cursor = document.getElementById('ai-cursor');
    if (cursor) {
        cursor.style.left = (x - 9) + 'px';
        cursor.style.top = (y - 9) + 'px';
        return true;
    }
    return false;
}
'''

class BrowserController:
    """Contrôleur pour gérer le navigateur Playwright"""
    
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page = None
        self.context = None
        self._is_running = False
        
    async def start(self) -> bool:
        """Démarre le navigateur Chrome"""
        try:
            logger.info("🚀 Démarrage du navigateur Chrome...")
            
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=BROWSER_CONFIG["headless"],
                slow_mo=BROWSER_CONFIG["slow_mo"]
            )
            
            self.context = await self.browser.new_context(
                viewport=BROWSER_CONFIG["viewport"]
            )
            
            self.page = await self.context.new_page()
            await self.page.goto(START_URL)
            
            # Injecter le curseur custom
            await self.inject_custom_cursor()
            
            self._is_running = True
            logger.info("✅ Navigateur démarré avec succès")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du démarrage du navigateur: {e}")
            return False
    
    async def inject_custom_cursor(self):
        """Injecte le point rouge comme curseur custom dans la page"""
        if self.page:
            try:
                await self.page.evaluate(INJECT_CURSOR_JS)
                logger.info("🔴 Curseur custom injecté dans la page")
            except Exception as e:
                logger.error(f"❌ Erreur lors de l'injection du curseur custom: {e}")
    
    async def update_custom_cursor(self, x: int, y: int):
        """Met à jour la position du curseur custom dans la page"""
        if self.page:
            try:
                # Utiliser la syntaxe correcte pour Playwright Python avec un objet
                result = await self.page.evaluate("""
                    (pos) => {
                        var cursor = document.getElementById('ai-cursor');
                        if (cursor) {
                            cursor.style.left = (pos.x - 9) + 'px';
                            cursor.style.top = (pos.y - 9) + 'px';
                            return true;
                        }
                        return false;
                    }
                """, {"x": x, "y": y})
                
                if result:
                    logger.debug(f"🔴 Curseur custom mis à jour à ({x}, {y})")
                else:
                    logger.warning("⚠️ Curseur custom non trouvé, réinjection...")
                    await self.inject_custom_cursor()
                    await self.page.evaluate("""
                        (pos) => {
                            var cursor = document.getElementById('ai-cursor');
                            if (cursor) {
                                cursor.style.left = (pos.x - 9) + 'px';
                                cursor.style.top = (pos.y - 9) + 'px';
                                return true;
                            }
                            return false;
                        }
                    """, {"x": x, "y": y})
            except Exception as e:
                logger.error(f"❌ Erreur lors de la mise à jour du curseur custom: {e}")
                # Réinjecter le curseur en cas d'erreur
                try:
                    await self.inject_custom_cursor()
                    await self.page.evaluate("""
                        (pos) => {
                            var cursor = document.getElementById('ai-cursor');
                            if (cursor) {
                                cursor.style.left = (pos.x - 9) + 'px';
                                cursor.style.top = (pos.y - 9) + 'px';
                                return true;
                            }
                            return false;
                        }
                    """, {"x": x, "y": y})
                except Exception as e2:
                    logger.error(f"❌ Échec de la réinjection du curseur: {e2}")
    
    async def stop(self):
        """Arrête le navigateur"""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            
            self._is_running = False
            logger.info("🛑 Navigateur arrêté")
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'arrêt du navigateur: {e}")
    
    async def move_cursor(self, x: int, y: int):
        """Déplace le curseur à la position spécifiée et le point rouge"""
        if not self._is_running or not self.page:
            logger.warning("⚠️ Navigateur non disponible")
            return False
        
        try:
            await self.page.mouse.move(x, y)
            await self.update_custom_cursor(x, y)
            logger.debug(f"🖱️ Curseur déplacé à ({x}, {y})")
            return True
        except Exception as e:
            logger.error(f"❌ Erreur lors du déplacement du curseur: {e}")
            return False
    
    async def click(self, x: int, y: int):
        """Clique à la position spécifiée (simple et fiable)"""
        if not self._is_running or not self.page:
            logger.warning("⚠️ Navigateur non disponible")
            return False
        
        try:
            # Forcer le focus sur la page
            await self.page.bring_to_front()
            
            # Clic simple et direct
            await self.page.mouse.click(x, y)
            logger.info(f"🖱️ Clic effectué à ({x}, {y})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du clic: {e}")
            return False
    
    async def get_viewport_size(self) -> Tuple[int, int]:
        """Retourne la taille de la fenêtre du navigateur"""
        if not self.page:
            return (0, 0)
        
        try:
            viewport = self.page.viewport_size
            return (viewport["width"], viewport["height"])
        except Exception as e:
            logger.error(f"❌ Erreur lors de la récupération de la taille: {e}")
            return (0, 0)
    
    async def get_current_url(self) -> str:
        """Retourne l'URL actuelle"""
        if not self.page:
            return ""
        
        try:
            return self.page.url
        except Exception as e:
            logger.error(f"❌ Erreur lors de la récupération de l'URL: {e}")
            return ""
    
    def is_running(self) -> bool:
        """Vérifie si le navigateur est en cours d'exécution"""
        return self._is_running
    
    async def navigate_to(self, url: str):
        """Navigue vers une URL spécifique et réinjecte le curseur custom"""
        if not self.page:
            logger.warning("⚠️ Navigateur non disponible")
            return False
        
        try:
            await self.page.goto(url)
            await self.inject_custom_cursor()
            logger.info(f"🌐 Navigation vers: {url}")
            return True
        except Exception as e:
            logger.error(f"❌ Erreur lors de la navigation: {e}")
            return False
    
    async def take_screenshot(self, path: str = "screenshot.png"):
        """Prend une capture d'écran"""
        if not self.page:
            logger.warning("⚠️ Navigateur non disponible")
            return False
        
        try:
            await self.page.screenshot(path=path)
            logger.info(f"📸 Capture d'écran sauvegardée: {path}")
            return True
        except Exception as e:
            logger.error(f"❌ Erreur lors de la capture d'écran: {e}")
            return False 