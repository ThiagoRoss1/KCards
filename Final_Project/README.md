# 🧠 KCards

KCards is an educational language learning app built to study **`Korean vocabulary`** using Interactive Flashcards. It was created as a personal tool to boost my Korean studies, with vocabulary based on my course's study plan. Inspired by [Quizlet](https://quizlet.com), it offers a simple and modern experience using [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)

You can also customize it to study **any language** by modifying the [`vocabulary.csv`](vocabulary.csv) file.  
> ⚠️ **Important**: If you change column names like - (`Hangul`, `English`, `Português`...) make sure to also update any related code that depends on those keys.
> [See full details about `vocabulary.csv` here.](#-about-vocabularycsv)

---

## 📦 Install Dependencies

Before running the project, install the required packages listed in `requirements.txt`.

### 💻 Windows

```bash
$ pip install -r requirements.txt
```

### 🐧 Linux / 🍎 macOS

```bash
$ python3 -m pip install -r requirements.txt
```

## 🔧 Usage

**Navigate** to the project folder, using the following command:

```bash
$ cd Final_Project
```

**Then** run the application:

```bash
$ python project.py
```

## 🛠 Features

### 💡 Interface Language
- Use the language switch to change the `interface language`.
  - Supported Languages - `English` and `Portuguese`

### ⚙ Module Selection
- Choose which module you'd like to study
- Select your `Flashcard Language`:
  - The language of the flashcards can be `English` or `Portuguese`.
  - It follows the interface language by default, but you can change it independently.
 
### 🧠 All Modes
- This app offers various ways to study:
  - 🃏 [Standard Flashcards](#-study-modes)
  - ⌨ [Input Practice](#-study-modes)
  - 🎯 [Matching Game](#-study-modes)
  - 🔠 [Multiple Choice](#-study-modes)
  - ❌ [True or False](#-study-modes)

### 🌌 Customize Study Session
- There are **several** ways to configure your study session:
  - `Words Number` - Set how many words you want to study (**minimum of 5**)
  - `Auto Correction` - A real-time corrector (**not available in all modes**)
  - `Answer With` - Choose how you want to answer the questions (**with Hangul or your selected language**)
  - `Session Timer` - Tracks how long your session takes.
  - `Select Difficulty` - Filter the words by difficulty (**All, Easy, Medium or Hard**)  

  
# 🛑 Before Start
Before you begin, here's some essential information to help you understand how the app works.

## 📃 About `vocabulary.csv`
The [`vocabulary.csv`](vocabulary.csv) file contains all the words used in your study session. Each row represents a vocabulary item with different language translations and data.

### 🧱 Expected Columns:

| Column     | Description                                                                 |
|------------|-----------------------------------------------------------------------------|
| `Level`    | The level group where the word belongs to                                     |
| `Module`   | Module/lesson number                                                        |
| `Hangul`   | The Korean word                                                             |
| `Português`  | Portuguese translation                                                    |
| `English`| English translation                                                  |
| `Difficulty`| Optional difficulty level (`Easy`, `Medium`, `Hard` or `All`)                                                                                     |
| `Type`     | Word type (`명사`, `동사`, `형용사`, etc.) - can be in korean or your preferred language                                                   |
| `MF`       | Gender marker for **Portuguese** — use `a` for feminine, `o` for masculine, or leave it blank. When both forms are present (e.g. Gato, Gata), the program defaults to the first one due to internal logic.                                                          |
| `ExtraPT`  | An extra column for another **portuguese variations** (e.g. Ator, Atriz) or differ some similar words by their classifications or status (e.g. City, Language)                                                   |
| `ExtraENG` | An extra column for **english variations** (e.g. Actor, Actress) or differ some similar words by their classifications or status (e.g. City, Language)                                                |
| `Extra`   | An extra column for **Hangul variations** or to differ similar words by their classifications or status (e.g. City, Language) |

> **❗ Info**: Empty fields in my [vocabulary.csv](vocabulary.csv) are marked with `-` to improve readability and differentiate intentional absence from missing data. However, you can let it Empty and the program will not be affected.

#### 🧪 Example

```csv
Level,Module,Hangul,Português,English,Difficulty,Type,MF,ExtraPT,ExtraENG,Extra
N1,1,고양이,"Gato, Gata",Cat,Easy,명사,a,-,-,-
N1,2,한국어 [한구거],Coreano,Korean,Easy,명사,-,língua,language,-
N1,1,차,Carro,Car,Easy,명사,,,,자동차
N1,2,날씬하다,Ser magro,"Slim, Slender, Thin",Easy,형용사,,,,
```
> ❕ **Note**: If a word has multiple synonyms, you can include them in quotes (e.g. "Slim, Slender, Thin"). The program will automatically split the string by commas and treat each word separately.

```markdown
You can modify the CSV to fit your target language or study goals. Just make sure the headers match the expected keys in the program, or update the corresponding code.
```

## 🔮 About `Prepared Words`
If any column in [vocabulary.csv](vocabulary.csv) is modified, it's recommended to review the `prepare_words` function in [`all_flashcards`](all_flashcards.py)
> ⚠️ **Note**: Each Game mode has its own `prepare_words` function and a corresponding `result screen`, as listed below:  
> 🃏 [Standard Flashcards](all_flashcards.py#L51) &nbsp;|&nbsp; 🔮 [Standard Results Screen](results_screen.py#L1486)  
> ⌨ [Input Practice](all_flashcards.py#L372) &nbsp;|&nbsp; 🔮 [Input Results Screen](results_screen.py#L173)  
> 🎯 [Matching Game](all_flashcards.py#L1050) &nbsp;|&nbsp; 🔮 [Matching Results Screen](results_screen.py#L925)  
> 🔠 [Multiple Choice](all_flashcards.py#L706) &nbsp;|&nbsp; 🔮 [Multiple Results Screen](results_screen.py#L540)  
> ❌ [True or False](all_flashcards.py#L1384) &nbsp;|&nbsp; 🔮 [True or False Results Screen](results_screen.py#L1063) | *No dedicated results screen for this mode*

## 📚 Study Modes

- `Standard Flashcards`
  - A classic flashcard mode where you **flip** cards to reveal answers.

- `Input Practice`
  - **Type** the correct answer using your keyboard.

- `Matching`
  - **Match** 6 pairs from a grid of 12 shuffled words. (Random-generated)

- `Multiple Choice`
  - **Choose** the correct answer from 4 options.

- `True or False`
  - Decide whether a statement is **true or false**.

## 💭 Final Thoughts
This project was created for personal use, but feel free to fork it and make your own changes!  
Pull requests and suggestions are welcome — Happy Studying! ✨

### 📝 Acknowledgements

#### 📒 Learning Resources & Content:
- Vocabulary translations supported by [Naver Dictionary](https://en.dict.naver.com/#/main)
- Korean Language course provided by [Coreano Online](https://coreanoonline.com.br/)

#### 💭 Project Inspirations & Tools
- English Translations 
- Inspired by [Quizlet](https://quizlet.com)
- Built using [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
- Designed as part of the [CS50P Final Project](https://cs50.harvard.edu/python/)


#### Thanks for stopping by 😉

![Python](https://img.shields.io/badge/Python-3.13.3-blue?logo=python)
