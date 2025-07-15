#!/usr/bin/env python3
"""
Script de lancement pour Cursor Browser Control
"""

import sys
import os
import asyncio

# Ajouter le répertoire src au path Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Importer et exécuter le module principal
if __name__ == "__main__":
    try:
        # Import direct du module main
        from src.main import main
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Au revoir !")
    except Exception as e:
        print(f"❌ Erreur fatale: {e}")
        sys.exit(1) 