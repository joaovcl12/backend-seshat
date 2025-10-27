# populate_db.py

import json
from sqlalchemy.orm import Session
from database import SessionLocal, engine # Importa do nosso arquivo database.py
import models, schemas # Importa nossos modelos e schemas
import crud # Importa nossas funções CRUD

# Garante que as tabelas existam antes de tentar inserir
models.Base.metadata.create_all(bind=engine)

def populate_questions_from_json(db: Session, json_filepath: str = "questoes.json"):
    """ Lê um arquivo JSON e insere as questões no banco de dados. """
    
    print(f"Lendo questões do arquivo: {json_filepath}")
    try:
        with open(json_filepath, 'r', encoding='utf-8') as f:
            questions_data = json.load(f)
    except FileNotFoundError:
        print(f"Erro: Arquivo '{json_filepath}' não encontrado.")
        return
    except json.JSONDecodeError:
        print(f"Erro: Falha ao decodificar o JSON no arquivo '{json_filepath}'. Verifique a formatação.")
        return

    print(f"Encontradas {len(questions_data)} questões no JSON.")
    
    questions_added = 0
    for q_data in questions_data:
        # Verifica se todos os campos obrigatórios estão presentes
        required_fields = ["subject", "text", "options", "correct_answer"]
        if not all(field in q_data for field in required_fields):
            print(f"AVISO: Pulando questão por falta de campos obrigatórios: {q_data.get('text', 'Texto não encontrado')}")
            continue

        # Cria um objeto schema Pydantic para validação (opcional, mas bom)
        try:
            question_schema = schemas.QuestionCreate(**q_data)
        except Exception as e:
            print(f"AVISO: Pulando questão devido a erro de validação Pydantic: {e} - Dados: {q_data.get('text', 'Texto não encontrado')}")
            continue

        # Verifica se uma questão com o mesmo texto já existe (evitar duplicatas simples)
        # Nota: Uma verificação melhor poderia usar source e year também
        existing_question = db.query(models.Question).filter(models.Question.text == question_schema.text).first()
        if existing_question:
            print(f"AVISO: Questão já existe no banco (baseado no texto), pulando: {question_schema.text[:50]}...")
            continue
            
        # Usa a função CRUD para criar a questão
        try:
            crud.create_question(db=db, question=question_schema)
            questions_added += 1
        except Exception as e:
            print(f"ERRO ao inserir questão: {e} - Dados: {question_schema.text[:50]}...")
            db.rollback() # Desfaz a tentativa de adição em caso de erro

    print(f"--------------------------------------------------")
    print(f"Total de questões adicionadas ao banco: {questions_added}")
    print(f"População do banco de dados concluída.")


if __name__ == "__main__":
    # Obtém uma sessão do banco de dados
    db = SessionLocal()
    try:
        populate_questions_from_json(db)
    finally:
        # Garante que a sessão seja fechada, mesmo se ocorrer um erro
        db.close()