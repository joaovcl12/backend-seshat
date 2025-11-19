# ai_service.py
import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configura a API com a chave
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

def generate_study_plan_ai(months: int, focus_areas: list[str]):
    """
    Usa o Gemini para gerar um plano de estudos estruturado.
    Retorna um dicionário Python pronto para ser salvo no banco.
    """
    
    # Escolhemos o modelo (o Flash é rápido e barato/gratuito)
    model = genai.GenerativeModel('gemini-pro')
    
    # O Prompt é a parte mais importante. Damos instruções estritas para retornar JSON.
    prompt = f"""
    Aja como um tutor especialista em vestibulares (ENEM/Vestibular).
    Crie um cronograma de estudos focado para um aluno que tem {months} meses até a prova.
    As áreas de foco principais são: {', '.join(focus_areas)}.
    
    Regras OBRIGATÓRIAS:
    1. Crie exatamente 3 matérias principais baseadas no foco.
    2. Para cada matéria, crie exatamente 3 tópicos fundamentais que cabem nesse tempo.
    3. Sua resposta deve ser APENAS um JSON válido, sem markdown, sem aspas triplas, sem texto antes ou depois.
    
    O formato do JSON deve ser estritamente este:
    {{
      "nome_plano": "Nome Criativo do Plano",
      "materias": [
        {{
          "nome": "Nome da Matéria",
          "topicos": ["Tópico 1", "Tópico 2", "Tópico 3"]
        }}
      ]
    }}
    """

    try:
        response = model.generate_content(prompt)
        
        # Limpeza básica caso o Gemini mande ```json ... ```
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        
        # Converte o texto da IA em objeto Python (Dicionário)
        plan_data = json.loads(clean_text)
        return plan_data
        
    except Exception as e:
        print(f"Erro na IA: {e}")
        return None
    
def generate_question_hint(question_text: str, options: dict, correct_option: str):
    """
    Usa o Gemini para gerar uma dica pedagógica sem revelar a resposta.
    """
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # O texto da opção correta
    correct_text = options.get(correct_option, "Desconhecida")
    
    prompt = f"""
    Você é um tutor inteligente e pedagógico (IAra).
    Um aluno está com dúvida na seguinte questão:
    
    Enunciado: "{question_text}"
    Opções: {json.dumps(options, ensure_ascii=False)}
    
    A resposta CORRETA é a opção {correct_option}: "{correct_text}".
    
    SUA TAREFA:
    Dê uma dica curta e direta para ajudar o aluno a chegar nessa conclusão sozinho.
    
    REGRAS OBRIGATÓRIAS:
    1. JAMAIS revele qual é a letra ou a resposta correta diretamente.
    2. Não explique a questão inteira, apenas aponte o caminho.
    3. Seja encorajador.
    4. Máximo de 3 frases.
    """

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Erro na IA (Dica): {e}")
        return "Tente reler o enunciado com calma, focando nas palavras-chave."