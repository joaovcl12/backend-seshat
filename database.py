# database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. URL antiga do SQLite (agora comentada)
# SQLALCHEMY_DATABASE_URL = "sqlite:///./seshat.db"

# 2. NOVA URL do PostgreSQL (copiada do Render)
SQLALCHEMY_DATABASE_URL = "postgresql://seshat_db_user:R42XbyBjGIkkVJJ6AI8ANw7V9tyImaEW@dpg-d43u7podl3ps73aa0qu0-a/seshat_db"


# 3. 'engine' antigo do SQLite (agora comentado)
# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
# )

# 4. NOVO 'engine' para PostgreSQL (sem connect_args)
engine = create_engine(SQLALCHEMY_DATABASE_URL)


# O resto do arquivo permanece o mesmo
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