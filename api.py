from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, status, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pypdf import PdfReader
from io import BytesIO
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import json
import ai_logic as ai
import database as db
import uvicorn

SECRET_KEY = "bardzo_tajny_klucz_inzynierski"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI(title="Generator Testów API (Interactive Only)")
db.init_db()

def verify_password(plain, hashed): return pwd_context.verify(plain, hashed)
def get_password_hash(password): return pwd_context.hash(password)
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None: raise HTTPException(status_code=401)
    except JWTError: raise HTTPException(status_code=401)
    return username

@app.post("/register")
def register(form_data: OAuth2PasswordRequestForm = Depends()):
    hashed_password = get_password_hash(form_data.password)
    if not db.create_user(form_data.username, hashed_password):
        raise HTTPException(status_code=400, detail="Użytkownik istnieje")
    return {"msg": "OK"}

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = db.get_user(form_data.username)
    if not user or not verify_password(form_data.password, user[1]):
        raise HTTPException(status_code=401, detail="Błąd logowania")
    return {"access_token": create_access_token(data={"sub": user[0]}), "token_type": "bearer"}

@app.get("/history")
def get_history(user: str = Depends(get_current_user)):
    raw_history = db.get_history(user)
    clean_history = []
    for item in raw_history:
        try:
            content_json = json.loads(item[3])
        except:
            content_json = item[3]
        clean_history.append({
            "id": item[0],
            "filename": item[1],
            "date": item[2],
            "content": content_json
        })
    return clean_history

@app.post("/generate-test/")
async def generate_test(
    file: UploadFile = File(...), 
    question_count: int = Form(5), 
    test_type: str = Form("mieszane"), 
    user: str = Depends(get_current_user)
):
    if not file.filename.endswith(".pdf"): raise HTTPException(400, "Tylko PDF")
    
    try:
        content = await file.read()
        pdf_reader = PdfReader(BytesIO(content))
        text_with_pages = ""
        for i, p in enumerate(pdf_reader.pages):
            page_text = p.extract_text()
            if page_text:
                text_with_pages += f"\n[Strona {i+1}]\n{page_text}"
        text = text_with_pages[:15000]
        
        quiz_data = ai.generate_test_ai(text, question_count, test_type)
        
        quiz_json_string = json.dumps(quiz_data)
        db.save_to_db(user, file.filename, quiz_json_string)
        
        return {"filename": file.filename, "quiz_data": quiz_data}
        
    except Exception as e:
        raise HTTPException(500, str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)