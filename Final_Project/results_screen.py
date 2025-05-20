import tkinter as tk
from tkinter import ttk, messagebox
import routes
from routes import return_to_main_menu, Retry


class ResultsScreen:
    def __init__(self, root, correct, incorrect, w_history, return_callback, settings=None):
        self.root = root
        self.correct = correct
        self.incorrect = incorrect
        self.total = correct + incorrect
        self.w_history = w_history
        self.return_callback = return_callback
        self.settings = settings or getattr(root, 'session_settings', {})

        if not hasattr(root, 'session_timer'):
            from utilities import SessionTimer
            root.session_timer = SessionTimer()
            root.session_timer.elapsed_time = 0

        # Safe Calc

        self.percentage = 0.0
        if self.total > 0:
            self.percentage = self.correct / self.total 

        self.create_widgets(root)


    def create_widgets(self, root):

        # Main Frame

        for widget in self.root.winfo_children():
            widget.pack_forget()

        self.main_frame = ttk.Frame(self.root, padding=20)
        self.main_frame.pack(fill=tk.BOTH, expand=True)


        if hasattr(root, 'session_timer') and getattr(root.session_timer, 'is_running', False):
            elapsed_time = root.session_timer.get_elapsed_time()
            time_text = f"Session Time: {root.session_timer.format_time(elapsed_time)}"
        else:
            time_text = ""
        
        time_label = ttk.Label(
            self.main_frame,
            text=time_text,
            font=("Arial", 12)
        )
        time_label.pack(pady=10)


        # Title Label

        main_label = ttk.Label(
            self.main_frame,
            text=f"Results: {self.correct}/{self.total} ({self.correct/self.total:.0%})",
            font=("Arial", 16, "bold")
        )
        main_label.pack(pady=10)

        # Stats Label

        stats_frame = ttk.Frame(self.main_frame)
        stats_frame.pack(fill=tk.X, pady=10)

        ttk.Label(
            stats_frame,
            text=f"✔ Corrects: {self.correct}",
            foreground="green"
        ).pack(side=tk.LEFT)

        ttk.Label(
            stats_frame,
            text=f"❌ Incorrects: {self.incorrect}",
            foreground="red"
        ).pack(side=tk.RIGHT)


        # Answer List Frame

        self.canvas = tk.Canvas(self.main_frame)
        self.canvas.bind("<MouseWheel>",
                         lambda e: self.canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        
        self.canvas.bind("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))
        self.canvas.bind("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))

        scrollbar = ttk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        scrollable_frame = ttk.Frame(self.canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda _: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side="right", fill="y")

        # History Label

        for item in self.w_history:
            if "user_answer" in item:
                self.add_input_item(scrollable_frame, item, item['user_answer'], item['correct'])
            elif "selected_option" in item:
                self.add_multiple_choice_item(scrollable_frame, item, item['selected_option'], item['correct'], item['expected'])
            elif "pairs" in item:
                for pair in item['pairs']:
                    self.add_input_item(scrollable_frame, pair, pair['user_answer'], pair['correct'])
        # Action Buttons Frame

        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(pady=10)

        # Buttons

       # retry_button = ttk.Button(
          #  button_frame,
          ## retry_button.pack(side=tk.LEFT, padx=8)

        from routes import return_to_main_menu, Retry
        from project import load_vocabulary
        vocabulary = load_vocabulary()
        ttk.Button(
            button_frame,
            text="🏠 Main Menu",
            command=lambda: return_to_main_menu(self.root, self.main_frame)
        ).pack() # pelo visto button aceita tanto pack quanto grid, mas o grid eh mais flexivel, testar depois o posicionamento

        retry_button = Retry(
            parent=button_frame,
            root=self.root,
            current_frame=self.main_frame,
            vocabulary=self.root.session_settings['words']
        )
        retry_button.pack(side=tk.RIGHT, padx=8)

        # restart_button = Restart(
        #     parent=button_frame,
        #     root=self.root,
        #     current_frame=self.main_frame,
        #     vocabulary=self.root.session_settings['words'],
        # )
        # restart_button.pack(side=tk.RIGHT, padx=8)

        # ebutton = ttk.Button(
        #     button_frame,
        #     text="Next",
        #     command=lambda: self.start_mistakes_session(),     # Kinda Advanced ( make it in later updates )
        #     width=15
        # )
        # ebutton.pack(side=tk.RIGHT, padx=8)

    def add_input_item(self, parent_frame, item, user_answer, correct):
        from project import LanguageManager, language_manager_flashcards
        word = item['word']

        study_direction = item.get('study_direction', 'hangul_to_lang')

        if study_direction == "hangul_to_lang":
            question_text = f"{word['Hangul']} ({language_manager_flashcards.get_translations(word)})"
            correct_answer = language_manager_flashcards.get_translations(word)
        else:
            question_text = f"{language_manager_flashcards.get_translations(word)} ({word['Hangul']})"
            correct_answer = word['Hangul']

        # Answers List

        a_frame = ttk.Frame(parent_frame, padding=10, relief="solid")
        a_frame.pack(fill=tk.X, pady=5)

        # Words

        w_label = ttk.Label(
            a_frame,
            text=question_text,
            font=("Malgun Gothic", 12, "bold")
        )
        w_label.pack(anchor="w")

        # User Answer

        status = "✔" if correct else "❌"
        color = "green" if correct else "red"

        u_label = ttk.Label(
            a_frame,
            text=f"{status} Your Answer: {user_answer}",   # Mudar isso para adaptar ao Multiple Choice
            font=("Arial", 12),
            foreground=color
        )
        u_label.pack(anchor="w")

        # Correct Answer (if incorrect)

        if not correct:
            c_label = ttk.Label(
                a_frame,
                text=f"❌ Correct Answer: {correct_answer}",
                foreground="blue",
            )
            c_label.pack(anchor="w")

        difficulty_color = {
            'Easy': "#585858",
            'Medium': "#531083",
            'Hard': "#A78B12"    #botar uma sombra
        }

        dlabel = ttk.Label(
            a_frame,
            text=f"📑 Difficulty: {word['Difficulty']}",
            foreground=difficulty_color.get(word['Difficulty'], 'black')
        )
        dlabel.pack(anchor="w")

    
    def add_multiple_choice_item(self, parent_frame, item, selected_option, selected_correct, correct_option):
        # Multiple Choice Item
        from project import language_manager_flashcards
        word = item['word']

        study_direction = item.get('study_direction', 'hangul_to_lang')

        if study_direction == "hangul_to_lang":
            question_text = f"{word['Hangul']} ({language_manager_flashcards.get_translations(word)})"
            correct_answer = language_manager_flashcards.get_translations(word)
        else:
            question_text = f"{language_manager_flashcards.get_translations(word)} ({word['Hangul']})"
            correct_answer = word['Hangul']

        m_frame = ttk.Frame(parent_frame, padding=10, relief="solid")
        m_frame.pack(fill=tk.X, pady=5)

        w_label = ttk.Label(
            m_frame,
            text=question_text,
            font=("Malgun Gothic", 12, "bold")
        )
        w_label.pack(anchor="w")

        # Selected Option

        status = "✔" if selected_correct else "❌"
        color = "green" if selected_correct else "red"

        m_label = ttk.Label(
            m_frame,
            text=f"{status} You Selected: {selected_option}",
            font=("Arial", 12),
            foreground=color
        )
        m_label.pack(anchor="w")

        # Correct Answer (if incorrect)

        if not selected_correct:
            c_label = ttk.Label(
                m_frame,
                text=f"❌ Correct Answer: {correct_answer}",
                foreground="blue"
            )
            c_label.pack(anchor="w")


class MatchingResultsScreen:
    def __init__(self, root, pairs, attempts, correct, incorrect, accuracy, w_history, return_callback, settings=None):
        self.root = root
        self.pairs = pairs
        self.attempts = attempts
        self.correct = correct
        self.incorrect = incorrect
        self.accuracy = accuracy
        self.w_history = w_history
        self.return_callback = return_callback
        self.settings = settings or getattr(root, 'session_settings', {})

        self.accuracy = (6 / self.attempts) if self.attempts > 0 else 0.0

        if not hasattr(root, 'session_timer'):
            from utilities import SessionTimer
            root.session_timer = SessionTimer()
            root.session_timer.elapsed_time = 0

        self.create_widgets(root)

    def create_widgets(self, root):
        for widget in self.root.winfo_children():
            widget.pack_forget()

        
        self.main_frame = ttk.Frame(self.root, padding=20)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Title Label

        tlabel = ttk.Label(
            self.main_frame,
            text="🎯 Matching Game Results",
            font=("Arial", 16, "bold")
        )
        tlabel.pack(pady=10)

        self.statsframe = ttk.Frame(self.main_frame)
        self.statsframe.pack(fill=tk.X, pady=10)

        accuracy_label = ttk.Label(
            self.statsframe,
            text=f"• ✔ Accuracy: {self.accuracy:.0%}",
            font=("Arial", 16, "bold"),
            foreground="#13e263" if self.accuracy >= 0.75 else "#ff3a00" if self.accuracy >= 0.5 else "#ca1d10"
        )
        accuracy_label.pack(anchor="center", pady=5)

        attempts_label = ttk.Label(
            self.statsframe,
            text=f"• 📑 Attempts: {self.attempts}",
            font=("Arial", 16, "bold"),
            foreground="#12eccf" if self.attempts == 6 else "#ff6400" if 6 < self.attempts < 12 else "#E0115F"
        )
        attempts_label.pack(anchor="center", pady=5)

        wrong_label = ttk.Label(
            self.statsframe,
            text=f"• ❌ Incorrects: {self.incorrect}",
            font=("Arial", 16, "bold"),
            foreground="#4dd6a2" if self.incorrect == 0 else "#ff8f00" if 6 < self.incorrect < 12 else "#FF073A"
        )
        wrong_label.pack(anchor="center", pady=5)

        if hasattr(root, 'session_timer') and getattr(root.session_timer, 'is_running', False):
            elapsed_time = root.session_timer.get_elapsed_time()
            time_text = f"• ⏱ Session Time: {root.session_timer.format_time(elapsed_time)}"
        else:
            time_text = ""

        time_label = ttk.Label(
            self.statsframe,
            text=time_text,
            font=("Arial", 16, "bold")
        )
        time_label.pack(anchor="center", pady=5)

        # Words List Frame

        words_frame = ttk.Frame(self.main_frame)
        words_frame.pack(fill=tk.BOTH, expand=True, pady=20)

        wlabel = ttk.Label(
            words_frame,
            text="🔠 Words List",
            font=("Arial", 16, "bold")
        )
        wlabel.pack(anchor="center", pady=5)

        container = ttk.Frame(words_frame)
        container.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(container)
        v_scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        h_scrollbar = ttk.Scrollbar(container, orient="horizontal", command=canvas.xview)

        canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        scrollable_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        canvas.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", on_mousewheel)

        # canvas = tk.Canvas(words_frame, height=200)
        # scrollbar = ttk.Scrollbar(words_frame, orient="vertical", command=canvas.yview)
        # scrollable_frame = ttk.Frame(canvas)

        # scrollable_frame.bind(
        #     "<Configure>",
        #     lambda e: canvas.configure(
        #         scrollregion=canvas.bbox("all")
        #     )
        # )

        # canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        # canvas.configure(yscrollcommand=scrollbar.set)

        # canvas.pack(side="left", fill="both", expand=True)
        # scrollbar.pack(side="right", fill="y")

        # bscrollbar = ttk.Scrollbar(words_frame, orient="horizontal", command=canvas.xview)
        # bscrollable_frame = ttk.Frame(canvas)

        # bscrollable_frame.bind(
        #     "<Configure>",
        #     lambda e: canvas.configure(
        #         scrollregion=canvas.bbox("all")
        #     )
        # )

        # canvas.create_window((0, 0), window=bscrollable_frame, anchor="nw")
        # canvas.configure(xscrollcommand=bscrollbar.set)

        # canvas.pack(side="left", fill="both", expand=True)
        # bscrollbar.pack(side="bottom", fill="x")

        unique_words = []
        seen_words = set()

        if isinstance(self.w_history, list):
            for item in self.w_history:
                if 'words_list' in item:
                    for word in item['words_list']:
                        if word ['Hangul'] not in seen_words:
                            seen_words.add(word['Hangul'])
                            unique_words.append(word)
                elif 'word' in item:
                    if item['word']['Hangul'] not in seen_words:
                        seen_words.add(item['word']['Hangul'])
                        unique_words.append(item['word'])

        for word in unique_words:
            self.add_word_pair(scrollable_frame, word)


        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(pady=10)

        from routes import return_to_main_menu, Retry
        from project import load_vocabulary
        vocabulary = load_vocabulary()

        Menu = ttk.Button(
            button_frame,
            text="🏠 Main Menu",
            command=lambda: return_to_main_menu(self.root, self.main_frame)
        )
        Menu.pack()

        RetryB = Retry(
            parent=button_frame,
            root=self.root,
            current_frame=self.main_frame,
            vocabulary=self.root.session_settings['words']
        )
        RetryB.pack(side=tk.RIGHT, padx=8)

    def add_word_pair(self, parent, word):
        from project import language_manager_flashcards

        pair_frame = ttk.Frame(parent, padding=10, relief="ridge")
        pair_frame.pack(fill=tk.X, pady=5)

        ttk.Label(
            pair_frame,
            text=word['Hangul'],
            font=("Malgun Gothic", 13, "bold"),
            width=15,
            anchor="center",
        ).pack(side=tk.LEFT, padx=5)

        ttk.Label(
            pair_frame,
            text="→",
            font=("Arial", 12),
            foreground="gray",
        ).pack(side=tk.LEFT, padx=5)

        ttk.Label(
            pair_frame,
            text=language_manager_flashcards.get_translations(word),
            font=("Arial", 12),
            width=20,
            anchor="center",
            wraplength=200
        ).pack(side=tk.LEFT, padx=5)


        # Difficulty Label

        difficulty_color = {
            'Easy': "#585858",
            'Medium': "#531083",
            'Hard': "#A78B12"
        }

        ttk.Label(
            pair_frame,
            text=f"📑 Difficulty: {word['Difficulty']}",
            font=("Arial", 10),
            foreground=difficulty_color.get(word['Difficulty'], 'gray')
        ).pack(side=tk.RIGHT, padx=5)