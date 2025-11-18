# security.py

import os # Importa a biblioteca para acessar o sistema
from dotenv import load_dotenv # Importa a biblioteca para ler o arquivo .env
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
import schemas, database, models, crud

# CHAMA A FUNÇÃO PARA CARREGAR O ARQUIVO .env (se ele existir)
# Isso permite que a variável SECRET_KEY seja lida localmente
load_dotenv()

# --- Configuração do Token ---

# LÊ A CHAVE SECRETA DAS VARIÁVEIS DE AMBIENTE
# Localmente, virá do .env. No Render, virá das "Environment Variables"
SECRET_KEY = os.environ.get("SECRET_KEY")

# Adiciona uma verificação para garantir que a chave foi carregada
if SECRET_KEY is None:
    raise EnvironmentError("FATAL: SECRET_KEY não foi definida no ambiente.")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 #7 dias

# Este é o "esquema" que diz ao FastAPI "Vá no Header da requisição, procure por
# 'Authorization' e me dê o token que está lá".
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# --- Funções de Criação e Verificação ---

def create_access_token(data: dict):
    """Cria um novo token JWT."""
    to_encode = data.copy()
    # Adiciona um tempo de expiração ao token
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    # Codifica o token com nossos dados, a chave secreta e o algoritmo
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str, credentials_exception) -> schemas.TokenData:
    """Decodifica e valida um token."""
    try:
        # Tenta decodificar o token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # Pega o email (que guardamos como 'sub' de 'subject') de dentro do token
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        # Valida os dados do token usando nosso schema Pydantic
        token_data = schemas.TokenData(email=email)
    except JWTError:
        # Se o token for inválido (expirado, assinatura errada, etc)
        raise credentials_exception
    return token_data

# --- Dependência "Get Current User" ---

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)) -> models.User:
    """
    Uma dependência do FastAPI que valida o token e retorna o usuário do banco.
    Nossos endpoints protegidos (como /cronograma/me) usarão isso.
    """
    # Exceção padrão para erros de autenticação
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    # Valida o token
    token_data = verify_token(token, credentials_exception)
    # Busca o usuário no banco de dados
    user = crud.get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    # Retorna o objeto User do SQLAlchemy
    return user