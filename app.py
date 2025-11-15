from flask import Flask, render_template, request
from io import BytesIO
from PyPDF2 import PdfReader

from ai_classifier import classificar_email
from nlp_utils import preprocess_text

ALLOWED_EXTENSIONS = {"txt", "pdf"}

app = Flask(__name__)


def arquivo_permitido(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def extrair_texto_arquivo(file_storage) -> str:
    """
    Lê o conteúdo de um arquivo .txt ou .pdf enviado pelo formulário
    e devolve o texto como string.
    """
    if not file_storage or not file_storage.filename:
        return ""

    filename = file_storage.filename
    ext = filename.rsplit(".", 1)[1].lower()

    # TXT
    if ext == "txt":
        raw = file_storage.read()
        try:
            return raw.decode("utf-8")
        except UnicodeDecodeError:
            # fallback simples
            return raw.decode("latin1", errors="ignore")

    # PDF
    if ext == "pdf":
        data = file_storage.read()
        reader = PdfReader(BytesIO(data))
        texto = ""
        for page in reader.pages:
            page_text = page.extract_text() or ""
            texto += page_text + "\n"
        return texto

    return ""


@app.route("/", methods=["GET", "POST"])
def index():
    erro = None
    resultado = None
    texto_original = ""
    tone_selected = "padrao"  # padrão: equilibrado

    if request.method == "POST":
        texto = (request.form.get("email_text") or "").strip()
        tone_selected = request.form.get("tone", "padrao")

        # Arquivo opcional
        file = request.files.get("email_file")
        if file and file.filename:
            if not arquivo_permitido(file.filename):
                erro = "Tipo de arquivo não suportado. Use apenas .txt ou .pdf."
            else:
                texto_arquivo = extrair_texto_arquivo(file)
                # Se não veio texto no textarea, usa o do arquivo
                if not texto and texto_arquivo:
                    texto = texto_arquivo

        texto_original = texto

        if not erro:
            if not texto or len(texto) < 10:
                erro = "Informe pelo menos 10 caracteres de texto (direto ou via arquivo)."
            else:
                try:
                    # Pré-processamento simples de NLP
                    texto_limpo = preprocess_text(texto)
                    categoria, score, resposta, motivo = classificar_email(
                        texto_limpo, tone_selected
                    )
                    resultado = {
                        "categoria": categoria,
                        "confianca": f"{score * 100:.1f}%",
                        "resposta": resposta,
                        "motivo": motivo,
                        "score": score,
                        "low_confidence": bool(score < 0.75),
                    }
                except Exception as e:
                    erro = f"Ocorreu um erro ao processar o email: {e}"

    return render_template(
        "index.html",
        erro=erro,
        resultado=resultado,
        texto_original=texto_original,
        tone_selected=tone_selected,
    )


@app.route("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    # Para desenvolvimento local
    app.run(host="0.0.0.0", port=5000, debug=True)
