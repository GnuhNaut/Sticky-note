import json
import os
from typing import List, Dict, Any

class Storage:
    _instance = None
    FILE_PATH = "notes.json"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Storage, cls).__new__(cls)
            cls._instance._ensure_file_exists()
        return cls._instance

    def _ensure_file_exists(self):
        if not os.path.exists(self.FILE_PATH):
            with open(self.FILE_PATH, 'w', encoding='utf-8') as f:
                json.dump([], f)

    def load_notes(self) -> List[Dict[str, Any]]:
        try:
            with open(self.FILE_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def save_all(self, notes_data: List[Dict[str, Any]]):
        """
        Save all notes to the file.
        notes_data: List of dictionaries representing note states.
        """
        with open(self.FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(notes_data, f, indent=4)

    def add_note(self, note_data: Dict[str, Any]):
        notes = self.load_notes()
        notes.append(note_data)
        self.save_all(notes)

    def update_note(self, note_id: str, note_data: Dict[str, Any]):
        notes = self.load_notes()
        for i, note in enumerate(notes):
            if note.get('id') == note_id:
                notes[i] = note_data
                break
        self.save_all(notes)

    def delete_note(self, note_id: str):
        notes = self.load_notes()
        notes = [n for n in notes if n.get('id') != note_id]
        self.save_all(notes)
