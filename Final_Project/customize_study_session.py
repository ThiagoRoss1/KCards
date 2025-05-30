import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from customtkinter import *
from tkinter import ttk, messagebox
from utilities import *
from language_manager import InterfaceTranslator, T_CTkLabel
import time

interface_translator = InterfaceTranslator()


# Customize Study Session

class CustomizeStudySession:
    from language_manager import LanguageManager
    def __init__(self, root, vocabulary, initial_settings=None):
        self.root = root
        self.vocabulary = vocabulary
        self.settings = {
            'word_count': 10,
            'realtime_feedback': ctk.BooleanVar(value=False),
            'study_direction': ctk.StringVar(value="hangul_to_lang"),
            'timer_enabled': ctk.BooleanVar(value=False),
            'difficulty': ctk.StringVar(value="All")
        }

        if initial_settings:
            self._apply_initial_settings(initial_settings)


        self.create_widgets()

    def _apply_initial_settings(self, settings):

        if 'word_count' in settings:
            self.settings['word_count'] = settings['word_count']

        if 'study_direction' in settings:
            self.settings['study_direction'].set(settings.get('study_direction', "hangul_to_lang"))

        if 'realtime_feedback' in settings:
            self.settings['realtime_feedback'].set(settings.get('realtime_feedback', False))

        if 'timer_enabled' in settings:
            self.settings['timer_enabled'].set(settings.get('timer_enabled', False))

        if 'difficulty' in settings:
            self.settings['difficulty'].set(settings.get('difficulty', "All"))

    def create_widgets(self):

        for widget in self.root.winfo_children():
            widget.pack_forget()


        # Gui Frame

        self.cframe = ctk.CTkFrame(self.root)
        self.cframe.pack(fill=ctk.BOTH, expand=True)

        # Header

        self.create_header()

        # Study Configs

        self.create_word_count_selector()
        self.create_feedback_switch()
        self.create_direction_selector()
        self.create_timer_button()
        self.create_difficulty_selector_button()


        self.create_start_button()
        self.create_back_button()


    def create_header(self):

        hframe = ctk.CTkFrame(self.cframe, fg_color="transparent")
        hframe.pack(fill=ctk.X, pady=(0, 20))


        tlabel = ctk.CTkLabel(
            hframe,
            text=interface_translator.get_translation("customize_study_session"),
            font=("Arial", 22, "bold")
        )
        tlabel.pack(anchor="center", padx=(20, 20), pady=(20, 5))

        minfo = f"{interface_translator.get_translation("module")} {self.vocabulary[0]['Module']} - {self.vocabulary[0]['Level']}"

        # mlabel_frame = ctk.CTkFrame(
        #     self.cframe,
        #     fg_color="transparent",
        #     border_width=1,
        #     border_color="gray70",
        #     corner_radius=20
        # )
        # mlabel_frame.pack(anchor="w", pady=(10, 10))
        
        mlabel = ctk.CTkLabel(
            self.cframe,
            text=minfo,
            font=("Arial", 14, "bold"),
            anchor="w"
        )
        mlabel.pack(anchor="w", padx=(5, 0), pady=(20, 0))

        separator = ctk.CTkLabel(master=self.cframe, text="───────────────────────────────────────────────", text_color="gray50")
        separator.pack(anchor="w", pady=(0, 10))

    def create_word_count_selector(self):

        if self.root.session_settings.get('selected_mode') != "matching":

            wframe = ctk.CTkFrame(self.cframe, fg_color="transparent", border_width=2, border_color="#3e3e3e", corner_radius=10)
            wframe.pack(fill=ctk.X, pady=10)

            wlabel = T_CTkLabel(
                wframe,
                text="words_number",
                font=("Arial", 15, "bold")
            )
            wlabel.pack(anchor="nw", side=ctk.LEFT, padx=5, pady=(5, 5))

            # Spinbox
            
            style = ttk.Style()
            style.theme_use('clam')

            fg_color = "white"
            bg_color = "#2b2b2b"
            border_color = "#3e3e3e"
            button_color = "#1f6aa5"  
            hover_color = "#144870"

            style.configure(
                'Custom.TSpinbox',
                foreground=fg_color,
                background=bg_color,
                bordercolor=border_color,
                lightcolor=bg_color,
                darkcolor=bg_color,
                arrowsize=14,
                padding=8,
                relief='flat',
                arrowcolor=fg_color,
                insertcolor=fg_color,
                fieldbackground=bg_color,
                selectbackground=button_color,
                selectforeground=fg_color,
                font=('Arial', 10),
                borderwidth=10,
                border=10
            )
            
            def remove_focus(event):
                self.root.focus_set()

            style.map(
                'Custom.TSpinbox',
                background=[('active', bg_color), ('!disabled', bg_color)],
                bordercolor=[
                    ('focus', button_color),
                    ('!focus', border_color),
                    ('hover', hover_color)
                ],
                lightcolor=[('focus', button_color), ('!focus', bg_color)],
                darkcolor=[('focus', button_color), ('!focus', bg_color)],
                arrowcolor=[('pressed', hover_color), ('!pressed', fg_color)]
            )

            min_words = min(5, len(self.vocabulary))
            default_value = max(min(10, len(self.vocabulary)), min_words)

            self.spinbox = ttk.Spinbox(                  
                wframe,
                from_=min_words,
                to=len(self.vocabulary),
                width=5,
                command=self.update_slider
            )
            self.spinbox.pack(anchor="nw", pady=8, padx=(2, 2), side=ctk.LEFT)
            self.spinbox.bind("<KeyRelease>", self.sync_widgets)
            self.spinbox.bind("<Return>", remove_focus)
            self.spinbox.bind("<FocusOut>", remove_focus)
            self.spinbox.bind("<<Increment>>", remove_focus)
            self.spinbox.bind("<<Decrement>>", remove_focus)

            # Slider

            self.slider = ctk.CTkSlider(
                wframe,
                from_=min_words,
                to=len(self.vocabulary),
                orientation=ctk.HORIZONTAL,
                command=self.update_spinbox
            )
            self.slider.pack(side=ctk.LEFT, fill=ctk.X, expand=True, padx=5)

            # Valores Iniciais
            
            self.spinbox.set(default_value)
            self.slider.set(default_value)

    def create_direction_selector(self):

        if self.root.session_settings.get('selected_mode') != "matching":
            tframe = ctk.CTkFrame(self.cframe, fg_color="transparent", border_width=2, border_color="#3e3e3e", corner_radius=10)
            tframe.pack(fill=ctk.X, pady=25)

            tlabel = T_CTkLabel(
                tframe,
                text="answer_with",
                font=("Arial", 15, "bold")
            )
            tlabel.pack(anchor="nw", side=ctk.LEFT, padx=5, pady=4)

            from project import language_manager_flashcards
            directions = [
                (f"{interface_translator.get_translation("hangul_to")} {language_manager_flashcards.get_language_lower()}", "hangul_to_lang"),
                (f"{language_manager_flashcards.get_language_lower()} {interface_translator.get_translation("lang_to")}", "lang_to_hangul")
            ]

            for text, value in directions:
                ctk.CTkRadioButton(
                    tframe,
                    text=text,
                    variable=self.settings['study_direction'],
                    value=value
                ).pack(anchor="nw", padx=(10, 20), pady=(7, 7), side=ctk.LEFT)

            if self.root.session_settings.get('selected_mode') == "input":
                info = ctk.CTkButton(
                    tframe,
                    text="i",
                    command=lambda: messagebox.showinfo("Info", f"{interface_translator.get_translation("info_hangul_entry")} \n {interface_translator.get_translation("n_info")}"),
                    width=20,
                    height=20,
                    corner_radius=20,
                    border_width=0,
                )
                info.pack(anchor="nw", padx=(5, 10),pady=(7, 7), side=ctk.LEFT)

    def create_feedback_switch(self):

        if self.root.session_settings.get('selected_mode') == "multiple_choice" or self.root.session_settings.get('selected_mode') == "true_or_false":
            sframe = ctk.CTkFrame(self.cframe, fg_color="transparent", border_width=2, border_color="#3e3e3e", corner_radius=10)
            sframe.pack(fill=ctk.X, pady=(25, 10))

            slabel = T_CTkLabel(
                sframe,
                text="auto_correction",
                font=("Arial", 15, "bold")
            )
            slabel.pack(anchor="nw", side=ctk.LEFT, padx=(6, 10), pady=4)

            self.feedback_switch = ctk.CTkSwitch(
                sframe,
                text="",
                variable=self.settings['realtime_feedback']
            )
            self.feedback_switch.pack(anchor="nw", pady=(7, 7), side=ctk.LEFT)

    def create_timer_button(self):
        tframe = ctk.CTkFrame(self.cframe, fg_color="transparent", border_width=2, border_color="#3e3e3e", corner_radius=10)
        tframe.pack(fill=ctk.X, pady=(15, 10))

        from utilities import SessionTimer

        tlabel = T_CTkLabel(
            tframe,
            text="timer",
            font=("Arial", 15, "bold")
        )
        tlabel.pack(anchor="nw", side=ctk.LEFT, padx=5, pady=4)

        self.timer_switch = ctk.CTkSwitch(
            tframe,
            text="",
            variable=self.settings['timer_enabled']
        )
        self.timer_switch.pack(anchor="nw", pady=(7, 7))

    def create_difficulty_selector_button(self):
        dframe = ctk.CTkFrame(self.cframe, fg_color="transparent", border_width=2, border_color="#3e3e3e", corner_radius=10)
        dframe.pack(fill=ctk.X, pady=25)

        dlabel = T_CTkLabel(
            dframe,
            text="difficulty_selector",
            font=("Arial", 15, "bold")
        )
        dlabel.pack(anchor="nw", side=ctk.LEFT, padx=5, pady=4)

        self.difficulty_var = ctk.StringVar(value="All")

        for level in ["All", "Easy", "Medium", "Hard"]:
            ctk.CTkRadioButton(
                dframe,
                text=interface_translator.get_difficulty_translation(level),
                variable=self.difficulty_var,
                value=level
            ).pack(anchor="nw", padx=(4, 0), pady=(7, 7), side=ctk.LEFT)
        
    def create_start_button(self):
        bframe = ctk.CTkFrame(self.cframe, fg_color="transparent")
        bframe.pack(fill=ctk.X, pady=(25, 0))

        sbutton = ctk.CTkButton(
            bframe,
            text=interface_translator.get_translation("start"),
            command=self.start_session,
            width=120,
            height=40,
            corner_radius=8,
            border_width=2,
            border_color="#ffffff",
            fg_color="#2CC985",
            hover_color="#207A4C",
            text_color="white"
        )
        sbutton.pack(pady=10, ipady=10)

    def create_back_button(self):
        bframe = ctk.CTkFrame(self.cframe, fg_color="transparent")
        bframe.pack(fill=ctk.X, pady=(10, 10))
        
        from routes import return_to_choose_study_mode
        bbutton = ctk.CTkButton(
            bframe,
            text=interface_translator.get_translation("back"),
            width=120,
            height=40,
            corner_radius=8,
            border_width=2,
            border_color="#ffffff",
            fg_color="#363636",
            hover_color="#242424",
            text_color="white",
            command=lambda: return_to_choose_study_mode(self.root, self.cframe, selected_module=self.vocabulary[0]['Module'])
        )
        bbutton.pack(anchor="s", pady=5, ipady=5)

    def start_session(self):
        from project import start_study_session, language_manager_flashcards
        from all_flashcards import StandardFlashcards, InputPractice, MultipleChoiceGame, MatchingGame, TrueFalseGame

        settings = {
            'word_count': int(self.spinbox.get()) if self.root.session_settings.get('selected_mode') != "matching" else None,
            'study_direction': self.settings['study_direction'].get(),
            'realtime_feedback': self.settings['realtime_feedback'].get(),
            'timer_enabled': self.timer_switch.get(),
            'difficulty': self.difficulty_var.get(),
            'selected_mode': self.root.session_settings['selected_mode']
        }

        if hasattr(self, 'feedback_switch'):
            settings['show_styles'] = self.feedback_switch.get()
        else:
            settings['show_styles'] = False

        if hasattr(self.root, 'session_timer'):
            del self.root.session_timer

        if settings['timer_enabled']:
            from utilities import SessionTimer
            self.root.session_timer = SessionTimer()
            self.root.session_timer.start()

        words = self.vocabulary[:settings['word_count']]

        if settings['difficulty'] != "All":
            words = [word for word in words if word['Difficulty'] == settings['difficulty']]

        if not words:
            messagebox.showinfo("No words available", "Please select a different difficulty level.")
            return

        from project import language_manager_flashcards
        processed_words = []
        for word in words:
            new_word = word.copy()
            if settings['study_direction'] == "hangul_to_lang":
                new_word['Question'] = word['Hangul']
                new_word['Answer'] = language_manager_flashcards.get_translations(word).lower()
            else:
                new_word['Question'] = language_manager_flashcards.get_translations(word)
                new_word['Answer'] = word['Hangul'].lower()
            processed_words.append(new_word)
        
        self.cframe.pack_forget()

        if self.root.session_settings['selected_mode'] == "standard":
            StandardFlashcards(self.root, processed_words, settings)
        elif self.root.session_settings['selected_mode'] == "input":
            InputPractice(self.root, processed_words, settings)
        elif self.root.session_settings['selected_mode'] == "multiple_choice":
            MultipleChoiceGame(self.root, processed_words, settings)
        elif self.root.session_settings['selected_mode'] == "matching":
            MatchingGame(self.root, processed_words, settings)
        elif self.root.session_settings['selected_mode'] == "true_or_false":
            TrueFalseGame(self.root, processed_words, settings)


    
    def update_slider(self):
        try:
            value = int(self.spinbox.get())
            if 1 <= value <= len(self.vocabulary):
                self.slider.set(value)
        except ValueError:
            pass

    def update_spinbox(self, value):
        try:
            int_value = int(float(value))
            self.spinbox.set(int_value)
        except ValueError:
            pass

    def sync_widgets(self, event=None):
        try:
            value = int(self.spinbox.get())
            if 1 <= value <= len(self.vocabulary):
                self.slider.set(value)
        except ValueError:
            pass
        