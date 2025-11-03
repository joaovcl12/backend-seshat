# main.py

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List 
# NOVO: Importa o timedelta para definir o tempo de expiração
from datetime import timedelta

import crud, models, schemas, database, security # NOVO: Importa security
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
origins = [
    "http://localhost:5173",
    "https://projeto-se-shat.vercel.app" 
]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# ... (Endpoints '/', '/materias', '/register', '/perguntas' não mudam) ...
@app.get("/")
def read_root(): return {"message": "API do Projeto SeShat está no ar!"}
@app.get("/materias")
def get_materias():
    subjects = ['Matemática', 'Português', 'História', 'Redação', 'Física', 'Linguagens', 'Química', 'Biologia', 'Geografia', 'Inglês']
    return {"materias_disponiveis": subjects}
@app.post("/register", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def register_user(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user_data.email)
    if db_user: raise HTTPException(status_code=400, detail="Este email já está registrado.")
    new_user = crud.create_user(db=db, user=user_data)
    return new_user
@app.post("/perguntas", response_model=schemas.Question, status_code=status.HTTP_201_CREATED)
def post_new_question(question: schemas.QuestionCreate, db: Session = Depends(get_db)):
    return crud.create_question(db=db, question=question)
@app.get("/perguntas/{subject}", response_model=List[schemas.Question])
def read_questions_by_subject(subject: str, count: int = 10, source: str | None = None, year: int | None = None, db: Session = Depends(get_db)):
    questions = crud.get_questions_by_subject(db=db, subject=subject, count=count, source=source, year=year)
    if not questions: raise HTTPException(status_code=404, detail=f"Nenhuma pergunta encontrada para os filtros: {subject}, {source}, {year}")
    return questions


# --- Endpoints de Autenticação (MODIFICADO E NOVO) ---

# ALTERADO: O endpoint /login agora retorna um Token
@app.post("/login", response_model=schemas.Token)
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """ Autentica um usuário e retorna um Token JWT """
    user_email = form_data.username
    password = form_data.password
    db_user = crud.get_user_by_email(db, email=user_email)
    
    if not db_user or not crud.verify_password(password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos.",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # Cria o token de acesso
    access_token = security.create_access_token(
        data={"sub": db_user.email} # "sub" (subject) é o nome padrão para o identificador do usuário no JWT
    )
    
    # Retorna o token
    return {"access_token": access_token, "token_type": "bearer"}

# NOVO: Endpoint protegido para testar a autenticação
@app.get("/users/me", response_model=schemas.User)
def read_users_me(current_user: models.User = Depends(security.get_current_user)):
    """
    Retorna os dados do usuário logado.
    Este endpoint requer um token JWT válido.
    """
    # A dependência 'get_current_user' faz todo o trabalho de validação.
    # Se chegarmos aqui, o 'current_user' é válido e vem do banco.
    return current_user

# --- Fim do Arquivo ---