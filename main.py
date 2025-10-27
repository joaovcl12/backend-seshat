# main.py

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
# NOVO: Importa Session do SQLAlchemy e nossas dependências/modelos/schemas
from sqlalchemy.orm import Session
import models, schemas, database # Nossos novos arquivos
from database import SessionLocal, engine, get_db # Funções de banco de dados
from passlib.context import CryptContext

# --- Criação das Tabelas no Banco de Dados ---
# Esta linha cria as tabelas definidas em models.py (se elas ainda não existirem)
# toda vez que a aplicação FastAPI inicia.
models.Base.metadata.create_all(bind=engine)

# --- Configuração ---
app = FastAPI()
origins = ["http://localhost:5173"]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Funções Auxiliares de Segurança (CRUD - Create, Read, Update, Delete) ---
# Vamos criar funções separadas para interagir com o banco de dados.

def get_user_by_email(db: Session, email: str):
    """ Busca um usuário pelo email no banco de dados """
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    """ Cria um novo usuário no banco de dados """
    hashed_password = get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user) # Adiciona o novo usuário à sessão
    db.commit() # Salva as mudanças no banco de dados
    db.refresh(db_user) # Atualiza o objeto db_user com dados do BD (como o ID)
    return db_user

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha fornecida corresponde ao hash guardado."""
    plain_password_bytes = plain_password.encode('utf-8')
    if len(plain_password_bytes) > 72: plain_password_bytes = plain_password_bytes[:72]
    return pwd_context.verify(plain_password_bytes, hashed_password)

def get_password_hash(password: str) -> str:
    """Gera o hash seguro de uma senha."""
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72: password_bytes = password_bytes[:72]
    return pwd_context.hash(password_bytes)

# --- Endpoints da API (Modificados) ---

@app.get("/")
def read_root():
    return {"message": "API do Projeto SeShat está no ar!"}

@app.get("/materias")
def get_materias():
    subjects = ['Matemática', 'Português', 'História', 'Redação', 'Física']
    return {"materias_disponiveis": subjects}

# Endpoint de Registro (Modificado)
# Agora recebe 'db: Session = Depends(get_db)' para obter a sessão do banco
@app.post("/register", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def register_user(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    """ Registra um novo usuário no banco de dados """
    db_user = get_user_by_email(db, email=user_data.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Este email já está registrado.")
    
    # Chama a função auxiliar para criar o usuário no BD
    new_user = create_user(db=db, user=user_data)
    # Retorna os dados do usuário criado (usando o schema.User que não inclui a senha)
    return new_user

# Endpoint de Login (Modificado)
@app.post("/login")
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """ Autentica um usuário usando o banco de dados """
    user_email = form_data.username
    password = form_data.password
    
    # Busca o usuário no banco de dados real
    db_user = get_user_by_email(db, email=user_email)
    
    # Verifica se o usuário existe E se a senha está correta
    if not db_user or not verify_password(password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos.",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # --- PRÓXIMO PASSO: Gerar e retornar um Token JWT ---
    return {"message": f"Login bem-sucedido para {user_email}!"}

# --- Fim do Arquivo ---