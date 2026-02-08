from fastapi import FastAPI, UploadFile, File, HTTPException
from pypdf import PdfReader
from io import BytesIO
import ai_logic as ai
import database as db 
import uvicorn

db.init_db()

app = FastAPI(title="Generator Testów API")

@app.get("/")
def read_root():
    return {"status": "online"}

@app.get("/history")
def get_history_endpoint():
    """Nowy endpoint: Zwraca historię testów z bazy"""
    return db.get_history()

@app.post("/generate-test/")
async def generate_test_endpoint(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Tylko pliki .pdf")
    
    try:
        content = await file.read()
        pdf_file = BytesIO(content)
        
        text = ""
        pdf_reader = PdfReader(pdf_file)
        for page in pdf_reader.pages:
            text += page.extract_text()
            
        if not text:
            raise HTTPException(status_code=400, detail="Pusty PDF")
        
        if len(text) > 15000: text = text[:15000]

        generated_test = ai.generate_test_ai(text)
        
        db.save_to_db(file.filename, generated_test)
        
        return {
            "filename": file.filename,
            "test_content": generated_test
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)