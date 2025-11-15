# AutoMail Insight · Classificador de E-mails com IA (Case AutoU)

Aplicação web desenvolvida para o **case prático da AutoU**, simulando uma solução
para uma grande empresa do **setor financeiro** que recebe um alto volume de e-mails
diariamente.

A solução usa **Python + Flask** no backend, uma interface web moderna em HTML/CSS/JS
e a **API da OpenAI (GPT)** para:

- **Classificar e-mails** nas categorias:
  - `Produtivo`
  - `Improdutivo`
- **Gerar uma resposta automática sugerida** em português do Brasil.
- **Explicar o motivo da classificação** em linguagem simples.
- **Adaptar o tom da resposta** (equilibrado, mais formal ou mais próximo).

---

## 1. Visão geral da solução

### Contexto

Uma grande empresa financeira recebe centenas de e-mails por dia: alguns são
solicitações de suporte, acompanhamento de chamados e problemas reais; outros
são felicitações, agradecimentos e mensagens sociais.

O objetivo da aplicação é:

1. Automatizar a **leitura e classificação** desses e-mails (Produtivo vs. Improdutivo).
2. Sugerir **respostas automáticas** adequadas ao contexto.
3. Aumentar a **produtividade da equipe**, mantendo governança sobre o uso de IA.

---

## 2. Arquitetura em alto nível

A solução está organizada em três grandes camadas:

### 2.1. Interface Web (HTML + CSS + JS)

- Página única (`templates/index.html`) com layout responsivo e foco em UX:
  - Área para **colar o texto do e-mail**.
  - **Upload de arquivos `.txt` ou `.pdf`**.
  - Seletor de **tom da resposta**:
    - `Equilibrado`
    - `Mais formal`
    - `Mais próximo`
  - Botão **“Rodar IA e classificar”**.
  - Botão **“Preencher com exemplo”** para facilitar demonstração.
  - Card de resultado com:
    - **Categoria** (Produtivo/Improdutivo).
    - **Confiança** da IA.
    - **Motivo da decisão** em linguagem acessível.
    - **Resposta automática sugerida** com botão “Copiar resposta”.

- Microinterações e detalhes visuais:
  - Métricas animadas (“Produtivos hoje”, “Improdutivos hoje”).
  - Estado vazio com um “ghost” ilustrativo.
  - Cores distintas para **alta vs. baixa confiança**.

- Aviso de **privacidade**:
  - Mensagem orientando a não enviar dados reais de clientes (CPF, cartões, contas),
    reforçando a consciência de LGPD e boas práticas.

### 2.2. Backend em Python (Flask)

Arquivo principal: `app.py`

Responsabilidades:

- Rota `/`:
  - Recebe o formulário (texto + upload + tom da resposta).
  - Lê arquivos `.txt` e `.pdf` (via `PyPDF2`).
  - Aplica pré-processamento simples (`nlp_utils.preprocess_text`).
  - Chama a função `classificar_email` (módulo `ai_classifier.py`), passando:
    - texto pré-processado;
    - tom selecionado pelo usuário.
  - Monta o objeto de resultado para o template:
    - `categoria`
    - `confianca` (já formatada em `%`)
    - `score` (0–1)
    - `motivo`
    - `resposta`
    - `low_confidence` (booleano para tratamento visual).

- Rota `/health`:
  - Endpoint simples para checagem de saúde da aplicação.

### 2.3. Camada de NLP e IA

#### `nlp_utils.py` — Pré-processamento de texto

- Etapas aplicadas:
  - Normalização de quebras de linha.
  - Conversão para minúsculas (`lowercase`).
  - Remoção de múltiplos espaços.

Essa camada cumpre o requisito de uso de **técnicas de NLP**, limpando o texto
antes de enviá-lo para a IA.

> Em um ambiente de produção, esta etapa poderia evoluir para incluir remoção de
> stopwords, lematização e outras técnicas, mas para o case o foco é manter a
> stack leve e didática.

#### `ai_classifier.py` — Integração com OpenAI GPT

É o “cérebro” da solução.

- Usa a biblioteca oficial `openai` (client `OpenAI`).
- Lê a chave da API a partir da variável de ambiente `OPENAI_API_KEY`.
- Utiliza o modelo `gpt-4.1-mini` da OpenAI.
- Define um **system prompt** em português com:
  - Contexto de **grande empresa financeira**.
  - Definição clara de `Produtivo` vs. `Improdutivo`.
  - Regras de tom de voz.
  - Instruções de segurança (não inventar protocolos, números de chamado etc.).
  - Especificação do **formato de saída em JSON**.

A função `_gerar_json_com_openai(texto_email, estilo_resposta)`:

1. Recebe o texto pré-processado e uma descrição de estilo de resposta
   (equilibrado / mais formal / mais próximo).
2. Envia mensagem ao modelo da OpenAI pedindo:
   - `categoria` (`Produtivo` ou `Improdutivo`);
   - `confianca` (0 a 1);
   - `resposta_sugerida` em PT-BR, no tom desejado;
   - `motivo` curto explicando a decisão.
3. Faz parse do JSON retornado (com fallback em caso de ```json ... ```).

A função pública `classificar_email(texto_email, tom_resposta)`:

- Mapeia o código de tom vindo do formulário (`padrao`, `formal`, `informal`) para
  descrições mais ricas, usadas no prompt.
- Chama `_gerar_json_com_openai`.
- Normaliza:
  - categoria → `"Produtivo"` ou `"Improdutivo"`;
  - confiança → `score` (float 0–1) com fallback;
  - resposta (gera uma resposta padrão se vier vazia);
  - motivo (gera explicação genérica se vier vazio).
- Retorna: `categoria`, `score`, `resposta`, `motivo`.

#### Tratamento de confiança (governança de IA)

Na camada de interface, foi implementado um **limiar de confiança**:

- Se `score >= 0.75`:
  - pill verde (`pill-active`), indicando alta confiança.
- Se `score < 0.75`:
  - pill amarela (`pill-warning`), exibindo o aviso:
    > “Confiança baixa: recomendamos revisão humana antes de enviar esta resposta ao cliente.”

Isso mostra uma preocupação explícita com **governança de IA**, algo essencial em
contexto financeiro.

---

## 3. Como rodar localmente

### 3.1. Clonar o repositório

```bash
git clone <URL_DO_SEU_REPOSITORIO.git>
cd autou_email_ai
```

*(ajuste o nome da pasta conforme seu repositório real)*

### 3.2. Criar ambiente virtual (opcional, recomendado)

**Windows (PowerShell):**

```bash
python -m venv venv
.env\Scriptsctivate
```

**Linux / Mac:**

```bash
python -m venv venv
source venv/bin/activate
```

### 3.3. Instalar dependências

```bash
pip install -r requirements.txt
```

As principais dependências são:

- `flask` — framework web.
- `openai` — cliente oficial da API da OpenAI.
- `PyPDF2` — leitura simples de arquivos PDF.

### 3.4. Configurar a chave da OpenAI

Crie uma conta na OpenAI (se ainda não tiver) e gere uma **API Key**.

Defina a variável de ambiente `OPENAI_API_KEY` **sem colocá-la no código**:

**Windows (PowerShell, sessão atual):**

```bash
$env:OPENAI_API_KEY = "SUA_CHAVE_AQUI"
```

**Linux / Mac:**

```bash
export OPENAI_API_KEY="SUA_CHAVE_AQUI"
```


### 3.5. Rodar a aplicação

```bash
python app.py
```

Acesse no navegador:

```text
http://127.0.0.1:5000/
```

Faça testes com e-mails:

- Pedido de atualização de status de uma solicitação → tendência a **Produtivo**.
- Mensagem apenas de agradecimento / feliz natal → tendência a **Improdutivo**.

---

## 4. Deploy na nuvem (exemplo com Render)

Existem várias opções de hospedagem gratuita ou de baixo custo:
Render, Railway, Replit, Hugging Face Spaces, etc.

Exemplo de fluxo com **Render**:

1. Suba o código em um repositório público no GitHub.
2. Crie uma conta em [Render](https://render.com).
3. Crie um novo **Web Service** apontando para o repositório.
4. Configure:
   - Build command:  
     `pip install -r requirements.txt`
   - Start command (modo simples de demo):  
     `python app.py`  
     (ou `gunicorn app:app` se optar por adicionar `gunicorn` ao `requirements.txt`).
5. Nas variáveis de ambiente do serviço, defina:
   - `OPENAI_API_KEY` com a sua chave.
6. Aguarde o deploy e copie a URL pública gerada.

Essa URL é a que deve ser informada no formulário do case como
**“link da aplicação publicada”**.

---



## 5. Estrutura de arquivos

```text
autou_email_ai/
├─ app.py               # Flask app: rotas, leitura de arquivos, integração com IA
├─ ai_classifier.py     # Camada de IA usando OpenAI (classificação + resposta + motivo)
├─ nlp_utils.py         # Pré-processamento simples de NLP
├─ requirements.txt     # Dependências do projeto
├─ README.md            # Este arquivo
├─ templates/
│  └─ index.html        # Interface principal (HTML + Jinja2)
└─ static/
   ├─ styles.css        # Estilos (layout, cores, animações, estados de confiança)
   └─ main.js           # JS (loading, exemplo, copiar resposta, métricas animadas)
```

---

## 6. Limitações atuais & próximos passos

### Limitações

- A aplicação funciona como um **protótipo de console web**:
  - Não está integrada a uma caixa de e-mail real (IMAP/Exchange).
  - Não persiste histórico em banco de dados (os resultados são apenas exibidos em tela).
- O modelo de IA utiliza **prompt engineering** em vez de fine-tuning dedicado.
- O pré-processamento de NLP é propositalmente simples para manter a stack enxuta.

### Próximos passos possíveis

- Integrar com a caixa de entrada real da empresa (via IMAP/Exchange/SMTP).
- Persistir classificações em um banco de dados e criar:
  - métricas por tipo de e-mail,
  - SLAs de resposta,
  - dashboards de produtividade.
- Implementar um fluxo de **feedback humano** (“classificação correta?” / “corrigir categoria”)
  para alimentar um pipeline de re-treinamento ou ajuste fino da IA.
- Evoluir o pré-processamento com técnicas adicionais de NLP (stopwords, lematização,
  detecção de idioma, anonimização de PII, etc.).

---

Se surgir qualquer dúvida sobre a execução, deploy ou ajustes na IA, basta consultar
as seções acima ou adaptar os prompts e parâmetros no módulo `ai_classifier.py`.
#   a u t o u - e m a i l - a i  
 