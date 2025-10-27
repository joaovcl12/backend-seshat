# database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Define a URL do banco de dados SQLite.
# 'sqlite:///./seshat.db' significa que usaremos SQLite
# e o arquivo do banco se chamará 'seshat.db' e ficará na mesma pasta do main.py.
SQLALCHEMY_DATABASE_URL = "sqlite:///./seshat.db"

# Cria o "motor" do SQLAlchemy. connect_args é específico para SQLite para permitir
# que o mesmo objeto seja usado em diferentes threads (necessário para FastAPI).
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Cria uma fábrica de sessões. Cada instância de SessionLocal será uma sessão de banco de dados.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Cria uma classe Base da qual nossos modelos ORM (tabelas) irão herdar.
Base = declarative_base()

# Função para obter uma sessão do banco de dados (será usada como dependência no FastAPI)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()