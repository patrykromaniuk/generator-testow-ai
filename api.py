from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pypdf import PdfReader
from io import BytesIO
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import ai_logic as ai
import database as db
import uvicorn

SECRET_KEY = "bardzo_tajny_klucz"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI(title="Generator Testów API (Secured)")

db.init_db()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Nieprawidłowe dane uwierzytelniające",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return username


@app.post("/register")
def register(form_data: OAuth2PasswordRequestForm = Depends()):
    hashed_password = get_password_hash(form_data.password)
    success = db.create_user(form_data.username, hashed_password)
    if not success:
        raise HTTPException(status_code=400, detail="Użytkownik już istnieje")
    return {"message": "Zarejestrowano pomyślnie"}

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = db.get_user(form_data.username)
    if not user or not verify_password(form_data.password, user[1]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Zły login lub hasło",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user[0]})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/history")
def get_history_endpoint(current_user: str = Depends(get_current_user)):
    """Zwraca historię TYLKO zalogowanego użytkownika"""
    return db.get_history(current_user)

@app.post("/generate-test/")
async def generate_test_endpoint(file: UploadFile = File(...), current_user: str = Depends(get_current_user)):
    """Endpoint chroniony - wymaga tokena"""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Tylko pliki .pdf")
    
    try:
        content = await file.read()
        pdf_file = BytesIO(content)
        
        text = ""
        pdf_reader = PdfReader(pdf_file)
        for page in pdf_reader.pages:
            text += page.extract_text()
            
        if len(text) > 15000: text = text[:15000]

        generated_test = ai.generate_test_ai(text)
        
        db.save_to_db(current_user, file.filename, generated_test)
        
        return {
            "filename": file.filename,
            "test_content": generated_test,
            "user": current_user
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)