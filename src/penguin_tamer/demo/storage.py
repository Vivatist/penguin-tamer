"""
Storage layer for demo sessions.

Handles all file I/O operations, path resolution, and serialization.
Follows Repository Pattern - abstracts data persistence.
"""

import json
from pathlib import Path
from typing import List, Optional
from platformdirs import user_config_dir

from .models import DemoSession


class DemoStorage:
    """
    Repository for demo session persistence.

    Encapsulates all file operations and path management.
    Can be easily replaced with different storage implementations
    (e.g., database, cloud storage) thanks to abstraction.
    """

    def __init__(self, app_name: str = "penguin-tamer"):
        """
        Initialize storage with application name.

        Args:
            app_name: Application name for config directory
        """
        self.app_name = app_name
        self._config_dir: Optional[Path] = None

    @property
    def config_dir(self) -> Path:
        """Get configuration directory, creating it if needed."""
        if self._config_dir is None:
            self._config_dir = Path(user_config_dir(self.app_name))
            self._config_dir.mkdir(parents=True, exist_ok=True)
        return self._config_dir

    def resolve_path(self, demo_file: str) -> Path:
        """
        Resolve demo file path.

        If path is absolute, use as-is.
        If relative, resolve relative to config directory.

        Args:
            demo_file: File path (absolute or relative)

        Returns:
            Resolved absolute path
        """
        demo_path = Path(demo_file)

        if demo_path.is_absolute():
            return demo_path

        return self.config_dir / demo_file

    def get_unique_path(self, filepath: Path | str) -> Path:
        """
        Get unique file path by adding sequence number if needed.

        Args:
            filepath: Desired file path (Path or string)

        Returns:
            Unique file path (may have _1, _2, etc. appended)
        """
        filepath = Path(filepath) if isinstance(filepath, str) else filepath

        if not filepath.exists():
            return filepath

        stem = filepath.stem
        suffix = filepath.suffix
        parent = filepath.parent

        counter = 1
        while counter <= 10000:
            new_path = parent / f"{stem}_{counter}{suffix}"
            if not new_path.exists():
                return new_path
            counter += 1

        # Fallback: use timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return parent / f"{stem}_{timestamp}{suffix}"

    def save_session(self, session: DemoSession, filepath: str,
                     auto_sequence: bool = True) -> Path:
        """
        Save demo session to file.

        Args:
            session: Session to save
            filepath: Target file path
            auto_sequence: If True, add sequence number to avoid overwrite

        Returns:
            Actual path where file was saved

        Raises:
            IOError: If file cannot be written
        """
        resolved_path = self.resolve_path(filepath)

        if auto_sequence:
            resolved_path = self.get_unique_path(resolved_path)

        # Ensure parent directory exists
        resolved_path.parent.mkdir(parents=True, exist_ok=True)

        # Serialize and save
        data = session.to_list()

        with open(resolved_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return resolved_path

    def load_session(self, filepath: str) -> DemoSession:
        """
        Load demo session from file.

        Args:
            filepath: Path to session file

        Returns:
            Loaded session

        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If file is not valid JSON
        """
        resolved_path = self.resolve_path(filepath)

        if not resolved_path.exists():
            raise FileNotFoundError(f"Demo file not found: {resolved_path}")

        with open(resolved_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return DemoSession.from_list(data)

    def list_sessions(self, directory: Optional[str] = None) -> List[str]:
        """
        List all available demo session files.

        Args:
            directory: Directory to search (default: config_dir/demo_sessions)

        Returns:
            List of session file paths as strings
        """
        if directory:
            search_dir = self.resolve_path(directory)
        else:
            search_dir = self.config_dir / "demo_sessions"

        if not search_dir.exists():
            return []

        return [str(p) for p in search_dir.glob("*.json")]

    def delete_session(self, filepath: str) -> bool:
        """
        Delete a demo session file.

        Args:
            filepath: Path to session file

        Returns:
            True if deleted, False if file didn't exist
        """
        resolved_path = self.resolve_path(filepath)

        if not resolved_path.exists():
            return False

        resolved_path.unlink()
        return True
