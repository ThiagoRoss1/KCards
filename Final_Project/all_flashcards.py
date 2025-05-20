import tkinter as tk
from tkinter import ttk, messagebox
import csv
import random
from results_screen import ResultsScreen
from language_manager import LanguageManager
from datetime import datetime
from unicodedata import normalize, combining

def normalize_text(text):
    text = str(text).strip().lower()
    text = normalize('NFKD', text)
    text = ''.join([c for c in text if not combining(c)])

    return text

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
            if settings['study_direction'] == "hangul_to_lang":
                new_word['Question'] = word['Hangul']
                new_word['Answer'] = language_manager_flashcards.get_translations(word).lower()
            else:
                new_word['Question'] = language_manager_flashcards.get_translations(word)
                new_word['Answer'] = word['Hangul'].lower()

            prepared_words.append(new_word)
        
        return prepared_words

    def setup_ui(self):
        self.frame = ttk.Frame(self.root, padding=20)
        self.frame.pack(fill=tk.BOTH, expand=True)

        if self.settings.get('timer_enabled', False):
            self.timer_label = ttk.Label(self.frame, text="00:00")
            self.timer_label.pack(anchor="se")

        # Progress Bar
        from utilities import ProgressBar
        self.progress = ProgressBar(self.frame, len(self.words))

        # Configured Word Label
        label_font = ("Malgun Gothic", 20) if self.settings['study_direction'] == "hangul_to_lang" else ("Arial", 20)
        entry_font = ("Malgun Gothic", 16) if self.settings['study_direction'] == "lang_to_hangul" else ("Arial", 16)

        self.word_label = ttk.Label(
            self.frame,
            font=label_font
        )
        self.word_label.pack(pady=20)

        self.answer_entry = ttk.Entry(
            self.frame,
            font=entry_font,
            width=30
        )
        self.answer_entry.pack(pady=5)
        self._setup_entry_placeholder()

        # Key Bindings
        self.answer_entry.bind("<Return>", lambda _: self.check_answer())

    def update_timer(self):
        if not hasattr(self, 'timer_label') or not hasattr(self.root, 'session_timer'):
            return
        
        elapsed = self.root.session_timer.get_elapsed_time()
        self.timer_label.config(
            text=self.root.session_timer.format_time(elapsed)
        )

        if self.settings.get('timer_enabled', False):
            self.root.after(1000, self.update_timer)

    def _setup_entry_placeholder(self):
        self.answer_entry.insert(0, "Type your answer")
        self.answer_entry.config(foreground="gray")
        self.answer_entry.icursor(0)
        self.answer_entry.focus()
        
        self.answer_entry.bind("<Key>", self._handle_entry_key)

    def _handle_entry_key(self, _):
        if self.answer_entry.get() == "Type your answer":
            self.answer_entry.delete(0, tk.END)
            self.answer_entry.config(foreground="#000000")

    def check_answer(self):
        user_input = self.answer_entry.get().lower().strip()
        expected = self.expected_answer

        user_normalized = normalize_text(user_input)
        expected_normalized = normalize_text(expected)

        is_correct = user_normalized == expected_normalized
        exact_match = user_input.lower().strip() == expected.lower().strip()

        if is_correct:
            self.correct += 1
        else:
            self.incorrect += 1
            
        self.progress.increment()
        
        self.word_history.append({
            "word": self.current_word,
            "user_answer": user_input,
            "correct": is_correct,
            "expected": self.expected_answer,
            "study_direction": self.settings['study_direction'],
            "exact_match": exact_match
        })
        
        self.next_word()

    def next_word(self):
        self.used_words.append(self.current_word)
        
        available_words = [word for word in self.words if word not in self.used_words]
        
        if available_words:
            self.current_word = random.choice(available_words)

            if self.settings['study_direction'] == "hangul_to_lang":
                self.word_label.config(
                    text=self.current_word['Question'],
                    font=("Malgun Gothic", 20)
                )
            else:
                self.word_label.config(
                    text=self.current_word['Question'],
                    font=("Arial", 20)
                )
            
            self.expected_answer = self.current_word['Answer'].lower()
            self._reset_entry()

        else:
            self._end_session()

    def _reset_entry(self):
        self.answer_entry.delete(0, tk.END)
        self.answer_entry.insert(0, "Type your answer")
        self.answer_entry.config(foreground="gray")
        self.answer_entry.icursor(0)

    def _end_session(self):
        self.frame.pack_forget()
        self.progress.reset()
        
        from routes import return_to_main_menu
        ResultsScreen(
            self.root,
            self.correct,
            self.incorrect,
            self.word_history,
            lambda: return_to_main_menu(self.root, self.frame)
        )





# def input_practice(root, words):

#     word_history = []

#     # Input practice module

#     s_frame = ttk.Frame(root, padding=20)
#     s_frame.pack(fill=tk.BOTH, expand=True)

#     # Progress Bar

#     from utilities import ProgressBar
#     progress = ProgressBar(s_frame, len(words))

#     # Variables 

#     used_words = []
#     current_word = random.choice(words)
#     correct = 0
#     incorrect = 0 
#     user_answer = tk.StringVar()

#     # Word Label

#     w_label = ttk.Label(
#         s_frame,
#         text=current_word['Hangul'],
#         font=("Malgun Gothic", 32),

#     )
#     w_label.pack(pady=20)

#     # Answer Entry

#     a_entry = ttk.Entry(
#         s_frame,
#         font=("Arial", 16),
#         width=30,
#     )
#     a_entry.pack(pady=5)

#     def show_placeholder():
#         a_entry.insert(0, "Type your answer")
#         a_entry.config(foreground="gray")
#         a_entry.icursor(0)

#     def hide_placeholder():
#         if a_entry.get() == "Type your answer":
#             a_entry.insert(0, "")
#             a_entry.delete(0, tk.END)
#         a_entry.config(foreground="#000000")

#     # Initial Config

#     show_placeholder()
#     a_entry.focus()
#     a_entry.icursor(0)

#     def on_key(_):
#         if a_entry.get() == "Type your answer":
#             hide_placeholder()

#     a_entry.bind("<Key>", on_key)

#     # Check Answer function

#     def check_answer():
#         nonlocal correct, incorrect, user_answer
        
#         user_input = a_entry.get().lower().strip()
#         from project import LanguageManager, language_manager_flashcards
#         translation = language_manager_flashcards.get_translations(current_word)
#         is_correct = user_input.lower().strip() == translation.lower()
#         if user_input.lower() == translation.lower():
#             correct += 1
#             progress.increment()

#         else:
#             incorrect += 1
#             progress.increment()

#         word_history.append({
#             "word": current_word,
#             "user_answer": user_input,
#             "correct": is_correct
#         })

#         next_word()
            

#     def next_word():
#         nonlocal current_word, used_words

#         used_words.append(current_word)

#         # Check used words to avoid repetition

#         available_words = [word for word in words if word not in used_words]

#         if available_words:
#             current_word = random.choice(available_words)
#             w_label.config(text=current_word['Hangul'])

#             # Reset Placeholder
#             a_entry.after(10, lambda: [
#                 a_entry.delete(0, tk.END),
#                 show_placeholder(),
#                 a_entry.focus()
#             ])
            
#         else:
#             if correct + incorrect > 0:
#                 s_frame.pack_forget()
#                 progress.reset()
#                 from routes import return_to_main_menu
#                 ResultsScreen(root, correct, incorrect, word_history,
#                               lambda: return_to_main_menu(root, s_frame))
#             messagebox.showinfo("End of Session!", "You have gone through all words!")
#             used_words = []

#     # Key Binding

#     a_entry.bind("<Return>", lambda _: check_answer())


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

    def prepare_words(self, words, settings):
        from project import language_manager_flashcards
        prepared_words = []

        for word in words:
            new_word = word.copy()
            if settings['study_direction'] == "hangul_to_lang":
                new_word['Question'] = word['Hangul']
                new_word['Answer'] = language_manager_flashcards.get_translations(word)
            else:
                new_word['Question'] = language_manager_flashcards.get_translations(word)
                new_word['Answer'] = word['Hangul']

            prepared_words.append(new_word)

        return prepared_words

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
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'expected': self.current_word['Answer'],
            'study_direction': self.settings['study_direction']
        })

        if self.settings['show_styles']:
            self.update_button_styles(selected_answer)
        else:
            for btn in self.answer_buttons:
                btn.config(state=tk.DISABLED)

        self.root.after(1000, self.next_question)

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

        self.card_width = 6
        self.card_height = 4
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
        game_words = words[:6]
        settings = settings.copy()
        pairs = []

        for word in game_words:
            pairs.append({
                'type': 'hangul',
                'text': word['Hangul'],
                'match_id': word['Hangul'],
                'translation': language_manager_flashcards.get_translations(word),
            })
            pairs.append({
                'type': 'translation',
                'text': language_manager_flashcards.get_translations(word),
                'match_id': word['Hangul']
            })

        random.shuffle(pairs)
        return pairs
    
    def setup_ui(self):
        self.frame = ttk.Frame(self.root, padding=20)
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Change the background color of the main frame and cards frame
        bg_color = "#b6badb"  # Set your desired background color here

        self.frame.configure(style="Custom.TFrame")
        style = ttk.Style()
        style.configure("Custom.TFrame", background=bg_color)

        if self.settings.get('timer_enabled', False):
            self.timer_label = ttk.Label(self.frame, text="00:00", background=bg_color)
            self.timer_label.pack(anchor="se")

        container = ttk.Frame(self.frame, style="Custom.TFrame")
        container.pack(expand=True, fill=tk.BOTH)

        self.cards_frame = ttk.Frame(container, style="Custom.TFrame")
        self.cards_frame.pack(expand=True, anchor="center")

        self.setup_grid()

        self.create_cards()

    def setup_grid(self):
        for i in range(3):
            self.cards_frame.grid_rowconfigure(i, weight=0, minsize=120)
        for i in range(4):
            self.cards_frame.grid_columnconfigure(i, weight=0, minsize=160)

    def update_timer(self):
        if not hasattr(self, 'timer_label') or not hasattr(self.root, 'session_timer'):
            return
        
        elapsed = self.root.session_timer.get_elapsed_time()
        self.timer_label.config(
            text=self.root.session_timer.format_time(elapsed)
        )

        if self.settings.get('timer_enabled', False):
            self.root.after(1000, self.update_timer)

    def create_cards(self):
        # Grid 3x4

        self.cards = []
        card_bg = "#f0f0f8"
        card_fg = "#0A0A0A"
        for i in range(12):
            row, col = divmod(i, 3)
            card = tk.Label(
                self.cards_frame,
                text=self.words[i]['text'],
                font=("Malgun Gothic", 16) if self.words[i]['type'] == 'hangul' else ("Arial", 16),
                relief="raised",
                width=self.card_width,
                height=self.card_height,
                wraplength=150,
                padx=10,
                pady=10,
                cursor="hand2",
                bg=card_bg,
                fg=card_fg,
                bd=2
            )
            card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            card.bind("<Button-1>", lambda e, idx=i: self.card_click(idx))
            self.cards.append(card)

            card.grid_info()['original_pos'] = (row, col)

    def window_resize(self, event):
        new_width = max(12, min(20, int(event.width / 80)))
        if new_width != self.card_width:
            self.card_width = new_width
            for card in self.cards:
                if card.winfo_ismapped():
                    card.config(width=self.card_width)

    def card_click(self, card_index):
        # Check if card is already selected
        selected_indices = [c[0] for c in self.selected_cards]
        card = self.cards[card_index]

        if card_index in selected_indices:
            # Deselect the card if already selected
            card.config(relief="raised", bg="#f0f0f8")
            self.selected_cards = [c for c in self.selected_cards if c[0] != card_index]
            return

        if len(self.selected_cards) >= 2:
            return

        card.config(relief="sunken")
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
            card1.config(bg="#96F97B", relief="flat")
            card2.config(bg="#96F97B", relief="flat")
            self.matched_pairs += 1
            self.selected_cards = []
            self.root.after(500, lambda: self.remove_cards(card1, card2))

            if self.matched_pairs == 6:
                self.root.after(500, lambda: self.end_game())
        
        else:
            card1.config(bg="#FF6347")
            card2.config(bg="#FF6347")
            self.root.after(500, self.reset_cards)

    def remove_cards(self, card1, card2):
        card1_pos = card1.grid_info()
        card2_pos = card2.grid_info()

        card1.grid_remove()
        card2.grid_remove()

        # Invisible Placeholders
        if 'row' in card1_pos and 'column' in card1_pos:
            placeholder1 = tk.Label(self.cards_frame, text="", width=self.card_width, height=self.card_height)
            placeholder1.grid(row=card1_pos['row'], column=card1_pos['column'], padx=5, pady=5, sticky="nsew")
            placeholder1.lower()
        
        if 'row' in card2_pos and 'column' in card2_pos:
            placeholder2 = tk.Label(self.cards_frame, text="", width=self.card_width, height=self.card_height)
            placeholder2.grid(row=card2_pos['row'], column=card2_pos['column'], padx=5, pady=5, sticky="nsew")
            placeholder2.lower()

    def reset_cards(self):
        for idx, card in self.selected_cards:
            card.config(bg="SystemButtonFace", relief="raised")
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
        
        
        # (
        #     self.root,
        #     correct=self.matched_pairs,
        #     incorrect=self.attempts - self.matched_pairs,
        #     w_history=history,
        #     pairs=self.max_pairs,
        #     attempts=self.attempts,
        #     accuracy=self.matched_pairs / self.attempts if self.attempts > 0 else 0.0,
        #     return_callback=lambda: return_to_main_menu(self.root, self.frame),
        #     settings=self.settings
        # )