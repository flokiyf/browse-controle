"""
Gestionnaire de positions pour sauvegarder et charger les positions du curseur
"""

import json
import os
import time
from typing import Dict, List, Tuple, Optional
import logging
from .config import SAVE_CONFIG

logger = logging.getLogger(__name__)


class PositionManager:
    """Gestionnaire pour sauvegarder et charger les positions du curseur"""
    
    def __init__(self):
        self.positions_file = SAVE_CONFIG["positions_file"]
        self.max_positions = SAVE_CONFIG["max_saved_positions"]
        self.positions = {}
        self._ensure_data_directory()
        self._load_positions()
    
    def _ensure_data_directory(self):
        """S'assure que le répertoire de données existe"""
        data_dir = os.path.dirname(self.positions_file)
        if data_dir and not os.path.exists(data_dir):
            os.makedirs(data_dir)
            logger.info(f"📁 Répertoire créé: {data_dir}")
    
    def _load_positions(self):
        """Charge les positions sauvegardées depuis le fichier"""
        try:
            if os.path.exists(self.positions_file):
                with open(self.positions_file, 'r', encoding='utf-8') as f:
                    self.positions = json.load(f)
                logger.info(f"📂 Positions chargées depuis: {self.positions_file}")
            else:
                self.positions = {}
                logger.info("📂 Aucun fichier de positions trouvé, création d'un nouveau")
        except Exception as e:
            logger.error(f"❌ Erreur lors du chargement des positions: {e}")
            self.positions = {}
    
    def _save_positions(self):
        """Sauvegarde les positions dans le fichier"""
        try:
            with open(self.positions_file, 'w', encoding='utf-8') as f:
                json.dump(self.positions, f, indent=2, ensure_ascii=False)
            logger.debug(f"💾 Positions sauvegardées dans: {self.positions_file}")
        except Exception as e:
            logger.error(f"❌ Erreur lors de la sauvegarde des positions: {e}")
    
    def save_position(self, name: str, x: int, y: int, url: str = "") -> bool:
        """Sauvegarde une position avec un nom"""
        try:
            # Vérifier si le nom existe déjà
            if name in self.positions:
                logger.warning(f"⚠️ Position '{name}' existe déjà, remplacement...")
            
            # Créer l'entrée de position
            position_data = {
                "x": x,
                "y": y,
                "url": url,
                "timestamp": time.time(),
                "date": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            self.positions[name] = position_data
            
            # Limiter le nombre de positions sauvegardées
            if len(self.positions) > self.max_positions:
                # Supprimer la plus ancienne
                oldest_key = min(self.positions.keys(), 
                               key=lambda k: self.positions[k]["timestamp"])
                del self.positions[oldest_key]
                logger.info(f"🗑️ Position la plus ancienne supprimée: {oldest_key}")
            
            self._save_positions()
            logger.info(f"💾 Position '{name}' sauvegardée: ({x}, {y})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la sauvegarde de la position: {e}")
            return False
    
    def load_position(self, name: str) -> Optional[Tuple[int, int, str]]:
        """Charge une position par son nom"""
        try:
            if name not in self.positions:
                logger.warning(f"⚠️ Position '{name}' non trouvée")
                return None
            
            position_data = self.positions[name]
            x = position_data["x"]
            y = position_data["y"]
            url = position_data.get("url", "")
            
            logger.info(f"📂 Position '{name}' chargée: ({x}, {y})")
            return (x, y, url)
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du chargement de la position: {e}")
            return None
    
    def get_all_positions(self) -> Dict[str, dict]:
        """Retourne toutes les positions sauvegardées"""
        return self.positions.copy()
    
    def list_positions(self) -> List[str]:
        """Retourne la liste des noms de positions disponibles"""
        return list(self.positions.keys())
    
    def delete_position(self, name: str) -> bool:
        """Supprime une position"""
        try:
            if name not in self.positions:
                logger.warning(f"⚠️ Position '{name}' non trouvée pour suppression")
                return False
            
            del self.positions[name]
            self._save_positions()
            logger.info(f"🗑️ Position '{name}' supprimée")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la suppression de la position: {e}")
            return False
    
    def clear_all_positions(self) -> bool:
        """Supprime toutes les positions"""
        try:
            self.positions.clear()
            self._save_positions()
            logger.info("🗑️ Toutes les positions supprimées")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la suppression de toutes les positions: {e}")
            return False
    
    def get_position_info(self, name: str) -> Optional[dict]:
        """Retourne les informations détaillées d'une position"""
        if name not in self.positions:
            return None
        
        position_data = self.positions[name]
        return {
            "name": name,
            "x": position_data["x"],
            "y": position_data["y"],
            "url": position_data.get("url", ""),
            "timestamp": position_data["timestamp"],
            "date": position_data["date"]
        }
    
    def search_positions(self, query: str) -> List[str]:
        """Recherche des positions par nom"""
        query_lower = query.lower()
        matching_positions = []
        
        for name in self.positions.keys():
            if query_lower in name.lower():
                matching_positions.append(name)
        
        return matching_positions
    
    def get_recent_positions(self, limit: int = 5) -> List[str]:
        """Retourne les positions les plus récentes"""
        sorted_positions = sorted(
            self.positions.items(),
            key=lambda x: x[1]["timestamp"],
            reverse=True
        )
        
        return [name for name, _ in sorted_positions[:limit]]
    
    def export_positions(self, filename: str) -> bool:
        """Exporte les positions vers un fichier JSON"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.positions, f, indent=2, ensure_ascii=False)
            logger.info(f"📤 Positions exportées vers: {filename}")
            return True
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'export des positions: {e}")
            return False
    
    def import_positions(self, filename: str) -> bool:
        """Importe les positions depuis un fichier JSON"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                imported_positions = json.load(f)
            
            # Fusionner avec les positions existantes
            for name, data in imported_positions.items():
                if name not in self.positions:
                    self.positions[name] = data
            
            self._save_positions()
            logger.info(f"📥 Positions importées depuis: {filename}")
            return True
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'import des positions: {e}")
            return False 