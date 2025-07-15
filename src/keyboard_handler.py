"""
Gestionnaire de clavier pour capturer les touches directionnelles
et autres contrôles du projet
"""

import keyboard
import threading
import time
from typing import Dict, Callable, Optional
import logging
from .config import KEY_CONFIG

logger = logging.getLogger(__name__)


class KeyboardHandler:
    """Gestionnaire pour capturer les événements clavier"""
    
    def __init__(self):
        self.is_running = False
        self.pressed_keys = set()
        self.key_handlers: Dict[str, Callable] = {}
        self.combination_handlers: Dict[str, Callable] = {}
        self._listener_thread = None
        
    def start(self):
        """Démarre l'écoute des événements clavier"""
        if self.is_running:
            logger.warning("⚠️ Gestionnaire de clavier déjà en cours")
            return
        
        self.is_running = True
        self._listener_thread = threading.Thread(target=self._listen_for_keys, daemon=True)
        self._listener_thread.start()
        logger.info("⌨️ Gestionnaire de clavier démarré")
    
    def stop(self):
        """Arrête l'écoute des événements clavier"""
        self.is_running = False
        if self._listener_thread:
            self._listener_thread.join(timeout=1)
        logger.info("🛑 Gestionnaire de clavier arrêté")
    
    def _listen_for_keys(self):
        """Boucle principale d'écoute des touches"""
        while self.is_running:
            try:
                # Détection des touches directionnelles
                for key in ['up', 'down', 'left', 'right']:
                    if keyboard.is_pressed(key):
                        if key not in self.pressed_keys:
                            self.pressed_keys.add(key)
                            self._handle_key_press(key)
                    else:
                        if key in self.pressed_keys:
                            self.pressed_keys.remove(key)
                            self._handle_key_release(key)
                
                # Détection des touches spéciales
                if keyboard.is_pressed(KEY_CONFIG["click_key"]):
                    self._handle_click_key()
                
                if keyboard.is_pressed(KEY_CONFIG["quit_key"]):
                    self._handle_quit_key()
                
                # Détection des combinaisons
                if keyboard.is_pressed('ctrl') and keyboard.is_pressed('s'):
                    self._handle_save_position()
                
                if keyboard.is_pressed('ctrl') and keyboard.is_pressed('l'):
                    self._handle_load_position()
                
                time.sleep(0.01)  # 10ms de délai pour éviter la surcharge CPU
                
            except Exception as e:
                logger.error(f"❌ Erreur dans l'écoute des touches: {e}")
                time.sleep(0.1)
    
    def _handle_key_press(self, key: str):
        """Gère l'appui sur une touche"""
        if LOG_CONFIG["show_key_presses"]:
            logger.debug(f"⌨️ Touche pressée: {key}")
        
        # Appeler le gestionnaire spécifique si défini
        if key in self.key_handlers:
            try:
                self.key_handlers[key]()
            except Exception as e:
                logger.error(f"❌ Erreur dans le gestionnaire de touche {key}: {e}")
    
    def _handle_key_release(self, key: str):
        """Gère le relâchement d'une touche"""
        if LOG_CONFIG["show_key_presses"]:
            logger.debug(f"⌨️ Touche relâchée: {key}")
    
    def _handle_click_key(self):
        """Gère la touche de clic (espace)"""
        if 'space' not in self.pressed_keys:
            self.pressed_keys.add('space')
            logger.info("🖱️ Touche clic pressée")
            
            # Appeler le gestionnaire de clic si défini
            if 'click' in self.key_handlers:
                try:
                    self.key_handlers['click']()
                except Exception as e:
                    logger.error(f"❌ Erreur dans le gestionnaire de clic: {e}")
    
    def _handle_quit_key(self):
        """Gère la touche de sortie (Q)"""
        logger.info("🚪 Touche de sortie pressée")
        if 'quit' in self.key_handlers:
            try:
                self.key_handlers['quit']()
            except Exception as e:
                logger.error(f"❌ Erreur dans le gestionnaire de sortie: {e}")
    
    def _handle_save_position(self):
        """Gère la combinaison Ctrl+S pour sauvegarder"""
        if 'ctrl+s' not in self.pressed_keys:
            self.pressed_keys.add('ctrl+s')
            logger.info("💾 Combinaison sauvegarde pressée")
            
            if 'save_position' in self.combination_handlers:
                try:
                    self.combination_handlers['save_position']()
                except Exception as e:
                    logger.error(f"❌ Erreur dans le gestionnaire de sauvegarde: {e}")
    
    def _handle_load_position(self):
        """Gère la combinaison Ctrl+L pour charger"""
        if 'ctrl+l' not in self.pressed_keys:
            self.pressed_keys.add('ctrl+l')
            logger.info("📂 Combinaison chargement pressée")
            
            if 'load_position' in self.combination_handlers:
                try:
                    self.combination_handlers['load_position']()
                except Exception as e:
                    logger.error(f"❌ Erreur dans le gestionnaire de chargement: {e}")
    
    def is_key_pressed(self, key: str) -> bool:
        """Vérifie si une touche est pressée"""
        return key in self.pressed_keys
    
    def is_precision_mode(self) -> bool:
        """Vérifie si le mode précision est activé (Shift)"""
        return keyboard.is_pressed(KEY_CONFIG["precision_modifier"])
    
    def get_pressed_direction(self) -> Optional[str]:
        """Retourne la direction actuellement pressée"""
        for direction in ['up', 'down', 'left', 'right']:
            if direction in self.pressed_keys:
                return direction
        return None
    
    def register_key_handler(self, key: str, handler: Callable):
        """Enregistre un gestionnaire pour une touche spécifique"""
        self.key_handlers[key] = handler
        logger.debug(f"📝 Gestionnaire enregistré pour la touche: {key}")
    
    def register_combination_handler(self, combination: str, handler: Callable):
        """Enregistre un gestionnaire pour une combinaison de touches"""
        self.combination_handlers[combination] = handler
        logger.debug(f"📝 Gestionnaire enregistré pour la combinaison: {combination}")
    
    def get_all_pressed_keys(self) -> set:
        """Retourne toutes les touches actuellement pressées"""
        return self.pressed_keys.copy()
    
    def clear_pressed_keys(self):
        """Efface toutes les touches pressées"""
        self.pressed_keys.clear()
        logger.debug("🧹 Toutes les touches pressées ont été effacées")


# Import de la configuration pour les logs
from .config import LOG_CONFIG 