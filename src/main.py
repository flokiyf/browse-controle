"""
Point d'entrée principal du projet Cursor Browser Control
Orchestre tous les modules et gère la boucle principale
"""

import asyncio
import logging
import sys
import time
from typing import Optional
import colorama
from colorama import Fore, Back, Style

# Import des modules du projet
try:
    from .browser_controller import BrowserController
    from .keyboard_handler import KeyboardHandler
    from .cursor_mover import CursorMover
    from .position_manager import PositionManager
    from .config import LOG_CONFIG, COLORS
except ImportError:
    # Fallback pour les imports directs
    from browser_controller import BrowserController
    from keyboard_handler import KeyboardHandler
    from cursor_mover import CursorMover
    from position_manager import PositionManager
    from config import LOG_CONFIG, COLORS

# Initialisation de colorama pour Windows
colorama.init()

# Configuration du logging
def setup_logging():
    """Configure le système de logging"""
    log_level = getattr(logging, LOG_CONFIG["log_level"].upper())
    
    # Configuration du format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Handler pour la console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Configuration du logger racine
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)
    
    # Désactiver les logs de Playwright si nécessaire
    if not LOG_CONFIG["enable_logging"]:
        logging.getLogger("playwright").setLevel(logging.WARNING)


class CursorBrowserControl:
    """Classe principale qui orchestre tous les modules"""
    
    def __init__(self):
        self.browser_controller = BrowserController()
        self.keyboard_handler = KeyboardHandler()
        self.cursor_mover = CursorMover()
        self.position_manager = PositionManager()
        
        self.is_running = False
        self.current_position = (0, 0)
        self.current_url = ""
        
    async def start(self) -> bool:
        """Démarre l'application"""
        try:
            print(f"{Fore.CYAN}🚀 Démarrage de Cursor Browser Control...{Style.RESET_ALL}")
            
            # Démarrer le navigateur
            if not await self.browser_controller.start():
                print(f"{Fore.RED}❌ Échec du démarrage du navigateur{Style.RESET_ALL}")
                return False
            
            # Obtenir la taille de la fenêtre
            viewport_size = await self.browser_controller.get_viewport_size()
            self.cursor_mover.set_viewport_size(*viewport_size)
            
            # Positionner le curseur au centre
            center_x = viewport_size[0] // 2
            center_y = viewport_size[1] // 2
            self.current_position = (center_x, center_y)
            await self.browser_controller.move_cursor(center_x, center_y)
            
            # Démarrer le gestionnaire de clavier
            self.keyboard_handler.start()
            
            # Enregistrer les gestionnaires d'événements
            self._register_event_handlers()
            
            self.is_running = True
            print(f"{Fore.GREEN}✅ Application démarrée avec succès{Style.RESET_ALL}")
            self._print_controls()
            
            return True
            
        except Exception as e:
            print(f"{Fore.RED}❌ Erreur lors du démarrage: {e}{Style.RESET_ALL}")
            return False
    
    def _register_event_handlers(self):
        """Enregistre les gestionnaires d'événements clavier"""
        
        # Gestionnaire de sortie
        self.keyboard_handler.register_key_handler('quit', self._handle_quit)
        
        # Gestionnaire de clic
        self.keyboard_handler.register_key_handler('click', self._handle_click)
        
        # Gestionnaires de combinaisons
        self.keyboard_handler.register_combination_handler('save_position', self._handle_save_position)
        self.keyboard_handler.register_combination_handler('load_position', self._handle_load_position)
    
    async def run(self):
        """Boucle principale de l'application"""
        if not self.is_running:
            print(f"{Fore.RED}❌ Application non démarrée{Style.RESET_ALL}")
            return
        
        print(f"{Fore.YELLOW}🎮 Contrôle actif - Utilisez les flèches pour déplacer le curseur{Style.RESET_ALL}")
        
        try:
            while self.is_running:
                # Traiter les mouvements du curseur
                await self._process_cursor_movement()
                
                # Mettre à jour l'URL actuelle
                self.current_url = await self.browser_controller.get_current_url()
                
                # Afficher les informations de statut
                if LOG_CONFIG["show_cursor_position"]:
                    self._display_status()
                
                # Petite pause pour éviter la surcharge CPU
                await asyncio.sleep(0.016)  # ~60 FPS
                
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}⚠️ Interruption détectée{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}❌ Erreur dans la boucle principale: {e}{Style.RESET_ALL}")
        finally:
            await self.stop()
    
    async def _process_cursor_movement(self):
        """Traite les mouvements du curseur basés sur les touches pressées"""
        direction = self.keyboard_handler.get_pressed_direction()
        
        if direction:
            # Mode précision
            precision_mode = self.keyboard_handler.is_precision_mode()
            
            # Calculer la nouvelle position
            new_x, new_y = self.cursor_mover.calculate_movement(direction, precision_mode)
            
            # Déplacer le curseur dans le navigateur
            if await self.browser_controller.move_cursor(new_x, new_y):
                self.current_position = (new_x, new_y)
        else:
            # Aucune touche pressée, réinitialiser l'état
            self.cursor_mover.reset_movement_state()
    
    def _handle_quit(self):
        """Gère la demande de sortie"""
        print(f"\n{Fore.YELLOW}🚪 Sortie demandée...{Style.RESET_ALL}")
        self.is_running = False
    
    async def _handle_click(self):
        """Gère le clic à la position actuelle"""
        x, y = self.current_position
        await self.browser_controller.click(x, y)
    
    def _handle_save_position(self):
        """Gère la sauvegarde de position"""
        x, y = self.current_position
        name = f"position_{int(time.time())}"
        
        if self.position_manager.save_position(name, x, y, self.current_url):
            print(f"{Fore.GREEN}💾 Position sauvegardée: {name} ({x}, {y}){Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}❌ Erreur lors de la sauvegarde{Style.RESET_ALL}")
    
    def _handle_load_position(self):
        """Gère le chargement de position"""
        positions = self.position_manager.list_positions()
        
        if not positions:
            print(f"{Fore.YELLOW}⚠️ Aucune position sauvegardée{Style.RESET_ALL}")
            return
        
        # Pour simplifier, charger la position la plus récente
        latest_position = self.position_manager.get_recent_positions(1)[0]
        result = self.position_manager.load_position(latest_position)
        
        if result:
            x, y, url = result
            asyncio.create_task(self._load_position_async(x, y, url))
            print(f"{Fore.GREEN}📂 Position chargée: {latest_position} ({x}, {y}){Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}❌ Erreur lors du chargement{Style.RESET_ALL}")
    
    async def _load_position_async(self, x: int, y: int, url: str):
        """Charge une position de manière asynchrone"""
        # Naviguer vers l'URL si spécifiée
        if url and url != self.current_url:
            await self.browser_controller.navigate_to(url)
        
        # Déplacer le curseur
        await self.browser_controller.move_cursor(x, y)
        self.current_position = (x, y)
    
    def _display_status(self):
        """Affiche le statut actuel"""
        x, y = self.current_position
        direction = self.keyboard_handler.get_pressed_direction()
        precision = self.keyboard_handler.is_precision_mode()
        
        status_line = f"📍 ({x:3d}, {y:3d})"
        if direction:
            status_line += f" | Direction: {direction.upper()}"
        if precision:
            status_line += " | PRÉCISION"
        
        # Afficher sur la même ligne
        print(f"\r{Fore.BLUE}{status_line}{Style.RESET_ALL}", end="", flush=True)
    
    def _print_controls(self):
        """Affiche les contrôles disponibles"""
        print(f"\n{Fore.CYAN}🎮 Contrôles disponibles:{Style.RESET_ALL}")
        print(f"{Fore.WHITE}  ↑↓←→ : Déplacer le curseur{Style.RESET_ALL}")
        print(f"{Fore.WHITE}  Shift + Direction : Mode précision{Style.RESET_ALL}")
        print(f"{Fore.WHITE}  Espace : Cliquer{Style.RESET_ALL}")
        print(f"{Fore.WHITE}  Ctrl+S : Sauvegarder la position{Style.RESET_ALL}")
        print(f"{Fore.WHITE}  Ctrl+L : Charger une position{Style.RESET_ALL}")
        print(f"{Fore.WHITE}  Q : Quitter{Style.RESET_ALL}")
        print()
    
    async def stop(self):
        """Arrête l'application"""
        print(f"{Fore.YELLOW}🛑 Arrêt de l'application...{Style.RESET_ALL}")
        
        # Arrêter le gestionnaire de clavier
        self.keyboard_handler.stop()
        
        # Arrêter le navigateur
        await self.browser_controller.stop()
        
        self.is_running = False
        print(f"{Fore.GREEN}✅ Application arrêtée{Style.RESET_ALL}")


async def main():
    """Fonction principale"""
    # Configuration du logging
    setup_logging()
    
    # Créer et démarrer l'application
    app = CursorBrowserControl()
    
    if await app.start():
        await app.run()
    else:
        print(f"{Fore.RED}❌ Impossible de démarrer l'application{Style.RESET_ALL}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}👋 Au revoir !{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}❌ Erreur fatale: {e}{Style.RESET_ALL}")
        sys.exit(1) 