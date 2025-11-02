# crud.py

from sqlalchemy.orm import Session
from sqlalchemy import func 
import models, schemas
from passlib.context import CryptContext

# ... (todo o código de hashing e CRUD de usuários permanece o mesmo) ...
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    plain_password_bytes = plain_password.encode('utf-8')
    if len(plain_password_bytes) > 72: plain_password_bytes = plain_password_bytes[:72]
    return pwd_context.verify(plain_password_bytes, hashed_password)

def get_password_hash(password: str) -> str:
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72: password_bytes = password_bytes[:72]
    return pwd_context.hash(password_bytes)

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# --- CRUD para Questões ---

# ALTERADO: A função agora aceita 'source' e 'year' como parâmetros opcionais
def get_questions_by_subject(db: Session, subject: str, count: int, source: str | None = None, year: int | None = None):
    """ 
    Busca um número ('count') de questões aleatórias por matéria,
    com filtros opcionais de fonte (source) e ano (year).
    """
    
    # 1. Começa a consulta (query) filtrando pela matéria (que é obrigatória)
    query = db.query(models.Question).filter(models.Question.subject == subject)
    
    # 2. Adiciona o filtro de 'source' (ex: "ENEM") se ele for fornecido
    if source:
        query = query.filter(models.Question.source == source)
        
    # 3. Adiciona o filtro de 'year' (ex: 2023) se ele for fornecido
    if year:
        query = query.filter(models.Question.year == year)
        
    # 4. Aplica a ordenação aleatória, limita a contagem e retorna os resultados
    return query.order_by(func.random()).limit(count).all()


def create_question(db: Session, question: schemas.QuestionCreate):
    # ... (esta função permanece a mesma) ...
    db_question = models.Question(
        subject=question.subject,
        text=question.text,
        options=question.options,
        correct_answer=question.correct_answer,
        source=question.source,
        year=question.year
    )
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    return db_question