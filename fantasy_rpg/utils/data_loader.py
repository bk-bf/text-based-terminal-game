"""Base class for loading JSON data files with consistent path resolution and caching."""

import json
from pathlib import Path
from typing import Dict, Any, Optional


class DataLoader:
    """Base class for all JSON data loaders.
    
    Provides centralized data directory discovery and JSON loading with caching.
    Eliminates duplicate path-finding code across ItemLoader, ClassLoader, RaceLoader, etc.
    """
    
    def __init__(self, data_dir: Optional[Path] = None):
        """Initialize with optional data directory path.
        
        Args:
            data_dir: Optional path to data directory. If None, will search for it.
        """
        self.data_dir = self._find_data_dir(data_dir)
        self._cache: Dict[str, Any] = {}
    
    @staticmethod
    def _find_data_dir(data_dir: Optional[Path] = None) -> Path:
        """Find the data directory using multiple search strategies.
        
        Search order:
        1. Provided data_dir parameter
        2. Parent directory's data folder (fantasy_rpg/data)
        3. Current directory's data folder (core/data)
        4. Relative path from working directory (fantasy_rpg/data)
        
        Args:
            data_dir: Optional explicit path to data directory
            
        Returns:
            Path to data directory (may not exist yet)
        """
        if data_dir is not None:
            return Path(data_dir) if not isinstance(data_dir, Path) else data_dir
        
        current_dir = Path(__file__).parent
        candidates = [
            current_dir.parent / "data",      # fantasy_rpg/data (most common)
            current_dir / "data",             # utils/data (unlikely)
            Path("fantasy_rpg/data")          # Relative to working directory
        ]
        
        for candidate in candidates:
            if candidate.exists():
                return candidate
        
        # Fallback - use first candidate even if it doesn't exist yet
        return candidates[0]
    
    def load_json(self, filename: str, cache_key: Optional[str] = None) -> Dict[str, Any]:
        """Load and cache JSON data from file.
        
        Args:
            filename: Name of JSON file to load (e.g., "items.json")
            cache_key: Optional cache key. Defaults to filename if not provided.
                      Use different keys if loading same file with different processing.
        
        Returns:
            Dictionary containing parsed JSON data
            
        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If file contains invalid JSON
        """
        cache_key = cache_key or filename
        
        if cache_key not in self._cache:
            file_path = self.data_dir / filename
            
            if not file_path.exists():
                raise FileNotFoundError(f"Data file not found: {file_path}")
            
            with open(file_path, 'r') as f:
                self._cache[cache_key] = json.load(f)
        
        return self._cache[cache_key]
    
    def clear_cache(self, cache_key: Optional[str] = None):
        """Clear cached data.
        
        Args:
            cache_key: Optional specific cache key to clear. If None, clears entire cache.
        """
        if cache_key is None:
            self._cache.clear()
        elif cache_key in self._cache:
            del self._cache[cache_key]
