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

def generate_test_ai(text, count=5):
    if not api_key:
        return {"error": "Brak klucza API"}
    
    llm = ChatOpenAI(api_key=api_key, model_name="gpt-3.5-turbo")
    
    template = """
    Jesteś profesjonalnym egzaminatorem. Na podstawie tekstu stwórz test sprawdzający wiedzę.
    
    TEKST ŹRÓDŁOWY:
    {text}
    
    WYMAGANIA:
    1. Stwórz DOKŁADNIE {count} pytań.
    2. Postaraj się wymieszać typy pytań (większość jednokrotnego wyboru, ale dodaj też wielokrotny i otwarte).
    3. Odpowiedz TYLKO czystym kodem JSON (bez ```json).

    FORMAT JSON (Lista obiektów):
    [
      {{
        "type": "single_choice",
        "question": "Pytanie?",
        "options": ["A", "B", "C", "D"],
        "correct_answer": "A"
      }},
      {{
        "type": "multiple_choice",
        "question": "Wybierz wszystkie poprawne:",
        "options": ["A", "B", "C", "D"],
        "correct_answer": ["A", "C"]
      }},
      {{
        "type": "open",
        "question": "Pytanie otwarte?",
        "correct_answer": "Wzorcowa odpowiedź"
      }}
    ]
    """
    
    prompt = PromptTemplate(template=template, input_variables=["text", "count"])
    chain = prompt | llm
    
    try:
        response = chain.invoke({"text": text, "count": count})
        content = response.content.strip()
        
        if content.startswith("```json"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]
            
        return json.loads(content)
        
    except Exception as e:
        return [{"type": "open", "question": "Błąd generowania. Spróbuj ponownie.", "correct_answer": ""}]