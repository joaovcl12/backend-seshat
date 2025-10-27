# crud.py

from sqlalchemy.orm import Session
# NOVO: Importa func do SQLAlchemy para usar funções SQL como RANDOM()
from sqlalchemy import func
import models, schemas # Importa nossos modelos SQLAlchemy e Pydantic
from passlib.context import CryptContext

# Define o contexto para hashing de senhas (usando bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Funções de Segurança ---

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha fornecida (texto puro) corresponde ao hash guardado."""
    # Converte a senha para bytes
    plain_password_bytes = plain_password.encode('utf-8')
    # Trunca se for maior que 72 bytes (limitação do bcrypt)
    if len(plain_password_bytes) > 72:
        plain_password_bytes = plain_password_bytes[:72]
    # Compara a senha (bytes) com o hash
    return pwd_context.verify(plain_password_bytes, hashed_password)

def get_password_hash(password: str) -> str:
    """Gera o hash seguro (bcrypt) de uma senha."""
    # Converte a senha para bytes
    password_bytes = password.encode('utf-8')
    # Trunca se for maior que 72 bytes
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    # Gera e retorna o hash
    return pwd_context.hash(password_bytes)

# --- Funções CRUD para Usuários ---
# CRUD = Create, Read, Update, Delete

def get_user_by_email(db: Session, email: str):
    """
    Busca um usuário no banco de dados pelo seu email.
    Retorna o objeto User (do models.py) ou None se não encontrar.
    """
    # db.query(models.User): Inicia uma consulta na tabela User.
    # .filter(models.User.email == email): Filtra onde a coluna email é igual ao email fornecido.
    # .first(): Retorna o primeiro resultado encontrado (ou None).
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    """
    Cria um novo usuário no banco de dados.
    Recebe a sessão do banco (db) e os dados do usuário (schema Pydantic).
    Retorna o objeto User recém-criado (com ID, etc.).
    """
    # Gera o hash da senha fornecida
    hashed_password = get_password_hash(user.password)
    # Cria uma instância do modelo SQLAlchemy User com os dados
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    # Adiciona o novo objeto à sessão do SQLAlchemy (prepara para salvar)
    db.add(db_user)
    # Efetivamente salva as mudanças no banco de dados
    db.commit()
    # Atualiza o objeto db_user com os dados que o banco gerou (como o ID)
    db.refresh(db_user)
    # Retorna o objeto do usuário criado
    return db_user

# --- Funções CRUD para Questões ---

def get_questions_by_subject(db: Session, subject: str, count: int = 10):
    """
    Busca um número específico ('count') de questões aleatórias por matéria.
    Recebe a sessão do banco (db), a matéria (subject) e a quantidade (count).
    Retorna uma lista de objetos Question (do models.py).
    """
    # db.query(models.Question): Inicia uma consulta na tabela Question.
    # .filter(models.Question.subject == subject): Filtra pela matéria fornecida.
    # .order_by(func.random()): Ordena os resultados aleatoriamente.
    # .limit(count): Limita o número de resultados à quantidade desejada.
    # .all(): Executa a consulta e retorna todos os resultados encontrados (como uma lista).
    return db.query(models.Question)\
             .filter(models.Question.subject == subject)\
             .order_by(func.random())\
             .limit(count)\
             .all()

def create_question(db: Session, question: schemas.QuestionCreate):
    """
    Cria uma nova questão no banco de dados.
    Recebe a sessão do banco (db) e os dados da questão (schema Pydantic).
    Retorna o objeto Question recém-criado.
    """
    # Cria uma instância do modelo SQLAlchemy Question
    db_question = models.Question(
        subject=question.subject,
        text=question.text,
        options=question.options, # SQLAlchemy lida bem com a conversão para JSON
        correct_answer=question.correct_answer,
        source=question.source,
        year=question.year
    )
    # Adiciona, salva e atualiza, como fizemos para o usuário
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    # Retorna o objeto da questão criada
    return db_question