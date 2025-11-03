# schemas.py

from pydantic import BaseModel, EmailStr
from typing import Dict, List, Union

# --- Esquemas para Usuários ---
# (Seu código para UserBase, UserCreate, User)
class UserBase(BaseModel):
    email: EmailStr
class UserCreate(UserBase):
    password: str
class User(UserBase):
    id: int
    class Config:
        from_attributes = True

# --- NOVO: Esquemas para Questões ---

# Esquema base para os dados de uma questão
class QuestionBase(BaseModel):
    subject: str
    text: str
    options: Union[List[str], Dict[str, str]] 
    source: str | None = None
    year: int | None = None

# <<< GARANTA QUE ESTA CLASSE EXISTA E ESTEJA CORRETA >>>
# Esquema para criar uma nova questão (inclui a resposta correta)
class QuestionCreate(QuestionBase): # <-- O nome deve ser exatamente este
    correct_answer: str

# Esquema para retornar uma questão pela API
class Question(QuestionBase):
    id: int
    class Config:
        from_attributes = True

# NOVO: Schema para o que está DENTRO do token JWT
class TokenData(BaseModel):
    email: str | None = None

# NOVO: Schema para o que será RETORNADO no endpoint de login
class Token(BaseModel):
    access_token: str
    token_type: str