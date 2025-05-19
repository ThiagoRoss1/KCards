import tkinter as tk
from tkinter import ttk, messagebox
import csv


class LanguageManager:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.__init__()
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self.current_language = "English"
            self.languages = ["English", "Portuguese"]
            self._initialized = True

    def set_language(self, language):
        if language in self.languages:
            self.current_language = language

    def get_language(self):
        return self.current_language
    
    def get_translations(self, word):
        if self.current_language == "English":
            return word.get('English', '')
        elif self.current_language == "Portuguese":
            return word.get('Portuguese', '')
        return word.get('English', '')
