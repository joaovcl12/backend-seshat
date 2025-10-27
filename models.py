# models.py

from sqlalchemy import Column, Integer, String, JSON, ForeignKey
from database import Base # Importa a Base que criamos

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

# <<< GARANTA QUE ESTA CLASSE EXISTA E ESTEJA CORRETA >>>
# Modelo para a tabela 'questions'
class Question(Base): # <-- O nome deve ser exatamente este
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String, index=True, nullable=False)
    text = Column(String, nullable=False)
    options = Column(JSON, nullable=False)
    correct_answer = Column(String, nullable=False)
    source = Column(String, index=True, nullable=True)
    year = Column(Integer, index=True, nullable=True)