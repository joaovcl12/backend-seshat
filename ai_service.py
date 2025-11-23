import os
import json
from google import genai
from dotenv import load_dotenv

load_dotenv()

# Cliente do SDK novo
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# MODELO RECOMENDADO
MODEL_NAME = "models/gemini-2.5-flash"   # ou gemini-3.0-pro-preview (se sua conta tiver acesso)


def generate_study_plan_ai(months: int, focus_areas: list[str]):
    """
    Gera o plano de estudos usando JSON mode REAL do novo SDK.
    """
    prompt = f"""
    Atue como um tutor especialista em vestibulares.
    Crie um cronograma de estudos de {months} meses focado em: {', '.join(focus_areas)}.

    O esquema JSON deve seguir EXATAMENTE esta estrutura:
    {{
      "nome_plano": "string",
      "materias": [
        {{
          "nome": "string",
          "topicos": ["string", "string", "string"]
        }}
      ]
    }}

    Regras:
    1. Crie exatamente 3 matérias.
    2. Crie exatamente 3 tópicos por matéria.
    """

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            generation_config={
                "response_mime_type": "application/json"
            }
        )

        return json.loads(response.text)

    except Exception as e:
        print(f"Erro na IA (Plano): {e}")
        return None



def generate_question_hint(question_text: str, options: dict, correct_option: str):
    """
    Gera uma dica pedagógica (texto comum).
    """
    correct_text = options.get(correct_option, "Resposta não identificada")

    prompt = f"""
    Você é a IAra, uma tutora amigável.
    O aluno está travado nesta questão:
    "{question_text}"

    Opções: {json.dumps(options, ensure_ascii=False)}
    A resposta certa é a {correct_option} ({correct_text}).

    Dê uma dica CURTA (máximo 2 frases) que ajude ele a pensar, sem dar a resposta.
    """

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
        )
        return response.text.strip()

    except Exception as e:
        print(f"Erro na IA (Dica): {e}")
        return "Tente revisar o enunciado com atenção aos detalhes principais."
