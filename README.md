# 🧠 KCards

KCards is an educational language learning app built to study **`Korean vocabulary`** using Interactive Flashcards. It was created as a personal tool to boost my Korean studies, with vocabulary based on my course's study plan. Inspired by [Quizlet](https://quizlet.com), it offers a simple and modern experience using [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)

You can also customize it to study **any language** by modifying the [`vocabulary.csv`](vocabulary.csv) file.  
> ⚠️ **Important**: If you change column names like - (`Hangul`, `English`, `Português`...) make sure to also update any related code that depends on those keys.
> [See full details about `vocabulary.csv` here.](#-about-vocabularycsv)

---

## 📦 Install Dependences

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
- Toggle the language button to change the `interface language`.
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
- There any **several** ways to configure your study session:
  - `Words Number` - Set how many words you want to study (**minimum of 5**)
  - `Auto Correction` - A real-time corrector (**not available in all modes**)
  - `Answer With` - Choose how you want to answer the questions (**with Hangul or your selected language**)
  - `Session Timer` - Tracks how long your session takes.
  - `Select Difficulty` - Filter the words by difficulty (**All, Easy, Medium or Hard**)  

  
# 🛑 Before Start
There are some important informations that you may know before starting.

## 📃 About `vocabulary.csv`
The [`vocabulary.csv`](vocabulary.csv) file contains all the words used in your study session. Each row represents a vocabulary item with different language translations and data.

### 🧱 Expected Columns:

| Column     | Description                                                                 |
|------------|-----------------------------------------------------------------------------|
| `Level`    | The level group where the word belongs to                                     |
| `Module`   | Module/lesson number                                                        |
| `Hangul`   | The Korean word                                                             |
| `English`  | English translation                                                     |
| `Português`| Portuguese translation                                                  |
| `Difficulty`| Optional difficulty level (`Easy`, `Medium`, `Hard` or `All`)                                                                                     |
| `Type`     | Word type (`명사`, `동사`, `형용사`, etc.) - can be in korean or your preferred language                                                   |
| `MF`       | Gender marker for **Portuguese** — use `a` for feminine, `o` for masculine, fill it with another word or leave it blank. When both forms are present (e.g.,gato,gata), the program defaults to the first one due to internal logic.

#### 🧪 Example

```csv
Level,Module,Hangul,English,Português,Difficulty,Type,MF
1,1,고양이,Cat,"Gato, Gata",Easy,명사,a
1,1,집,House,Casa,Easy,명사,
```

```markdown
You can modify the CSV to fit your target language or study goals. Just make sure the headers match the expected keys in the program, or update he corresponding code.
```

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
- English Tranlations 
- Inspired by [Quizlet](https://quizlet.com)
- Built using [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
- Designed as part of the [CS50P Final Project](https://cs50.harvard.edu/python/)


#### Thanks for stopping by 😉 (teste commit)