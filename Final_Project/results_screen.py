import tkinter as tk
from tkinter import ttk, messagebox
import routes
from routes import return_to_main_menu, Retry


class ResultsScreen:
    def __init__(self, root, correct, incorrect, w_history, return_callback):
        self.root = root
        self.correct = correct
        self.incorrect = incorrect
        self.total = correct + incorrect
        self.w_history = w_history
        self.return_callback = return_callback

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


        from utilities import SessionTimer
        elapsed_time = root.session_timer.get_elapsed_time()
        time_label = ttk.Label(
            self.main_frame,
            text=f"Session Time: {root.session_timer.format_time(elapsed_time)}",
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
                self.add_input_item(scrollable_frame, item['word'], item['user_answer'], item['correct'])
            elif "selected_option" in item:
                self.add_multiple_choice_item(scrollable_frame, item['word'], item['selected_option'], item['selected_correct'], item['correct_option'])
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
            text="Back to Main Menu",
            command=lambda: return_to_main_menu(self.root, self.main_frame)
        ).pack() # pelo visto button aceita tanto pack quanto grid, mas o grid eh mais flexivel, testar depois o posicionamento

        retry_button = Retry(
            parent=button_frame,
            root=self.root,
            current_frame=self.main_frame,
            vocabulary=self.root.session_settings['words']
        )
        retry_button.pack(side=tk.RIGHT, padx=8)


        # ebutton = ttk.Button(
        #     button_frame,
        #     text="Next",
        #     command=lambda: self.start_mistakes_session(),     # Kinda Advanced ( make it in later updates )
        #     width=15
        # )
        # ebutton.pack(side=tk.RIGHT, padx=8)

    def add_input_item(self, parent_frame, word, user_answer, correct):

        from project import LanguageManager, language_manager_flashcards
        translation = language_manager_flashcards.get_translations(word)

        # Answers List

        a_frame = ttk.Frame(parent_frame, padding=10, relief="solid")
        a_frame.pack(fill=tk.X, pady=5)

        # Words

        w_label = ttk.Label(
            a_frame,
            text=f"{word['Hangul']} ({translation})",
            font=("Malgun Gothic", 12, "bold")
        )
        w_label.pack(anchor="w")

        # User Answer

        status = "✔" if correct else "❌"
        color = "green" if correct else "red"

        u_label = ttk.Label(
            a_frame,
            text=f"{status} Your Answer: {user_answer}",
            font=("Arial", 12),
            foreground=color
        )
        u_label.pack(anchor="w")

        # Correct Answer (if incorrect)

        if not correct:
            c_label = ttk.Label(
                a_frame,
                text=f"❌ Correct Answer: {language_manager_flashcards.get_translations(word)}", # caso tenha 2 versoes isso sera mudado
                foreground="blue",
            )
            c_label.pack(anchor="w")

    
    def add_multiple_choice_item(self, parent_frame, word, selected_option, selected_correct, correct_option):
        # Multiple Choice Item
        from project import language_manager_flashcards
        translation = language_manager_flashcards.get_translations(word)

        m_frame = ttk.Frame(parent_frame, padding=10, relief="solid")
        m_frame.pack(fill=tk.X, pady=5)

        w_label = ttk.Label(
            m_frame,
            text=f"{word['Hangul']} ({translation})",
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
                text=f"❌ Correct Answer: {translation}",
                foreground="blue"
            )
            c_label.pack(anchor="w")

    # def start_mistakes_session(self):
    #     from utilities import GetMistakes
    #     from all_flashcards import standard_flashcards, input_practice, MultipleChoiceGame

    #     mistake_words = GetMistakes(self.root, history=self.w_history).get_mistakes()
    #     full_settings = {
    #         **self.root.session_settings,
    #         'word_count': len(mistake_words),
    #         'study_direction': 'hangul_to_lang'
    #     }

    #     if not mistake_words:
    #         messagebox.showinfo("100% Correct", "You got all answers correct!")
    #         return
        
    #     if self.root.session_settings['selected_mode'] == "multiple_choice":
    #         self.main_frame.pack_forget()
    #         MultipleChoiceGame(
    #             self.root,
    #             words=mistake_words,
    #             settings=full_settings
    #         )

        # elif self.root.session_settings['selected_mode'] == "Input":
        #     input_practice.InputPractice(
        #         self.root,
        #         words=mistake_words,
        #         settings=self.root.session_settings
        #     )
