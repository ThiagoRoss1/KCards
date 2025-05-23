import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from customtkinter import *
from tkinter import ttk, messagebox
import time

# Progress Bar

class ProgressBar:
    def __init__(self, root, total_questions):                  # Ajeitar o toggle e ProgressBar para o customtkinter
        self.root = root
        self.total_questions = total_questions
        self.current_question = 0

        # Progress Bar Frame

        self.progress_frame = ctk.CTkFrame(self.root)
        self.progress_frame.pack(fill=ctk.X, pady=10)

        # Progress Bar

        self.bar = ctk.CTkProgressBar(
            self.progress_frame,
            orientation="horizontal",
            width=300,
            mode="determinate"
        )
        self.bar.set(0)  # Start at 0 progress
        self.bar.pack(fill=ctk.X, expand=True)

        # Progress text

        self.percent_label = ctk.CTkLabel(
            self.progress_frame,
            text=f"{self.current_question} of {self.total_questions}"
        )
        self.percent_label.pack()


        # Progress Bar Increment

    def increment(self):
        self.current_question += 1
        self.update_display()

    def update_display(self):
        self.bar['value'] = self.current_question
        self.percent_label.configure(
            text=f"{self.current_question} of {self.total_questions}"
        )

    def reset(self, new_total=None):
        if new_total:
            self.total_questions = new_total
        self.current_question = 0
        self.bar['value'] = 0
        self.bar['maximum'] = self.total_questions
        self.update_display()


# Toggle Switch




#
#
#
#             ############################ Ajustar Spinbox e ToggleSwitch para o CustomTkinter #############################################
#                                               ScrollBar no Select a Module
#
#
##






















class ToggleSwitch(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.state = tk.BooleanVar(value=False)

        self.canvas = tk.Canvas(self, width=60, height=30, bg="white", highlightthickness=0)
        self.canvas.pack()
        
        self.bg = self.canvas.create_rectangle(0, 0, 60, 30, fill="#e0e0e0", outline="")
        self.button = self.canvas.create_oval(2, 2, 28, 28, fill="white", outline="#aaaaaa")

        self.canvas.tag_bind(self.button, "<Button-1>", self.toggle)
        self.canvas.tag_bind(self.bg, "<Button-1>", self.toggle)
        self.update_appearence()


    def toggle(self, event=None):
        self.state.set(not self.state.get())
        self.animate()

    def animate(self):
        current_pos = self.canvas.coords(self.button)[0]
        target = 32 if self.state.get() else 2
        distance = abs(target - current_pos)

        if distance > 0:
            step = 3
            direction = 1 if target > current_pos else -1
            self.canvas.move(self.button, step * direction, 0)
            self.after(10, self.animate)
        else:
            self.update_appearence()

    def update_appearence(self):
        if self.state.get():
            self.canvas.coords(self.button, 32, 2, 58, 28)
            self.canvas.itemconfigure(self.bg, fill="#4285F4")
        else:
            self.canvas.coords(self.button, 2, 2, 28, 28)
            self.canvas.itemconfigure(self.bg, fill="#e0e0e0")


class SessionTimer:
    def __init__(self):
        self.start_time = None
        self.elapsed_time = 0
        self.is_running = False

    def start(self):
        if not self.is_running:
            self.start_time = time.time()
            self.is_running = True

    def pause(self):
        if self.is_running:
            self.elapsed_time += time.time() - self.start_time
            self.start_time = None
            self.is_running = False
    
    def get_elapsed_time(self):
        if self.start_time is not None:
            return self.elapsed_time + (time.time() - self.start_time)
        return self.elapsed_time
    
    def format_time(self, seconds):
        minutes, seconds = divmod(int(seconds), 60)
        return f"{minutes:02}:{seconds:02}"
    
    def should_display(self, settings):
        return self.is_running and settings.get('timer_enabled', False)
    


class GetMistakes:
    def __init__(self, root, history):
        self.root = root
        self.history = history
        self.mistakes = []
        self._process_history()

    def _process_history(self):
        unique_words = set()
        for item in self.history:
            if not item.get('correct', False):          
                word_id = item['word']['Hangul']
                if word_id not in unique_words:
                    unique_words.add(word_id)
                    self.mistakes.append(item['word'])

    def get_mistakes(self):
        return self.mistakes.copy()
    

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

        hframe = ctk.CTkFrame(self.cframe)
        hframe.pack(fill=ctk.X, pady=(0, 20))


        tlabel = ctk.CTkLabel(
            hframe,
            text="Customize Your Study Session",
            font=("Arial", 16, "bold")
        )
        tlabel.pack(anchor="nw", pady=10)

        minfo = f"Module {self.vocabulary[0]['Module']} - {self.vocabulary[0]['Level']}"

        mlabel = ctk.CTkLabel(
            self.cframe,
            text=minfo,
            font=("Arial", 10)
        )
        mlabel.pack(anchor="nw")

        separator = ctk.CTkLabel(master=self.cframe, text="───────────────────────────────────────────────", text_color="gray50")
        separator.pack(anchor="w", pady=10)

    def create_word_count_selector(self):

        if self.root.session_settings.get('selected_mode') != "matching":

            wframe = ctk.CTkFrame(self.cframe)
            wframe.pack(fill=ctk.X, pady=10)

            wlabel = ctk.CTkLabel(
                wframe,
                text="Words Number:",
                font=("Arial", 12)
            )
            wlabel.pack(anchor="nw", side=ctk.LEFT, padx=5)

            # Spinbox

            min_words = min(4, len(self.vocabulary))
            default_value = max(min(10, len(self.vocabulary)), min_words)

            self.spinbox = ttk.Spinbox(                  
                wframe,
                from_=min_words,
                to=len(self.vocabulary),
                width=5,
                command=self.update_slider
            )
            self.spinbox.pack(anchor="nw", pady=5, side=ctk.LEFT)
            self.spinbox.bind("<KeyRelease>", self.sync_widgets)

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
            tframe = ctk.CTkFrame(self.cframe)
            tframe.pack(fill=ctk.X, pady=10)

            tlabel = ctk.CTkLabel(
                tframe,
                text="Answer With:",
                font=("Arial", 12)
            )
            tlabel.pack(anchor="nw", side=ctk.LEFT, padx=5)

            from project import language_manager_flashcards
            directions = [
                (f"Hangul to {language_manager_flashcards.get_language()}", "hangul_to_lang"),
                (f"{language_manager_flashcards.get_language()} to Hangul", "lang_to_hangul")
            ]

            for text, value in directions:
                ctk.CTkRadioButton(
                    tframe,
                    text=text,
                    variable=self.settings['study_direction'],
                    value=value
                ).pack(anchor="nw", padx=10, side=ctk.LEFT)

    def create_feedback_switch(self):

        if self.root.session_settings.get('selected_mode') == "multiple_choice" or self.root.session_settings.get('selected_mode') == "true_or_false":
            sframe = ctk.CTkFrame(self.cframe)
            sframe.pack(fill=ctk.X, pady=10)

            slabel = ctk.CTkLabel(
                sframe,
                text="Auto Correction:",
                font=("Arial", 12)
            )
            slabel.pack(anchor="nw", side=ctk.LEFT, padx=5)

            self.feedback_switch = ToggleSwitch(sframe)
            self.feedback_switch.pack(anchor="nw", pady=5)
            self.settings['realtime_feedback'] = self.feedback_switch.state

    def create_timer_button(self):
        tframe = ctk.CTkFrame(self.cframe)
        tframe.pack(fill=ctk.X, pady=10)

        from utilities import SessionTimer

        tlabel = ctk.CTkLabel(
            tframe,
            text="Timer",
            font=("Arial", 12)
        )
        tlabel.pack(anchor="nw", side=ctk.LEFT, padx=5)

        self.timer_switch = ToggleSwitch(tframe)
        self.timer_switch.pack(anchor="nw", pady=5)

    def create_difficulty_selector_button(self):
        dframe = ctk.CTkFrame(self.cframe)
        dframe.pack(fill=ctk.X, pady=10)

        dlabel = ctk.CTkLabel(
            dframe,
            text="Difficulty Selector:",
            font=("Arial", 12)
        )
        dlabel.pack(anchor="nw", side=ctk.LEFT, padx=5)

        self.difficulty_var = ctk.StringVar(value="All")

        for level in ["All", "Easy", "Medium", "Hard"]:
            ctk.CTkRadioButton(
                dframe,
                text=level,
                variable=self.difficulty_var,
                value=level
            ).pack(anchor="nw", padx=10, side=ctk.LEFT)
        
    def create_start_button(self):
        bframe = ctk.CTkFrame(self.cframe)
        bframe.pack(fill=ctk.X, pady=10)

        sbutton = ctk.CTkButton(
            bframe,
            text="Start",
            command=self.start_session,
            width=20
        )
        sbutton.pack(pady=10, ipady=10)

    def create_back_button(self):
        bframe = ctk.CTkFrame(self.cframe)
        bframe.pack(fill=ctk.X, pady=10)
        
        from routes import return_to_choose_study_mode
        bbutton = ctk.CTkButton(
            bframe,
            text="Back",
            width=10,
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
            'timer_enabled': self.timer_switch.state.get(),
            'difficulty': self.difficulty_var.get(),
            'selected_mode': self.root.session_settings['selected_mode']
        }

        if hasattr(self, 'feedback_switch'):
            settings['show_styles'] = self.feedback_switch.state.get()
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
        