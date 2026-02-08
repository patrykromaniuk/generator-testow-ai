from pypdf import PdfReader
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

def get_text_from_pdf(pdf_file):
    """Wyciąga surowy tekst z pliku PDF"""
    pdf_reader = PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def generate_test_ai(text):
    """Komunikuje się z API OpenAI"""
    if not api_key:
        return "Błąd: Brak klucza API w pliku .env"
    
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
    
    try:
        response = chain.invoke({"text": text})
        return response.content
    except Exception as e:
        return f"Wystąpił błąd AI: {e}"