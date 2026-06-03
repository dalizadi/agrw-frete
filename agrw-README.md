# AGRW – Calculadora de Frete

Site completo com piso mínimo ANTT, impostos (CT-e e GNRE) e documentação obrigatória.

---

## Arquivos

```
agrw-frete/
├── index.html   ← Frontend completo (logo embutida em base64)
├── server.py    ← Backend FastAPI
└── README.md    ← Este arquivo
```

---

## Pré-requisitos

- Python 3.9 ou superior
- Conta na Anthropic com uma API Key (https://console.anthropic.com)

---

## Instalação

### 1. Instale as dependências Python

```bash
pip install fastapi uvicorn httpx
```

### 2. Configure sua API Key da Anthropic

**Linux / macOS:**
```bash
export ANTHROPIC_API_KEY="sk-ant-api03-SUA-CHAVE-AQUI"
```

**Windows (PowerShell):**
```powershell
$env:ANTHROPIC_API_KEY="sk-ant-api03-SUA-CHAVE-AQUI"
```

> ⚠️ Nunca coloque sua chave diretamente no código. Use variáveis de ambiente.

### 3. Rode o servidor

Coloque `index.html` e `server.py` na mesma pasta e execute:

```bash
python server.py
```

Ou, para produção com reload automático:

```bash
uvicorn server:app --host 0.0.0.0 --port 8000
```

### 4. Acesse

Abra o navegador em: **http://localhost:8000**

---

## Como funciona

1. O usuário preenche origem, destino e dados do caminhão
2. O frontend chama `POST /api/distancia` no backend
3. O backend chama a API da Anthropic (Claude Haiku) para estimar a distância rodoviária
4. O frontend calcula o piso mínimo usando os coeficientes da Portaria SUROC nº 4/2026
5. CT-e (7,4%), GNRE (12% se fora do PR) e seguro são somados automaticamente

---

## Hospedagem em produção

### Opção A – VPS simples (Render, Railway, Fly.io)

Configure a variável de ambiente `ANTHROPIC_API_KEY` no painel da plataforma e faça deploy do repositório.

**Procfile (para plataformas que usam):**
```
web: uvicorn server:app --host 0.0.0.0 --port $PORT
```

### Opção B – Servidor próprio (Ubuntu)

```bash
# Instalar dependências
pip install fastapi uvicorn httpx gunicorn

# Rodar com Gunicorn + Uvicorn workers
gunicorn server:app -w 2 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

Coloque um Nginx na frente para HTTPS.

---

## Atualização dos coeficientes ANTT

Os coeficientes estão no arquivo `index.html`, no objeto `COEF` dentro do `<script>`.
A ANTT atualiza os valores semestralmente (janeiro e julho) ou quando o diesel varia +5%.
Confira sempre a portaria vigente em: https://www.gov.br/antt/pt-br

---

## Notas legais

Os valores calculados são estimativas com base nos coeficientes oficiais da ANTT (Portaria SUROC nº 4/2026, diesel R$ 7,35/litro). Confirme sempre na calculadora oficial: https://calculadorafrete.antt.gov.br/
