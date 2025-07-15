"""
Module de déplacement du curseur
Gère la logique de mouvement, l'accélération et les contraintes
"""

import time
from typing import Tuple, Optional
import logging
from .config import CURSOR_CONFIG

logger = logging.getLogger(__name__)


class CursorMover:
    """Gestionnaire du déplacement du curseur"""
    
    def __init__(self):
        self.current_x = 0
        self.current_y = 0
        self.last_move_time = time.time()
        self.hold_start_time = None
        self.current_direction = None
        self.max_x = 1280  # Valeur par défaut
        self.max_y = 720   # Valeur par défaut
        
    def set_viewport_size(self, width: int, height: int):
        """Définit la taille de la fenêtre pour les contraintes"""
        self.max_x = width
        self.max_y = height
        logger.info(f"📐 Taille de la fenêtre définie: {width}x{height}")
    
    def set_current_position(self, x: int, y: int):
        """Définit la position actuelle du curseur"""
        self.current_x = max(0, min(x, self.max_x))
        self.current_y = max(0, min(y, self.max_y))
        logger.debug(f"📍 Position actuelle: ({self.current_x}, {self.current_y})")
    
    def get_current_position(self) -> Tuple[int, int]:
        """Retourne la position actuelle du curseur"""
        return (self.current_x, self.current_y)
    
    def calculate_movement(self, direction: str, precision_mode: bool = False) -> Tuple[int, int]:
        """Calcule le mouvement basé sur la direction et le mode"""
        current_time = time.time()
        time_held = 0
        
        # Calculer le temps de maintien de la touche
        if self.current_direction == direction:
            if self.hold_start_time:
                time_held = current_time - self.hold_start_time
            else:
                self.hold_start_time = current_time
        else:
            self.current_direction = direction
            self.hold_start_time = current_time
            time_held = 0
        
        # Déterminer la vitesse de base
        if precision_mode:
            base_speed = CURSOR_CONFIG["precision_speed"]
        else:
            base_speed = CURSOR_CONFIG["base_speed"]
        
        # Calculer l'accélération
        acceleration_factor = min(
            CURSOR_CONFIG["acceleration"] ** (time_held * 10),  # Accélération basée sur le temps
            CURSOR_CONFIG["max_speed"] / base_speed
        )
        
        # Vitesse finale
        speed = max(
            int(base_speed * acceleration_factor),
            CURSOR_CONFIG["min_speed"]
        )
        
        # Calculer le déplacement
        dx, dy = 0, 0
        
        if direction == 'up':
            dy = -speed
        elif direction == 'down':
            dy = speed
        elif direction == 'left':
            dx = -speed
        elif direction == 'right':
            dx = speed
        
        # Appliquer les contraintes
        new_x = max(0, min(self.current_x + dx, self.max_x))
        new_y = max(0, min(self.current_y + dy, self.max_y))
        
        # Mettre à jour la position
        self.current_x = new_x
        self.current_y = new_y
        
        # Log du mouvement
        if LOG_CONFIG["show_cursor_position"]:
            mode_str = "PRÉCISION" if precision_mode else "NORMAL"
            logger.debug(f"🖱️ Mouvement {direction.upper()} ({mode_str}): ({dx}, {dy}) -> ({new_x}, {new_y})")
        
        return (new_x, new_y)
    
    def move_to_position(self, x: int, y: int) -> Tuple[int, int]:
        """Déplace le curseur directement à une position"""
        # Appliquer les contraintes
        new_x = max(0, min(x, self.max_x))
        new_y = max(0, min(y, self.max_y))
        
        self.current_x = new_x
        self.current_y = new_y
        
        logger.info(f"🖱️ Curseur déplacé à: ({new_x}, {new_y})")
        return (new_x, new_y)
    
    def reset_movement_state(self):
        """Réinitialise l'état du mouvement (quand aucune touche n'est pressée)"""
        self.current_direction = None
        self.hold_start_time = None
    
    def get_movement_info(self) -> dict:
        """Retourne les informations sur le mouvement actuel"""
        current_time = time.time()
        time_held = 0
        
        if self.hold_start_time and self.current_direction:
            time_held = current_time - self.hold_start_time
        
        return {
            "position": (self.current_x, self.current_y),
            "direction": self.current_direction,
            "time_held": time_held,
            "viewport_size": (self.max_x, self.max_y)
        }
    
    def is_at_boundary(self, direction: str) -> bool:
        """Vérifie si le curseur est à la limite dans une direction"""
        if direction == 'up' and self.current_y <= 0:
            return True
        elif direction == 'down' and self.current_y >= self.max_y:
            return True
        elif direction == 'left' and self.current_x <= 0:
            return True
        elif direction == 'right' and self.current_x >= self.max_x:
            return True
        return False
    
    def get_distance_to_boundary(self, direction: str) -> int:
        """Retourne la distance jusqu'à la limite dans une direction"""
        if direction == 'up':
            return self.current_y
        elif direction == 'down':
            return self.max_y - self.current_y
        elif direction == 'left':
            return self.current_x
        elif direction == 'right':
            return self.max_x - self.current_x
        return 0
    
    def smooth_move_to(self, target_x: int, target_y: int, steps: int = 10) -> list:
        """Génère une liste de positions pour un mouvement fluide"""
        start_x, start_y = self.current_x, self.current_y
        positions = []
        
        for i in range(1, steps + 1):
            progress = i / steps
            x = int(start_x + (target_x - start_x) * progress)
            y = int(start_y + (target_y - start_y) * progress)
            positions.append((x, y))
        
        return positions


# Import de la configuration pour les logs
from .config import LOG_CONFIG 