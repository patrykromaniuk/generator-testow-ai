from pypdf import PdfReader
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
import os
import json
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

def get_text_from_pdf(pdf_file):
    pdf_reader = PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def generate_test_ai(text):
    if not api_key:
        return {"error": "Brak klucza API"}
    
    llm = ChatOpenAI(api_key=api_key, model_name="gpt-3.5-turbo")
    
    template = """
    Jesteś asystentem edukacyjnym. Na podstawie podanego tekstu stwórz test wyboru.
    ODPOWIEDZ TYLKO CZYSTYM KODEM JSON. Bez formatowania markdown (```json).
    
    TEKST:
    {text}
    
    WYMAGANIA FORMATU JSON:
    Stwórz listę 3-5 pytań w takim formacie:
    [
      {{
        "question": "Treść pytania?",
        "options": ["Opcja A", "Opcja B", "Opcja C", "Opcja D"],
        "correct_answer": "Opcja B"
      }},
      ...
    ]
    
    Ważne: "correct_answer" musi być identyczne jak jedna z opcji.
    """
    
    prompt = PromptTemplate(template=template, input_variables=["text"])
    chain = prompt | llm
    
    try:
        response = chain.invoke({"text": text})
        content = response.content.strip()
        
        if content.startswith("```json"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]
            
        quiz_data = json.loads(content)
        return quiz_data
        
    except Exception as e:
        return [{"question": "Błąd generowania JSON", "options": [], "correct_answer": ""}]