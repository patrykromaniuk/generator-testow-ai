import streamlit as st
from pypdf import PdfReader
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
import os
import sqlite3
import datetime

# --- 1. KONFIGURACJA I BAZA DANYCH ---
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="Generator Testów AI", page_icon="🎓", layout="wide")

# Funkcja tworząca bazę danych (jeśli nie istnieje)
def init_db():
    conn = sqlite3.connect('testy.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            generated_date TEXT,
            content TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Funkcja zapisu do bazy
def save_to_db(filename, content):
    conn = sqlite3.connect('testy.db')
    c = conn.cursor()
    date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    c.execute('INSERT INTO history (filename, generated_date, content) VALUES (?, ?, ?)', 
              (filename, date_str, content))
    conn.commit()
    conn.close()

# Funkcja odczytu historii
def get_history():
    conn = sqlite3.connect('testy.db')
    c = conn.cursor()
    c.execute('SELECT id, filename, generated_date, content FROM history ORDER BY id DESC')
    data = c.fetchall()
    conn.close()
    return data

# Uruchomienie bazy na starcie
init_db()

# --- 2. LOGIKA AI ---
def get_text_from_pdf(pdf_file):
    pdf_reader = PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def generate_test_ai(text):
    if not api_key:
        return "Brak klucza API!"
    
    llm = ChatOpenAI(api_key=api_key, model_name="gpt-3.5-turbo")
    template = """
    Jesteś ekspertem edukacyjnym. Stwórz krótki test z podanego tekstu.
    
    TEKST:
    {text}
    
    WYMAGANIA:
    1. 3 pytania zamknięte (A,B,C,D) z pogrubioną poprawną odpowiedzią.
    2. 1 pytanie otwarte na końcu.
    3. Język polski.
    """
    prompt = PromptTemplate(template=template, input_variables=["text"])
    chain = prompt | llm
    return chain.invoke({"text": text}).content

# --- 3. INTERFEJS (Frontend) ---

# Panel boczny - HISTORIA
with st.sidebar:
    st.header("📜 Historia Testów")
    if st.button("Odśwież historię"):
        st.rerun()
        
    history_data = get_history()
    if not history_data:
        st.write("Brak zapisanych testów.")
    else:
        for item in history_data:
            # item = (id, filename, date, content)
            with st.expander(f"{item[2]} - {item[1]}"):
                st.write(item[3])
                st.download_button(
                    label="Pobierz",
                    data=item[3],
                    file_name=f"test_{item[0]}.txt",
                    key=f"btn_{item[0]}"
                )

# Główna część
st.title("🎓 Generator Testów + Baza Danych")
st.write("Wgraj plik, a AI wygeneruje test i **zapisze go automatycznie w bazie SQLite**.")

uploaded_file = st.file_uploader("Wgraj notatki (PDF)", type=["pdf"])

if 'result' not in st.session_state:
    st.session_state.result = None

if uploaded_file is not None:
    if st.button("🚀 Generuj i Zapisz"):
        if not api_key:
            st.error("⚠️ Brak klucza API w pliku .env!")
        else:
            with st.spinner('Przetwarzanie...'):
                try:
                    # 1. Czytanie
                    text = get_text_from_pdf(uploaded_file)
                    if len(text) > 10000: text = text[:10000] # Limit znaków
                    
                    # 2. Generowanie
                    generated_content = generate_test_ai(text)
                    st.session_state.result = generated_content
                    
                    # 3. ZAPIS DO BAZY
                    save_to_db(uploaded_file.name, generated_content)
                    st.success("Test wygenerowany i zapisany w bazie!")
                    
                except Exception as e:
                    st.error(f"Błąd: {e}")

# Wyświetlanie wyniku głównego
if st.session_state.result:
    st.markdown("### 📝 Wynik:")
    st.markdown(st.session_state.result)