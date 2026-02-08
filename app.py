import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Generator Testów (Klient)", page_icon="🖥️", layout="wide")

with st.sidebar:
    st.header("📜 Historia (z API)")
    if st.button("Odśwież"):
        st.rerun()
        
    try:
        # Frontend pyta API o historię! Nie dotyka pliku .db
        response = requests.get(f"{API_URL}/history")
        if response.status_code == 200:
            history_data = response.json()
            for item in history_data:
                # item = [id, filename, date, content]
                with st.expander(f"{item[2]} - {item[1]}"):
                    st.write(item[3])
        else:
            st.error("Błąd pobierania historii")
    except:
        st.warning("Nie można połączyć z API (Historia niedostępna)")

st.title("🖥️ System Klient-Serwer (SQLite via API)")

uploaded_file = st.file_uploader("Wybierz plik PDF", type=["pdf"])

if 'result' not in st.session_state:
    st.session_state.result = None

if uploaded_file is not None:
    if st.button("🚀 Wyślij do API"):
        with st.spinner('Przetwarzanie na serwerze...'):
            try:
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                
                response = requests.post(f"{API_URL}/generate-test/", files=files)
                
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.result = data["test_content"]
                    st.success("Gotowe!")
                    st.rerun() 
                else:
                    st.error(f"Błąd: {response.text}")
                    
            except Exception as e:
                st.error(f"Serwer nie odpowiada: {e}")

if st.session_state.result:
    st.markdown("---")
    st.markdown(st.session_state.result)