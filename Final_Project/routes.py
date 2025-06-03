import customtkinter as ctk
from customtkinter import *
from language_manager import InterfaceTranslator

translation = InterfaceTranslator()


def return_to_main_menu(root, current_frame):
    from project import main_menu_gui, load_vocabulary
    current_frame.destroy()
    main_menu_gui(root, load_vocabulary())

# Return to Module Selection

def return_to_setup_module_selection(root, current_frame):
    from project import setup_module_selection, load_vocabulary
    current_frame.destroy()
    setup_module_selection(root, load_vocabulary(), selection_frame=current_frame)

# Return to Choose Study Mode  

def return_to_choose_study_mode(root, current_frame, selected_module):
    from project import choose_study_mode, load_vocabulary
    current_frame.destroy()
    vocabulary = load_vocabulary()
    words = [word for word in vocabulary if word['Module'] == selected_module]

    choose_study_mode(root, words)

class Retry(ctk.CTkButton):
    def __init__(self, parent, root, current_frame, vocabulary):
        self.root = root
        self.current_frame = current_frame
        self.vocabulary = vocabulary
        self.session_settings = getattr(root, 'session_settings', None)

        super().__init__(
            master=parent,
            text=f"⚙ {translation.get_translation("retry")}",
            command=self._retry_session,
            width=20,
            height=30,
            fg_color="#C9AF5C",
            hover_color="#AC913B",
            text_color="white",
            border_width=0,
            corner_radius=20  
        )


    def _retry_session(self):

        if not hasattr(self.root, 'session_settings'):
            return

        self.current_frame.pack_forget()

        from customize_study_session import CustomizeStudySession
        customize_frame = ctk.CTkFrame(self.root)
        customize_frame.pack(fill=ctk.BOTH, expand=True)

        CustomizeStudySession(
            self.root,
            self.vocabulary,
            initial_settings=self.root.session_settings
        )

