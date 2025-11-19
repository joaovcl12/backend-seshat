import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Função auxiliar para instanciar o modelo correto
def get_model():
    # Usamos o flash por ser mais rápido e barato/gratuito na tier atual
    return genai.GenerativeModel('gemini-1.5-flash')

def generate_study_plan_ai(months: int, focus_areas: list[str]):
    model = get_model() # <--- ALTERADO AQUI
    
    prompt = f"""
    Aja como um tutor especialista em vestibulares.
    Crie um cronograma de estudos focado para {months} meses.
    Áreas de foco: {', '.join(focus_areas)}.
    
    Retorne APENAS um JSON válido neste formato exato, sem markdown:
    {{
      "nome_plano": "Nome Criativo",
      "materias": [
        {{ "nome": "Matéria", "topicos": ["Tópico 1", "Tópico 2", "Tópico 3"] }}
      ]
    }}
    """

    try:
        response = model.generate_content(prompt)
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_text)
    except Exception as e:
        print(f"Erro na IA (Plano): {e}")
        return None
    
def generate_question_hint(question_text: str, options: dict, correct_option: str):
    model = get_model() # <--- ALTERADO AQUI
    
    correct_text = options.get(correct_option, "Desconhecida")
    
    prompt = f"""
    Você é um tutor pedagógico. O aluno errou esta questão:
    Enunciado: "{question_text}"
    Opções: {json.dumps(options, ensure_ascii=False)}
    Resposta Correta: {correct_option} ({correct_text})
    
    Dê uma dica curta (máx 3 frases) para guiar o aluno sem dar a resposta direta.
    Seja encorajador.
    """

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Erro na IA (Dica): {e}")
        return "Revise o enunciado com atenção aos detalhes principais."