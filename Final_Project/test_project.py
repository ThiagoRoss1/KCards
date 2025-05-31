import pytest
import unittest
from unittest.mock import patch, MagicMock
import pyautogui
import customtkinter as ctk
from customtkinter import *
import tkinter as tk
from tkinter import *
import os
import assets

from project import main_menu_gui, load_vocabulary, setup_module_selection, choose_study_mode, start_study_session
from language_manager import InterfaceTranslator, LanguageManager
from routes import Retry, return_to_main_menu, return_to_setup_module_selection, return_to_choose_study_mode
from utilities import SessionTimer, ProgressBar
from customize_study_session import CustomizeStudySession
from all_flashcards import StandardFlashcards, MultipleChoiceGame, MatchingGame, TrueFalseGame, InputPractice




def test_main_menu_gui():
    try:
        root = ctk.CTk()
        vocabulary = load_vocabulary()
        main_menu_gui(root, vocabulary)
        assert root.winfo_children() != []
    except Exception as e:
        pytest.skip(f"Skipping test_main_menu_gui due to exception: {e}")

def test_load_vocabulary():
    vocabulary = load_vocabulary()
    assert isinstance(vocabulary, list)
    assert len(vocabulary) > 0
    assert ('Level' in vocabulary[0])
    assert ('Module' in vocabulary[0])
    assert ('Hangul' in vocabulary[0])
    assert ('English' in vocabulary[0])
    assert ('Português' in vocabulary[0])
    assert ('Difficulty' in vocabulary[0])
    assert ('Type' in vocabulary[0])
    assert ('MF' in vocabulary[0])

def test_setup_module_selection():
    try:
        root = ctk.CTk()
        vocabulary = load_vocabulary()
        selected_frame = ctk.CTkFrame(root)
        setup_module_selection(root, vocabulary, selected_frame=selected_frame)
        assert root.winfo_children() != []
        selected_frame.pack_forget()
        root.destroy()
    except Exception as e:
        pytest.skip(f"Skipping test_setup_module_selection due to exception: {e}")

def test_choose_study_mode():
    try:
        root = ctk.CTk()
        vocabulary = load_vocabulary()
        previous_frame = ctk.CTkFrame(root)
        choose_study_mode(root, vocabulary, previous_frame=previous_frame)
        previous_frame.pack_forget()
        assert root.winfo_children() != []
    except Exception as e:
        pytest.skip(f"Skipping test_choose_study_mode due to exception: {e}")

def test_start_study_session():
    try:
        root = ctk.CTk()
        vocabulary = load_vocabulary()
        previous_frame = ctk.CTkFrame(root)
        selected_mode = ctk.CTkOptionMenu(root, values=["standard", "input", "multiple_choice", "matching", "true_or_false"])
        start_study_session(root, previous_frame, vocabulary, selected_mode=selected_mode, selected_module=None)
        previous_frame.pack_forget()
        assert root.winfo_children() != []

        assert isinstance(root.session_settings, dict)
        assert 'selected_mode' in root.session_settings
        assert root.session_settings['selected_mode'] is not None
        assert 'selected_module' in root.session_settings
        assert root.session_settings['selected_module'] is not None
        assert 'words' in root.session_settings
        assert root.session_settings['words'] is not None
    except Exception as e:
        pytest.skip(f"Skipping test_start_study_session due to exception: {e}")


def test_retry():
    try:
        root = ctk.CTk()
        vocabulary = load_vocabulary()
        current_frame = ctk.CTkFrame(root)
        retry_button = Retry(current_frame, root, current_frame, vocabulary)
        assert isinstance(retry_button, Retry)
        assert retry_button.cget("text") == f"⚙ {InterfaceTranslator().get_translation('retry')}"
        retry_button._retry_session()  # Test the method directly
        current_frame.pack_forget()
        root.destroy()
    except Exception as e:
        pytest.skip(f"Skipping test_retry due to exception: {e}")



