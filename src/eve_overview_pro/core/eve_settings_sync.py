"""
EVE Settings Synchronization
Copies EVE Online client settings between characters
"""
import logging
import shutil
import json
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class EVECharacterSettings:
    """EVE character settings location"""
    character_name: str
    settings_dir: Path
    core_char_file: Path
    core_user_file: Path
    has_settings: bool = False


class EVESettingsSync:
    """Manages EVE Online settings synchronization"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Common EVE installation paths
        self.eve_paths = [
            Path.home() / '.eve' / 'wineenv' / 'drive_c' / 'users' / 'crossover' / 
            'Local Settings' / 'Application Data' / 'CCP' / 'EVE',
            
            Path.home() / '.wine' / 'drive_c' / 'users' / Path.home().name / 
            'Local Settings' / 'Application Data' / 'CCP' / 'EVE',
            
            Path.home() / 'EVE' / 'settings',
            Path.home() / '.local' / 'share' / 'CCP' / 'EVE',
        ]
        
        self.custom_paths = []
        self.character_settings = {}
        
    def add_custom_path(self, path: Path):
        """Add custom EVE settings path"""
        if path.exists() and path.is_dir():
            self.custom_paths.append(path)
            self.logger.info(f"Added custom EVE path: {path}")
    
    def scan_for_characters(self) -> List[EVECharacterSettings]:
        """Scan for EVE character settings
        
        Returns:
            List of found character settings
        """
        found_characters = []
        all_paths = self.eve_paths + self.custom_paths
        
        for base_path in all_paths:
            if not base_path.exists():
                continue
            
            self.logger.info(f"Scanning EVE path: {base_path}")
            
            # Look for character directories
            # EVE structure: /EVE/<tranquility|serenity>/settings_<CharacterName>_<ID>/
            try:
                for server_dir in base_path.iterdir():
                    if not server_dir.is_dir():
                        continue
                    
                    for settings_dir in server_dir.iterdir():
                        if settings_dir.is_dir() and settings_dir.name.startswith('settings_'):
                            char_settings = self._parse_character_settings(settings_dir)
                            if char_settings:
                                found_characters.append(char_settings)
                                self.character_settings[char_settings.character_name] = char_settings
            except Exception as e:
                self.logger.error(f"Error scanning {base_path}: {e}")
        
        self.logger.info(f"Found {len(found_characters)} character settings")
        return found_characters
    
    def _parse_character_settings(self, settings_dir: Path) -> Optional[EVECharacterSettings]:
        """Parse character settings directory
        
        Args:
            settings_dir: Settings directory path
            
        Returns:
            EVECharacterSettings if valid, None otherwise
        """
        try:
            # Extract character name from directory
            # Format: settings_CharacterName_12345678
            dir_name = settings_dir.name
            if '_' in dir_name:
                parts = dir_name.split('_')
                if len(parts) >= 2:
                    char_name = parts[1]
                else:
                    char_name = "Unknown"
            else:
                char_name = dir_name
            
            # Look for core files
            core_char = settings_dir / 'core_char_12345.dat'  # Placeholder
            core_user = settings_dir / 'core_user_12345.dat'
            
            # Find actual core files
            core_files = list(settings_dir.glob('core_*.dat'))
            
            has_settings = len(core_files) > 0
            
            char_settings = EVECharacterSettings(
                character_name=char_name,
                settings_dir=settings_dir,
                core_char_file=core_files[0] if core_files else core_char,
                core_user_file=core_files[1] if len(core_files) > 1 else core_user,
                has_settings=has_settings
            )
            
            return char_settings
            
        except Exception as e:
            self.logger.error(f"Error parsing settings dir {settings_dir}: {e}")
            return None
    
    def sync_settings(self, source_char: str, target_chars: List[str],
                     backup: bool = True) -> Dict[str, bool]:
        """Synchronize settings from source to target characters
        
        Args:
            source_char: Source character name
            target_chars: List of target character names
            backup: Create backups before overwriting
            
        Returns:
            Dict mapping target character names to success status
        """
        results = {}
        
        if source_char not in self.character_settings:
            self.logger.error(f"Source character '{source_char}' not found")
            return results
        
        source = self.character_settings[source_char]
        
        if not source.has_settings:
            self.logger.error(f"Source character '{source_char}' has no settings")
            return results
        
        for target_char in target_chars:
            if target_char not in self.character_settings:
                self.logger.warning(f"Target character '{target_char}' not found")
                results[target_char] = False
                continue
            
            target = self.character_settings[target_char]
            
            try:
                # Create backup if requested
                if backup:
                    self._backup_settings(target)
                
                # Copy settings files
                success = self._copy_settings(source, target)
                results[target_char] = success
                
                if success:
                    self.logger.info(f"Synced settings to '{target_char}'")
                else:
                    self.logger.error(f"Failed to sync settings to '{target_char}'")
                    
            except Exception as e:
                self.logger.error(f"Error syncing to '{target_char}': {e}")
                results[target_char] = False
        
        return results
    
    def _backup_settings(self, char_settings: EVECharacterSettings):
        """Create backup of character settings
        
        Args:
            char_settings: Character settings to backup
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = char_settings.settings_dir.parent / f"backup_{char_settings.character_name}_{timestamp}"
        
        try:
            shutil.copytree(char_settings.settings_dir, backup_dir)
            self.logger.info(f"Created backup: {backup_dir}")
        except Exception as e:
            self.logger.error(f"Backup failed: {e}")
            raise
    
    def _copy_settings(self, source: EVECharacterSettings, 
                      target: EVECharacterSettings) -> bool:
        """Copy settings files from source to target
        
        Args:
            source: Source character settings
            target: Target character settings
            
        Returns:
            True if successful
        """
        try:
            source_dir = source.settings_dir
            target_dir = target.settings_dir
            
            # Files to copy
            files_to_copy = [
                'core_char_*.dat',
                'core_user_*.dat',
                'prefs.ini',
                'overview.yaml',
                'shortcuts.yaml',
                'wnd_*.dat',  # Window layouts
                'chat_*.txt',  # Chat settings
            ]
            
            copied_count = 0
            
            for pattern in files_to_copy:
                for source_file in source_dir.glob(pattern):
                    target_file = target_dir / source_file.name
                    
                    try:
                        shutil.copy2(source_file, target_file)
                        copied_count += 1
                    except Exception as e:
                        self.logger.warning(f"Failed to copy {source_file.name}: {e}")
            
            self.logger.info(f"Copied {copied_count} settings files")
            return copied_count > 0
            
        except Exception as e:
            self.logger.error(f"Settings copy error: {e}")
            return False
    
    def get_settings_summary(self, char_name: str) -> Optional[Dict]:
        """Get summary of character's settings
        
        Args:
            char_name: Character name
            
        Returns:
            Dict with settings info, or None if not found
        """
        if char_name not in self.character_settings:
            return None
        
        char_settings = self.character_settings[char_name]
        
        # Count settings files
        settings_files = list(char_settings.settings_dir.glob('*.dat'))
        settings_files += list(char_settings.settings_dir.glob('*.ini'))
        settings_files += list(char_settings.settings_dir.glob('*.yaml'))
        
        return {
            'character': char_name,
            'settings_dir': str(char_settings.settings_dir),
            'has_settings': char_settings.has_settings,
            'total_files': len(settings_files),
            'last_modified': max(
                (f.stat().st_mtime for f in settings_files),
                default=0
            ) if settings_files else 0
        }
    
    def list_available_characters(self) -> List[str]:
        """Get list of characters with available settings
        
        Returns:
            List of character names
        """
        return [name for name, settings in self.character_settings.items() 
                if settings.has_settings]
