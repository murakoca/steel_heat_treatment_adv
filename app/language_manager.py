"""Dil Yönetimi Sınıfı"""
import json, os
from PyQt5.QtCore import QObject, pyqtSignal

class LanguageManager(QObject):
    language_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        base = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base, "..", "database", "translations.json")
        with open(path, encoding='utf-8') as f:
            self.translations = json.load(f)
        self._current_lang = "tr"

    @property
    def current_lang(self):
        return self._current_lang

    def set_language(self, lang):
        if lang in ("tr", "en"):
            self._current_lang = lang
            self.language_changed.emit(lang)

    def tr(self, key, default=""):
        return self.translations.get(key, {}).get(self._current_lang, default or key)

    def toggle(self):
        self.set_language("en" if self._current_lang == "tr" else "tr")