#CS50P Final Project 
import tkinter as tk
from tkinter import ttk, messagebox
import csv
import random
import all_flashcards
from all_flashcards import StandardFlashcards, InputPractice, MultipleChoiceGame, MatchingGame, TrueFalseGame
import routes
from language_manager import LanguageManager
from utilities import CustomizeStudySession
from utilities import SessionTimer



language_manager_flashcards = LanguageManager()


def main():

    # Main function to run the application
    
    root = tk.Tk()

    def configure_hangul_support():
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass

        root.option_add("*Font", ("Malgun Gothic", 10))

    configure_hangul_support()

    # Loads Vocabulary function
    vocabulary = load_vocabulary()

    # Starts the GUI
    myapp_gui(root)

    main_menu_gui(root, vocabulary)

    root.mainloop()


def myapp_gui(root):

    # Graphical User Interface

    root.title("Flashcard App - Coreano")
    root.geometry("600x700")
    # root.minsize(400, 300)
    # root.columnconfigure(0, weight=1)   # Resize uniforme, ver depois
    # root.rowconfigure(0, weight=1)
    root.resizable(True, True)

    style = ttk.Style()
    style.configure(
        "Correct.TButton",
        background="green",          # Funcionando (Testado apenas no Multiple Choice)
        foreground="white",
    )
    style.configure(
        "Incorrect.TButton",
        background="red",
        foreground="white",
    )

def load_vocabulary(filepath='vocabulary.csv'):

    # Load vocabulary from a CSV file

    try:
        with open(filepath, "r", encoding="utf-8") as file:
            reader = list(csv.DictReader(file))
            return reader
    except FileNotFoundError:
        messagebox.showerror("Error", f"File not found: {filepath}")
        return []
    

def main_menu_gui(root, vocabulary):

    # Main menu GUI

    n_selection_frame = ttk.Frame(root, padding=20)
    n_selection_frame.pack(fill=tk.BOTH, expand=True)

    n_t_label = ttk.Label(
        n_selection_frame,
        text="Korean Flashcards App",
        font=("Arial", 22, "bold")
    )
    n_t_label.pack(pady=10)

    n_b_label = ttk.Label(
        n_selection_frame,
        text="Select a Level",
        font=("Arial", 16, "bold")
    )
    n_b_label.pack(pady=10)

    buttons_frame = ttk.Frame(n_selection_frame)
    buttons_frame.pack(pady=20)

    levels = sorted(set(word['Level'] for word in vocabulary))

    # All Levels button
    levels.append("All Levels")

    # Auto Button generator

    for _, level in enumerate(levels[:-1]):

        if level == "All Levels":
            button_style = "Accent.TButton"
        
        else:
            button_style = "TButton"

        button = ttk.Button(
            buttons_frame,
            text=f"{level}",
            style=button_style,
            command=lambda _=level: setup_module_selection(root, vocabulary, selected_frame=n_selection_frame)
        )
        button.grid(row=_//3, column=_%3, padx=10, pady=10, ipadx=10, ipady=10)

    # All levels button

    # a_button = ttk.Button(
    #     buttons_frame,
    #     text="All Levels",
    #     style="Accent.TButton",
    #     command=lambda: setup_module_selection(root, vocabulary, selected_frame=n_selection_frame)  # Esta funcionando, mas eu queria que chamasse direto o Choose Study Mode
    # )
    # a_button.grid(row=(len(levels)-1)//3 + 1, column=0, columnspan=3, pady=20, ipadx=10, ipady=5)


def setup_module_selection(root, vocabulary, selected_frame):

    # Remove the previous frame

    selected_frame.pack_forget()


    # Setup the module selection frame

    selection_frame = ttk.Frame(root, padding=20)
    selection_frame.pack(fill=tk.BOTH, expand=True)

    ttk.Label(
        selection_frame,
        text="Select a Module",
        font=("Arial", 16, "bold")
        ).pack(pady=10
    )

    # Language Button

    language_container = ttk.Frame(selection_frame)
    language_container.pack(pady=10)

    language_button = ttk.Button(
        language_container,
        text=f"🌎 {language_manager_flashcards.get_language()[:3]}",
        command=lambda: toggle_language_controls()
    )
    language_button.pack()

    controls_frame = ttk.Frame(language_container)

    # Combobox

    language_combobox = ttk.Combobox(
        controls_frame,
        values=["English", "Portuguese"],
        state="readonly",
    )
    language_combobox.pack(side="top")

    # Confirm Button

    confirm_button = ttk.Button(
        controls_frame,
        text="✔",
        command=lambda: confirm_language()
    )
    confirm_button.pack(side="top")

    controls_frame.pack_forget()

    def toggle_language_controls():
        if controls_frame.winfo_ismapped():
            controls_frame.pack_forget()
        else:
            language_combobox.set(language_manager_flashcards.get_language())
            language_combobox.focus()
            controls_frame.pack()


    def confirm_language():
        selected_lang = language_combobox.get()
        if selected_lang in ["English", "Portuguese"]:
            language_manager_flashcards.set_language(selected_lang)
            language_button.config(text=f"🌎 {selected_lang[:3]}")
            controls_frame.pack_forget()
            
    # Modules buttons

    buttons_frame = ttk.Frame(selection_frame)
    buttons_frame.pack(pady=20)

    # Get all modules from vocabulary.csv

    modules = sorted(set(word["Module"] for word in vocabulary), key=int)

    modules.append("All Modules")


    for _, module in enumerate(modules[:-1]):

        if module == "All Modules":
            button_style = "Accent.TButton"
        
        else:
            button_style = "TButton"

        button = ttk.Button(
            buttons_frame,
            text=f"Module {module}",
            style=button_style,
            command=lambda m=module: start_session(root, selection_frame, vocabulary, m)
        )
        button.grid(row=_//3, column=_%3, padx=10, pady=10, ipadx=10, ipady=10)

    # All Modules button

    all_button = ttk.Button(
        buttons_frame,
        text="All Modules",
        style="Accent.TButton",
        command=lambda: start_session(root, selection_frame, vocabulary, "All Modules")
    )
    all_button.grid(row=(len(modules)-1)//3 + 1, column=0, columnspan=3, pady=20, ipadx=10, ipady=5)

    # Return to Main Menu

    from routes import return_to_main_menu
    m_menu = ttk.Button(
        buttons_frame,
        text="Back",
        command=lambda: [selection_frame.pack_forget(), return_to_main_menu(root, buttons_frame)]
    )
    m_menu.grid(row=(len(modules)-1)//3 + 2, column=0, columnspan=3, pady=20, ipadx=10, ipady=5)





def start_session(root, selection_frame, vocabulary, selected_module):

    # Start a new session according to the selected module

    if selected_module == "All Modules":
        words = vocabulary

    else:
        words = [word for word in vocabulary if word['Module'] == selected_module]

    # Remove the selection frame

    selection_frame.pack_forget()

    # Create a new frame (interface) for the study session

    choose_study_mode(root, words)


def choose_study_mode(root, words, previous_frame=None):
    if previous_frame:
        previous_frame.pack_forget()

    # Create a new GUI for the study session

    study_frame = ttk.Frame(root, padding=20)
    study_frame.pack(fill=tk.BOTH, expand=True)

    study_frame.vocabulary = words

    ttk.Label(
        study_frame,
        text="Choose Study Mode",
        font=("Arial", 16, "bold")
    ).pack(pady=10)

    # Study modes buttons

    modes = {
        "Standard Flashcards": {
            "mode": "standard",
        },
        "Input Practice": {
            "mode": "input",
        },
        "Matching Game": {
            "mode": "matching",
        },
        "Multiple Choice": {
            "mode": "multiple_choice",
        },
        "True or False": {
            "mode": "true_or_false",
        },
        #"Listening Practice": {
        #    "mode": "listening",
       # }
    }

    style = ttk.Style()

    for text, config in modes.items():

        ttk.Button(
            study_frame,
            text=text,
            command=lambda m=config["mode"]: start_study_session(root, study_frame, words, m),
            width=25
        ).pack(pady=10, ipady=5)


    # Back button to return to module selection

    style.configure(
        "Back.TButton",
        font=("Arial", 12, "bold"),
        foreground="white",
        background="black"
    )

    ttk.Button(
        study_frame,
        text="Back",
        style="Back.TButton",
        command=lambda: [study_frame.pack_forget(), setup_module_selection(root, load_vocabulary(), selected_frame=study_frame)],
        width=15
    ).pack(side=tk.LEFT, padx=10, pady=20)

    # Return to Main Menu button
    
    from routes import return_to_main_menu
    m_m_button = ttk.Button(
        study_frame,
        style="Back.TButton",
        text="Back to Main Menu",
        command=lambda: [study_frame.pack_forget(), return_to_main_menu(root, study_frame)],
        width=0
    )
    m_m_button.pack(side=tk.RIGHT, padx=10, pady=20)


def return_to_main_menu(root, current_frame):      # se eu precisar de um botao para voltar ( TUDO ) eu utilizo a funcao

    # Return to the module selection frame

    current_frame.pack_forget()
    setup_module_selection(root, load_vocabulary())


def start_study_session(root, previous_frame, words, selected_mode, selected_module=None):

    # Start the study session according to the selected mode

    if previous_frame and previous_frame.winfo_ismapped():
        previous_frame.pack_forget()

    root.session_timer = SessionTimer()
    root.session_timer.start()

    root.session_settings = {
        'selected_mode': selected_mode,
        'selected_module': selected_module or words[0]['Module'],
        'words': words
    }

    if selected_mode == "standard":
        CustomizeStudySession(root, words)

    elif selected_mode == "input":
        CustomizeStudySession(root, words)

    elif selected_mode == "multiple_choice":
        CustomizeStudySession(root, words)
    
    elif selected_mode == "matching":
        CustomizeStudySession(root, words)
    
    elif selected_mode == "true_or_false":
        CustomizeStudySession(root, words)
        



        
    







    







    
if __name__ == "__main__":
    main()
