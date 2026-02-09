# 🎓 Inteligentny System Generowania Testów (AI Quiz Generator)

Projekt inżynierski realizujący system typu RAG (Retrieval-Augmented Generation), który automatycznie tworzy interaktywne sprawdziany wiedzy na podstawie wgranych notatek (plików PDF). Aplikacja wykorzystuje modele językowe OpenAI oraz architekturę Klient-Serwer.

## 🚀 Główne Funkcjonalności

* **Analiza Dokumentów PDF:** System przetwarza treść wykładów i notatek, wyciągając kluczowe informacje.
* **Generowanie Pytań Hybrydowych:** AI tworzy zróżnicowany zestaw pytań:
    * Jednokrotnego wyboru (Single Choice).
    * Wielokrotnego wyboru (Multiple Choice).
    * Pytania otwarte (Open Ended) z wzorcową odpowiedzią.
* **Parametryzacja:** Użytkownik decyduje o długości testu (suwak od 3 do 20 pytań).
* **Bezpieczeństwo:**
    * Rejestracja i Logowanie użytkowników.
    * Uwierzytelnianie tokenami **JWT (JSON Web Tokens)**.
    * Bezpieczne haszowanie haseł algorytmem **Bcrypt**.
* **Historia i Personalizacja:** Każdy użytkownik ma dostęp do swojej historii wygenerowanych testów zapisanej w bazie danych.
* **Interaktywny Interfejs:** Sprawdzanie wiedzy w czasie rzeczywistym z natychmiastową informacją zwrotną (poprawne/błędne odpowiedzi).

## 🛠️ Stack Technologiczny

### Backend (API)
* **Python 3.10+**
* **FastAPI:** Wydajny framework do budowy API.
* **LangChain:** Orkiestracja logiki AI i komunikacja z LLM.
* **OpenAI API (GPT-3.5-turbo):** Silnik generujący pytania.
* **SQLite:** Relacyjna baza danych (przechowywanie użytkowników i historii).
* **Pydantic & Python-Jose:** Walidacja danych i obsługa tokenów bezpieczeństwa.

### Frontend (Interfejs)
* **Streamlit:** Budowa interaktywnego interfejsu webowego.
* **Requests:** Komunikacja z API Backendowym.

## ⚙️ Instalacja i Konfiguracja

1.  **Sklonuj repozytorium:**
    ```bash
    git clone [https://github.com/TWOJA_NAZWA_UZYTKOWNIKA/generator-testow.git](https://github.com/TWOJA_NAZWA_UZYTKOWNIKA/generator-testow.git)
    cd generator-testow
    ```

2.  **Utwórz i aktywuj środowisko wirtualne (zalecane):**
    * Windows:
        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```
    * Mac/Linux:
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```

3.  **Zainstaluj zależności:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Skonfiguruj zmienne środowiskowe:**
    Utwórz plik `.env` w głównym folderze i dodaj swój klucz API:
    ```
    OPENAI_API_KEY=sk-proj-twoj-klucz-openai...
    ```

## ▶️ Uruchomienie Aplikacji

System składa się z dwóch niezależnych procesów (Backend i Frontend). Można je uruchomić ręcznie lub automatycznie.

### Metoda 1: Automatyczna (Zalecana na Windows)
Uruchom plik **`start.bat`** (kliknij dwukrotnie). Skrypt sam uruchomi oba serwery w nowych oknach.

### Metoda 2: Ręczna (Wymaga dwóch terminali)

**Terminal 1 (Backend):**
```bash
uvicorn api:app --reload