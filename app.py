import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Generator Testów (Secure)", page_icon="🔐", layout="wide")

if 'token' not in st.session_state:
    st.session_state.token = None
if 'username' not in st.session_state:
    st.session_state.username = None

def login_user(username, password):
    try:
        data = {"username": username, "password": password}
        response = requests.post(f"{API_URL}/token", data=data)
        if response.status_code == 200:
            token = response.json()["access_token"]
            st.session_state.token = token
            st.session_state.username = username
            st.success("Zalogowano!")
            st.rerun()
        else:
            st.error("Błędny login lub hasło")
    except Exception as e:
        st.error(f"Błąd połączenia: {e}")

def register_user(username, password):
    try:
        data = {"username": username, "password": password}
        response = requests.post(f"{API_URL}/register", data=data)
        if response.status_code == 200:
            st.success("Konto utworzone! Możesz się zalogować.")
        else:
            st.error(f"Błąd rejestracji: {response.json().get('detail')}")
    except Exception as e:
        st.error(f"Błąd połączenia: {e}")

def logout():
    st.session_state.token = None
    st.session_state.username = None
    st.rerun()

if not st.session_state.token:
    st.title("🔐 Panel Logowania")
    
    tab1, tab2 = st.tabs(["Logowanie", "Rejestracja"])
    
    with tab1:
        username = st.text_input("Login", key="login_user")
        password = st.text_input("Hasło", type="password", key="login_pass")
        if st.button("Zaloguj"):
            login_user(username, password)
            
    with tab2:
        new_user = st.text_input("Nowy Login", key="reg_user")
        new_pass = st.text_input("Nowe Hasło", type="password", key="reg_pass")
        if st.button("Utwórz konto"):
            register_user(new_user, new_pass)

else:
    with st.sidebar:
        st.write(f"Zalogowany jako: **{st.session_state.username}**")
        if st.button("Wyloguj"):
            logout()
        
        st.divider()
        st.header("📜 Twoja Historia")
        if st.button("Odśwież"):
            st.rerun()
            
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        try:
            res = requests.get(f"{API_URL}/history", headers=headers)
            if res.status_code == 200:
                for item in res.json():
                    with st.expander(f"{item[2]} - {item[1]}"):
                        st.write(item[3])
        except:
            st.write("Błąd pobierania historii.")

    st.title("🎓 Generator Testów (Secured)")
    st.info("System zabezpieczony protokołem JWT. Twoje pliki są przypisane do konta.")
    
    uploaded_file = st.file_uploader("Wybierz plik PDF", type=["pdf"])
    
    if uploaded_file and st.button("🚀 Generuj"):
        with st.spinner('Przetwarzanie...'):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
            headers = {"Authorization": f"Bearer {st.session_state.token}"}
            
            try:
                res = requests.post(f"{API_URL}/generate-test/", files=files, headers=headers)
                if res.status_code == 200:
                    st.markdown("### Wynik:")
                    st.write(res.json()["test_content"])
                    st.success("Zapisano w bazie!")
                elif res.status_code == 401:
                    st.error("Sesja wygasła. Zaloguj się ponownie.")
                    logout()
                else:
                    st.error(f"Błąd: {res.text}")
            except Exception as e:
                st.error(f"Błąd: {e}")