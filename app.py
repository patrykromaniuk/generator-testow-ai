import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Interaktywny Quiz AI", page_icon="🎓", layout="wide")

if 'token' not in st.session_state: st.session_state.token = None
if 'quiz_data' not in st.session_state: st.session_state.quiz_data = None
if 'user_answers' not in st.session_state: st.session_state.user_answers = {}

def login(username, password):
    try:
        res = requests.post(f"{API_URL}/token", data={"username": username, "password": password})
        if res.status_code == 200:
            st.session_state.token = res.json()["access_token"]
            st.session_state.username = username
            st.rerun()
        else: st.error("Błąd logowania")
    except: st.error("Błąd połączenia z API")

def register(u, p):
    requests.post(f"{API_URL}/register", data={"username": u, "password": p})
    st.success("Zarejestrowano!")

def logout():
    st.session_state.token = None
    st.session_state.quiz_data = None
    st.rerun()

if not st.session_state.token:
    st.title("🔐 Panel Studenta")
    tab1, tab2 = st.tabs(["Logowanie", "Rejestracja"])
    with tab1:
        u = st.text_input("Login")
        p = st.text_input("Hasło", type="password")
        if st.button("Wejdź"): login(u, p)
    with tab2:
        nu = st.text_input("Nowy Login")
        np = st.text_input("Nowe Hasło", type="password")
        if st.button("Załóż konto"): register(nu, np)

else:
    with st.sidebar:
        st.write(f"Zalogowany: **{st.session_state.username}**")
        if st.button("Wyloguj"): logout()
        st.divider()
        st.header("📜 Historia")
        if st.button("Odśwież"): st.rerun()
        
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        try:
            res = requests.get(f"{API_URL}/history", headers=headers)
            if res.status_code == 200:
                for item in res.json():
                    if st.button(f"{item['date']} - {item['filename']}", key=item['id']):
                        st.session_state.quiz_data = item['content']
                        st.session_state.user_answers = {}
        except: st.write("Błąd historii")

    st.title("🎓 Interaktywny Quiz z Notatek")
    
    uploaded_file = st.file_uploader("Wgraj wykład (PDF)", type=["pdf"])
    
    if uploaded_file and st.button("🚀 Generuj Quiz"):
        with st.spinner('AI analizuje materiał...'):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
            try:
                res = requests.post(f"{API_URL}/generate-test/", files=files, headers=headers)
                if res.status_code == 200:
                    st.session_state.quiz_data = res.json()["quiz_data"]
                    st.session_state.user_answers = {}
                    st.rerun()
            except Exception as e: st.error(f"Błąd: {e}")

    if st.session_state.quiz_data:
        data = st.session_state.quiz_data
        
        if isinstance(data, str):
            st.warning("To jest stary format testu (tylko tekst). Wygeneruj nowy, aby mieć klikalne pytania.")
            st.write(data)
        else:
            st.markdown("---")
            st.header("📝 Sprawdź swoją wiedzę")
            
            with st.form("quiz_form"):
                score = 0
                for i, q in enumerate(data):
                    st.subheader(f"{i+1}. {q['question']}")
                    choice = st.radio("Wybierz odpowiedź:", q['options'], key=f"q_{i}", index=None)
                    
                submitted = st.form_submit_button("✅ Sprawdź Wyniki")
                
                if submitted:
                    correct_count = 0
                    for i, q in enumerate(data):
                        user_choice = st.session_state.get(f"q_{i}")
                        
                        if user_choice == q['correct_answer']:
                            st.success(f"Pytanie {i+1}: Dobrze! ({user_choice})")
                            correct_count += 1
                        else:
                            st.error(f"Pytanie {i+1}: Źle. Twój wybór: {user_choice}. Poprawna: {q['correct_answer']}")
                    
                    st.metric(label="Twój Wynik", value=f"{correct_count} / {len(data)}")
                    if correct_count == len(data):
                        st.balloons()