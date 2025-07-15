#!/usr/bin/env python3
"""
Script d'installation pour Playwright et ses navigateurs
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Exécute une commande et affiche le résultat"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} terminé avec succès")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de {description}: {e}")
        print(f"Sortie d'erreur: {e.stderr}")
        return False

def main():
    """Fonction principale d'installation"""
    print("🚀 Installation de Playwright et des navigateurs...")
    print("=" * 50)
    
    # Vérifier si Python est installé
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ est requis")
        sys.exit(1)
    
    # Installer Playwright
    if not run_command("pip install playwright", "Installation de Playwright"):
        print("❌ Échec de l'installation de Playwright")
        sys.exit(1)
    
    # Installer les navigateurs
    if not run_command("playwright install chromium", "Installation de Chromium"):
        print("❌ Échec de l'installation de Chromium")
        sys.exit(1)
    
    # Vérifier l'installation
    print("\n🔍 Vérification de l'installation...")
    try:
        result = subprocess.run("playwright --version", shell=True, capture_output=True, text=True)
        print(f"✅ Playwright installé: {result.stdout.strip()}")
    except Exception as e:
        print(f"⚠️ Impossible de vérifier la version de Playwright: {e}")
    
    print("\n🎉 Installation terminée avec succès!")
    print("Vous pouvez maintenant utiliser Cursor Browser Control")
    print("\nPour démarrer l'application:")
    print("  python run.py")
    print("  ou")
    print("  python src/main.py")

if __name__ == "__main__":
    main() 