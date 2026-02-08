import streamlit as st
import database as db
import ai_logic as ai

st.set_page_config(page_title="Generator Testów AI", page_icon="🎓", layout="wide")

db.init_db()

with st.sidebar:
    st.header("📜 Historia")
    if st.button("Odśwież"):
        st.rerun()
        
    history_data = db.get_history()
    if not history_data:
        st.write("Pusto...")
    else:
        for item in history_data:
            with st.expander(f"{item[2]} - {item[1]}"):
                st.download_button("Pobierz .txt", item[3], file_name=f"test_{item[0]}.txt")
                st.write(item[3])

st.title("🎓 Generator Testów (Architecture v2)")
st.write("Wgraj notatki, resztę zrobi **Python + OpenAI**.")

uploaded_file = st.file_uploader("Wybierz plik PDF", type=["pdf"])

if 'result' not in st.session_state:
    st.session_state.result = None

if uploaded_file is not None:
    if st.button("Generuj Test"):
        with st.spinner('AI pracuje...'):
            text = ai.get_text_from_pdf(uploaded_file)
            
            if len(text) > 10000: text = text[:10000]
            
            generated_content = ai.generate_test_ai(text)
            st.session_state.result = generated_content
            
            db.save_to_db(uploaded_file.name, generated_content)
            st.success("Zapisano w bazie!")

if st.session_state.result:
    st.markdown("---")
    st.markdown(st.session_state.result)