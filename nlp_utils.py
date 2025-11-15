import re


def preprocess_text(text: str) -> str:
    """
    Pré-processamento simples de NLP:
    - normaliza quebras de linha
    - converte para minúsculas
    - remove espaços duplicados

    Essa etapa é intencionalmente simples para cumprir o requisito
    de "técnicas de NLP" sem complicar a stack.
    """
    if not text:
        return ""

    # normaliza quebras de linha
    text = text.replace("\r", " ").replace("\n", " ")

    # lower case
    text = text.lower()

    # remove múltiplos espaços
    text = re.sub(r"\s+", " ", text)

    return text.strip()
