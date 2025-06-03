# import tkinter as tk
# from tkinter import ttk, messagebox
import customtkinter as ctk
from customtkinter import *
import csv
import random
from results_screen import ResultsScreen
from language_manager import LanguageManager, InterfaceTranslator
from datetime import datetime
from unicodedata import normalize, combining

translation = InterfaceTranslator()

def normalize_text(text):
    if not text:
        return ""
    
    text = str(text).strip().lower()
    text = normalize('NFKD', text)
    text = ''.join(c for c in text if not combining(c))
    text = ''.join(c for c in text if c.isalnum() or c.isspace() or c in {'ç', 'ñ', '-', "'"})
    return text

# Standard Flashcards Game Mode

class StandardFlashcards:
    def __init__(self, root, words, settings):
        self.root = root
        self.words = self.prepare_words(words.copy(), settings)
        self.settings = settings
        self.used_words = []
        self.current_word = None
        self.correct = 0
        self.incorrect = 0
        self.showing_translation = False
        self.history = []
        self.buttons_locked = False

        self.setup_ui()

        if settings.get('timer_enabled', False):
            from utilities import SessionTimer
            if not hasattr(root, 'session_timer'):
                root.session_timer = SessionTimer()
                root.session_timer.start()
            self.update_timer()

        self.next_word()


    def prepare_words(self, words, settings):
        from project import language_manager_flashcards
        prepared_words = []

        for word in words:
            new_word = word.copy()
            word_hangul = word['Hangul']
            if word.get('Extra') and word.get('Extra') != "-" and word.get('Type') and word.get('Type') != "-":
                word_hangul += f"[{word['Extra']}] ({word['Type']})"
            elif word.get('Type') and word['Type'] != "-":
                word_hangul += f" ({word['Type']})"
            
            elif word.get('Extra') and word.get('Extra') != "-":
                word_hangul += f"[{word['Extra']}]"

            else:
                word_hangul = word['Hangul']


            original_translations = language_manager_flashcards.get_translations(word)
            translations_list = original_translations.split(',')

            if word.get('Type') is not None and word.get('Type').strip() == "조사":
                if (translations_list[0]).startswith("Indica") or (translations_list[0]).startswith("Conecta"):
                    translations = translations_list[0].strip()
                
                elif len(translations_list) > 4:
                    translations = ','.join([t.strip() for t in translations_list[:2]])

                else:
                    translations = language_manager_flashcards.get_translations(word)

            elif word.get('Type') is not None and word.get('Type').strip() == "어미":
                if (translations_list[0]).startswith("Indica") or (translations_list[0]).startswith("Conecta"):
                    translations = translations_list[0].strip()

                elif len(translations_list) > 4:
                    translations = ','.join([t.strip() for t in translations_list[:2]])
                
                else:
                    translations = language_manager_flashcards.get_translations(word)
            
            elif word.get('Type') is not None and word.get('Type').strip() == "구성":
                translations = translations_list[0].strip()

            elif len(translations_list) > 4:
                translations = ','.join([t.strip() for t in translations_list[:2]])
                if word.get('MF') and word.get('MF') != "-":
                    translations += f"({word['MF']})"

            elif language_manager_flashcards.get_language() == "Português" and word.get('MF') and word.get('MF') != "-":
                translations = translations_list[0].strip()
                translations += f"({word['MF']})"
            
            elif language_manager_flashcards.get_language() == "Português" and word.get('ExtraPT') and word.get('ExtraPT') != "-":
                translations = translations_list[0].strip()
                translations += f"({word['ExtraPT']})"

            else:
                translations = language_manager_flashcards.get_translations(word).strip()
                

            if language_manager_flashcards.get_language() != "Português":

                if word.get('Type') is not None and word.get('Type').strip() == "조사":
                    if (translations_list[0]).startswith("Indicates") or (translations_list[0]).startswith("Connects"):
                        translations = translations_list[0].strip()

                    elif len(translations_list) > 4:
                        translations = ','.join([t.strip() for t in translations_list[:2]])

                    else:
                        translations = language_manager_flashcards.get_translations(word)
                
                elif word.get('Type') is not None and word.get('Type').strip() == "어미":
                    if (translations_list[0]).startswith("Indicates") or (translations_list[0]).startswith("Connects"):
                        translations = translations_list[0].strip()
                    elif len(translations_list) > 4:
                        translations = ','.join([t.strip() for t in translations_list[:2]])
                        
                    else:
                        translations = language_manager_flashcards.get_translations(word)
                
                elif word.get('Type') is not None and word.get('Type').strip() == "구성":
                    translations = translations_list[0].strip()

                elif word.get('ExtraENG') and word.get('ExtraENG') != "-":
                    translations = translations_list[0].strip()
                    translations += f" ({word['ExtraENG']})"

                elif len(translations_list) >= 1 and len(translations_list) < 3:
                    translations = ','.join([t.strip() for t in translations_list[:2]])
                    if word.get('ExtraENG') and word.get('ExtraENG') != "-":
                        translations += f" ({word['ExtraENG']})"

                elif len(translations_list) >= 3:
                    translations = ','.join([t.strip() for t in translations_list[:2]])
                    if word.get('ExtraENG') and word.get('ExtraENG') != "-":
                        translations += f" ({word['ExtraENG']})"

                else:
                    translations = language_manager_flashcards.get_translations(word).strip()
                    if word.get('ExtraENG') and word.get('ExtraENG') != "-":
                        translations += f" ({word['ExtraENG']})"     
                    
                    
            if settings['study_direction'] == "hangul_to_lang":
                new_word['Question'] = word_hangul
                new_word['Answer'] = translations
            else:
                new_word['Question'] = translations
                new_word['Answer'] = word_hangul

            prepared_words.append(new_word)
        
        return prepared_words
    

    def setup_ui(self):
        self.frame = ctk.CTkFrame(self.root)
        self.frame.pack(fill=ctk.BOTH, expand=True)

        from utilities import ProgressBar
        self.progress = ProgressBar(self.frame, len(self.words))

        if self.settings.get('timer_enabled', False):
            self.timer_label = ctk.CTkLabel(self.frame, text="00:00")
            self.timer_label.pack(anchor="n")

        card_container = ctk.CTkFrame(
            self.frame,
            fg_color="transparent"
        )
        card_container.pack(expand=True, padx=20, pady=20)

        self.card_frame = ctk.CTkFrame(
            card_container,
            border_width=4,
            width=300,
            height=400,
            border_color=("gray70", "gray30"),
            corner_radius=20,
            fg_color=("white", "gray15")
        )
        self.card_frame.pack_propagate(False)
        self.card_frame.pack(pady=(0, 10))

        # Card Style

        self.card = ctk.CTkLabel(
            self.card_frame,
            font=("Malgun Gothic", 36) if self.settings['study_direction'] == "hangul_to_lang" else ("Arial", 36),
            anchor="center",
            wraplength=280,
            justify="center",
            cursor="hand2",
            text_color=("black", "white")
        )
        self.card.pack(fill=ctk.BOTH, expand=True, padx= 10, pady=10)
        self.card.bind("<Button-1>", self.flip_card)

        # Answer Buttons

        self.answer_buttons = []

        # Error

        self.ebutton = ctk.CTkButton(
            self.frame,
            text="❌",
            width=120,
            height=50,
            corner_radius=20,
            fg_color="transparent",
            text_color="white",
            hover_color="#FF6347",
            border_width=2,
            border_color=("gray70", "gray30"),
            command=lambda: self.check_answer(False)
        )
        self.ebutton.pack(side=ctk.LEFT, padx=(156, 0), pady=(0, 120))

        # Correct

        self.cbutton = ctk.CTkButton(
            self.frame,
            text="✅",
            width=120,
            height=50,
            corner_radius=20,
            fg_color="transparent",
            text_color="white",
            hover_color="#2ecc71",
            border_width=2,
            border_color=("gray70", "gray30"),
            command=lambda: self.check_answer(True)
        )
        self.cbutton.pack(side=ctk.RIGHT, padx=(0, 156), pady=(0, 120))

    def update_timer(self):
        if not hasattr(self, 'timer_label') or not hasattr(self.root, 'session_timer'):
            return

        elapsed_time = self.root.session_timer.get_elapsed_time()
        self.timer_label.configure(text=self.root.session_timer.format_time(elapsed_time))

        if self.settings.get('timer_enabled', False):
            self.root.after(1000, self.update_timer)


    def flip_card(self, event=None):
        if not self.current_word:
            return
        
        if self.showing_translation:
            self.card.configure(
                text=self.current_word['Question'],
                font=("Malgun Gothic", 36) if self.settings['study_direction'] == "hangul_to_lang" else ("Arial", 36)
            )
            self.showing_translation = False
        else:
            self.card.configure(
                text=self.current_word['Answer'],
                font=("Arial", 36) if self.settings['study_direction'] == "hangul_to_lang" else ("Malgun Gothic", 36)
            )
            self.showing_translation = True

    def check_answer(self, selected_answer):
        if self.buttons_locked:
            return
        
        self.buttons_locked = True

        is_correct = (selected_answer == True)

        if is_correct:
            self.correct += 1
            self.progress.increment()
        else:
            self.incorrect += 1
            self.progress.increment()

        self.history.append({
            'word': self.current_word,
            'viewed': True,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'study_direction': self.settings['study_direction'],
            'correct': is_correct,
            'incorrect': not is_correct,
            'expected': self.current_word['Answer'],
            'user_answer': selected_answer,
            'exact_match': False
        })

        if self.settings['show_styles']:
            self.update_button_styles(selected_answer)
        else:
            for btn in self.answer_buttons:
                btn.configure(state=ctk.DISABLED)

        self.root.after(300, self.next_word)
    

    def next_word(self):
        self.buttons_locked = False
        available_words = [word for word in self.words if word not in self.used_words]

        if not available_words:
            self.show_results()
            return
        
        self.current_word = random.choice(available_words)
        self.used_words.append(self.current_word)
        self.showing_translation = False

        self.card.configure(
            text=self.current_word['Question'],
            font=("Malgun Gothic", 36) if self.settings['study_direction'] == "hangul_to_lang" else ("Arial", 36)
        )


    def show_results(self):
        from results_screen import StandardResultsScreen
        from routes import return_to_main_menu

        self.frame.pack_forget()
        StandardResultsScreen(
            self.root,
            self.correct,
            self.incorrect,
            self.history,
            lambda: return_to_main_menu(self.root, self.frame),
            settings=self.settings
        )
        self.used_words = []
        self.progress.reset()


class InputPractice:
    def __init__(self, root, words, settings):
        self.root = root
        self.words = self.prepare_words(words.copy(), settings)
        self.settings = settings
        self.used_words = []
        self.word_history = []
        self.correct = 0
        self.incorrect = 0
        self.current_word = None
        
        self.setup_ui()

        if settings.get('timer_enabled', False):
            from utilities import SessionTimer
            if not hasattr(root, 'session_timer'):
                root.session_timer = SessionTimer()
                root.session_timer.start()
            self.update_timer()


        self.next_word()

    def prepare_words(self, words, settings):
        from project import language_manager_flashcards
        prepared_words = []

        for word in words:
            new_word = word.copy()
            word_hangul = word['Hangul']
            if word.get('Extra') and word.get('Extra') != "-" and word.get('Type') and word.get('Type') != "-":
                word_hangul += f"[{word['Extra']}] ({word['Type']})"
            elif word.get('Type') and word['Type'] != "-":
                word_hangul += f" ({word['Type']})"
            
            elif word.get('Extra') and word.get('Extra') != "-":
                word_hangul += f"[{word['Extra']}]"

            else:
                word_hangul = word['Hangul']


            original_translations = language_manager_flashcards.get_translations(word)
            translations_list = original_translations.split(',')

            if word.get('Type') is not None and word.get('Type').strip() == "조사":
                if (translations_list[0]).startswith("Indica") or (translations_list[0]).startswith("Conecta"):
                    translations = translations_list[0].strip()
                
                elif len(translations_list) > 4:
                    translations = ','.join([t.strip() for t in translations_list[:2]])

                else:
                    translations = language_manager_flashcards.get_translations(word)

            elif word.get('Type') is not None and word.get('Type').strip() == "어미":
                if (translations_list[0]).startswith("Indica") or (translations_list[0]).startswith("Conecta"):
                    translations = translations_list[0].strip()

                elif len(translations_list) > 4:
                    translations = ','.join([t.strip() for t in translations_list[:2]])
                
                else:
                    translations = language_manager_flashcards.get_translations(word)
            
            elif word.get('Type') is not None and word.get('Type').strip() == "구성":
                translations = translations_list[0].strip()

            elif len(translations_list) > 4:
                translations = ','.join([t.strip() for t in translations_list[:2]])
                if word.get('MF') and word.get('MF') != "-":
                    translations += f"({word['MF']})"

            elif language_manager_flashcards.get_language() == "Português" and word.get('MF') and word.get('MF') != "-":
                translations = translations_list[0].strip()
                translations += f"({word['MF']})"
            
            elif language_manager_flashcards.get_language() == "Português" and word.get('ExtraPT') and word.get('ExtraPT') != "-":
                translations = translations_list[0].strip()
                translations += f"({word['ExtraPT']})"

            else:
                translations = language_manager_flashcards.get_translations(word).strip()
        

            if language_manager_flashcards.get_language() != "Português":

                if word.get('Type') is not None and word.get('Type').strip() == "조사":
                    if (translations_list[0]).startswith("Indicates") or (translations_list[0]).startswith("Connects"):
                        translations = translations_list[0].strip()

                    elif len(translations_list) > 4:
                        translations = ','.join([t.strip() for t in translations_list[:2]])

                    else:
                        translations = language_manager_flashcards.get_translations(word)
                
                elif word.get('Type') is not None and word.get('Type').strip() == "어미":
                    if (translations_list[0]).startswith("Indicates") or (translations_list[0]).startswith("Connects"):
                        translations = translations_list[0].strip()
                    elif len(translations_list) > 4:
                        translations = ','.join([t.strip() for t in translations_list[:2]])
                        
                    else:
                        translations = language_manager_flashcards.get_translations(word)
                
                elif word.get('Type') is not None and word.get('Type').strip() == "구성":
                    translations = translations_list[0].strip()

                elif word.get('ExtraENG') and word.get('ExtraENG') != "-":
                    translations = translations_list[0].strip()
                    translations += f" ({word['ExtraENG']})"

                elif len(translations_list) >= 1 and len(translations_list) < 3:
                    translations = ','.join([t.strip() for t in translations_list[:2]])
                    if word.get('ExtraENG') and word.get('ExtraENG') != "-":
                        translations += f" ({word['ExtraENG']})"

                elif len(translations_list) >= 3:
                    translations = ','.join([t.strip() for t in translations_list[:2]])
                    if word.get('ExtraENG') and word.get('ExtraENG') != "-":
                        translations += f" ({word['ExtraENG']})"

                else:
                    translations = language_manager_flashcards.get_translations(word).strip()
                    if word.get('ExtraENG') and word.get('ExtraENG') != "-":
                        translations += f" ({word['ExtraENG']})"     

                
            if settings['study_direction'] == "hangul_to_lang":
                new_word['Question'] = word_hangul
                new_word['Answer'] = language_manager_flashcards.get_translations(word).lower()
            else:
                new_word['Question'] = translations
                new_word['Answer'] = word['Hangul'].lower()

            prepared_words.append(new_word)
        
        return prepared_words

    def setup_ui(self):
        self.frame = ctk.CTkFrame(self.root)
        self.frame.pack(fill=ctk.BOTH, expand=True)

        # Progress Bar
        from utilities import ProgressBar
        self.progress = ProgressBar(self.frame, len(self.words))

        if self.settings.get('timer_enabled', False):
            self.timer_label = ctk.CTkLabel(self.frame, text="00:00")
            self.timer_label.pack(anchor="n")

        # Configured Word Label

        word_container = ctk.CTkFrame(
            self.frame,
            fg_color="transparent"
        )
        word_container.pack(expand=True, anchor="center", padx=20, pady=(20, 10))

        self.word_frame = ctk.CTkFrame(
            word_container,
            border_width=4,
            width=450,
            height=250,
            border_color=("gray70", "gray30"),
            corner_radius=20,
            fg_color=("white", "gray15")
        )
        self.word_frame.pack_propagate(False)
        self.word_frame.pack(anchor="n", pady=(0, 20))

        label_font = ("Malgun Gothic", 52) if self.settings['study_direction'] == "hangul_to_lang" else ("Arial", 52)
        entry_font = ("Malgun Gothic", 26) if self.settings['study_direction'] == "lang_to_hangul" else ("Arial", 26)

        self.word_label = ctk.CTkLabel(
            self.word_frame,
            wraplength=360,
            font=label_font,
            text_color=("black", "white")
        )
        self.word_label.pack(anchor="center", fill=ctk.BOTH, expand=True, padx=10, pady=10)

        entry_container = ctk.CTkFrame(
            self.frame,
            fg_color="transparent"
        )
        entry_container.pack(expand=True, anchor="n", pady=(0, 20))

        self.entry_frame = ctk.CTkFrame(
            entry_container,
            border_width=0,
            width=380,
            height=120,
            corner_radius=20,
            fg_color=("transparent")
        )
        self.entry_frame.pack_propagate(False)
        self.entry_frame.pack(anchor="n")

        self.answer_entry = ctk.CTkEntry(
            self.entry_frame,
            font=entry_font,
            text_color=("white", "black") if ctk.get_appearance_mode() == "dark" else ("black", "white"),
            width=300,
            height=50,
            corner_radius=20,
            border_width=2,
            border_color=("gray70", "gray30"),
            fg_color=("white", "gray15"),
        )
        self.answer_entry.pack(fill=ctk.X, pady=5)
        self._setup_entry_placeholder()

        # Key Bindings
        self.answer_entry.bind("<Return>", lambda _: self.check_answer())

    def update_timer(self):
        if not hasattr(self, 'timer_label') or not hasattr(self.root, 'session_timer'):
            return
        
        elapsed = self.root.session_timer.get_elapsed_time()
        self.timer_label.configure(
            text=self.root.session_timer.format_time(elapsed)
        )

        if self.settings.get('timer_enabled', False):
            self.root.after(1000, self.update_timer)

    def _setup_entry_placeholder(self):
        self.answer_entry.insert(0, f"{translation.get_translation("type_your_answer")}")
        self.answer_entry.configure(text_color="white")
        self.answer_entry.icursor(0)
        self.answer_entry.focus()
        
        self.answer_entry.bind("<Key>", self._handle_entry_key)

    def _handle_entry_key(self, event):
        current_text = self.answer_entry.get()
        if current_text == f"{translation.get_translation("type_your_answer")}":
            self.answer_entry.delete(0, ctk.END)
            self.answer_entry.configure(text_color="#F1F1F1")
        
        if event.keysym == "Return" and current_text == f"{translation.get_translation("type_your_answer")}":
            return "break"

    def check_answer(self):
        user_input = self.answer_entry.get().lower().strip()

        if user_input == translation.get_translation("type_your_answer").lower().strip():
            user_input = ""

        expected = self.current_word['Answer'].lower()

        # user_normalized = normalize_text(user_input)
        # expected_normalized = normalize_text(expected)

        valid_options = [opt.strip() for opt in expected.split(',')]
        # exact_match = user_input.lower().strip() == expected.lower().strip()

        user_normalized = normalize_text(user_input)

        is_correct = any(
            normalize_text(opt) == user_normalized for opt in valid_options
        )

        if is_correct:
            self.correct += 1
        else:
            self.incorrect += 1
            
        self.progress.increment()
        
        self.word_history.append({
            "word": self.current_word,
            "user_answer": user_input,
            "correct": is_correct,
            "expected": valid_options[0],
            "study_direction": self.settings['study_direction'],
            "all_valid": valid_options
        })
        
        self.next_word()

    def next_word(self):
        self.used_words.append(self.current_word)
        
        available_words = [word for word in self.words if word not in self.used_words]
        
        if available_words:
            self.current_word = random.choice(available_words)

            if self.settings['study_direction'] == "hangul_to_lang":
                self.word_label.configure(
                    text=self.current_word['Question'],
                    font=("Malgun Gothic", 52)
                )
            else:
                self.word_label.configure(
                    text=self.current_word['Question'],
                    font=("Arial", 52)
                )

            self.expected_answer = self.current_word['Answer'].lower()
            self._reset_entry()

        else:
            self._end_session()

    def _reset_entry(self):
        self.answer_entry.delete(0, ctk.END)
        self.answer_entry.insert(0, f"{translation.get_translation("type_your_answer")}")
        self.answer_entry.configure(text_color="gray")
        self.answer_entry.icursor(0)

    def _end_session(self):
        self.frame.pack_forget()
        self.progress.reset()
        self.answer_entry.unbind("<Return>")
        from routes import return_to_main_menu
        ResultsScreen(
            self.root,
            self.correct,
            self.incorrect,
            self.word_history,
            lambda: return_to_main_menu(self.root, self.frame)
        )


# Multiple choice Game Mode

class MultipleChoiceGame:
    def __init__(self, root, words, settings):
        self.root = root
        self.words = self.prepare_words(words.copy(), settings)
        self.settings = settings
        self.current_word = None
        self.correct = 0
        self.incorrect = 0
        self.score = 0
        self.used_words = []  
        self.history = []
        self.buttons_locked = False

        self.setup_ui()

        if settings.get('timer_enabled', False):
            from utilities import SessionTimer
            if not hasattr(root, 'session_timer'):
                root.session_timer = SessionTimer()
                root.session_timer.start()
            self.update_timer()

        self.configure_button_styles()

        self.next_question()

    def prepare_words(self, words, settings):
        from project import language_manager_flashcards
        prepared_words = []

        for word in words:
            new_word = word.copy()
            word_hangul = word['Hangul']
            if word.get('Extra') and word.get('Extra') != "-" and word.get('Type') and word.get('Type') != "-":
                word_hangul += f"[{word['Extra']}] ({word['Type']})"
            elif word.get('Type') and word['Type'] != "-":
                word_hangul += f" ({word['Type']})"
            
            elif word.get('Extra') and word.get('Extra') != "-":
                word_hangul += f"[{word['Extra']}]"

            else:
                word_hangul = word['Hangul']


            original_translations = language_manager_flashcards.get_translations(word)
            translations_list = original_translations.split(',')

            if word.get('Type') is not None and word.get('Type').strip() == "조사":
                if (translations_list[0]).startswith("Indica") or (translations_list[0]).startswith("Conecta"):
                    translations = translations_list[0].strip()
                
                elif len(translations_list) > 4:
                    translations = ','.join([t.strip() for t in translations_list[:2]])

                else:
                    translations = language_manager_flashcards.get_translations(word)

            elif word.get('Type') is not None and word.get('Type').strip() == "어미":
                if (translations_list[0]).startswith("Indica") or (translations_list[0]).startswith("Conecta"):
                    translations = translations_list[0].strip()

                elif len(translations_list) > 4:
                    translations = ','.join([t.strip() for t in translations_list[:2]])
                
                else:
                    translations = language_manager_flashcards.get_translations(word)
            
            elif word.get('Type') is not None and word.get('Type').strip() == "구성":
                translations = translations_list[0].strip()

            elif len(translations_list) > 4:
                translations = ','.join([t.strip() for t in translations_list[:2]])
                if word.get('MF') and word.get('MF') != "-":
                    translations += f"({word['MF']})"

            elif language_manager_flashcards.get_language() == "Português" and word.get('MF') and word.get('MF') != "-":
                translations = translations_list[0].strip()
                translations += f"({word['MF']})"
            
            elif language_manager_flashcards.get_language() == "Português" and word.get('ExtraPT') and word.get('ExtraPT') != "-":
                translations = translations_list[0].strip()
                translations += f"({word['ExtraPT']})"

            else:
                translations = language_manager_flashcards.get_translations(word).strip()
                
            
            if language_manager_flashcards.get_language() != "Português":

                if word.get('Type') is not None and word.get('Type').strip() == "조사":
                    if (translations_list[0]).startswith("Indicates") or (translations_list[0]).startswith("Connects"):
                        translations = translations_list[0].strip()

                    elif len(translations_list) > 4:
                        translations = ','.join([t.strip() for t in translations_list[:2]])

                    else:
                        translations = language_manager_flashcards.get_translations(word)
                
                elif word.get('Type') is not None and word.get('Type').strip() == "어미":
                    if (translations_list[0]).startswith("Indicates") or (translations_list[0]).startswith("Connects"):
                        translations = translations_list[0].strip()
                    elif len(translations_list) > 4:
                        translations = ','.join([t.strip() for t in translations_list[:2]])
                        
                    else:
                        translations = language_manager_flashcards.get_translations(word)
                
                elif word.get('Type') is not None and word.get('Type').strip() == "구성":
                    translations = translations_list[0].strip()

                elif word.get('ExtraENG') and word.get('ExtraENG') != "-":
                    translations = translations_list[0].strip()
                    translations += f" ({word['ExtraENG']})"

                elif len(translations_list) >= 1 and len(translations_list) < 3:
                    translations = ','.join([t.strip() for t in translations_list[:2]])
                    if word.get('ExtraENG') and word.get('ExtraENG') != "-":
                        translations += f" ({word['ExtraENG']})"

                elif len(translations_list) >= 3:
                    translations = ','.join([t.strip() for t in translations_list[:2]])
                    if word.get('ExtraENG') and word.get('ExtraENG') != "-":
                        translations += f" ({word['ExtraENG']})"

                else:
                    translations = language_manager_flashcards.get_translations(word).strip()
                    if word.get('ExtraENG') and word.get('ExtraENG') != "-":
                        translations += f" ({word['ExtraENG']})"     


            if settings['study_direction'] == "hangul_to_lang":
                new_word['Question'] = word_hangul
                new_word['Answer'] = translations
            else:
                new_word['Question'] = translations
                new_word['Answer'] = word_hangul

            prepared_words.append(new_word)

        return prepared_words

    def setup_ui(self):
        self.frame = ctk.CTkFrame(self.root)
        self.frame.pack(fill=ctk.BOTH, expand=True)

        from utilities import ProgressBar
        self.progress = ProgressBar(self.frame, len(self.words))

        if self.settings.get('timer_enabled', False):
            self.timer_label = ctk.CTkLabel(self.frame, text="00:00")
            self.timer_label.pack(anchor="n", pady=(0, 10))

        main_container = ctk.CTkFrame(
            self.frame,
            fg_color="transparent"
        )
        main_container.pack(expand=True, fill=ctk.BOTH)

        q_frame = ctk.CTkFrame(
            main_container,
            fg_color="transparent",
            border_width=4,
            border_color=("gray70", "gray30"),
            corner_radius=20
        )
        q_frame.pack(pady=(0, 20))

        self.question_label = ctk.CTkLabel(
            q_frame,
            font=("Malgun Gothic", 40) if self.settings['study_direction'] == "hangul_to_lang" else ("Arial", 40),
            wraplength=500,
            width=400,
            height=200,
            anchor="center",
            text_color="white"
        )
        self.question_label.pack(pady=20, padx=60)

        self.original_button_config = {
        'corner_radius': 8,
        'fg_color': "transparent",
        'text_color': "white",                           
        'hover_color': "#3B8ED0",
        'border_width': 2,
        'border_color': ("gray70", "gray30"),
    }
        
        buttons_frame = ctk.CTkFrame(
            main_container,
            fg_color="transparent"
        )
        buttons_frame.pack(fill=ctk.X, pady=(16, 10))

        # Answer Buttons
        self.answer_buttons = []
        for _ in range(4):
            a_button = ctk.CTkButton(             
                buttons_frame,
                **self.original_button_config,
                width=500,
                height=60,
                font=("Malgun Gothic", 18) if self.settings['study_direction'] == "lang_to_hangul" else ("Arial", 18)
            )
            a_button.pack(pady=(10, 0)) 
            self.answer_buttons.append(a_button)

    def reset_button_styles(self):
        for btn in self.answer_buttons:
            btn.configure(
                **self.original_button_config,
                state=ctk.NORMAL
            )


    def update_timer(self):
        if not hasattr(self, 'timer_label') or not hasattr(self.root, 'session_timer'):
            return
        
        elapsed = self.root.session_timer.get_elapsed_time()
        self.timer_label.configure(
            text=self.root.session_timer.format_time(elapsed)
        )

        if self.settings.get('timer_enabled', False):
            self.root.after(1000, self.update_timer)

    def generate_options(self, correct_answer):
        wrong_answers = [
            word['Answer'] for word in random.sample(
                [word for word in self.words if word['Answer'] != correct_answer],
                min(3, len(self.words) - 1)  
            )
        ]
        options = [correct_answer] + wrong_answers
        random.shuffle(options)
        return options
    
    def next_question(self):
        self.buttons_locked = False
        self.reset_button_styles()

        available_words = [word for word in self.words if word not in self.used_words]

        if not available_words:
            self.show_results()
            return
        

        self.current_word = random.choice(available_words)
        self.used_words.append(self.current_word)

        options = self.generate_options(self.current_word['Answer'])

        self.question_label.configure(text=self.current_word['Question'])

        for button, answer in zip(self.answer_buttons, options):
            button.configure(
                text=answer,
                command=lambda a=answer: self.check_answer(a),
                state=ctk.NORMAL
            )
            
    def check_answer(self, selected_answer):
        if self.buttons_locked:
            return
        
        self.buttons_locked = True
        correct = (selected_answer == self.current_word['Answer'])

        if correct:
            self.correct += 1
            self.score += 1
            self.progress.increment()

        else:
            self.incorrect += 1
            self.progress.increment()

        self.history.append({
            'word': self.current_word,
            'user_answer': selected_answer,
            'correct': correct,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'expected': self.current_word['Answer'],
            'study_direction': self.settings['study_direction']
        })

        if self.settings['show_styles']:
            self.update_button_styles(selected_answer)
        else:
            for btn in self.answer_buttons:
                btn.configure(state=ctk.DISABLED)

        self.root.after(1000, self.next_question)

    def configure_button_styles(self):    
        self.correct_style = {
            'fg_color': "#2ecc71",     
            'hover_color': "#27ae60",   
            'text_color': "white"
        }
        
        self.incorrect_style = {
            'fg_color': "#e74c3c",     
            'hover_color': "#c0392b",   
            'text_color': "white"
        }
        

    def update_button_styles(self, selected_answer):
        correct_answer = self.current_word['Answer']

        for btn in self.answer_buttons:
            btn_text = btn.cget("text")
            btn.configure(state=ctk.DISABLED)

            if btn_text == correct_answer:
                btn.configure(**self.correct_style)

            elif btn_text == selected_answer:
                btn.configure(**self.incorrect_style)
            
    def show_results(self):
        from results_screen import MultipleChoiceResultsScreen
        from routes import return_to_main_menu

        self.frame.pack_forget()
        MultipleChoiceResultsScreen(
            self.root,
            self.correct,
            self.incorrect,
            self.history,
            lambda: return_to_main_menu(self.root, self.frame),
            settings=self.settings
        )
        self.used_words = []
        self.progress.reset()


# Matching Game Mode 

class MatchingGame:
    def __init__(self, root, words, settings):
        self.root = root
        self.words = self.prepare_words(words.copy(), settings)
        self.settings = settings
        self.selected_cards = []
        self.matched_pairs = 0
        self.attempts = 0

        self.card_width = 200
        self.card_height = 160
        self.max_pairs = min(6, len(self.words))

        self.words = self.prepare_words(words, settings)

        self.setup_ui()

        if not hasattr(root, 'session_timer'):
            from utilities import SessionTimer
            root.session_timer = SessionTimer()
            root.session_timer.start()
    
        if settings.get('timer_enabled', False):
            self.update_timer()

        self.root.bind("<Configure>", self.window_resize)

    def prepare_words(self, words, settings):
        from project import language_manager_flashcards
        game_words = random.sample(words, 6)
        settings = settings.copy()
        pairs = []

        for word in game_words:
            word_hangul = word['Hangul']
            if word.get('Extra') and word.get('Extra') != "-" and word.get('Type') and word.get('Type') != "-":
                word_hangul += f"[{word['Extra']}] ({word['Type']})"
            elif word.get('Type') and word['Type'] != "-":
                word_hangul += f" ({word['Type']})"
            
            elif word.get('Extra') and word.get('Extra') != "-":
                word_hangul += f"[{word['Extra']}]"

            else:
                word_hangul = word['Hangul']


            original_translations = language_manager_flashcards.get_translations(word)
            translations_list = original_translations.split(',')

            if word.get('Type') is not None and word.get('Type').strip() == "조사":
                if (translations_list[0]).startswith("Indica") or (translations_list[0]).startswith("Conecta"):
                    translations = translations_list[0].strip()
                
                elif len(translations_list) > 4:
                    translations = ','.join([t.strip() for t in translations_list[:2]])

                else:
                    translations = language_manager_flashcards.get_translations(word)

            elif word.get('Type') is not None and word.get('Type').strip() == "어미":
                if (translations_list[0]).startswith("Indica") or (translations_list[0]).startswith("Conecta"):
                    translations = translations_list[0].strip()

                elif len(translations_list) > 4:
                    translations = ','.join([t.strip() for t in translations_list[:2]])
                
                else:
                    translations = language_manager_flashcards.get_translations(word)
            
            elif word.get('Type') is not None and word.get('Type').strip() == "구성":
                translations = translations_list[0].strip()

            elif len(translations_list) > 4:
                translations = ','.join([t.strip() for t in translations_list[:2]])
                if word.get('MF') and word.get('MF') != "-":
                    translations += f"({word['MF']})"

            elif language_manager_flashcards.get_language() == "Português" and word.get('MF') and word.get('MF') != "-":
                translations = translations_list[0].strip()
                translations += f"({word['MF']})"
            
            elif language_manager_flashcards.get_language() == "Português" and word.get('ExtraPT') and word.get('ExtraPT') != "-":
                translations = translations_list[0].strip()
                translations += f"({word['ExtraPT']})"

            else:
                translations = translations_list[0].strip()
                

            if language_manager_flashcards.get_language() != "Português":

                if word.get('Type') is not None and word.get('Type').strip() == "조사":
                    if (translations_list[0]).startswith("Indicates") or (translations_list[0]).startswith("Connects"):
                        translations = translations_list[0].strip()

                    elif len(translations_list) > 4:
                        translations = ','.join([t.strip() for t in translations_list[:2]])

                    else:
                        translations = language_manager_flashcards.get_translations(word)
                
                elif word.get('Type') is not None and word.get('Type').strip() == "어미":
                    if (translations_list[0]).startswith("Indicates") or (translations_list[0]).startswith("Connects"):
                        translations = translations_list[0].strip()
                    elif len(translations_list) > 4:
                        translations = ','.join([t.strip() for t in translations_list[:2]])
                        
                    else:
                        translations = language_manager_flashcards.get_translations(word)
                
                elif word.get('Type') is not None and word.get('Type').strip() == "구성":
                    translations = translations_list[0].strip()

                elif word.get('ExtraENG') and word.get('ExtraENG') != "-":
                    translations = translations_list[0].strip()
                    translations += f" ({word['ExtraENG']})"

                elif len(translations_list) >= 1 and len(translations_list) < 3:
                    translations = ','.join([t.strip() for t in translations_list[:2]])
                    if word.get('ExtraENG') and word.get('ExtraENG') != "-":
                        translations += f" ({word['ExtraENG']})"

                elif len(translations_list) >= 3:
                    translations = ','.join([t.strip() for t in translations_list[:2]])
                    if word.get('ExtraENG') and word.get('ExtraENG') != "-":
                        translations += f" ({word['ExtraENG']})"

                else:
                    translations = translations_list[0].strip()
                    if word.get('ExtraENG') and word.get('ExtraENG') != "-":
                        translations += f" ({word['ExtraENG']})"     

            pairs.append({
                'type': 'hangul',
                'text': word_hangul,
                'match_id': word['Hangul'],
                'translation': translations,
            })
            pairs.append({
                'type': 'translation',
                'text': translations,
                'match_id': word['Hangul']
            })

        random.shuffle(pairs)
        return pairs
    
    def setup_ui(self):
        self.frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.frame.pack(fill=ctk.BOTH, expand=True)

        from utilities import ProgressBar
        self.progress = ProgressBar(self.frame, self.max_pairs)

        if self.settings.get('timer_enabled', False):
            self.timer_label = ctk.CTkLabel(self.frame, text="00:00")
            self.timer_label.pack(anchor="n")

        container = ctk.CTkFrame(self.frame, fg_color="transparent")
        container.pack(expand=True, fill=ctk.BOTH)

        self.cards_frame = ctk.CTkFrame(container, fg_color="transparent")
        self.cards_frame.pack(expand=True, anchor="center")

        self.setup_grid()

        self.create_cards()

    def setup_grid(self):
        for i in range(3):
            self.cards_frame.grid_rowconfigure(i, weight=1, uniform="row")
        for i in range(4):
            self.cards_frame.grid_columnconfigure(i, weight=1, uniform="col")

    def update_timer(self):
        if not hasattr(self, 'timer_label') or not hasattr(self.root, 'session_timer'):
            return
        
        elapsed = self.root.session_timer.get_elapsed_time()
        self.timer_label.configure(
            text=self.root.session_timer.format_time(elapsed)
        )

        if self.settings.get('timer_enabled', False):
            self.root.after(1000, self.update_timer)

    def create_cards(self):
        # Grid 3x4
        self.cards = []
        self.card_placeholders = []
        card_fg_color = "#2B2B2B"
        card_text_color = "#FFFFFF"
        for i in range(12):
            row, col = divmod(i, 4)

            placeholder = ctk.CTkLabel(
                self.cards_frame,
                text="",
                width=self.card_width,
                height=self.card_height,
                fg_color="transparent"
            )
            placeholder.grid(row=row, column=col, padx=5, pady=5)
            self.card_placeholders.append(placeholder)

            original_text = self.words[i]['text']
            max_chars_per_line = 9 if self.words[i]['type'] == 'hangul' else 14 
            text_with_breaks = '\n'.join([original_text[j:j+max_chars_per_line] 
                                    for j in range(0, len(original_text), max_chars_per_line)])

            card = ctk.CTkButton(
                self.cards_frame,
                text=text_with_breaks,
                font=("Malgun Gothic", 16) if self.words[i]['type'] == 'hangul' else ("Arial", 16),
                width=self.card_width,
                height=self.card_height,
                fg_color=card_fg_color,
                text_color=card_text_color,
                border_width=2,
                border_color=("gray70", "gray30"),
                corner_radius=6,
                command=lambda idx=i: self.card_click(idx),
                anchor="center",
            )
            card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            self.cards.append(card)

            card.grid_info()['original_pos'] = (row, col)

    def window_resize(self, event):
        pass

    def card_click(self, card_index):
        if len(self.selected_cards) >= 2:
            return
        
        card = self.cards[card_index]
        
        if any(c[0] == card_index for c in self.selected_cards):
            card.configure(fg_color="#2B2B2B")
            self.selected_cards = [c for c in self.selected_cards if c[0] != card_index]
            return

        card.configure(fg_color="#3B8ED0")
        self.selected_cards.append((card_index, card))

        if len(self.selected_cards) == 2:
            self.attempts += 1
            self.check_match()

    def check_match(self):
        idx1, card1 = self.selected_cards[0]
        idx2, card2 = self.selected_cards[1]
        word1 = self.words[idx1]
        word2 = self.words[idx2]

        if word1['match_id'] == word2['match_id'] and word1['type'] != word2['type']:
            card1.configure(fg_color="#96F97B", hover_color="#96F97B")
            card2.configure(fg_color="#96F97B", hover_color="#96F97B")
            self.matched_pairs += 1
            self.progress.increment()
            self.selected_cards = []
            self.root.after(500, lambda: self.remove_cards(card1, card2))

            if self.matched_pairs == self.max_pairs:
                self.root.after(500, lambda: self.end_game())
        
        else:
            card1.configure(fg_color="#FF6347", hover_color="#FF6347")
            card2.configure(fg_color="#FF6347", hover_color="#FF6347")
            self.root.after(500, self.reset_cards)

    def remove_cards(self, card1, card2):
        idx1 = self.cards.index(card1)
        idx2 = self.cards.index(card2)

        card1.grid_remove()
        card2.grid_remove()

        from PIL import Image

        self.card_placeholders[idx1].configure(text="✔", text_color="gray70")
        self.card_placeholders[idx2].configure(text="✔", text_color="gray70")

    def reset_cards(self):
        for idx, card in self.selected_cards:
            card.configure(fg_color="#2B2B2B")
        self.selected_cards = []

    def end_game(self):
        from results_screen import MatchingResultsScreen
        from routes import return_to_main_menu

        unique_words = []
        words_ids = set()

        for word_data in self.words:
            if word_data['match_id'] not in words_ids:
                words_ids.add(word_data['match_id'])

                original_word = next(
                    (w for w in self.root.session_settings['words']
                     if w['Hangul'] == word_data['match_id']),
                     None
                )
                if original_word:
                    unique_words.append(original_word)

        history = [{
            'mode': 'matching',
            'attempts': self.attempts,
            'pairs': self.max_pairs,
            'accuracy': self.max_pairs / self.attempts if self.attempts > 0 else 0,
            'words_list': unique_words
        }]

        self.frame.pack_forget()

        MatchingResultsScreen(
            root=self.root,
            pairs=self.max_pairs,
            attempts=self.attempts,
            correct=self.matched_pairs,
            incorrect=self.attempts - self.matched_pairs,
            w_history=history,
            accuracy=self.matched_pairs / self.attempts if self.attempts > 0 else 0.0,
            return_callback=lambda: return_to_main_menu(self.root, self.frame),
            settings=self.settings
        )
        
        
# True or False Game Mode 

class TrueFalseGame:
    def __init__(self, root, words, settings):
        self.root = root
        self.words = self.prepare_words(words.copy(), settings)
        self.settings = settings
        self.current_word = None
        self.correct = 0
        self.incorrect = 0
        self.score = 0
        self.used_words = []
        self.history = []
        self.buttons_locked = False


        self.setup_ui()

        if not hasattr(root, 'session_timer'):
            from utilities import SessionTimer
            root.session_timer = SessionTimer()
            root.session_timer.start()
    
        if settings.get('timer_enabled', False):
            self.update_timer()

        self.next_question()


    def prepare_words(self, words, settings):
        from project import language_manager_flashcards
        prepared_words = []

        for word in words:
            new_word = word.copy()
            word_hangul = word['Hangul']
            if word.get('Extra') and word.get('Extra') != "-" and word.get('Type') and word.get('Type') != "-":
                word_hangul += f"[{word['Extra']}] ({word['Type']})"
            elif word.get('Type') and word['Type'] != "-":
                word_hangul += f" ({word['Type']})"
            
            elif word.get('Extra') and word.get('Extra') != "-":
                word_hangul += f"[{word['Extra']}]"

            else:
                word_hangul = word['Hangul']


            original_translations = language_manager_flashcards.get_translations(word)
            translations_list = original_translations.split(',')

            if word.get('Type') is not None and word.get('Type').strip() == "조사":
                if (translations_list[0]).startswith("Indica") or (translations_list[0]).startswith("Conecta"):
                    translations = translations_list[0].strip()
                
                elif len(translations_list) > 4:
                    translations = ','.join([t.strip() for t in translations_list[:2]])

                else:
                    translations = language_manager_flashcards.get_translations(word)

            elif word.get('Type') is not None and word.get('Type').strip() == "어미":
                if (translations_list[0]).startswith("Indica") or (translations_list[0]).startswith("Conecta"):
                    translations = translations_list[0].strip()

                elif len(translations_list) > 4:
                    translations = ','.join([t.strip() for t in translations_list[:2]])
                
                else:
                    translations = language_manager_flashcards.get_translations(word)
            
            elif word.get('Type') is not None and word.get('Type').strip() == "구성":
                translations = translations_list[0].strip()

            elif len(translations_list) > 4:
                translations = ','.join([t.strip() for t in translations_list[:2]])
                if word.get('MF') and word.get('MF') != "-":
                    translations += f"({word['MF']})"

            elif language_manager_flashcards.get_language() == "Português" and word.get('MF') and word.get('MF') != "-":
                translations = translations_list[0].strip()
                translations += f"({word['MF']})"
            
            elif language_manager_flashcards.get_language() == "Português" and word.get('ExtraPT') and word.get('ExtraPT') != "-":
                translations = translations_list[0].strip()
                translations += f"({word['ExtraPT']})"

            else:
                translations = language_manager_flashcards.get_translations(word).strip()
                
            if language_manager_flashcards.get_language() != "Português":

                if word.get('Type') is not None and word.get('Type').strip() == "조사":
                    if (translations_list[0]).startswith("Indicates") or (translations_list[0]).startswith("Connects"):
                        translations = translations_list[0].strip()

                    elif len(translations_list) > 4:
                        translations = ','.join([t.strip() for t in translations_list[:2]])

                    else:
                        translations = language_manager_flashcards.get_translations(word)
                
                elif word.get('Type') is not None and word.get('Type').strip() == "어미":
                    if (translations_list[0]).startswith("Indicates") or (translations_list[0]).startswith("Connects"):
                        translations = translations_list[0].strip()
                    elif len(translations_list) > 4:
                        translations = ','.join([t.strip() for t in translations_list[:2]])
                        
                    else:
                        translations = language_manager_flashcards.get_translations(word)
                
                elif word.get('Type') is not None and word.get('Type').strip() == "구성":
                    translations = translations_list[0].strip()

                elif word.get('ExtraENG') and word.get('ExtraENG') != "-":
                    translations = translations_list[0].strip()
                    translations += f" ({word['ExtraENG']})"

                elif len(translations_list) >= 1 and len(translations_list) < 3:
                    translations = ','.join([t.strip() for t in translations_list[:2]])
                    if word.get('ExtraENG') and word.get('ExtraENG') != "-":
                        translations += f" ({word['ExtraENG']})"

                elif len(translations_list) >= 3:
                    translations = ','.join([t.strip() for t in translations_list[:2]])
                    if word.get('ExtraENG') and word.get('ExtraENG') != "-":
                        translations += f" ({word['ExtraENG']})"

                else:
                    translations = language_manager_flashcards.get_translations(word).strip()
                    if word.get('ExtraENG') and word.get('ExtraENG') != "-":
                        translations += f" ({word['ExtraENG']})"     

            
            if settings['study_direction'] == "hangul_to_lang":
                new_word['Question'] = word_hangul
                new_word['Answer'] = translations
            else:
                new_word['Question'] = word_hangul
                new_word['Answer'] = translations

            prepared_words.append(new_word)
        
        return prepared_words
    
    def setup_ui(self):
        self.frame = ctk.CTkFrame(self.root)
        self.frame.pack(fill=ctk.BOTH, expand=True)

        from utilities import ProgressBar
        self.progress = ProgressBar(self.frame, len(self.words))

        if self.settings.get('timer_enabled', False):
            self.timer_label = ctk.CTkLabel(self.frame, text="00:00")
            self.timer_label.pack(anchor="n")

        qs_container = ctk.CTkFrame(
            self.frame,
            fg_color="transparent"
        )
        qs_container.pack(expand=True, anchor="center", padx=20, pady=(10, 0))

        qs_frame = ctk.CTkFrame(
            qs_container,
            fg_color="transparent",
            border_width=4,
            width=300,
            height=200,
            border_color=("gray70", "gray30"),
            corner_radius=20,
        )
        qs_frame.pack(expand=True, anchor="center", padx=20, pady=(10, 0))

        content_frame = ctk.CTkFrame(
            qs_frame,
            fg_color="transparent"
        )
        content_frame.pack(expand=True, anchor="center", padx=10, pady=10)

        self.question_label = ctk.CTkLabel(
            content_frame,
            font=("Malgun Gothic", 45) if self.settings['study_direction'] == "hangul_to_lang" else ("Arial", 45),
            fg_color="transparent",
            text_color="white",
            width=500,
            height=20,
            wraplength=500
        )
        self.question_label.pack(pady=10)

        self.elabel = ctk.CTkLabel(
            content_frame,
            text="=",
            font=("Arial", 30),
            fg_color="transparent",
            text_color="white",
            width=50,
            height=20,
            wraplength=200
        )
        self.elabel.pack(pady=20)

        self.statement_label = ctk.CTkLabel(
            content_frame,
            font=("Malgun Gothic", 45) if self.settings['study_direction'] == "lang_to_hangul" else ("Arial", 45),
            fg_color="transparent",
            text_color="white",
            width=500,
            height=50,
            wraplength=500
        )
        self.statement_label.pack(pady=10)

        # Answer Buttons

        buttons_container = ctk.CTkFrame(
            self.frame,
            fg_color="transparent",
        )
        buttons_container.pack(expand=True, anchor="center", padx=20, pady=(0, 20))

        buttons_frame = ctk.CTkFrame(buttons_container)
        buttons_frame.pack(pady=0)

        self.answer_buttons = []
        self.true_button = ctk.CTkButton(
            buttons_frame,
            text=translation.get_translation("true"),
            fg_color="transparent",
            text_color="white",
            hover_color="#3B8ED0",
            border_width=2,
            border_color=("gray70", "gray30"),
            corner_radius=20,
            width=250,
            height=50,
            command=lambda: self.check_answer("True")
        )
        self.true_button.pack(side=ctk.LEFT, padx=10)

        self.false_button = ctk.CTkButton(
            buttons_frame,
            text=translation.get_translation("false"),
            fg_color="transparent",
            text_color="white",
            hover_color="#3B8ED0",
            border_width=2,
            border_color=("gray70", "gray30"),
            corner_radius=20,
            width=250,
            height=50,
            command=lambda: self.check_answer("False")
        )
        self.false_button.pack(side=ctk.LEFT, padx=10)
        self.answer_buttons.append(self.true_button)
        self.answer_buttons.append(self.false_button)

    def update_timer(self):
        if not hasattr(self, 'timer_label') or not hasattr(self.root, 'session_timer'):
            return
        
        elapsed = self.root.session_timer.get_elapsed_time()
        self.timer_label.configure(
            text=self.root.session_timer.format_time(elapsed)
        )

        if self.settings.get('timer_enabled', False):
            self.root.after(1000, self.update_timer)
            

    def next_question(self):
        self.buttons_locked = False
        self.reset_button_styles()

        available_words = [word for word in self.words if word not in self.used_words]

        if not available_words:
            self.show_results()
            return
        

        self.current_word = random.choice(available_words)
        self.used_words.append(self.current_word)

        self.current_statement_is_true = random.choice([True, False])

        if self.current_statement_is_true:
            statement_text = f"{self.current_word['Answer']}"
        else:
            wrong_answer = random.choice([
                word['Answer'] for word in self.words if word['Answer'] != self.current_word['Answer']
            ])
            statement_text = f"{wrong_answer}"

        self.question_label.configure(text=self.current_word['Question'])
        self.elabel.configure(text=self.elabel.cget("text"))
        self.statement_label.configure(text=statement_text)

        for btn in self.answer_buttons:
            btn.configure(state=ctk.NORMAL)


    def reset_button_styles(self):
        for btn in self.answer_buttons:
            btn.configure(
                fg_color="transparent",
                text_color="white",
                hover_color="#3B8ED0",
                border_width=2,
                border_color=("gray70", "gray30"),
            )

    def check_answer(self, selected_answer):
        if self.buttons_locked:
            return
        
        self.buttons_locked = True
        
        is_correct = (selected_answer == str(self.current_statement_is_true))

        if is_correct:
            self.correct += 1
            self.score += 1
            self.progress.increment()
        else:
            self.incorrect += 1
            self.progress.increment()
        
        self.history.append({
            'word': self.current_word,
            'user_answer': selected_answer,
            'correct': is_correct,
            'statement_question': self.statement_label.cget("text"),
            'correct_answer': str(self.current_statement_is_true),
            'question_word': self.current_word['Question'],
            'is_true': self.current_statement_is_true,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })
    
        
        if self.settings['show_styles']:
            self.update_button_styles(selected_answer)
        else:
            for btn in self.answer_buttons:
                btn.configure(state=ctk.DISABLED)

        self.root.after(1000, self.next_question)

    def update_button_styles(self, selected_answer):
        self.correct_style = {
            'fg_color': "#2ecc71",     
            'hover_color': "#27ae60",   
            'text_color': "white"
        }
        
        self.incorrect_style = {
            'fg_color': "#e74c3c",     
            'hover_color': "#c0392b",   
            'text_color': "white"
        }

        for btn in self.answer_buttons:
            btn_text = btn.cget("text")
            is_correct_button = (btn_text == "True" and self.current_statement_is_true) or \
                               (btn_text == "False" and not self.current_statement_is_true)

            btn.configure(state=ctk.DISABLED)

            if selected_answer == str(self.current_statement_is_true):
                if is_correct_button:
                    btn.configure(**self.correct_style)

            else:
                if is_correct_button:
                    btn.configure(**self.correct_style)
                elif btn_text == selected_answer:
                    btn.configure(**self.incorrect_style)

    def show_results(self):
        from results_screen import TrueFalseResultsScreen
        from routes import return_to_main_menu

        self.frame.pack_forget()

        TrueFalseResultsScreen(
            root=self.root,
            correct=self.correct,
            incorrect=self.incorrect,
            w_history=self.history,
            return_callback=lambda: return_to_main_menu(self.root, self.frame),
            settings=self.settings
        )
        self.used_words = []
        self.progress.reset()

