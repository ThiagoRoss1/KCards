import tkinter as tk
from tkinter import ttk, messagebox
import time

# Progress Bar

class ProgressBar:
    def __init__(self, root, total_questions):
        self.root = root
        self.total_questions = total_questions
        self.current_question = 0

        # Progress Bar Frame

        self.progress_frame = ttk.Frame(self.root, padding=20)
        self.progress_frame.pack(fill=tk.X, pady=10)
        
        # Progress Bar

        self.bar = ttk.Progressbar(
            self.progress_frame,
            orient="horizontal",
            length=300,
            mode="determinate",
            maximum=self.total_questions
        )
        self.bar.pack(fill=tk.X, expand=True)

        # Progress text

        self.percent_label = ttk.Label(
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
        self.percent_label.config(
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

class ToggleSwitch(ttk.Frame):
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
            self.canvas.itemconfig(self.bg, fill="#4285F4")
        else:
            self.canvas.coords(self.button, 2, 2, 28, 28)
            self.canvas.itemconfig(self.bg, fill="#e0e0e0")


class SessionTimer:
    def __init__(self):
        self.start_time = None
        self.elapsed_time = 0

    def start(self):
        self.start_time = time.time()
    
    def pause(self):
        if self.start_time is not None:
            self.elapsed_time += time.time() - self.start_time
            self.start_time = None
    
    def get_elapsed_time(self):
        if self.start_time is not None:
            return self.elapsed_time + (time.time() - self.start_time)
    
    def format_time(self, seconds):
        minutes, seconds = divmod(int(seconds), 60)
        return f"{minutes:02}:{seconds:02}"















# Customize Study Session

class CustomizeStudySession:
    from language_manager import LanguageManager
    def __init__(self, root, vocabulary):
        self.root = root
        self.vocabulary = vocabulary
        self.settings = {
            'word_count': 10,
            'realtime_feedback': tk.BooleanVar(value=False),
            'study_direction': tk.StringVar(value="hangul_to_lang")
        }
        self.create_widgets()

    def create_widgets(self):

        for widget in self.root.winfo_children():
            widget.pack_forget()


        # Gui Frame

        self.cframe = ttk.Frame(self.root, padding=20)
        self.cframe.pack(fill=tk.BOTH, expand=True)

        # Header

        self.create_header()

        # Study Configs

        self.create_word_count_selector()
        self.create_feedback_switch()
        self.create_direction_selector()
        self.create_timer_button()


        self.create_start_button()
        self.create_back_button()


    def create_header(self):

        hframe = ttk.Frame(self.cframe)
        hframe.pack(fill=tk.X, pady=(0, 20))


        tlabel = ttk.Label(
            hframe,
            text="Customize Your Study Session",
            font=("Arial", 16, "bold")
        )
        tlabel.pack(anchor="nw", pady=10)

        minfo = f"Module {self.vocabulary[0]['Module']} - {self.vocabulary[0]['Level']}"

        mlabel = ttk.Label(
            self.cframe,
            text=minfo,
            font=("Arial", 10)
        )
        mlabel.pack(anchor="nw")

        ttk.Separator(self.cframe).pack(fill=tk.X, pady=10)

    def create_word_count_selector(self):

        wframe = ttk.Frame(self.cframe)
        wframe.pack(fill=tk.X, pady=10)

        wlabel = ttk.Label(
            wframe,
            text="Words Number:",
            font=("Arial", 12)
        )
        wlabel.pack(anchor="nw", side=tk.LEFT, padx=5)

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
        self.spinbox.pack(anchor="nw", pady=5, side=tk.LEFT)
        self.spinbox.bind("<KeyRelease>", self.sync_widgets)

        # Slider

        self.slider = ttk.Scale(
            wframe,
            from_=min_words,
            to=len(self.vocabulary),
            orient=tk.HORIZONTAL,
            command=self.update_spinbox
        )
        self.slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Valores Iniciais
        
        self.spinbox.set(default_value)
        self.slider.set(default_value)

    def create_direction_selector(self):
        tframe = ttk.Frame(self.cframe)
        tframe.pack(fill=tk.X, pady=10)

        tlabel = ttk.Label(
            tframe,
            text="Answer With:",
            font=("Arial", 12)
        )
        tlabel.pack(anchor="nw", side=tk.LEFT, padx=5)

        from project import language_manager_flashcards
        directions = [
            (f"Hangul to {language_manager_flashcards.get_language()}", "hangul_to_lang"),
            (f"{language_manager_flashcards.get_language()} to Hangul", "lang_to_hangul")
        ]

        for text, value in directions:
            ttk.Radiobutton(
                tframe,
                text=text,
                variable=self.settings['study_direction'],
                value=value
            ).pack(anchor="nw", padx=10, side=tk.LEFT)

    def create_feedback_switch(self):
        sframe = ttk.Frame(self.cframe)
        sframe.pack(fill=tk.X, pady=10)

        slabel = ttk.Label(
            sframe,
            text="Auto Correction:",
            font=("Arial", 12)
        )
        slabel.pack(anchor="nw", side=tk.LEFT, padx=5)

        self.feedback_switch = ToggleSwitch(sframe)
        self.feedback_switch.pack(anchor="nw", pady=5)
        self.settings['realtime_feedback'] = self.feedback_switch.state

    def create_timer_button(self):
        tframe = ttk.Frame(self.cframe)
        tframe.pack(fill=tk.X, pady=10)

        from utilities import SessionTimer

        tlabel = ttk.Label(
            tframe,
            text="Timer",
            font=("Arial", 12)
        )
        tlabel.pack(anchor="nw", side=tk.LEFT, padx=5)

        self.timer_switch = ToggleSwitch(tframe)
        self.timer_switch.pack(anchor="nw", pady=5)
        self.timer = SessionTimer()


    def create_start_button(self):
        bframe = ttk.Frame(self.cframe)
        bframe.pack(fill=tk.X, pady=10)

        sbutton = ttk.Button(
            bframe,
            text="Start",
            style="Accent.TButton",
            command=self.start_session,
            width=20
        )
        sbutton.pack(pady=10, ipady=10)

    def create_back_button(self):
        bframe = ttk.Frame(self.cframe)
        bframe.pack(fill=tk.X, pady=10)
        
        from routes import return_to_choose_study_mode
        bbutton = ttk.Button(
            bframe,
            text="Back",
            width=10,
            style="Accent.TButton",
            command=lambda: return_to_choose_study_mode(self.root, self.cframe, selected_module=self.vocabulary[0]['Module'])
        )
        bbutton.pack(anchor="s", pady=5, ipady=5)

    def start_session(self):
        from project import start_study_session, language_manager_flashcards
        from all_flashcards import standard_flashcards, input_practice, MultipleChoiceGame

        settings = {
            'word_count': int(self.spinbox.get()),
            'study_direction': self.settings['study_direction'].get(),
            'realtime_feedback': self.settings['realtime_feedback'].get(),
            'show_styles': self.feedback_switch.state.get()
        }

        words = self.vocabulary[:settings['word_count']]

        for word in words:
            if settings['study_direction'] == "hangul_to_lang":
                word['Question'] = word['Hangul']
                word['Answer'] = language_manager_flashcards.get_translations(word)
            else:
                word['Question'] = language_manager_flashcards.get_translations(word)
                word['Answer'] = word['Hangul']
        
        self.cframe.pack_forget()

        if self.root.session_settings['selected_mode'] == "standard":
            standard_flashcards(self.root, words, settings)
        elif self.root.session_settings['selected_mode'] == "input":
            input_practice(self.root, words, settings)
        elif self.root.session_settings['selected_mode'] == "multiple_choice":
            MultipleChoiceGame(self.root, words, settings)

    
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























        # # Module Label

        # from project import start_session
        # mlabel = ttk.Label(
        #     self.cframe,
        #     text=f"Module {self.vocabulary[0]['Module']} - {self.vocabulary[0]['Level']}",
        #     font=("Arial", 10)
        # )
        # mlabel.pack(anchor="nw")

        # tlabel = ttk.Label(
        #     self.cframe,
        #     text="Configure your study session",
        #     font=("Arial", 16, "bold")
        # )
        # tlabel.pack(anchor="nw", pady=10)

        # plabel = ttk.Label(
        #     self.cframe,
        #     text="Your last grade: ",   # ainda tenho que fazer o sistema de save 
        #     font=("Arial", 12)
        # )
        # plabel.pack(anchor="nw", pady=5)

        # _label = ttk.Label(
        #     self.cframe,
        #     text="------------------------------------------------------------------",
        #     font=("Arial", 12)	
        # )
        # _label.pack(anchor="nw", pady=5, fill=tk.X,)


        # bframe = ttk.Frame(self.cframe)
        # bframe.pack(fill=tk.X, pady=10)

        # # Words Count

        # wlabel = ttk.Label(
        #     bframe,
        #     text="Words Number:",
        #     font=("Arial", 12)
        # )
        # wlabel.pack(anchor="nw", side=tk.LEFT, pady=5)

        # self.spinbox = ttk.Spinbox(
        #     bframe,
        #     from_=1,
        #     to=len(self.vocabulary),
        #     width=5,
        #     command=self._update_slider
        # )
        # self.spinbox.pack(anchor="nw", pady=5)
        # self.spinbox.bind("<KeyRelease>", self._sync_widgets)

        # self.slider = ttk.Scale(
        #     bframe,
        #     from_=1,
        #     to=len(self.vocabulary),
        #     orient=tk.HORIZONTAL,
        #     command=self._update_spinbox
        # )
        # self.slider.pack(side=tk.LEFT, fill="x", pady=5)

        # self.spinbox.set(10)
        # self.slider.set(10)
 
        # # Auto Correction 
        # # Corrects the answer during the study session -- Fazer um if para o standard_flashcards visto que ele ja tem (terá) esse sistema

        # fframe = ttk.Frame(self.cframe)
        # fframe.pack(fill=tk.X, pady=10)

        # flabel = ttk.Label(
        #     fframe,
        #     text="Auto Correction:",
        #     font=("Arial", 12)
        # )
        # flabel.pack(anchor="nw", side=tk.LEFT, pady=5)

        # self.feedback_switch = ToggleSwitch(fframe)
        # self.feedback_switch.pack(anchor="nw", pady=5)

        # self.settings['realtime_feedback'] = self.feedback_switch.state

        # # Answer Choose
        
        # aframe = ttk.Frame(self.cframe)
        # aframe.pack(fill=tk.X, pady=10)

        # alabel = ttk.Label(
        #     aframe,
        #     text="Answer With:",
        #     font=("Arial", 12)
        # )
        # alabel.pack(anchor="nw", side=tk.LEFT, pady=5)


        # from project import language_manager_flashcards
        # ttk.Radiobutton(
        #     aframe,
        #     text=f"Hangul to {language_manager_flashcards.get_language()}",
        #     variable=self.settings['study_direction'],
        #     value="hangul_to_lang",
        # ).pack(anchor="nw", pady=5, side=tk.LEFT)

        # ttk.Radiobutton(
        #     aframe,
        #     text=f"{language_manager_flashcards.get_language()} to Hangul",
        #     variable=self.settings['study_direction'],
        #     value="lang_to_hangul"
        # ).pack(anchor="nw", pady=5, side=tk.LEFT)
        

        






        































    # Difficulty (easy, medium, hard) -- Padrao - All (ou apenas para o sistema Leitner)




    # def get_settings(self):
    #     return {
    #         'word_count': self.get_value(),
    #         'auto_correction': self.settings['realtime_feedback'].get()
    #     }



    # def _update_slider(self):
    #     try:
    #         value = int(self.spinbox.get())
    #         if 1 <= value <= len(self.vocabulary):
    #             self.slider.set(value)
    #     except ValueError:
    #         pass
        
    # def _update_spinbox(self, value):
    #     try:
    #         int_value = int(float(value))
    #         self.spinbox.set(int_value)
    #     except ValueError:
    #         pass

    # def _sync_widgets(self, _):
    #     try:
    #         value = int(self.spinbox.get())
    #         if 1 <= value <= len(self.vocabulary):
    #             self.slider.set(value)
    #     except ValueError:
    #         pass
    
    # def get_value(self):
    #     return int(self.spinbox.get())
    
    
    

    

    


















# class CustomizeStudySession:
#     def __init__(self, root, vocabulary):
#         self.root = root
#         self.vocabulary = vocabulary
#         self.create_widgets()

#     def create_widgets(self):
#         # Create a new GUI for the study session
#         self.customize_frame = ttk.Frame(self.root, padding=20)
#         self.customize_frame.pack(fill=tk.BOTH, expand=True)

#         # Title Label
#         title_label = ttk.Label(
#             self.customize_frame,
#             text="Customize Study Session",
#             font=("Arial", 16, "bold")
#         )
#         title_label.pack(pady=10)
        
#         test_button = ttk.Button(
#             self.customize_frame,
#             text="Test",
#             command=self.study
#         )
#         test_button.pack(pady=10, ipady=5)

#     def study(self):
#         self.customize_frame.pack_forget()
#         from all_flashcards import MultipleChoiceGame
#         MultipleChoiceGame(self.root, self.vocabulary)
        

#### Inicio gerado por ia apenas para teste, refazer tudo (esta funcionando a logica) ####
        

            


