import os
import json
from openai import OpenAI

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise RuntimeError(
        "A variável de ambiente OPENAI_API_KEY não está definida. "
        "Configure a chave da OpenAI antes de rodar a aplicação."
    )

client = OpenAI(api_key=api_key)

SYSTEM_PROMPT = """
Você é um assistente especialista em interpretação de e-mails corporativos
para uma grande empresa do setor financeiro que recebe centenas de mensagens
por dia (acompanhamento de solicitações, envio de anexos, felicitações etc.).

Objetivo:
- Classificar cada e-mail recebido em duas categorias:
  - "Produtivo": quando o e-mail exige alguma ação, resposta ou acompanhamento
    (ex: pedido de suporte, atualização de status de uma requisição, dúvida
    sobre um produto/serviço, reclamação, incidente).
  - "Improdutivo": quando o e-mail é apenas uma mensagem cordial, felicitação,
    agradecimento ou conteúdo que não exige ação objetiva imediata.

- Gerar uma resposta automática sugerida em português do Brasil, profissional,
  cordial e concisa, que possa ser enviada ao remetente, respeitando um TOM
  DE RESPOSTA informado pelo usuário (mais formal, mais próximo etc.).

Regras:
- SEMPRE responda em PT-BR.
- Mantenha tom profissional, empático e claro.
- Se a categoria for "Produtivo":
  - Agradeça o contato.
  - Demonstre que a mensagem foi entendida.
  - Informe que a equipe irá analisar a solicitação/requisição e retornará.
- Se a categoria for "Improdutivo":
  - Agradeça a mensagem.
  - Retribua o reconhecimento/felicitação/elogio de forma breve.
- Nunca invente protocolos, números de chamado ou informações específicas
  que não estejam no texto do e-mail.

Formato da saída:
Responda APENAS com um JSON válido, sem comentários nem texto extra, no formato:

{
  "categoria": "Produtivo" ou "Improdutivo",
  "confianca": número entre 0 e 1,
  "resposta_sugerida": "texto da resposta em português",
  "motivo": "explicação breve, em uma ou duas frases, do porquê da classificação"
}
"""


def _gerar_json_com_openai(texto_email: str, estilo_resposta: str) -> dict:
    """
    Chama a API da OpenAI para classificar o e-mail e gerar a resposta sugerida.
    Espera receber um JSON no formato especificado no SYSTEM_PROMPT.
    """

    user_content = f"""
Texto do e-mail recebido:

\"\"\"{texto_email}\"\"\"

O tom desejado da resposta automática é: {estilo_resposta}.

Tarefas:
1. Classifique esse e-mail como "Produtivo" ou "Improdutivo".
2. Informe um nível de confiança entre 0 e 1 (por exemplo 0.82).
3. Gere uma resposta automática sugerida em português do Brasil,
   seguindo as regras definidas no contexto e o tom desejado.
4. Explique de forma curta o MOTIVO da classificação, em linguagem simples
   (ex: "o e-mail pede atualização de status de um chamado em aberto").
"""

    completion = client.chat.completions.create(
        model="gpt-4.1-mini",
        temperature=0.2,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
    )

    raw_output = completion.choices[0].message.content.strip()

    # Tenta parsear JSON diretamente
    try:
        data = json.loads(raw_output)
        return data
    except json.JSONDecodeError:
        # Caso venha com ```json ... ``` envolto
        cleaned = raw_output.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            # remove possível palavra json no início
            if cleaned.lower().startswith("json"):
                cleaned = cleaned[4:].strip()
        try:
            data = json.loads(cleaned)
            return data
        except json.JSONDecodeError:
            raise ValueError(
                f"Não foi possível interpretar a saída da IA como JSON: {raw_output}"
            )


def classificar_email(texto_email: str, tom_resposta: str = "padrao"):
    """
    Interface usada pelo Flask (app.py).
    Retorna:
      - categoria: "Produtivo" ou "Improdutivo"
      - score: float entre 0 e 1
      - resposta: string com a resposta sugerida
      - motivo: explicação curta da classificação
    """
    if not texto_email or len(texto_email.strip()) < 10:
        raise ValueError("Texto de email muito curto para classificação.")

    # Mapeia o código vindo do formulário para uma descrição de estilo
    estilos = {
        "padrao": "equilibrado, profissional e cordial",
        "formal": "mais formal, corporativo e objetivo",
        "informal": "mais próximo, leve e amigável, porém ainda profissional",
    }
    estilo_resposta = estilos.get(tom_resposta or "padrao", estilos["padrao"])

    data = _gerar_json_com_openai(texto_email, estilo_resposta)

    categoria_raw = (data.get("categoria") or "").strip()
    confianca_raw = data.get("confianca", 1.0)
    resposta = (data.get("resposta_sugerida") or "").strip()
    motivo = (data.get("motivo") or "").strip()

    # Normaliza categoria
    cat_lower = categoria_raw.lower()
    if "improdut" in cat_lower:
        categoria = "Improdutivo"
    else:
        categoria = "Produtivo"

    # Confiança
    try:
        score = float(confianca_raw)
        if score < 0 or score > 1:
            score = 1.0
    except (TypeError, ValueError):
        score = 1.0

    # Fallback de resposta, caso venha vazio
    if not resposta:
        if categoria == "Produtivo":
            resposta = (
                "Olá! Obrigado pelo contato. Recebemos a sua solicitação e nossa equipe "
                "já está analisando o que você descreveu. Em breve retornaremos com uma atualização.\n\n"
                "Abraços,\nEquipe de Atendimento"
            )
        else:
            resposta = (
                "Olá! Muito obrigado pela sua mensagem e pelo retorno positivo. "
                "Se precisar de algo, é só chamar.\n\n"
                "Abraços,\nEquipe de Atendimento"
            )

    # Fallback de motivo
    if not motivo:
        motivo = (
            "A classificação considera se o texto pede alguma ação ou atualização "
            "objetiva (Produtivo) ou se é apenas uma mensagem cordial/agradecimento "
            "sem pedido de ação (Improdutivo)."
        )

    return categoria, score, resposta, motivo
