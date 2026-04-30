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

def generate_test_ai(text, count=5, test_type="mieszane"):
    if not api_key:
        return {"error": "Brak klucza API"}
    
    llm = ChatOpenAI(api_key=api_key, model_name="gpt-4o-mini")
    
    if test_type == "jednokrotny":
        type_instruction = 'Generuj WYŁĄCZNIE pytania typu "single_choice" (jednokrotny wybór).'
    elif test_type == "wielokrotny":
        type_instruction = 'Generuj WYŁĄCZNIE pytania typu "multiple_choice" (wielokrotny wybór).'
    else:
        type_instruction = 'Wymieszaj losowo typy pytań: używaj "single_choice" (jednokrotny wybór) oraz "multiple_choice" (wielokrotny wybór).'

    template = """
    Jesteś profesjonalnym egzaminatorem. Na podstawie tekstu stwórz obiektywny test sprawdzający wiedzę.
    
    TEKST ŹRÓDŁOWY (zawiera znaczniki stron, np. [Strona 1]):
    {text}
    
    WYMAGANIA:
    1. LICZBA PYTAŃ: Musisz wygenerować bezwzględnie {count} elementów w głównej tablicy JSON. Zanim zakończysz odpowiedź, upewnij się, że tablica ma dokładnie {count} obiektów. Nie generuj 10 pytań, jeśli zażądano 11.
    2. {type_instruction}
    3. Zwróć wynik TYLKO w postaci czystego kodu JSON bez żadnych dodatkowych tekstów.
    4. Nigdy nie dodawaj pytań otwartych.
    5. BARDZO WAŻNE: Wewnątrz treści pytań i odpowiedzi absolutnie nie używaj znaków cudzysłowu. Zastąp je pojedynczymi apostrofami.
    6. Zlokalizuj, z której strony pochodzi odpowiedź na dane pytanie i dodaj tę informację w polu "source".

    FORMAT JSON:
    [
      {{
        "type": "single_choice",
        "question": "Treść pytania jednokrotnego wyboru?",
        "options": ["A", "B", "C", "D"],
        "correct_answer": "A",
        "source": "Strona 2"
      }},
      {{
        "type": "multiple_choice",
        "question": "Zaznacz wszystkie poprawne odpowiedzi:",
        "options": ["Opcja 1", "Opcja 2", "Opcja 3", "Opcja 4"],
        "correct_answer": ["Opcja 1", "Opcja 3"],
        "source": "Strona 5"
      }}
    ]
    """
    
    prompt = PromptTemplate(template=template, input_variables=["text", "count", "type_instruction"])
    chain = prompt | llm
    
    try:
        response = chain.invoke({"text": text, "count": count, "type_instruction": type_instruction})
        content = response.content.strip()
        
        if content.startswith("```json"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]
            
        return json.loads(content)
        
    except Exception as e:
        return [{"type": "single_choice", "question": f"Błąd generowania AI: {str(e)}", "options": ["OK"], "correct_answer": "OK"}]