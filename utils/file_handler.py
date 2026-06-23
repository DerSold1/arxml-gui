"""Utility functions for file handling"""

import json
import csv
from typing import Dict, List, Any, Optional
from pathlib import Path
import pickle


class FileHandler:
    """Handles file operations for projects and exports"""

    @staticmethod
    def save_json(data: Dict[str, Any], filepath: str) -> bool:
        """Save data as JSON file"""
        try:
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving JSON: {e}")
            return False

    @staticmethod
    def load_json(filepath: str) -> Optional[Dict[str, Any]]:
        """Load data from JSON file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading JSON: {e}")
            return None

    @staticmethod
    def save_csv(data: List[Dict[str, Any]], filepath: str, fieldnames: List[str] = None) -> bool:
        """Save data as CSV file"""
        try:
            if not data:
                return False

            if fieldnames is None:
                fieldnames = list(data[0].keys())

            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            return True
        except Exception as e:
            print(f"Error saving CSV: {e}")
            return False

    @staticmethod
    def load_csv(filepath: str) -> Optional[List[Dict[str, Any]]]:
        """Load data from CSV file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                return list(reader)
        except Exception as e:
            print(f"Error loading CSV: {e}")
            return None

    @staticmethod
    def save_pickle(data: Any, filepath: str) -> bool:
        """Save data as pickle file"""
        try:
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'wb') as f:
                pickle.dump(data, f)
            return True
        except Exception as e:
            print(f"Error saving pickle: {e}")
            return False

    @staticmethod
    def load_pickle(filepath: str) -> Optional[Any]:
        """Load data from pickle file"""
        try:
            with open(filepath, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            print(f"Error loading pickle: {e}")
            return None

    @staticmethod
    def file_exists(filepath: str) -> bool:
        """Check if file exists"""
        return Path(filepath).exists()

    @staticmethod
    def delete_file(filepath: str) -> bool:
        """Delete file"""
        try:
            Path(filepath).unlink()
            return True
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False

    @staticmethod
    def get_file_size(filepath: str) -> int:
        """Get file size in bytes"""
        try:
            return Path(filepath).stat().st_size
        except Exception:
            return 0

    @staticmethod
    def list_files(directory: str, extension: str = None) -> List[str]:
        """List files in directory"""
        try:
            path = Path(directory)
            if extension:
                return [str(f) for f in path.glob(f"*{extension}")]
            return [str(f) for f in path.glob("*")]
        except Exception as e:
            print(f"Error listing files: {e}")
            return []
