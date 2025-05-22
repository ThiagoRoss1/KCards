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

        if hasattr(root, 'session_timer') and root.session_timer.should_display(self.settings):
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
            if canvas.winfo_exists():
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

class TrueFalseResultsScreen:
    def __init__(self, root, correct, incorrect, w_history, return_callback, settings=None):
        self.root = root
        self.correct = correct
        self.incorrect = incorrect
        self.total = correct + incorrect
        self.w_history = w_history
        self.return_callback = return_callback
        self.settings = settings or getattr(root, 'session_settings', {})

        self.create_widgets(root)

    def create_widgets(self, root):
        for widget in self.root.winfo_children():
            widget.pack_forget()

        self.main_frame = ttk.Frame(self.root, padding=20)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        if hasattr(self.root, 'session_timer') and self.root.session_timer.should_display(self.settings):
            elapsed_time = self.root.session_timer.get_elapsed_time()
            time_text = f"Session Time: {self.root.session_timer.format_time(elapsed_time)}"
        else:
            time_text = ""

        time_label = ttk.Label(
            self.main_frame,
            text=time_text,
            font=("Arial", 12)
        )
        time_label.pack(pady=10)

        tlabel = ttk.Label(
            self.main_frame,
            text="⚫ True or False Game Results",
            font=("Arial", 16, "bold")
        )
        tlabel.pack(pady=10)

        rlabel = ttk.Label(
            self.main_frame,
            text=f"Results: {self.correct}/{self.total} ({self.correct/self.total:.0%})",
            font=("Arial", 16, "bold")
        )
        rlabel.pack(pady=10)

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

        for item in self.w_history:
            self.add_result_item(scrollable_frame, item)

        # Buttons Frame

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

    def add_result_item(self, parent_frame, item):
        from project import language_manager_flashcards
        word = item['word']
        frame = ttk.Frame(parent_frame, padding=10, relief="solid")
        frame.pack(fill=tk.X, pady=5)

        user_answer = item.get('user_answer', 'False')
        correct_answer = item.get('expected', 'False')
        is_correct = item.get('correct', False)

        user_answer = str(user_answer) if isinstance(user_answer, bool) else user_answer
        correct_answer = str(correct_answer) if isinstance(correct_answer, bool) else correct_answer

        ttk.Label(
            frame,
            text=f"Word: {item.get('question_word', '')}",
            font=("Arial", 12, "bold")
        ).pack(anchor="w")

        ttk.Label(
            frame,
            text=f"Question: {item.get('statement_question', '')}",
            font=("Arial", 12)
        ).pack(anchor="w")

        status = "✔" if is_correct else "❌"
        color = "green" if is_correct else "red"
        
        ttk.Label(
            frame,
            text=f"{status} Your Answer: {user_answer}",
            font=("Arial", 12),
            foreground=color
        ).pack(anchor="w")

        if not is_correct:
            ttk.Label(
                frame,
                text=f"Correct Answer: {correct_answer}",
                font=("Arial", 12),
                foreground="blue"
            ).pack(anchor="w")

        difficulty_color = {
            'Easy': "#585858",
            'Medium': "#531083",
            'Hard': "#A78B12"
        }

        ttk.Label(
            frame,
            text=f"📑 Difficulty: {word['Difficulty']}",
            foreground=difficulty_color.get(word['Difficulty'], 'black')
        ).pack(anchor="w")

        # ttk.Label(
        #     frame,
        #     text=item['timestamp'],  # Funcionando mas amanha tentar botar em todos
        #     font=("Arial", 9),
        #     foreground="gray"
        # ).pack(side=tk.RIGHT)


class StandardResultsScreen:
    def __init__(self, root, correct, incorrect, w_history, return_callback, settings=None):
        self.root = root
        self.correct = correct
        self.incorrect = incorrect
        self.w_history = w_history
        self.return_callback = return_callback
        self.settings = settings or getattr(root, 'session_settings', {})

        if not hasattr(root, 'session_timer'):
            from utilities import SessionTimer
            root.session_timer = SessionTimer()
            root.session_timer.elapsed_time = 0

        self.setup_styles()
        self.setup_ui()
        
    def setup_styles(self):
        self.style = ttk.Style()
        self.style.configure("Title.TLabel", font=("Arial", 16, "bold"))
        self.style.configure("Stats.TLabel", font=("Arial", 12))
        self.style.configure("Correct.TLabel", foreground="#2ecc71")
        self.style.configure("Incorrect.TLabel", foreground="#e74c3c") 
        self.style.configure("Word.TLabel", font=("Malgun Gothic", 14))
        self.style.configure("Translation.TLabel", font=("Arial", 12, "bold") if self.settings.get('study_direction') == "hangul_to_lang" else ("Malgun Gothic", 12, "bold"))
        self.style.configure("History.TFrame", relief="solid", borderwidth=1)
        
    def setup_ui(self):
        self.main_frame = ttk.Frame(self.root, padding=20)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.create_header()
        
        self.create_stats_section()
        
        self.create_history_section()
        
        self.create_action_buttons()
        
    def create_header(self):
        from utilities import SessionTimer
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))

        if hasattr(self.root, 'session_timer') and getattr(self.root.session_timer, 'is_running', False):
            elapsed_time = self.root.session_timer.get_elapsed_time()
            time_text = f"Session Time: {self.root.session_timer.format_time(elapsed_time)}"
        else:
            time_text = ""
        
        time_label = ttk.Label(
            self.main_frame,
            text=time_text,
            font=("Arial", 12)
        )
        time_label.pack(pady=10)
        
        ttk.Label(
            header_frame,
            text="Standard Flashcards Results",
            font=("Arial", 16, "bold"),
        ).pack(pady=5)
        
    def create_stats_section(self):
        stats_frame = ttk.Frame(self.main_frame)
        stats_frame.pack(fill=tk.X, pady=(0, 20))
        
        total = self.correct + self.incorrect
        accuracy = self.correct / total if total > 0 else 0
        
        ttk.Label(
            stats_frame,
            text=f"✔ Corrects: {self.correct}",
            style="Correct.TLabel"
        ).pack(side=tk.LEFT, expand=True)
        
        ttk.Label(
            stats_frame,
            text=f"Results: {self.correct}/{total} ({accuracy:.0%})",
            font=("Arial", 16, "bold"),
        ).pack(side=tk.LEFT, expand=True)
        
        ttk.Label(
            stats_frame,
            text=f"✖ Incorrects: {self.incorrect}",
            style="Incorrect.TLabel"
        ).pack(side=tk.RIGHT, expand=True)
    
    def create_history_section(self):
        
        container = ttk.Frame(self.main_frame)
        container.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(container)
        v_scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        h_scrollbar = ttk.Scrollbar(container, orient="horizontal", command=self.canvas.xview)

        self.canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        self.canvas.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        scrollable_frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        self.canvas.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        def on_mousewheel(event):
            if hasattr(self, 'canvas') and self.canvas.winfo_exists():
                self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        self._mousewheel_binding = self.root.bind_all("<MouseWheel>", on_mousewheel)
        
        for item in self.w_history:
            self.add_history_item(scrollable_frame, item)

    def __del__(self):
        if hasattr(self, '_mousewheel_binding'):
            try:
                if self.root.winfo_exists():
                    self.root.unbind_all("<MouseWheel>")
            except tk.TclError:
                pass
    
    def add_history_item(self, parent, item):
        from project import language_manager_flashcards
        frame = ttk.Frame(parent, padding=10, style="History.TFrame")
        frame.pack(fill=tk.X, pady=2)
        
        word = item['word']
        is_correct = item.get('correct', False)
        
        top_frame = ttk.Frame(frame)
        top_frame.pack(fill=tk.X)
        
        ttk.Label(
            top_frame,
            text=word['Hangul'] if self.settings['study_direction'] == "hangul_to_lang" else language_manager_flashcards.get_translations(word),
            style="Word.TLabel"
        ).pack(side=tk.LEFT)
        
        status = "✔" if is_correct else "✖"
        status_style = "Correct.TLabel" if is_correct else "Incorrect.TLabel"
        ttk.Label(
            top_frame,
            text=status,
            style=status_style
        ).pack(side=tk.RIGHT)
        
        ttk.Label(
            frame,
            text=f"→ {language_manager_flashcards.get_translations(word)}" if self.settings['study_direction'] == "hangul_to_lang" else f"→ {word['Hangul']}",
            style="Translation.TLabel"
        ).pack(anchor="w")
        
        bottom_frame = ttk.Frame(frame)
        bottom_frame.pack(fill=tk.X)

        difficulty_color = {
            'Easy': "#585858",
            'Medium': "#531083",
            'Hard': "#A78B12"    #botar uma sombra
        }
        
        ttk.Label(
            bottom_frame,
            text=f"Dificuldade: {word['Difficulty']}",
            font=("Arial", 9),
            foreground=difficulty_color.get(word['Difficulty'], "black")
        ).pack(side=tk.LEFT)
        
        # ttk.Label(
        #     bottom_frame,
        #     text=item['timestamp'],   # Funcionando mas amanha tentar botar em todos
        #     font=("Arial", 9),
        #     foreground="gray"
        # ).pack(side=tk.RIGHT)

    def create_action_buttons(self):
        from routes import return_to_main_menu, Retry
        from project import load_vocabulary
        vocabulary = load_vocabulary()

        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(pady=10)

        Menu = ttk.Button(
            button_frame,
            text="🏠 Main Menu",
            command=lambda: return_to_main_menu(self.root, self.main_frame),
        )
        Menu.pack(side=tk.RIGHT, padx=8)

        RetryB = Retry(
            parent=button_frame,
            root=self.root,
            current_frame=self.main_frame,
            vocabulary=self.root.session_settings['words']
        )
        RetryB.pack(side=tk.RIGHT, padx=8)



        # Matching e TrueFalse showing timer even if off 