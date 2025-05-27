import customtkinter as ctk
from customtkinter import *
from language_manager import InterfaceTranslator, T_CTkLabel

# import tkinter as tk
# from tkinter import ttk, messagebox
import routes
from routes import return_to_main_menu, Retry

translation = InterfaceTranslator()


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

        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill=ctk.BOTH, expand=True)


        if hasattr(root, 'session_timer') and getattr(root.session_timer, 'is_running', False):
            elapsed_time = root.session_timer.get_elapsed_time()
            time_text = f"Session Time: {root.session_timer.format_time(elapsed_time)}"
        else:
            time_text = ""
        
        time_label = ctk.CTkLabel(
            self.main_frame,
            text=time_text,
            font=("Arial", 12)
        )
        time_label.pack(pady=10)

        # Title Label

        tlabel = T_CTkLabel(
            self.main_frame,
            text=f"⌨ {translation.get_translation("input_results")}",
            font=("Arial", 16, "bold")
        )
        tlabel.pack(pady=10)

        main_label = T_CTkLabel(
            self.main_frame,
            text=f"{translation.get_translation("results")}: {self.correct}/{self.total} ({self.correct/self.total:.0%})",
            font=("Arial", 16, "bold")
        )
        main_label.pack(pady=10)

        # Stats Label

        stats_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent",
            border_width=2,
            border_color=("gray70", "gray30"),
            corner_radius=4,
            width=300,
            height=50
        )
        stats_frame.pack_propagate(False)
        stats_frame.pack(expand=False, fill=ctk.X, pady=10, padx=10)

        stats_content_frame = ctk.CTkFrame(
            stats_frame,
            fg_color="transparent"
        )
        stats_content_frame.pack(expand=True, fill=ctk.BOTH, pady=5, padx=5)

        T_CTkLabel(
            stats_content_frame,
            text=f"✔ {translation.get_translation("corrects")}: {self.correct}",
            text_color="green"
        ).pack(side=ctk.LEFT, padx=(100, 0))

        T_CTkLabel(
            stats_content_frame,
            text=f"❌ {translation.get_translation("incorrects")}: {self.incorrect}",
            text_color="red"
        ).pack(side=ctk.RIGHT, padx=(0, 100))


        # Answer List Frame

        self.scrollable_frame = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent", width=300)
        self.scrollable_frame.pack(fill=ctk.BOTH, expand=True, padx=5)

        inner_frame = ctk.CTkFrame(self.scrollable_frame)
        inner_frame.pack(fill=ctk.BOTH, expand=True, padx=5, pady=5)

        # History Label

        for item in self.w_history:
            if "user_answer" in item:
                self.add_input_item(inner_frame, item, item['user_answer'], item['correct'])
            elif "selected_option" in item:
                self.add_multiple_choice_item(inner_frame, item, item['selected_option'], item['correct'], item['expected'])
            elif "pairs" in item:
                for pair in item['pairs']:
                    self.add_input_item(inner_frame, pair, pair['user_answer'], pair['correct'])
        # Action Buttons Frame

        button_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        button_frame.pack(pady=10)

        # Buttons

       # retry_button = ctk.CTkButton(
          #  button_frame,
          ## retry_button.pack(side=ctk.LEFT, padx=8)

        from routes import return_to_main_menu, Retry
        from project import load_vocabulary
        vocabulary = load_vocabulary()
        ctk.CTkButton(
            button_frame,
            text=f"🏠 {translation.get_translation("main_menu")}",
            command=lambda: return_to_main_menu(self.root, self.main_frame),
            fg_color="#3B8ED0",
            hover_color="#36719F",
            text_color="white",
            border_width=0,
            width=30,
            height=30,
            corner_radius=20
            
        ).pack(anchor="s", pady=0)

        retry_button = Retry(
            parent=button_frame,
            root=self.root,
            current_frame=self.main_frame,
            vocabulary=self.root.session_settings['words']
        )
        retry_button.pack(anchor="s", pady=8)

        # restart_button = Restart(
        #     parent=button_frame,
        #     root=self.root,
        #     current_frame=self.main_frame,
        #     vocabulary=self.root.session_settings['words'],
        # )
        # restart_button.pack(side=ctk.RIGHT, padx=8)

        # ebutton = ctk.CTkButton(
        #     button_frame,
        #     text="Next",
        #     command=lambda: self.start_mistakes_session(),     # Kinda Advanced ( make it in later updates )
        #     width=15
        # )
        # ebutton.pack(side=ctk.RIGHT, padx=8)

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

        if not hasattr(self, 'columns_created'):
            self.columns_created = True
            self.current_column = 0

            self.col_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
            self.col_frame.pack(fill=ctk.BOTH, expand=True)

            self.left_column = ctk.CTkFrame(self.col_frame, fg_color="transparent")
            self.left_column.grid(row=0, column=0, sticky="nsew", padx=5)
            
            self.right_column = ctk.CTkFrame(self.col_frame, fg_color="transparent")
            self.right_column.grid(row=0, column=1, sticky="nsew", padx=5)

            self.col_frame.grid_columnconfigure(0, weight=1)
            self.col_frame.grid_columnconfigure(1, weight=1)
            self.col_frame.grid_rowconfigure(0, weight=1)

        target_column = self.left_column if self.current_column % 2 == 0 else self.right_column
        self.current_column += 1
    

        a_frame = ctk.CTkFrame(
            target_column,
            fg_color="transparent",
            border_width=2,
            border_color=("gray70", "gray30"),
            corner_radius=20,
            width=250,
            height=130
        )
        a_frame.pack_propagate(False)
        a_frame.pack(expand=False, anchor="w", padx=10, pady=5)

        content_frame = ctk.CTkFrame(
            a_frame,
            fg_color="transparent",
        )
        content_frame.pack(expand=True, fill=ctk.BOTH, padx=10, pady=10)

        content_frame.grid_columnconfigure(0, weight=1)
        for i in range(4):
            content_frame.grid_rowconfigure(i, weight=0)

        # Words

        w_label = ctk.CTkLabel(
            content_frame,
            text=question_text,
            fg_color="transparent",
            text_color="white",
            font=("Malgun Gothic", 14, "bold"),
        )
        w_label.pack(anchor="w")

        # User Answer

        status = "✔" if correct else "❌"
        color = "#2ecc71" if correct else "#e74c3c"

        u_label = T_CTkLabel(
            content_frame,
            text=f"{status} {translation.get_translation("your_answer")}: {str(user_answer).capitalize()}",
            font=("Arial", 12),
            wraplength=200,
            text_color=color
        )
        u_label.pack(anchor="w")

        # Correct Answer (if incorrect)

        if not correct:
            c_label = T_CTkLabel(
                content_frame,
                text=f"✔ {translation.get_translation("correct_answer")}: {correct_answer}",
                font=("Arial", 13),
                text_color="#3B8ED0",
            )
            c_label.pack(anchor="w")

        difficulty_color = {
            'Easy': "#585858",
            'Medium': "#531083",
            'Hard': "#A78B12"    #botar uma sombra
        }

        dlabel = T_CTkLabel(
            content_frame,
            text=f"📑 {translation.get_translation("difficulty")}: {translation.get_difficulty_translation(word["Difficulty"])}",
            text_color=difficulty_color.get(word['Difficulty'], 'black')
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

        m_frame = ctk.CTkFrame(parent_frame)
        m_frame.pack(fill=ctk.X, pady=5)

        w_label = ctk.CTkLabel(
            m_frame,
            text=question_text,
            font=("Malgun Gothic", 12, "bold")
        )
        w_label.pack(anchor="w")

        # Selected Option

        status = "✔" if selected_correct else "❌"
        color = "green" if selected_correct else "red"

        m_label = ctk.CTkLabel(
            m_frame,
            text=f"{status} You Selected: {selected_option}",
            font=("Arial", 12),
            text_color=color
        )
        m_label.pack(anchor="w")

        # Correct Answer (if incorrect)

        if not selected_correct:
            c_label = ctk.CTkLabel(
                m_frame,
                text=f"❌ Correct Answer: {correct_answer}",
                text_color="blue"
            )
            c_label.pack(anchor="w")

#####tirar essa bomba

class MultipleChoiceResultsScreen:
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

        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill=ctk.BOTH, expand=True)


        if hasattr(root, 'session_timer') and getattr(root.session_timer, 'is_running', False):
            elapsed_time = root.session_timer.get_elapsed_time()
            time_text = f"Session Time: {root.session_timer.format_time(elapsed_time)}"
        else:
            time_text = ""
        
        time_label = ctk.CTkLabel(
            self.main_frame,
            text=time_text,
            font=("Arial", 12)
        )
        time_label.pack(pady=10)

        # Title Label

        tlabel = ctk.CTkLabel(
            self.main_frame,
            text="🔠 Multiple Choice Game Results",
            font=("Arial", 16, "bold")
        )
        tlabel.pack(pady=10)

        main_label = ctk.CTkLabel(
            self.main_frame,
            text=f"Results: {self.correct}/{self.total} ({self.correct/self.total:.0%})",
            font=("Arial", 16, "bold")
        )
        main_label.pack(pady=10)

        # Stats Label

        stats_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent",
            border_width=2,
            border_color=("gray70", "gray30"),
            corner_radius=4,
            width=300,
            height=50
        )
        stats_frame.pack_propagate(False)
        stats_frame.pack(expand=False, fill=ctk.X, pady=10, padx=10)

        stats_content_frame = ctk.CTkFrame(
            stats_frame,
            fg_color="transparent"
        )
        stats_content_frame.pack(expand=True, fill=ctk.BOTH, pady=5, padx=5)

        ctk.CTkLabel(
            stats_content_frame,
            text=f"✔ Corrects: {self.correct}",
            text_color="green"
        ).pack(side=ctk.LEFT, padx=(100, 0))

        ctk.CTkLabel(
            stats_content_frame,
            text=f"❌ Incorrects: {self.incorrect}",
            text_color="red"
        ).pack(side=ctk.RIGHT, padx=(0, 100))


        # Answer List Frame

        self.scrollable_frame = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent", width=300)
        self.scrollable_frame.pack(fill=ctk.BOTH, expand=True, padx=5)

        inner_frame = ctk.CTkFrame(self.scrollable_frame)
        inner_frame.pack(fill=ctk.BOTH, expand=True, padx=5, pady=5)

        # History Label

        for item in self.w_history:
            if "user_answer" in item:
                self.multiple_choice_item(inner_frame, item, item['user_answer'], item['correct'])
        # Action Buttons Frame

        button_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        button_frame.pack(pady=10)

        # Buttons

       # retry_button = ctk.CTkButton(
          #  button_frame,
          ## retry_button.pack(side=ctk.LEFT, padx=8)

        from routes import return_to_main_menu, Retry
        from project import load_vocabulary
        vocabulary = load_vocabulary()
        ctk.CTkButton(
            button_frame,
            text="🏠 Main Menu",
            command=lambda: return_to_main_menu(self.root, self.main_frame),
            fg_color="#3B8ED0",
            hover_color="#36719F",
            text_color="white",
            border_width=0,
            width=30,
            height=30,
            corner_radius=20
            
        ).pack(anchor="s", pady=0)

        retry_button = Retry(
            parent=button_frame,
            root=self.root,
            current_frame=self.main_frame,
            vocabulary=self.root.session_settings['words']
        )
        retry_button.pack(anchor="s", pady=8)

    def multiple_choice_item(self, parent_frame, item, user_answer, correct):
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

        if not hasattr(self, 'columns_created'):
            self.columns_created = True
            self.current_column = 0

            self.col_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
            self.col_frame.pack(fill=ctk.BOTH, expand=True)

            self.left_column = ctk.CTkFrame(self.col_frame, fg_color="transparent")
            self.left_column.grid(row=0, column=0, sticky="nsew", padx=5)
            
            self.right_column = ctk.CTkFrame(self.col_frame, fg_color="transparent")
            self.right_column.grid(row=0, column=1, sticky="nsew", padx=5)

            self.col_frame.grid_columnconfigure(0, weight=1)
            self.col_frame.grid_columnconfigure(1, weight=1)
            self.col_frame.grid_rowconfigure(0, weight=1)

        target_column = self.left_column if self.current_column % 2 == 0 else self.right_column
        self.current_column += 1
    

        a_frame = ctk.CTkFrame(
            target_column,
            fg_color="transparent",
            border_width=2,
            border_color=("gray70", "gray30"),
            corner_radius=20,
            width=250,
            height=130
        )
        a_frame.pack_propagate(False)
        a_frame.pack(expand=False, anchor="w", padx=10, pady=5)

        content_frame = ctk.CTkFrame(
            a_frame,
            fg_color="transparent",
        )
        content_frame.pack(expand=True, fill=ctk.BOTH, padx=10, pady=10)

        content_frame.grid_columnconfigure(0, weight=1)
        for i in range(4):
            content_frame.grid_rowconfigure(i, weight=0)

        # Words

        w_label = ctk.CTkLabel(
            content_frame,
            text=question_text,
            fg_color="transparent",
            text_color="white",
            font=("Malgun Gothic", 14, "bold"),

        )
        w_label.pack(anchor="w")

        # User Answer

        status = "✔" if correct else "❌"
        color = "#2ecc71" if correct else "#e74c3c"

        u_label = ctk.CTkLabel(
            content_frame,
            text=f"{status} You Selected: {str(user_answer).capitalize()}",
            font=("Arial", 13),
            wraplength=200,
            text_color=color
        )
        u_label.pack(anchor="w")

        # Correct Answer (if incorrect)

        if not correct:
            c_label = ctk.CTkLabel(
                content_frame,
                text=f"✔ Correct Choice: {correct_answer}",
                font=("Arial", 13),
                text_color="#3B8ED0",
            )
            c_label.pack(anchor="w")

        difficulty_color = {
            'Easy': "#585858",
            'Medium': "#531083",
            'Hard': "#A78B12"    
        }

        dlabel = ctk.CTkLabel(
            content_frame,
            text=f"📑 Difficulty: {word['Difficulty']}",
            text_color=difficulty_color.get(word['Difficulty'], 'black')
        )
        dlabel.pack(anchor="w")


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

        
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill=ctk.BOTH, expand=True)

        # Title Label

        tlabel = ctk.CTkLabel(
            self.main_frame,
            text="🎯 Matching Game Results",
            font=("Arial", 16, "bold")
        )
        tlabel.pack(pady=10)

        self.statsframe = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent",
            border_width=2,
            border_color=("gray70", "gray30"),
            corner_radius=12,
            width=300
        )
        self.statsframe.pack(fill=ctk.X, pady=10)

        accuracy_label = ctk.CTkLabel(
            self.statsframe,
            text=f"• ✔ Accuracy: {self.accuracy:.0%}",
            font=("Arial", 16, "bold"),
            text_color="#13e263" if self.accuracy >= 0.75 else "#ff3a00" if self.accuracy >= 0.5 else "#ca1d10"
        )
        accuracy_label.pack(anchor="center", pady=5)

        attempts_label = ctk.CTkLabel(
            self.statsframe,
            text=f"• 📑 Attempts: {self.attempts}",
            font=("Arial", 16, "bold"),
            text_color="#12eccf" if self.attempts == 6 else "#ff6400" if 6 < self.attempts < 12 else "#E0115F"
        )
        attempts_label.pack(anchor="center", pady=5)

        wrong_label = ctk.CTkLabel(
            self.statsframe,
            text=f"• ❌ Incorrects: {self.incorrect}",
            font=("Arial", 16, "bold"),
            text_color="#4dd6a2" if self.incorrect == 0 else "#ff8f00" if 6 < self.incorrect < 12 else "#FF073A"
        )
        wrong_label.pack(anchor="center", pady=5)

        if hasattr(root, 'session_timer') and root.session_timer.should_display(self.settings):
            elapsed_time = root.session_timer.get_elapsed_time()
            time_text = f"• ⏱ Session Time: {root.session_timer.format_time(elapsed_time)}"
        else:
            time_text = ""

        time_label = ctk.CTkLabel(
            self.statsframe,
            text=time_text,
            font=("Arial", 16, "bold")
        )
        time_label.pack(anchor="center", pady=5)

        # Words List Frame

        words_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        words_frame.pack(fill=ctk.BOTH, expand=True, pady=(0, 20))

        wlabel = ctk.CTkLabel(
            words_frame,
            text="🔠 Words List",
            font=("Arial", 16, "bold")
        )
        wlabel.pack(anchor="center", pady=(0, 10))

        self.scrollable_frame = ctk.CTkScrollableFrame(
            words_frame,
            fg_color="transparent",
            width=300
        )
        self.scrollable_frame.pack(fill=ctk.BOTH, expand=True, padx=5)

        # inner_frame = ctk.CTkFrame(self.scrollable_frame)
        # inner_frame.pack(fill=ctk.BOTH, expand=True, padx=5, pady=5)

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
            self.add_word_pair(self.scrollable_frame, word)


        button_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        button_frame.pack(pady=10)

        from routes import return_to_main_menu, Retry
        from project import load_vocabulary
        vocabulary = load_vocabulary()

        Menu = ctk.CTkButton(
            button_frame,
            text="🏠 Main Menu",
            command=lambda: return_to_main_menu(self.root, self.main_frame),
            fg_color="#3B8ED0",
            hover_color="#36719F",
            text_color="white",
            border_width=0,
            width=30,
            height=30,
            corner_radius=20           
        )
        Menu.pack(anchor="s", pady=0)

        RetryB = Retry(
            parent=button_frame,
            root=self.root,
            current_frame=self.main_frame,
            vocabulary=self.root.session_settings['words']
        )
        RetryB.pack(anchor="s", pady=8)

    def add_word_pair(self, parent, word):
        from project import language_manager_flashcards

        a_frame = ctk.CTkFrame(
            parent,
            fg_color="transparent",
            border_width=2,
            border_color=("gray70", "gray30"),
            corner_radius=20,
            width=400,
            height=50
        )
        a_frame.pack_propagate(False)
        a_frame.pack(expand=False, fill=ctk.X, padx=22, pady=6)

        content_frame = ctk.CTkFrame(a_frame, fg_color="transparent")
        content_frame.pack(fill=ctk.BOTH, expand=True, padx=12, pady=3)

        content_frame.grid_rowconfigure(0, weight=1)       
        content_frame.grid_columnconfigure(0, weight=1)  
        content_frame.grid_columnconfigure(1, weight=3)  
        content_frame.grid_columnconfigure(2, weight=3)  
        content_frame.grid_columnconfigure(3, weight=2)  

        ctk.CTkLabel(
            content_frame,
            text=word['Hangul'],
            font=("Malgun Gothic", 15, "bold"),
            width=15,
            anchor="w",
        ).grid(row=0, column=0, padx=5, sticky="nsew")

        ctk.CTkLabel(
            content_frame,
            text="→",
            font=("Arial", 13),
            text_color="gray",
        ).grid(row=0, column=1, padx=5, sticky="ns")

        ctk.CTkLabel(
            content_frame,
            text=language_manager_flashcards.get_translations(word),
            font=("Arial", 15),
            anchor="center",
            wraplength=150
        ).grid(row=0, column=2, padx=5, sticky="nsew")

        # Difficulty Label

        difficulty_color = {
            'Easy': "#585858",
            'Medium': "#531083",
            'Hard': "#A78B12"
        }

        ctk.CTkLabel(
            content_frame,
            text=f"📑 Difficulty: {word['Difficulty']}",
            font=("Arial", 10),
            text_color=difficulty_color.get(word['Difficulty'], 'gray')
        ).grid(row=0, column=3, padx=(10, 5), sticky="nse")

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

        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill=ctk.BOTH, expand=True)

        if hasattr(self.root, 'session_timer') and self.root.session_timer.should_display(self.settings):
            elapsed_time = self.root.session_timer.get_elapsed_time()
            time_text = f"Session Time: {self.root.session_timer.format_time(elapsed_time)}"
        else:
            time_text = ""

        time_label = ctk.CTkLabel(
            self.main_frame,
            text=time_text,
            font=("Arial", 12)
        )
        time_label.pack(pady=10)

        tlabel = ctk.CTkLabel(
            self.main_frame,
            text="⚫ True or False Game Results",
            font=("Arial", 16, "bold")
        )
        tlabel.pack(pady=10)

        rlabel = ctk.CTkLabel(
            self.main_frame,
            text=f"Results: {self.correct}/{self.total} ({self.correct/self.total:.0%})",
            font=("Arial", 16, "bold")
        )
        rlabel.pack(pady=10)

        stats_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent",
            border_width=2,
            border_color=("gray70", "gray30"),
            corner_radius=4,
            width=300,
            height=50
        )
        stats_frame.pack_propagate(False)
        stats_frame.pack(expand=False, fill=ctk.X, pady=10, padx=10)

        stats_content_frame = ctk.CTkFrame(stats_frame, fg_color="transparent")
        stats_content_frame.pack(expand=True, fill=ctk.BOTH, pady=5, padx=5)

        ctk.CTkLabel(
            stats_content_frame,
            text=f"✔ Corrects: {self.correct}",
            text_color="green"
        ).pack(side=ctk.LEFT, padx=(100, 0))

        ctk.CTkLabel(
            stats_content_frame,
            text=f"❌ Incorrects: {self.incorrect}",
            text_color="red"
        ).pack(side=ctk.RIGHT, padx=(0, 100))

        self.scrollable_frame = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent", width=300)
        self.scrollable_frame.pack(fill=ctk.BOTH, expand=True, padx=5)

        inner_frame = ctk.CTkFrame(self.scrollable_frame)
        inner_frame.pack(fill=ctk.BOTH, expand=True, padx=5, pady=5)

        for item in self.w_history:
            self.add_result_item(inner_frame, item)

        # Buttons Frame

        button_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        button_frame.pack(pady=10)

        from routes import return_to_main_menu, Retry
        from project import load_vocabulary
        vocabulary = load_vocabulary()

        Menu = ctk.CTkButton(
            button_frame,
            text="🏠 Main Menu",
            command=lambda: return_to_main_menu(self.root, self.main_frame),fg_color="#3B8ED0",
            hover_color="#36719F",
            text_color="white",
            border_width=0,
            width=30,
            height=30,
            corner_radius=20        
        )
        Menu.pack(anchor="s", pady=0)

        RetryB = Retry(
            parent=button_frame,
            root=self.root,
            current_frame=self.main_frame,
            vocabulary=self.root.session_settings['words']
        )
        RetryB.pack(anchor="s", pady=8)

    def add_result_item(self, parent_frame, item):
        from project import language_manager_flashcards
        word = item['word']

        user_answer = str(item.get('user_answer', 'False')).capitalize()
        correct_answer = str(item.get('expected', 'False')).capitalize()
        is_correct = item.get('correct', False)

        user_answer = str(user_answer) if isinstance(user_answer, bool) else user_answer
        correct_answer = str(correct_answer) if isinstance(correct_answer, bool) else correct_answer

        # Answers List

        if not hasattr(self, 'columns_created'):
            self.columns_created = True
            self.current_column = 0

            self.col_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
            self.col_frame.pack(fill=ctk.BOTH, expand=True)

            self.left_column = ctk.CTkFrame(self.col_frame, fg_color="transparent")
            self.left_column.grid(row=0, column=0, sticky="nsew", padx=5)
            
            self.right_column = ctk.CTkFrame(self.col_frame, fg_color="transparent")
            self.right_column.grid(row=0, column=1, sticky="nsew", padx=5)

            self.col_frame.grid_columnconfigure(0, weight=1)
            self.col_frame.grid_columnconfigure(1, weight=1)
            self.col_frame.grid_rowconfigure(0, weight=1)

        target_column = self.left_column if self.current_column % 2 == 0 else self.right_column
        self.current_column += 1

        a_frame = ctk.CTkFrame(
            target_column,
            fg_color="transparent",
            border_width=2,
            border_color=("gray70", "gray30"),
            corner_radius=20,
            width=250,
            height=130
        )
        a_frame.pack_propagate(False)
        a_frame.pack(expand=False, anchor="w", padx=10, pady=5)

        content_frame = ctk.CTkFrame(a_frame, fg_color="transparent")
        content_frame.pack(expand=True, fill=ctk.BOTH, padx=10, pady=10)

        content_frame.grid_columnconfigure(0, weight=1)
        for i in range(4):
            content_frame.grid_rowconfigure(i, weight=0)
            
        w_label = ctk.CTkLabel(
            content_frame,
            text=f"Word: {item.get('question_word', '')}",
            font=("Arial", 14, "bold"),
            fg_color="transparent",
            text_color="white",
        )
        w_label.pack(anchor="w")

        q_label = ctk.CTkLabel(
            content_frame,
            text=f"Question: {item.get('statement_question', '')}",
            font=("Arial", 14),
            fg_color="transparent",
            text_color="white"
        )
        q_label.pack(anchor="w")

        status = "✔" if is_correct else "❌"
        color = "#2ecc71" if is_correct else "#e74c3c"
        
        u_label = ctk.CTkLabel(
            content_frame,
            text=f"{status} Your Answer: {user_answer}",
            font=("Arial", 12),
            text_color=color
        )
        u_label.pack(anchor="w")

        if not is_correct:
            c_label = ctk.CTkLabel(
                content_frame,
                text=f"Correct Answer: {correct_answer}",
                font=("Arial", 12),
                text_color="#3B8ED0"
            )
            c_label.pack(anchor="w")

        difficulty_color = {
            'Easy': "#585858",
            'Medium': "#531083",
            'Hard': "#A78B12"
        }

        d_label = ctk.CTkLabel(
            content_frame,
            text=f"📑 Difficulty: {word['Difficulty']}",
            text_color=difficulty_color.get(word['Difficulty'], 'black')
        )
        d_label.pack(anchor="w")

        # ctk.CTkLabel(
        #     frame,
        #     text=item['timestamp'],  # Funcionando mas amanha tentar botar em todos
        #     font=("Arial", 9),
        #     text_color="gray"
        # ).pack(side=ctk.RIGHT)


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
        
        self.total = self.correct + self.incorrect
        self.accuracy = self.correct / self.total if self.total > 0 else 0

        self.create_widgets(root)
           
    def create_widgets(self, root):
        for widget in self.root.winfo_children():
            widget.pack_forget()

        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill=ctk.BOTH, expand=True)

        if hasattr(self.root, 'session_timer') and getattr(self.root.session_timer, 'is_running', False):
            elapsed_time = self.root.session_timer.get_elapsed_time()
            time_text = f"Session Time: {self.root.session_timer.format_time(elapsed_time)}"
        else:
            time_text = ""
        
        time_label = ctk.CTkLabel(
            self.main_frame,
            text=time_text,
            font=("Arial", 12)
        )
        time_label.pack(pady=10)
        
        tlabel = T_CTkLabel(
            self.main_frame,
            text=f"📘 {translation.get_translation("standard_results")}", 
            font=("Arial", 16, "bold")
        )
        tlabel.pack(pady=10)

        rlabel = T_CTkLabel(
            self.main_frame,
            text=f"{translation.get_translation("results")}: {self.correct}/{self.total} ({self.accuracy:.0%})",
            font=("Arial", 16, "bold"),
        )
        rlabel.pack(pady=10)
            
        stats_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent",
            border_width=2,
            border_color=("gray70", "gray30"),
            corner_radius=4,
            width=300,
            height=50
        )
        stats_frame.pack_propagate(False)
        stats_frame.pack(expand=False, fill=ctk.X, pady=10, padx=10)

        stats_content_frame = ctk.CTkFrame(
            stats_frame,
            fg_color="transparent"
        )
        stats_content_frame.pack(expand=True, fill=ctk.BOTH, pady=5, padx=5)
        
        ctk.CTkLabel(
            stats_content_frame,
            text=f"✔ {translation.get_translation("corrects")}: {self.correct}",
            text_color="green"
        ).pack(side=ctk.LEFT, padx=(100, 0))
        
        ctk.CTkLabel(
            stats_content_frame,
            text=f"❌ {translation.get_translation("incorrects")}: {self.incorrect}",
            text_color="red"
        ).pack(side=ctk.RIGHT, padx=(0, 100))

        self.scrollable_frame = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent", width=300)
        self.scrollable_frame.pack(fill=ctk.BOTH, expand=True, padx=5)

        inner_frame = ctk.CTkFrame(self.scrollable_frame)
        inner_frame.pack(fill=ctk.BOTH, expand=True, padx=5, pady=5)

        for item in self.w_history:
            self.add_result_item(inner_frame, item)

        # Buttons Frame

        button_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        button_frame.pack(pady=10)
   
        from routes import return_to_main_menu, Retry
        from project import load_vocabulary
        vocabulary = load_vocabulary()

        Menu = ctk.CTkButton(
            button_frame,
            text=f"🏠 {translation.get_translation("main_menu")}",
            command=lambda: return_to_main_menu(self.root, self.main_frame),
            hover_color="#36719F",
            text_color="white",
            border_width=0,
            width=30,
            height=30,
            corner_radius=20        
        )
        Menu.pack(anchor="s", pady=0)

        RetryB = Retry(
            parent=button_frame,
            root=self.root,
            current_frame=self.main_frame,
            vocabulary=self.root.session_settings['words']
        )
        RetryB.pack(anchor="s", pady=8)

    def add_result_item(self, parent_frame, item):
        from project import language_manager_flashcards
        word = item['word']
        is_correct = item.get('correct', False)

        if not hasattr(self, 'columns_created'):
            self.columns_created = True
            self.current_column = 0

            self.col_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
            self.col_frame.pack(fill=ctk.BOTH, expand=True)

            self.left_column = ctk.CTkFrame(self.col_frame, fg_color="transparent")
            self.left_column.grid(row=0, column=0, sticky="nsew", padx=5)
            
            self.right_column = ctk.CTkFrame(self.col_frame, fg_color="transparent")
            self.right_column.grid(row=0, column=1, sticky="nsew", padx=5)

            self.col_frame.grid_columnconfigure(0, weight=1)
            self.col_frame.grid_columnconfigure(1, weight=1)
            self.col_frame.grid_rowconfigure(0, weight=1)

        target_column = self.left_column if self.current_column % 2 == 0 else self.right_column
        self.current_column += 1

        a_frame = ctk.CTkFrame(
            target_column,
            fg_color="transparent",
            border_width=2,
            border_color="#2ecc71" if is_correct else "#e74c3c",
            corner_radius=20,
            width=250,
            height=130
        )
        a_frame.pack_propagate(False)
        a_frame.pack(expand=False, anchor="w", padx=10, pady=5)

        content_frame = ctk.CTkFrame(a_frame, fg_color="transparent")
        content_frame.pack(expand=True, fill=ctk.BOTH, padx=10, pady=10)

        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=0)
        content_frame.grid_rowconfigure(0, weight=1)

        content_frame.grid_columnconfigure(0, weight=1)
        for i in range(4):
            content_frame.grid_rowconfigure(i, weight=0)

        status = "✔" if is_correct else "✖"
        status_color = "#2ecc71" if is_correct else "#e74c3c"

        top_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        top_frame.grid(row=0, column=0, columnspan=2, sticky="nsew")
        top_frame.grid_columnconfigure(0, weight=1)
        top_frame.grid_columnconfigure(1, weight=0)

        w_label = ctk.CTkLabel(
            top_frame,
            text=word['Hangul'] if self.settings['study_direction'] == "hangul_to_lang" else language_manager_flashcards.get_translations(word),
            text_color="white",
            fg_color="transparent",
            font=("Malgun Gothic", 16, "bold") if self.settings['study_direction'] == "hangul_to_lang" else ("Arial", 16)
        )
        w_label.grid(row=0, column=0, sticky="w")

        status_label = ctk.CTkLabel(
            top_frame,
            text=status,
            text_color=status_color
        )
        status_label.grid(row=0, column=1, sticky="e")

        tdlabel = ctk.CTkLabel(
            content_frame,
            text=f"→ {language_manager_flashcards.get_translations(word)}" if self.settings['study_direction'] == "hangul_to_lang" else f"→ {word['Hangul']}",
            font=("Arial", 16) if self.settings['study_direction'] == "hangul_to_lang" else ("Malgun Gothic", 16),
            text_color="white",
            fg_color="transparent"
        )
        tdlabel.grid(row=1, column=0, columnspan=2, sticky="w", pady=(5, 0))

        difficulty_color = {
            'Easy': "#585858",
            'Medium': "#531083",
            'Hard': "#A78B12"    
        }
        
        dlabel = ctk.CTkLabel(
            content_frame,
            text=f"📑 {translation.get_translation("difficulty")}: {translation.get_difficulty_translation(word['Difficulty'])}",
            text_color=difficulty_color.get(word['Difficulty'], "black")
        )
        dlabel.grid(row=2, column=0, columnspan=2, sticky="w", pady=(5, 0))
        
        # ctk.CTkLabel(
        #     bottom_frame,
        #     text=item['timestamp'],   # Funcionando mas amanha tentar botar em todos
        #     font=("Arial", 9),
        #     text_color="gray"
        # ).pack(side=ctk.RIGHT)