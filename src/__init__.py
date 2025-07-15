"""
Cursor Browser Control - Package principal
"""

__version__ = "1.0.0"
__author__ = "Cursor Browser Control Team"
__description__ = "Contrôle du curseur dans le navigateur via les touches directionnelles"

# Import des modules principaux pour faciliter l'accès
from .browser_controller import BrowserController
from .keyboard_handler import KeyboardHandler
from .cursor_mover import CursorMover
from .position_manager import PositionManager
from .config import *

__all__ = [
    'BrowserController',
    'KeyboardHandler', 
    'CursorMover',
    'PositionManager',
    'BROWSER_CONFIG',
    'CURSOR_CONFIG',
    'KEY_CONFIG',
    'SAVE_CONFIG',
    'LOG_CONFIG',
    'COLORS'
] 