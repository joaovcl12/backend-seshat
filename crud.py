# crud.py

from sqlalchemy.orm import Session
from sqlalchemy import func
# Importa HTTPException para podermos retornar erros de lógica de negócio
from fastapi import HTTPException, status 
import models, schemas
from passlib.context import CryptContext

# ... (pwd_context, verify_password, get_password_hash, ... )
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    plain_password_bytes = plain_password.encode('utf-8')
    if len(plain_password_bytes) > 72: plain_password_bytes = plain_password_bytes[:72]
    return pwd_context.verify(plain_password_bytes, hashed_password)

def get_password_hash(password: str) -> str:
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72: password_bytes = password_bytes[:72]
    return pwd_context.hash(password_bytes)

# --- CRUD para Usuários ---
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
def get_questions_by_subject(db: Session, subject: str, count: int, source: str | None = None, year: int | None = None):
    query = db.query(models.Question).filter(models.Question.subject == subject)
    if source:
        query = query.filter(models.Question.source == source)
    if year:
        query = query.filter(models.Question.year == year)
    return query.order_by(func.random()).limit(count).all()

# // NOVO: Função para buscar uma única questão pelo seu ID (necessária para verificação)
def get_question_by_id(db: Session, question_id: int):
    """ Busca uma questão específica pelo seu ID. """
    return db.query(models.Question).filter(models.Question.id == question_id).first()
# // FIM DO NOVO CÓDIGO

def create_question(db: Session, question: schemas.QuestionCreate):
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

# --- CRUD para Cronogramas ---

def get_cronograma_by_owner_id(db: Session, owner_id: int):
    """
    Busca o primeiro cronograma pertencente a um usuário.
    (Por enquanto, vamos assumir que um usuário tem apenas um cronograma principal)
    """
    return db.query(models.Cronograma).filter(models.Cronograma.owner_id == owner_id).first()

def create_user_cronograma(db: Session, cronograma: schemas.CronogramaCreate, owner_id: int):
    """ Cria um novo cronograma "pai" para um usuário. """
    # Cria o objeto do banco de dados, ligando-o ao 'owner_id'
    db_cronograma = models.Cronograma(**cronograma.model_dump(), owner_id=owner_id)
    db.add(db_cronograma)
    db.commit()
    db.refresh(db_cronograma)
    return db_cronograma

def add_materia_to_cronograma(db: Session, materia: schemas.MateriaCronogramaCreate, cronograma_id: int):
    """ Adiciona uma nova matéria a um cronograma, respeitando o limite de 3. """
    
    # 1. Pega o cronograma pai para verificar o limite
    db_cronograma = db.query(models.Cronograma).filter(models.Cronograma.id == cronograma_id).first()
    
    # 2. Verifica a lógica de negócio (limite de 3 matérias)
    if len(db_cronograma.materias) >= 3:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Limite de 3 matérias por cronograma atingido.")
    
    # 3. Se o limite estiver OK, cria e salva a nova matéria
    db_materia = models.MateriaCronograma(nome=materia.nome, cronograma_id=cronograma_id)
    db.add(db_materia)
    db.commit()
    db.refresh(db_materia)
    return db_materia

def get_materia_by_id(db: Session, materia_id: int):
    """ Função auxiliar para buscar uma matéria específica """
    return db.query(models.MateriaCronograma).filter(models.MateriaCronograma.id == materia_id).first()

def add_topico_to_materia(db: Session, topico: schemas.TopicoCronogramaCreate, materia_id: int):
    """ Adiciona um novo tópico a uma matéria, respeitando o limite de 3. """
    
    # 1. Pega a matéria pai para verificar o limite
    db_materia = get_materia_by_id(db, materia_id)
    
    # 2. Verifica se a matéria existe
    if not db_materia:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Matéria não encontrada.")
    
    # 3. Verifica a lógica de negócio (limite de 3 tópicos)
    if len(db_materia.topicos) >= 3:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Limite de 3 tópicos por matéria atingido.")
    
    # 4. Se tudo estiver OK, cria e salva o novo tópico
    db_topico = models.TopicoCronograma(nome=topico.nome, materia_id=materia_id)
    db.add(db_topico)
    db.commit()
    db.refresh(db_topico)
    return db_topico

# --- NOVO: Funções de Lógica do Cronograma ---

def generate_weekly_schedule(db: Session, cronograma_id: int):
    """
    Gera uma sugestão de cronograma semanal, rotacionando os tópicos das matérias.
    Retorna um dicionário formatado por dia da semana.
    """
    
    # 1. Busca o cronograma e suas matérias/tópicos
    db_cronograma = db.query(models.Cronograma).filter(models.Cronograma.id == cronograma_id).first()
    
    if not db_cronograma or not db_cronograma.materias:
        return {"detalhe": "Nenhuma matéria encontrada neste cronograma."}

    # 2. Extrai todos os tópicos de todas as matérias
    # Ex: [[mat1_top1, mat1_top2], [mat2_top1]]
    topicos_por_materia = []
    for materia in db_cronograma.materias:
        topicos_nao_concluidos = [t.nome for t in materia.topicos if not t.concluido]
        if topicos_nao_concluidos:
            topicos_por_materia.append(topicos_nao_concluidos)
            
    if not topicos_por_materia:
        return {"detalhe": "Todos os tópicos já foram concluídos!"}

    # 3. Define os dias da semana para o estudo
    dias_da_semana = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
    
    plano_semanal = {dia: "Descanso" for dia in dias_da_semana} # Começa com todos os dias como "Descanso"
    
    # 4. Lógica de distribuição (Intercalação / Round-Robin)
    # Pega um tópico de cada matéria, depois o próximo tópico de cada, etc.
    
    dia_idx = 0
    topico_idx = 0
    continuar = True
    
    while dia_idx < len(dias_da_semana) and continuar:
        continuar = False # Assume que terminamos, a menos que encontremos um tópico
        
        for materia_topicos in topicos_por_materia:
            if topico_idx < len(materia_topicos):
                # Se esta matéria ainda tem um tópico neste nível (topico_idx)
                plano_semanal[dias_da_semana[dia_idx]] = materia_topicos[topico_idx]
                dia_idx += 1 # Avança para o próximo dia
                continuar = True # Encontramos um tópico, então continuamos o loop
            
            if dia_idx >= len(dias_da_semana):
                break # Para se os dias da semana acabarem
        
        topico_idx += 1 # Avança para o próximo "nível" de tópicos
        
    return plano_semanal