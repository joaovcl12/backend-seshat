# main.py

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List 
from datetime import timedelta

# Importa todos os nossos módulos
import crud, models, schemas, database, security 
from database import engine, get_db

# Cria todas as tabelas (incluindo as novas do cronograma)
models.Base.metadata.create_all(bind=engine)

# Configuração do App e CORS
app = FastAPI()
origins = [
    "http://localhost:5173",
    "https://projeto-se-shat.vercel.app/" # Substitua pela URL do Vercel
]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


# --- Endpoints Públicos (Autenticação, Matérias, Questões) ---

@app.get("/")
def read_root(): return {"message": "API do Projeto SeShat está no ar!"}

@app.get("/materias")
def get_materias():
    # No futuro, podemos ler isso do banco também
    subjects = ['Matemática', 'Português', 'História', 'Redação', 'Física','Linguagens', 'Química', 'Biologia', 'Geografia', 'Inglês']
    return {"materias_disponiveis": subjects}

@app.post("/register", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def register_user(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user_data.email)
    if db_user: raise HTTPException(status_code=400, detail="Este email já está registrado.")
    new_user = crud.create_user(db=db, user=user_data)
    return new_user

@app.post("/login", response_model=schemas.Token)
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=form_data.username)
    if not db_user or not crud.verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email ou senha incorretos.", headers={"WWW-Authenticate": "Bearer"})
    
    access_token = security.create_access_token(data={"sub": db_user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/perguntas", response_model=schemas.Question, status_code=status.HTTP_201_CREATED)
def post_new_question(question: schemas.QuestionCreate, db: Session = Depends(get_db)):
    return crud.create_question(db=db, question=question)

@app.get("/perguntas/{subject}", response_model=List[schemas.Question])
def read_questions_by_subject(
    subject: str, 
    count: int = 10, 
    source: str | None = None,
    year: int | None = None,
    db: Session = Depends(get_db)
):
    questions = crud.get_questions_by_subject(db=db, subject=subject, count=count, source=source, year=year)
    if not questions:
         raise HTTPException(status_code=404, detail=f"Nenhuma pergunta encontrada para os filtros.")
    return questions


# --- Endpoint para Verificar Resposta ---

@app.post("/perguntas/verificar", response_model=schemas.AnswerCheckResponse)
def check_question_answer(
    answer_data: schemas.AnswerCheckRequest, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_user) 
):
    """
    Verifica se a resposta do usuário para uma questão está correta.
    Requer autenticação.
    """
    question = crud.get_question_by_id(db, question_id=answer_data.question_id)
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Questão não encontrada.")
    
    is_correct = (question.correct_answer == answer_data.user_answer)
    
    return {
        "is_correct": is_correct,
        "correct_answer": question.correct_answer,
        "question_id": question.id 
    }

# --- Dependência para o Cronograma do Usuário ---

def get_current_user_cronograma(db: Session = Depends(get_db), current_user: models.User = Depends(security.get_current_user)) -> models.Cronograma:
    """
    Dependência que busca o cronograma do usuário logado.
    Se não existir, cria um cronograma padrão para ele.
    """
    cronograma = crud.get_cronograma_by_owner_id(db, owner_id=current_user.id)
    
    if not cronograma:
        default_cronograma = schemas.CronogramaCreate(nome=f"Cronograma de {current_user.email.split('@')[0]}")
        cronograma = crud.create_user_cronograma(db, cronograma=default_cronograma, owner_id=current_user.id)
        
    return cronograma


# --- Endpoints do Cronograma (Protegidos) ---

@app.get("/cronograma/me", response_model=schemas.Cronograma)
def get_my_cronograma(
    # Esta dependência já faz o trabalho de buscar ou criar o cronograma
    cronograma: models.Cronograma = Depends(get_current_user_cronograma)
):
    """
    Busca o cronograma completo (com matérias e tópicos) do usuário logado.
    Cria um cronograma padrão se for o primeiro acesso.
    """
    return cronograma

# --- NOVO: Endpoint para o Cronograma Semanal ---

@app.get("/cronograma/me/semanal")
def get_my_weekly_schedule(
    db: Session = Depends(get_db),
    # Esta dependência garante que o usuário está logado e que o cronograma existe
    cronograma: models.Cronograma = Depends(get_current_user_cronograma)
):
    """
    Busca o cronograma do usuário e o formata em um plano de estudos
    semanal, distribuindo os tópicos (não concluídos) pelos dias.
    """
    # Chama a nova função de lógica que criamos no crud.py
    return crud.generate_weekly_schedule(db, cronograma_id=cronograma.id)

# --- FIM DO NOVO CÓDIGO ---

@app.post("/cronograma/materias", response_model=schemas.MateriaCronograma)
def add_materia_to_my_cronograma(
    materia_data: schemas.MateriaCronogramaCreate,
    db: Session = Depends(get_db),
    cronograma: models.Cronograma = Depends(get_current_user_cronograma)
):
    """
    Adiciona uma nova matéria ao cronograma do usuário logado.
    Limita a 3 matérias por cronograma.
    """
    return crud.add_materia_to_cronograma(db, materia=materia_data, cronograma_id=cronograma.id)


@app.post("/cronograma/materias/{materia_id}/topicos", response_model=schemas.TopicoCronograma)
def add_topico_to_my_materia(
    materia_id: int,
    topico_data: schemas.TopicoCronogramaCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    """
    Adiciona um novo tópico customizado a uma matéria específica.
    Verifica se o usuário é dono da matéria e se o limite de 3 tópicos foi atingido.
    """
    db_materia = crud.get_materia_by_id(db, materia_id=materia_id)
    
    if not db_materia:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Matéria não encontrada.")
        
    if db_materia.cronograma.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Você não tem permissão para editar esta matéria.")
    
    return crud.add_topico_to_materia(db, topico=topico_data, materia_id=materia_id)

# --- Fim do Arquivo ---