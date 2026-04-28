import streamlit as st
import requests
import time
from streamlit_javascript import st_javascript

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Interaktywny Quiz AI", page_icon="", layout="wide")

saved_token = st_javascript("localStorage.getItem('token');")
saved_username = st_javascript("localStorage.getItem('username');")

if saved_token == 0: saved_token = None
if saved_username == 0: saved_username = None

if 'token' not in st.session_state: st.session_state.token = None
if 'username' not in st.session_state: st.session_state.username = None
if 'quiz_data' not in st.session_state: st.session_state.quiz_data = None
if 'user_answers' not in st.session_state: st.session_state.user_answers = {}

if saved_token and saved_token != 0 and st.session_state.token is None:
    st.session_state.token = saved_token
    if saved_username and saved_username != 0:
        st.session_state.username = saved_username
    st.rerun()

def login(username, password):
    try:
        res = requests.post(f"{API_URL}/token", data={"username": username, "password": password})
        if res.status_code == 200:
            token = res.json()["access_token"]
            
            st.session_state.token = token
            st.session_state.username = username
            
            st_javascript(f"localStorage.setItem('token', '{token}'); localStorage.setItem('username', '{username}');")
            
            time.sleep(0.5)
            st.rerun()
        else:
            st.error("Błędny login lub hasło")
    except Exception as e:
        st.error(f"Błąd połączenia z API: {e}")

def register(u, p):
    try:
        res = requests.post(f"{API_URL}/register", data={"username": u, "password": p})
        if res.status_code == 200:
            st.success("Zarejestrowano pomyślnie! Możesz się zalogować.")
            login(u,p)
        else:
            st.error("Błąd: Użytkownik już istnieje lub błąd danych.")
    except Exception as e:
        st.error(f"Błąd połączenia: {e}")

def logout():
    st.session_state.clear()
    
    st.components.v1.html(
        "<script>localStorage.clear(); window.parent.location.reload();</script>",
        height=0
    )

if not st.session_state.token:
    st.title("Panel Studenta")
    
    tab1, tab2 = st.tabs(["Logowanie", "Rejestracja"])
    
    with tab1:
        with st.form("login_form"):
            u = st.text_input("Login")
            p = st.text_input("Hasło", type="password")
            submitted = st.form_submit_button("Wejdź")
            
            if submitted:
                if not u or not p:
                    st.warning("Podaj login i hasło!")
                else:
                    login(u, p)
            
    with tab2:
        with st.form("register_form"):
            nu = st.text_input("Nowy Login")
            np = st.text_input("Nowe Hasło", type="password")
            reg_submitted = st.form_submit_button("Załóż konto")
            
            if reg_submitted:
                if not nu or not np:
                    st.warning("Podaj login i hasło!")
                else:
                    register(nu, np)

else:
    with st.sidebar:
        if st.button("Wyloguj"): logout()
        st.divider()
        st.header("Historia")
        if st.button("Odśwież"): st.rerun()
        
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        try:
            res = requests.get(f"{API_URL}/history", headers=headers)
            if res.status_code == 200:
                for item in res.json():
                    if st.button(f"{item['date']} - {item['filename']}", key=f"hist_{item['id']}"):
                        st.session_state.quiz_data = item['content']
                        st.session_state.user_answers = {}
        except: st.write("Błąd historii")

    st.title("Interaktywny Quiz z Notatek")
    
    st.markdown("Konfiguracja testu")
    col1, col2 = st.columns(2)
    with col1:
        uploaded_file = st.file_uploader("Wgraj wykład (PDF)", type=["pdf"])
    with col2:
        questions_count = st.slider("Liczba pytań do wygenerowania:", min_value=3, max_value=20, value=5)
        test_type_ui = st.radio("Wybierz rodzaj pytań:", ["Mieszane", "Tylko jednokrotny wybór", "Tylko wielokrotny wybór"])

    type_mapping = {
        "Mieszane": "mieszane", 
        "Tylko jednokrotny wybór": "jednokrotny", 
        "Tylko wielokrotny wybór": "wielokrotny"
    }

    if uploaded_file and st.button("Generuj Quiz"):
        with st.spinner(f'AI generuje test ({questions_count} pytań, {test_type_ui.lower()})...'):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
            data_payload = {
                "question_count": questions_count,
                "test_type": type_mapping[test_type_ui]
            }
            headers = {"Authorization": f"Bearer {st.session_state.token}"}
            
            try:
                res = requests.post(f"{API_URL}/generate-test/", files=files, data=data_payload, headers=headers)
                if res.status_code == 200:
                    st.session_state.quiz_data = res.json()["quiz_data"]
                    st.session_state.user_answers = {}
                    st.rerun()
                else:
                    st.error(f"Błąd API: {res.text}")
            except Exception as e: st.error(f"Błąd: {e}")

    if st.session_state.quiz_data:
        data = st.session_state.quiz_data
        
        if isinstance(data, str) or (len(data) > 0 and 'type' not in data[0]):
            st.warning("Stary format danych lub błąd. Wygeneruj quiz ponownie.")
        else:
            st.markdown("---")
            st.header(f"Sprawdź swoją wiedzę ({len(data)} pytań)")
            
            with st.form("quiz_form"):
                results = {}
                for i, q in enumerate(data):
                    st.subheader(f"{i+1}. {q.get('question', '')}")
                    
                    q_type = q.get('type', 'single_choice')
                    options = q.get('options', [])
                    
                    if q_type == 'single_choice':
                        results[i] = st.radio("Wybierz poprawną odpowiedź:", options, key=f"q_{i}", index=None)
                    elif q_type == 'multiple_choice':
                        st.write("Wybierz wszystkie poprawne odpowiedzi (wielokrotny wybór):")
                        results[i] = []
                        for opt in options:
                            if st.checkbox(opt, key=f"chk_{i}_{opt}"):
                                results[i].append(opt)

                    st.markdown("---")

                submitted = st.form_submit_button("Sprawdź Wyniki")
                
                if submitted:
                    score = 0
                    for i, q in enumerate(data):
                        user_ans = results.get(i)
                        correct = q.get('correct_answer')
                        q_type = q.get('type', 'single_choice')
                        source_info = q.get('source', 'Brak informacji o źródle')
                        
                        st.markdown(f"**Pytanie {i+1}:** {q.get('question')}")
                        
                        if q_type == 'single_choice':
                            if user_ans == correct:
                                st.success(f"Brawo! Poprawna odpowiedź to: {user_ans}")
                                score += 1
                            else:
                                st.error(f"Błąd. Wybrano: {user_ans} | Poprawna: {correct}")
                                st.info(f"Wskazówka: Odpowiedzi szukaj w notatkach: {source_info}")
                        
                        elif q_type == 'multiple_choice':
                            if set(user_ans or []) == set(correct):
                                st.success(f"Idealnie! Poprawne odpowiedzi to: {', '.join(correct)}")
                                score += 1
                            else:
                                st.error(f"Nie do końca. Wybrałeś: {', '.join(user_ans or ['Brak'])} | Wymagane: {', '.join(correct)}")
                                st.info(f"Wskazówka: Odpowiedzi szukaj w notatkach: {source_info}")
                                
                    st.metric("Twój Wynik Końcowy", f"{score} / {len(data)}")
                    if score == len(data): st.balloons()