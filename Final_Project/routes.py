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


# Criar todas as rotas, nao apenas a do main menu

# Reutn to Choose Study Mode 

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
            fg_color="#EED585",
            hover_color="#D8BD66",
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

# class Restart(ttk.Button):
#     def __init__(self, parent, root, current_frame, vocabulary):
#         self.root = root
#         self.current_frame = current_frame
#         self.vocabulary = vocabulary

#         super().__init__(
#             master=parent,
#             text="🔄 Restart",
#             command=self._restart_session,
#             width=15
#         )

#     def _restart_session(self):
#         from all_flashcards import standard_flashcards, input_practice, MultipleChoiceGame

#         if not hasattr(self.root, 'session_settings'):
#             self.root.session_settings = {}

#         self.current_frame.pack_forget()

#         s_settings = {
#             'study_direction': self.root.session_settings.get('study_direction', 'hangul_to_lang'),
#             'realtime_feedback': self.root.session_settings.get('realtime_feedback', False),
#             'timer_enabled': self.root.session_settings.get('timer_enabled', False),
#             'show_styles': self.root.session_settings.get('show_styles', True),
#             'word_count': self.root.session_settings.get('word_count', len(self.vocabulary)),
#             'difficulty': self.root.session_settings.get('difficulty', "All")

#         }

#         if self.root.session_settings.get('selected_mode') == 'standard':
#             standard_flashcards(
#                 self.root,
#                 words=self.vocabulary,
#                 settings=s_settings
#             )
        
#         elif self.root.session_settings.get('selected_mode') == 'input':
#             input_practice(
#                 self.root,
#                 words=self.vocabulary,
#                 settings=s_settings
#             )
        
#         elif self.root.session_settings.get('selected_mode') == 'multiple_choice':
#             MultipleChoiceGame(
#                 self.root,
#                 words=self.vocabulary,
#                 settings=s_settings
#             )

#### Do it after ####

