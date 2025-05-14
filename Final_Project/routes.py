import tkinter as tk
from tkinter import ttk, messagebox


def return_to_main_menu(root, current_frame):
    from project import main_menu_gui, load_vocabulary
    current_frame.destroy()
    main_menu_gui(root, load_vocabulary())

# Return to Module Selection

def return_to_setup_module_selection(root, current_frame):
    from project import setup_module_selection, load_vocabulary
    current_frame.destroy()
    setup_module_selection(root, load_vocabulary(), selection_frame=current_frame)


# Criar todas as rotas, nao apenas a do main menu

# Reutn to Choose Study Mode 

def return_to_choose_study_mode(root, current_frame):
    from project import choose_study_mode, load_vocabulary
    current_frame.destroy()
    choose_study_mode(root, load_vocabulary())


