import tkinter as tk
from tkinter import ttk, messagebox
import csv
import random
from results_screen import ResultsScreen
from language_manager import LanguageManager
from datetime import datetime



def standard_flashcards(root, words):

    # Standard flashcards module

    s_frame = ttk.Frame(root, padding=20)
    s_frame.pack(fill=tk.BOTH, expand=True)

    # Variables

    used_words = []
    current_word = random.choice(words)
    showing_translation = False

    # Card

    style = ttk.Style()
    style.configure(
        "Card.TLabel",
        font=("Malgun Gothic", 36),
        relief="solid",
        padding=40,
        anchor="center",
        wraplength=400
    )

    # Label UI

    card = ttk.Label(
        s_frame,
        text=current_word['Hangul'],
        style="Card.TLabel",
        cursor="hand2"
    )
    card.pack(expand=True)

    # Def a function to flip the card

    def flip_card(_):
        if card.cget("text") == current_word['Hangul']:
            from project import LanguageManager, language_manager_flashcards
            translation = language_manager_flashcards.get_translations(current_word)
            card.config(text=translation, font=("Arial", 36)) # mudar futuramente ao adicionar ingles 
        else:
            card.config(text=current_word['Hangul'], font=("Malgun Gothic", 36))
    
    # Flip Action

    card.bind("<Button-1>", flip_card)

    # Next Word Button

    n_button = ttk.Button(
        s_frame,
        text="Next Word",
        command=lambda: next_word()
    )
    n_button.pack(pady=20)

    # Update Card function

    def next_word():
        nonlocal current_word, used_words

        used_words.append(current_word)

        # Check used words to avoid repetition

        available_words = [word for word in words if word not in used_words]

        if available_words:
            current_word = random.choice(available_words)
            card.config(text=current_word['Hangul'], font=("Malgun Gothic", 36))
        else:
            messagebox.showinfo("End of Session!", "You have gone through all words!")
            used_words = []


def input_practice(root, words):

    word_history = []

    # Input practice module

    s_frame = ttk.Frame(root, padding=20)
    s_frame.pack(fill=tk.BOTH, expand=True)

    # Progress Bar

    from utilities import ProgressBar
    progress = ProgressBar(s_frame, len(words))

    # Variables 

    used_words = []
    current_word = random.choice(words)
    correct = 0
    incorrect = 0 
    user_answer = tk.StringVar()

    # Word Label

    w_label = ttk.Label(
        s_frame,
        text=current_word['Hangul'],
        font=("Malgun Gothic", 32),

    )
    w_label.pack(pady=20)

    # Answer Entry

    a_entry = ttk.Entry(
        s_frame,
        font=("Arial", 16),
        width=30,
    )
    a_entry.pack(pady=5)

    def show_placeholder():
        a_entry.insert(0, "Type your answer")
        a_entry.config(foreground="gray")
        a_entry.icursor(0)

    def hide_placeholder():
        if a_entry.get() == "Type your answer":
            a_entry.insert(0, "")
            a_entry.delete(0, tk.END)
        a_entry.config(foreground="#000000")

    # Initial Config

    show_placeholder()
    a_entry.focus()
    a_entry.icursor(0)

    def on_key(_):
        if a_entry.get() == "Type your answer":
            hide_placeholder()

    a_entry.bind("<Key>", on_key)

    # Check Answer function

    def check_answer():
        nonlocal correct, incorrect, user_answer
        
        user_input = a_entry.get().lower().strip()
        from project import LanguageManager, language_manager_flashcards
        translation = language_manager_flashcards.get_translations(current_word)
        is_correct = user_input.lower().strip() == translation.lower()
        if user_input.lower() == translation.lower():
            correct += 1
            progress.increment()

        else:
            incorrect += 1
            progress.increment()

        word_history.append({
            "word": current_word,
            "user_answer": user_input,
            "correct": is_correct
        })

        next_word()
            

    def next_word():
        nonlocal current_word, used_words

        used_words.append(current_word)

        # Check used words to avoid repetition

        available_words = [word for word in words if word not in used_words]

        if available_words:
            current_word = random.choice(available_words)
            w_label.config(text=current_word['Hangul'])

            # Reset Placeholder
            a_entry.after(10, lambda: [
                a_entry.delete(0, tk.END),
                show_placeholder(),
                a_entry.focus()
            ])
            
        else:
            if correct + incorrect > 0:
                s_frame.pack_forget()
                progress.reset()
                from routes import return_to_main_menu
                ResultsScreen(root, correct, incorrect, word_history,
                              lambda: return_to_main_menu(root, s_frame))
            messagebox.showinfo("End of Session!", "You have gone through all words!")
            used_words = []

    # Key Binding

    a_entry.bind("<Return>", lambda _: check_answer())


# Multiple choice Game Mode

class MultipleChoiceGame:
    def __init__(self, root, words, settings):
        self.root = root
        self.words = words.copy()
        self.settings = settings
        self.current_word = None
        self.correct = 0
        self.incorrect = 0
        self.score = 0
        self.used_words = []  # Talvez tirar esse used_words ao adicionar o sistema de revisao espaçada
        self.history = []
        self.buttons_locked = False

        self.setup_ui()

        if settings.get('timer_enabled', False):
            from utilities import SessionTimer
            if not hasattr(root, 'session_timer'):
                root.session_timer = SessionTimer()
                root.session_timer.start()
            self.update_timer()
        # self.settings.setdefault('study_direction', 'hangul_to_lang')
        # self.settings.setdefault('show_styles', True)
        # self.settings.setdefault('timer_enabled', False)

        self.next_question()

    def setup_ui(self):
        self.frame = ttk.Frame(self.root, padding=20)
        self.frame.pack(fill=tk.BOTH, expand=True)

        from utilities import ProgressBar
        self.progress = ProgressBar(self.frame, len(self.words))

        self.question_label = ttk.Label(
            self.frame,
            font=("Malgun Gothic", 20) if self.settings['study_direction'] == "hangul_to_lang" else ("Arial", 20),
            wraplength=500,
        )
        self.question_label.pack(pady=20)

        if self.settings.get('timer_enabled', False):
            self.timer_label = ttk.Label(self.frame, text="00:00")
            self.timer_label.pack(anchor="se")

        # Answer Buttons
        self.answer_buttons = []
        for _ in range(4):
            a_button = ttk.Button(
                self.frame,
            )
            a_button.pack(pady=5, fill=tk.X)
            self.answer_buttons.append(a_button)


    def update_timer(self):
        if not hasattr(self, 'timer_label') or not hasattr(self.root, 'session_timer'):
            return
        
        elapsed = self.root.session_timer.get_elapsed_time()
        self.timer_label.config(
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

        available_words = [word for word in self.words if word not in self.used_words]

        if not available_words:
            self.show_results()
            return
        

        self.current_word = random.choice(available_words)
        self.used_words.append(self.current_word)

        options = self.generate_options(self.current_word['Answer'])

        self.question_label.config(text=self.current_word['Question'])

        for button, answer in zip(self.answer_buttons, options):
            button.config(
                text=answer,
                command=lambda a=answer: self.check_answer(a),
                style="TButton",
                state=tk.NORMAL
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
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        if self.settings['show_styles']:
            self.update_button_styles(selected_answer)
        else:
            for btn in self.answer_buttons:
                btn.config(state=tk.DISABLED)

        self.root.after(1200, self.next_question)

    def update_button_styles(self, selected_answer):
        for btn in self.answer_buttons:
            btn.config(state=tk.DISABLED)
            if btn['text'] == self.current_word['Answer']:
                btn.config(style="Correct.TButton")
            elif btn['text'] == selected_answer:
                btn.config(style="Incorrect.TButton")
            else:
                btn.config(style="TButton")


        # style = ttk.Style()
        # style.configure(
        #     "Correct.TButton",
        #     background="green", 
        #     foreground="white",
        # )
        # style.configure(
        #     "Incorrect.TButton",
        #     background="red",
        #     foreground="white",
        # )

    def show_results(self):
        from results_screen import ResultsScreen
        from routes import return_to_main_menu

        self.frame.pack_forget()
        ResultsScreen(
            self.root,
            self.correct,
            self.incorrect,
            self.history,
            lambda: return_to_main_menu(self.root, self.frame)
        )
        self.used_words = []
        self.progress.reset()










        

    #     self.next_question()

    # def generate_options(self, correct_word):
    #     wrong_words = random.sample(
    #         [word for word in self.words if word != correct_word],
    #         3
    #     )
    #     from project import language_manager_flashcards
    #     correct_word = language_manager_flashcards.get_translations(correct_word)
    #     options = [(correct_word, True)]
    #     options.extend([
    #         (language_manager_flashcards.get_translations(word), False)
    #         for word in wrong_words
    #     ])
    #     random.shuffle(options)
    #     return options[:4]
    
    # def check_answer(self, option_index):
    #     selected_option = self.answer_buttons[option_index]

    #     for a_button in self.answer_buttons:
    #         a_button.config(state=tk.DISABLED)

    #     self.history.append({
    #         'word': self.current_word,
    #         'selected_option': selected_option.cget("text"),
    #         'selected_correct': selected_option.correct,
    #         'correct_option': selected_option.correct_text
    #     })

    #     if selected_option.correct:
    #         selected_option.config(style="Correct.TButton")
    #         self.correct += 1
    #         self.score += 1
    #     else:
    #         selected_option.config(style="Incorrect.TButton")
    #         self.incorrect += 1

    #         for a_button in self.answer_buttons:
    #             if a_button.correct:
    #                 a_button.config(style="Correct.TButton")

    #     self.root.after(1200, self.next_question)


    # def next_question(self):

    #     available_words = [word for word in self.words if word not in self.used_words]

    #     if not available_words:
    #         self.frame.pack_forget()
    #         from routes import return_to_main_menu
    #         ResultsScreen(self.root, self.correct, self.incorrect, self.history,
    #                       lambda: return_to_main_menu(self.root, self.frame))
    #         return


    #     self.current_word = random.choice(available_words)

    #     ### Non Repeated Words ###
    #     self.used_words.append(self.current_word)
    #     ### Maybe remove this later ###

    #     options = self.generate_options(self.current_word)

    #     self.question_label.config(text=self.current_word['Hangul']) # Change when adding the reverse mode

    #     for i in range(4):
    #         if i < len(options):
    #             text, is_correct = options[i]
    #             self.answer_buttons[i].config(
    #                 text=text,
    #                 state=tk.NORMAL,
    #                 style="TButton"
    #             )
    #             self.answer_buttons[i].correct = is_correct
    #             from project import language_manager_flashcards
    #             self.answer_buttons[i].correct_text = language_manager_flashcards.get_translations(self.current_word)
    #         else:
    #             self.answer_buttons[i].config(state=tk.DISABLED, text="")


    # def reset_next_question(self):
    #     for a_button in self.answer_buttons:
    #         a_button.config(state=tk.NORMAL)
    #         a_button.config(style="TButton")

    #     self.frame.pack_forget()
        





    



    

            