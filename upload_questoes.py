# upload_questoes.py
import requests # A biblioteca que acabamos de instalar
import json
from time import sleep # Para adicionar um pequeno atraso e não sobrecarregar a API

# --- Configuração ---
# A URL da sua API que está online no Render
API_URL = "https://seshat-api-m30w.onrender.com" 
ENDPOINT = f"{API_URL}/perguntas"
JSON_FILE = "questoes.json"

print(f"Iniciando upload para: {API_URL}")
print("Lendo questões de:", JSON_FILE)

try:
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        questions_data = json.load(f)
except FileNotFoundError:
    print(f"ERRO: Arquivo '{JSON_FILE}' não encontrado.")
    exit()
except json.JSONDecodeError:
    print(f"ERRO: Falha ao ler o arquivo JSON. Verifique a formatação.")
    exit()

print(f"Encontradas {len(questions_data)} questões. Iniciando envio...")
print("--------------------------------------------------")

questions_added = 0
questions_failed = 0

# Faz um loop por cada questão no arquivo JSON
for q_data in questions_data:
    try:
        # Tenta enviar a questão para o endpoint POST /perguntas
        response = requests.post(ENDPOINT, json=q_data)

        # Verifica o código de status da resposta
        if response.status_code == 201: # 201 Created (Sucesso!)
            print(f"SUCESSO: Questão '{q_data['text'][:50]}...' adicionada.")
            questions_added += 1
        elif response.status_code == 400: # 400 Bad Request (Provavelmente duplicada)
            print(f"AVISO: Questão '{q_data['text'][:50]}...' provavelmente já existe ou dados inválidos. (Servidor disse: {response.json().get('detail')})")
            questions_failed += 1
        else:
            # Outros erros (500, 404, etc.)
            print(f"ERRO: Falha ao adicionar questão '{q_data['text'][:50]}...'. Status: {response.status_code}, Resposta: {response.text}")
            questions_failed += 1

    except requests.exceptions.RequestException as e:
        print(f"ERRO DE CONEXÃO: Não foi possível conectar à API. {e}")
        print("Verifique se a API está online e a URL está correta.")
        exit()
    
    # Adiciona um pequeno atraso para não sobrecarregar o plano gratuito do Render
    sleep(0.5) # Meio segundo de pausa entre cada requisição

print("--------------------------------------------------")
print("Upload concluído!")
print(f"Questões adicionadas com sucesso: {questions_added}")
print(f"Falhas ou duplicatas: {questions_failed}")