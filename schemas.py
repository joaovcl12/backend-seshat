# schemas.py

from pydantic import BaseModel, EmailStr
# ALTERADO: Importa 'List' de 'typing'
from typing import Dict, List, Union

# --- Esquemas para Usuários ---
class UserBase(BaseModel):
    email: EmailStr
class UserCreate(UserBase):
    password: str
class User(UserBase):
    id: int
    class Config:
        from_attributes = True

# --- Esquemas para Autenticação (Token) ---
class TokenData(BaseModel):
    email: str | None = None
class Token(BaseModel):
    access_token: str
    token_type: str

# --- Esquemas para Questões ---
class QuestionBase(BaseModel):
    subject: str
    text: str
    options: Union[List[str], Dict[str, str]] 
    source: str | None = None
    year: int | None = None
class QuestionCreate(QuestionBase):
    correct_answer: str
class Question(QuestionBase):
    id: int
    class Config:
        from_attributes = True

# --- NOVO: Esquemas para Tópicos do Cronograma ---

# O que o usuário envia para criar um tópico (apenas o nome)
class TopicoCronogramaCreate(BaseModel):
    nome: str

# Como o tópico será retornado pela API (com ID e status)
class TopicoCronograma(TopicoCronogramaCreate):
    id: int
    concluido: bool

    class Config:
        from_attributes = True # Permite ler de objetos SQLAlchemy

# --- NOVO: Esquemas para Matérias do Cronograma ---

# O que o usuário envia para criar uma matéria (apenas o nome)
class MateriaCronogramaCreate(BaseModel):
    nome: str

# Como a matéria será retornada pela API (com ID e a lista de seus tópicos)
class MateriaCronograma(MateriaCronogramaCreate):
    id: int
    topicos: List[TopicoCronograma] = [] # Lista aninhada de tópicos

    class Config:
        from_attributes = True # Permite ler de objetos SQLAlchemy

# --- NOVO: Esquemas para o Cronograma Principal ---

# O que o usuário envia para criar um cronograma (apenas o nome)
class CronogramaCreate(BaseModel):
    nome: str

# Como o cronograma completo será retornado pela API (com ID, dono e a lista de matérias)
class Cronograma(CronogramaCreate):
    id: int
    owner_id: int
    materias: List[MateriaCronograma] = [] # Lista aninhada de matérias

    class Config:
        from_attributes = True # Permite ler de objetos SQLAlchemy