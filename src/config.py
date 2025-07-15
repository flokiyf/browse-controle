"""
Configuration du projet Cursor Browser Control
"""

# Paramètres du navigateur
BROWSER_CONFIG = {
    "headless": False,  # Afficher le navigateur
    "slow_mo": 50,      # Délai entre les actions (ms)
    "viewport": {
        "width": 1280,
        "height": 720
    }
}

# URL de départ
START_URL = "https://www.google.com"

# Paramètres de déplacement du curseur
CURSOR_CONFIG = {
    "base_speed": 10,        # Vitesse de base (pixels par frame)
    "precision_speed": 2,     # Vitesse en mode précision
    "acceleration": 1.2,      # Facteur d'accélération
    "max_speed": 50,         # Vitesse maximale
    "min_speed": 1           # Vitesse minimale
}

# Paramètres des touches
KEY_CONFIG = {
    "quit_key": "q",
    "click_key": "space",
    "precision_modifier": "shift",
    "save_position": "ctrl+s",
    "load_position": "ctrl+l"
}

# Paramètres de sauvegarde
SAVE_CONFIG = {
    "positions_file": "data/saved_positions.json",
    "max_saved_positions": 10
}

# Paramètres de logging
LOG_CONFIG = {
    "enable_logging": True,
    "log_level": "INFO",
    "show_cursor_position": True,
    "show_key_presses": True
}

# Couleurs pour l'affichage (avec colorama)
COLORS = {
    "info": "cyan",
    "success": "green",
    "warning": "yellow",
    "error": "red",
    "position": "blue"
} 