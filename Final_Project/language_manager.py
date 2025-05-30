import customtkinter as ctk
from customtkinter import *
import os 
from typing import Dict, List
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
            self.translations = InterfaceTranslator()

    def set_language(self, language):
        if language in self.languages:
            self.current_language = language

    def get_language(self):
        return self.current_language
    
    def get_language_lower(self):
        return self.translations.get_translation(self.current_language.lower())
    
    def get_translations(self, word):
        if self.current_language == "English":
            return word.get('English', '')
        elif self.current_language == "Portuguese":
            return word.get('Portuguese', '')
        return word.get('English', '')
    
#@singleton -> Could be used instead of __new__ and cls.
class InterfaceTranslator:
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
            self.interface_translation = self._load_interface_translations()
            self.observers = []

    def add_observer(self, callback):
        self.observers.append(callback)
    
    def remove_observer(self, callback):
        if callback in self.observers:
            self.observers.remove(callback)

    def _load_interface_translations(self) -> Dict[str, Dict[str, str]]:
        translations = {}
        try:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            file_path = os.path.join(dir_path, "interface_translations.csv")

            with open(file_path, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    key = row['Key']
                    translations[key] = {
                        'English': row['English'],
                        'Portuguese': row['Portuguese']
                    }
        except FileNotFoundError:
            translations = self._get_default_translations()

        return translations
    
    def get_difficulty_translation(self, difficulty_level):
        translations = {
            "Easy": {"English": "Easy", "Portuguese": "Fácil"},
            "Medium": {"English": "Medium", "Portuguese": "Médio"},
            "Hard": {"English": "Hard", "Portuguese": "Difícil"},
            "All": {"English": "All", "Portuguese": "Todas"}
        }
        return translations.get(difficulty_level, {}).get(self.current_language, difficulty_level)
    
    def get_true_false_ua_translation(self, user_answer):
        translation = {
            "True": {"English": "True", "Portuguese": "Verdadeiro"},
            "False": {"English": "False", "Portuguese": "Falso"}
        }
        return translation.get(user_answer, {}).get(self.current_language, user_answer)

    def get_true_false_ca_translation(self, correct_answer):
        translation = {
            "True": {"English": "True", "Portuguese": "Verdadeiro"},
            "False": {"English": "False", "Portuguese": "Falso"}
        }
        return translation.get(correct_answer, {}).get(self.current_language, correct_answer)
    
    
    # def _get_default_translations(self) -> Dict[str, Dict[str, str]]:
    #     return {
    #         'main_menu_title': {
    #             'English': 'Korean Flashcards App',
    #             'Portuguese': 'Aplicativo de Flashcards Coreano'
    #         },
    #         'select_level': {
    #             'English': 'Select a Level',
    #             'Portuguese': 'Selecione um Nível'
    #         },

    #         # ADICIONAR MAIS DEPOIS
    #     }
    
    def set_language(self, language: str):
        if language in self.languages:
            self.current_language = language
            self.notify_observers()
    
    def notify_observers(self):
        for callback in self.observers:
            callback()
    
    def get_language(self) -> str:
        return self.current_language
    
    def get_translation(self, key: str) -> str:
        return self.interface_translation.get(key, {}).get(self.current_language, key)
    
    def get_translations(self, word: Dict[str, str]) -> str:
        if self.current_language == "English":
            return word.get('English', '')
        elif self.current_language == "Portuguese":
            return word.get('Portuguese', '')
        return word.get('English', '')
    


class T_CTkLabel(ctk.CTkLabel):
    def __init__(self, master, text, **kwargs):
        super().__init__(master, **kwargs)
        self.text = text
        self.translator = InterfaceTranslator()
        self.translator.add_observer(self.update_text)
        self.update_text()
    
    def update_text(self):
        self.configure(text=self.translator.get_translation(self.text))

    def destroy(self):
        self.translator.remove_observer(self.update_text)
        super().destroy()
    



