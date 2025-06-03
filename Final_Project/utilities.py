import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from customtkinter import *
from tkinter import ttk, messagebox
import time
from language_manager import InterfaceTranslator

translations = InterfaceTranslator()

# Progress Bar

class ProgressBar:
    def __init__(self, root, total_questions):
        self.root = root
        self.total_questions = total_questions
        self.current_question = 0

        # Progress Bar Frame

        self.progress_frame = ctk.CTkFrame(self.root, fg_color="transparent", bg_color="transparent")
        self.progress_frame.pack(fill=ctk.X, pady=10)

        # Progress Bar

        self.bar = ctk.CTkProgressBar(
            self.progress_frame,
            orientation="horizontal",
            width=300,
            height=10,
            mode="determinate"
        )
        self.bar.set(0)
        self.bar.pack(fill=ctk.X, expand=True)

        # Progress text

        self.percent_label = ctk.CTkLabel(
            self.progress_frame,
            text=f"{self.current_question} {translations.get_translation("of")} {self.total_questions}"
        )
        self.percent_label.pack()


        # Progress Bar Increment

    def increment(self):
        self.current_question += 1
        self.update_display()

    def update_display(self):
        progress = self.current_question / self.total_questions
        self.bar.set(progress)
        self.percent_label.configure(
            text=f"{self.current_question} {translations.get_translation("of")} {self.total_questions}"
        )

    def reset(self, new_total=None):
        if new_total:
            self.total_questions = new_total
        self.current_question = 0
        self.bar.set(0)
        self.update_display()


## Used for Tkinter -- No more using -- 

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
    

## Still not in use ##

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


