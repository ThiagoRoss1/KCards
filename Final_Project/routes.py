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

def return_to_choose_study_mode(root, current_frame, selected_module):
    from project import choose_study_mode, load_vocabulary
    current_frame.destroy()
    vocabulary = load_vocabulary()
    words = [word for word in vocabulary if word['Module'] == selected_module]

    choose_study_mode(root, words)

class Retry(ttk.Button):
    def __init__(self, parent, root, current_frame, vocabulary):
        self.root = root
        self.current_frame = current_frame
        self.vocabulary = vocabulary

        super().__init__(
            master=parent,
            text="🔄 Retry",
            command=self._retry_session,
            width=15  
        )


    def _retry_session(self):

        self.current_frame.pack_forget()
        
        current_module = self.vocabulary[0]['Module']
        
        filtered_words = [word for word in self.vocabulary if word['Module'] == current_module]
        
        from project import start_study_session
        start_study_session(
            root=self.root,
            previous_frame=None, 
            words=filtered_words,
            selected_mode=self.root.session_settings['selected_mode']
        )
        



