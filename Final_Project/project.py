#CS50P Final Project 
import customtkinter as ctk
from customtkinter import *
import os
from PIL import Image
from tkinter import ttk, messagebox
import csv
import random
import all_flashcards
from all_flashcards import StandardFlashcards, InputPractice, MultipleChoiceGame, MatchingGame, TrueFalseGame
import routes
from language_manager import LanguageManager, InterfaceTranslator, T_CTkLabel
from customize_study_session import CustomizeStudySession
from utilities import SessionTimer
import emoji



language_manager_flashcards = LanguageManager()
interface_translator = InterfaceTranslator()


def main():

    # Main function to run the application

    root = ctk.CTk()

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

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
    #ctk.set_default_color_theme("dark-blue")

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

    # style = ttk.Style()
    # style.configure(
    #     "Correct.TButton",
    #     background="green",          # Funcionando (Testado apenas no Multiple Choice)
    #     foreground="white",
    # )
    # style.configure(
    #     "Incorrect.TButton",
    #     background="red",
    #     foreground="white",
    # )

def load_vocabulary(filepath='vocabulary.csv'):

    # Load vocabulary from a CSV file

    try:
        with open(filepath, "r", encoding="utf-8") as file:
            reader = list(csv.DictReader(file))
            # for word in reader:
            #     word['Type'] = word.get('Type', '')
            return reader
    except FileNotFoundError:
        messagebox.showerror("Error", f"File not found: {filepath}")
        return []
    

def main_menu_gui(root, vocabulary):

    # image_path = os.path.join("assets", "ning.png")
    # image = Image.open(image_path)

    # ctk_image = ctk.CTkImage(light_image=image, dark_image=image, size=(200, 200))

    # image_label = ctk.CTkLabel(
    #     root,
    #     image=ctk_image,
    #     text="",
    # )
    # image_label.pack(pady=20)

    # Main menu GUI

    # image = ctk.CTkImage(dark_image=Image.open(os.path.join("assets", "ning.png")), size=(200, 200))
    # image_label = ctk.CTkLabel(
    #     root,
    #     image=image,
    #     text="",
    # )
    # image_label.pack(pady=20)

    n_selection_frame = ctk.CTkFrame(root)
    n_selection_frame.pack(fill="both", expand=True)

    image = ctk.CTkImage(dark_image=Image.open(os.path.join("assets", "kr.png")), size=(70, 100))
    image_label = ctk.CTkLabel(
        n_selection_frame,
        fg_color="transparent",
        image=image,
        text="",
    )
    image_label.pack(pady=0)

    n_t_label = T_CTkLabel(
        n_selection_frame,
        text="main_menu_korean",
        font=("Arial", 30, "bold")
    )
    n_t_label.pack(pady=(0, 30))

    lbutton_frame = ctk.CTkFrame(
        n_selection_frame,
        fg_color="transparent"
    )
    lbutton_frame.pack(pady=(0, 10))

    translation_button = ctk.CTkButton(
        lbutton_frame,
        text=f"🌎 {interface_translator.get_language()[:3]}",
        corner_radius=20,
        command=lambda: toggle_translation_controls(),
        width=100,
        height=32,
        fg_color="#3B8ED0",
        hover_color="#36719F"
    )
    translation_button.pack(padx=10, pady=(0, 2))

    controls_frame = ctk.CTkFrame(lbutton_frame, fg_color="transparent", bg_color="transparent")

    translation_combobox = ctk.CTkComboBox(
        controls_frame,
        values=["English", "Portuguese"],
        state="readonly",
        corner_radius=20,
        dropdown_fg_color="#777777",
        dropdown_hover_color="#414141",
        text_color="white",
    )
    translation_combobox.pack(side="top", pady=(0, 2))

    confirm_button = ctk.CTkButton(
        controls_frame,
        text="✔",
        width=90,
        height=28,
        fg_color="#3B8ED0",
        hover_color="#36719F",
        corner_radius=20,
        command=lambda: confirm_translation()
    )
    confirm_button.pack(side="top")
    controls_frame.pack_forget()

    def toggle_translation_controls():
        if controls_frame.winfo_ismapped():
            controls_frame.pack_forget()
        else:
            translation_combobox.set(interface_translator.get_language())
            translation_combobox.focus()
            controls_frame.pack()
    
    def confirm_translation():
        selected_lang = translation_combobox.get()
        if selected_lang in ["English", "Portuguese"]:
            interface_translator.set_language(selected_lang)
            translation_button.configure(text=f"🌎 {selected_lang[:3]}")
            controls_frame.pack_forget()
           # n_t_label.configure(text=interface_translator.get_translation('main_menu')) # Necessary for labels

    n_b_label = T_CTkLabel(
        n_selection_frame,
        text="select_level",
        font=("Arial", 24, "bold")
    )
    n_b_label.pack(pady=(50, 20))

    buttons_frame = ctk.CTkFrame(n_selection_frame, fg_color="transparent", bg_color="transparent")
    buttons_frame.pack(pady=20)

    levels = sorted(set(word['Level'] for word in vocabulary))

    # All Levels button
    levels.append("All Levels")

    # Auto Button generator

    for _, level in enumerate(levels[:-1]):

        if level == "All Levels":
            fg_color = "#2CC985"
            hover_color = "#207a4c"

        else:
            fg_color = "#3B8ED0"
            hover_color = "#36719F"

        button = ctk.CTkButton(
            buttons_frame,
            text=f"{level}",
            border_width=0,
            border_color=fg_color,
            fg_color=fg_color,
            hover_color=hover_color,
            text_color="white",
            height=60,
            width=160,
            command=lambda _=level: setup_module_selection(root, vocabulary, selected_frame=n_selection_frame),
            corner_radius=20
        )
        button.grid(row=_//2, column=_%2, sticky="nsew", padx=10, pady=10) #padx=10, pady=10

    # All levels button

    # a_button = ctk.CTkButton(
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

    selection_frame = ctk.CTkFrame(root, bg_color="transparent")
    selection_frame.pack(fill=ctk.BOTH, expand=True)

    T_CTkLabel(
        selection_frame,
        text="select_module",
        font=("Arial", 30, "bold")
    ).pack(pady=(30, 10))

    # Language Button

    language_container = ctk.CTkFrame(selection_frame, bg_color="transparent", fg_color="transparent")
    language_container.pack(pady=10)

    language_button = ctk.CTkButton(
        language_container,
        text=f"🌎 {language_manager_flashcards.get_language()[:3]}",
        corner_radius=20,
        width=100,
        height=32,
        fg_color="#3B8ED0",
        hover_color="#36719F",
        border_color="#3B8ED0",
        text_color="white",
        command=lambda: toggle_language_controls()
    )
    language_button.pack(padx=10, pady=(0, 2))

    controls_frame = ctk.CTkFrame(language_container, fg_color="transparent", bg_color="transparent")

    # Combobox

    language_combobox = ctk.CTkComboBox(
        controls_frame,
        values=["English", "Portuguese"],
        dropdown_fg_color="#777777",
        dropdown_hover_color="#414141",
        corner_radius=20,
        text_color="white",
        state="readonly",
    )
    language_combobox.pack(side="top", pady=(0, 2))

    # Confirm Button

    confirm_button = ctk.CTkButton(
        controls_frame,
        text="✔",
        fg_color="#3B8ED0",
        hover_color="#36719F",
        border_color="#3B8ED0",
        corner_radius=20,
        width=90,
        height=28,
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
            language_button.configure(text=f"🌎 {selected_lang[:3]}")
            controls_frame.pack_forget()
            
    # Modules buttons

    scrollable_frame = ctk.CTkScrollableFrame(
        master=selection_frame,
        fg_color="transparent",
        scrollbar_button_color="#3B8ED0",
        scrollbar_button_hover_color="#36719F",
        height=300
    )
    scrollable_frame.pack(fill=ctk.BOTH, expand=True)

    buttons_frame = ctk.CTkFrame(master=scrollable_frame, bg_color="transparent", fg_color="transparent")
    buttons_frame.pack(pady=20)

    button_back_frame = ctk.CTkFrame(
        selection_frame,
        fg_color="transparent",
        bg_color="transparent"
    )
    button_back_frame.pack(side=ctk.BOTTOM, pady=10)

    # Get all modules from vocabulary.csv

    modules = sorted(set(word["Module"] for word in vocabulary), key=int)

    modules.append("All Modules")


    for _, module in enumerate(modules[:-1]):

        if module == "All Modules":
            fg_color = "#2CC985"
            hover_color = "#207a4c"
        
        else:
            fg_color = "#3B8ED0"
            hover_color = "#36719F"

        button = ctk.CTkButton(
            buttons_frame,
            text=f"{interface_translator.get_translation("module")} {module}",
            fg_color=fg_color,
            hover_color=hover_color,
            text_color="white",
            height=50,
            width=140,
            border_width=0,
            border_color=fg_color,
            corner_radius=12,
            command=lambda m=module: start_session(root, selection_frame, vocabulary, m)
        )
        button.grid(row=_//2, column=_%2, padx=10, pady=10, ipadx=10, ipady=10) #padx=10, pady=10, ipadx=10, ipady=10

    # All Modules button

    all_button = ctk.CTkButton(
        buttons_frame,
        text=interface_translator.get_translation("all_modules"),
        fg_color="#DFC675",
        hover_color="#c2a855",
        text_color="white",
        height=40,
        width=120,
        border_width=0,
        border_color=fg_color,
        corner_radius=8,
        command=lambda: start_session(root, selection_frame, vocabulary, "All Modules")
    )
    all_button.grid(row=(len(modules)-1)//2 + 1, column=0, columnspan=3, pady=20, ipadx=10, ipady=5)  #pady=20, ipadx=10, ipady=5

    # Return to Main Menu

    from routes import return_to_main_menu
    m_menu = ctk.CTkButton(
        button_back_frame,
        text=interface_translator.get_translation("back"),
        fg_color="#363636",
        hover_color="#242424",
        text_color="white",
        height=35,
        width=180,
        border_width=0,
        border_color="#363636",
        corner_radius=8,
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

    study_frame = ctk.CTkFrame(root)
    study_frame.pack(fill="both", expand=True)

    study_frame.vocabulary = words

    T_CTkLabel(
        study_frame,
        text="choose_study_mode",
        font=("Arial", 30, "bold")
    ).pack(pady=(50, 20))

    # Study modes buttons

    modes = {
        f"{interface_translator.get_translation("standard_flashcards")}": {  #change names here
            "mode": "standard",
        },
        f"{interface_translator.get_translation("input_practice")}": {
            "mode": "input",
        },
        f"{interface_translator.get_translation("matching_game")}": {
            "mode": "matching",
        },
        f"{interface_translator.get_translation("multiple_choice")}": {
            "mode": "multiple_choice",
        },
        f"{interface_translator.get_translation("true_or_false")}": {
            "mode": "true_or_false",
        },
        #"Listening Practice": {
        #    "mode": "listening",
       # }
    }

    for text, config in modes.items():

        ctk.CTkButton(
            study_frame,
            text=text,
            command=lambda m=config["mode"]: start_study_session(root, study_frame, words, m),
            text_color="white",
            fg_color="#C7AA49",
            hover_color="#9c8129",
            width=200,
            height=50,
            corner_radius=20
        ).pack(pady=10, ipady=5)


    # Back button to return to module selection
    
    ctk.CTkButton(
        study_frame,
        text=interface_translator.get_translation("back"),
        fg_color="#363636",
        hover_color="#242424",
        text_color="white",
        command=lambda: [study_frame.pack_forget(), setup_module_selection(root, load_vocabulary(), selected_frame=study_frame)],
        height=55,
        width=130,
        corner_radius=8,
        border_width=2,
        border_color="#ffffff"
    ).pack(side=ctk.LEFT, padx=(100, 10), pady=(15, 35))

    # Return to Main Menu button
    
    from routes import return_to_main_menu
    m_m_button = ctk.CTkButton(
        study_frame,
        text=interface_translator.get_translation("back_to_main_menu"),
        command=lambda: [study_frame.pack_forget(), return_to_main_menu(root, study_frame)],
        fg_color="#363636",
        hover_color="#242424",
        text_color="white",
        border_width=2,
        border_color="#ffffff",
        height=55,
        width=130,
        corner_radius=8
    )
    m_m_button.pack(side=ctk.RIGHT, padx=(10, 100), pady=(15, 35))


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
