# main.py

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List # Importe o List
import crud, models, schemas, database
from database import engine, get_db

# ... (código de criação de tabelas, app, CORS, e endpoints de / a /login) ...
models.Base.metadata.create_all(bind=engine)
app = FastAPI()
origins = [
    "http://localhost:5173",
    "https://inovatech-seshat.vercel.app" # URL do Vercel do seu colega
]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.get("/")
def read_root(): return {"message": "API do Projeto SeShat está no ar!"}
@app.get("/materias")
def get_materias():
    subjects = ['Matemática', 'Português', 'História', 'Redação', 'Física' 'Linguagens', 'Química', 'Biologia', 'Geografia', 'Inglês']
    return {"materias_disponiveis": subjects}
@app.post("/register", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def register_user(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user_data.email)
    if db_user: raise HTTPException(status_code=400, detail="Este email já está registrado.")
    new_user = crud.create_user(db=db, user=user_data)
    return new_user
@app.post("/login")
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user_email = form_data.username
    password = form_data.password
    db_user = crud.get_user_by_email(db, email=user_email)
    if not db_user or not crud.verify_password(password, db_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email ou senha incorretos.", headers={"WWW-Authenticate": "Bearer"})
    return {"message": f"Login bem-sucedido para {user_email}!"}

# --- Endpoint para Questões ---

@app.post("/perguntas", response_model=schemas.Question, status_code=status.HTTP_201_CREATED)
def post_new_question(question: schemas.QuestionCreate, db: Session = Depends(get_db)):
    return crud.create_question(db=db, question=question)

# ALTERADO: O endpoint agora aceita 'source' e 'year' como query parameters opcionais
@app.get("/perguntas/{subject}", response_model=List[schemas.Question])
def read_questions_by_subject(
    subject: str, 
    count: int = 10, 
    source: str | None = None, # Parâmetro opcional: ?source=ENEM
    year: int | None = None,   # Parâmetro opcional: ?year=2023
    db: Session = Depends(get_db)
):
    """ 
    Busca perguntas aleatórias por matéria, com filtros opcionais de fonte e ano.
    Exemplo: /perguntas/Matemática?count=5&source=ENEM&year=2023
    """
    # Chama a função CRUD atualizada, passando todos os filtros
    questions = crud.get_questions_by_subject(
        db=db, subject=subject, count=count, source=source, year=year
    )
    
    if not questions:
         raise HTTPException(status_code=404, detail=f"Nenhuma pergunta encontrada para os filtros: {subject}, {source}, {year}")
    return questions

# --- Fim do Arquivo ---