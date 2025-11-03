# models.py

# ALTERADO: Importa ForeignKey e relationship
from sqlalchemy import Boolean, Column, Integer, String, JSON, ForeignKey
from sqlalchemy.orm import relationship # Importa relationship
from database import Base

# --- Tabela de Usuários (Já existe) ---
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # NOVO: Adiciona um "relacionamento" reverso.
    # Isso cria um atributo "user.cronogramas" que listará os cronogramas deste usuário.
    # 'back_populates' aponta para o atributo "owner" no modelo Cronograma.
    cronogramas = relationship("Cronograma", back_populates="owner")


# --- Tabela de Questões (Já existe) ---
class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String, index=True, nullable=False)
    text = Column(String, nullable=False)
    options = Column(JSON, nullable=False)
    correct_answer = Column(String, nullable=False)
    source = Column(String, index=True, nullable=True)
    year = Column(Integer, index=True, nullable=True)


# --- NOVO: Tabela 'cronogramas' ---
# Cada linha é um cronograma "pai"
class Cronograma(Base):
    __tablename__ = "cronogramas"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True, default="Meu Cronograma") # Ex: "Plano Reta Final ENEM"
    
    # Chave estrangeira para ligar este cronograma a um usuário
    owner_id = Column(Integer, ForeignKey("users.id"))

    # Relacionamento: Define o atributo "cronograma.owner" que acessará
    # o objeto User correspondente.
    owner = relationship("User", back_populates="cronogramas")
    
    # Relacionamento Reverso: O atributo "cronograma.materias" listará
    # todas as matérias deste cronograma.
    materias = relationship("MateriaCronograma", back_populates="cronograma", cascade="all, delete-orphan")


# --- NOVO: Tabela 'materias_cronograma' ---
# Armazena as matérias (e o limite de 3) para um cronograma
class MateriaCronograma(Base):
    __tablename__ = "materias_cronograma"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True, nullable=False) # Ex: "Matemática"
    
    # Chave estrangeira para ligar esta matéria a um cronograma
    cronograma_id = Column(Integer, ForeignKey("cronogramas.id"))

    # Relacionamento
    cronograma = relationship("Cronograma", back_populates="materias")
    
    # Relacionamento Reverso: "materia.topicos" listará os tópicos
    topicos = relationship("TopicoCronograma", back_populates="materia", cascade="all, delete-orphan")

# --- NOVO: Tabela 'topicos_cronograma' ---
# Armazena os tópicos customizados (limite de 3) para uma matéria
class TopicoCronograma(Base):
    __tablename__ = "topicos_cronograma"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False) # Ex: "Álgebra Linear" (o texto do usuário)
    concluido = Column(Boolean, default=False) # Para o usuário marcar se já estudou
    
    # Chave estrangeira para ligar este tópico a uma matéria
    materia_id = Column(Integer, ForeignKey("materias_cronograma.id"))
    
    # Relacionamento
    materia = relationship("MateriaCronograma", back_populates="topicos")