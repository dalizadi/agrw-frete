"""
AGRW – Calculadora de Frete
Backend FastAPI: serve o HTML e calcula distâncias via Claude API
"""

import os
import json
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

app = FastAPI(title="AGRW Calculadora de Frete")

# ── Variável de ambiente ───────────────────────────────────────────────────────
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

# ── Modelos ────────────────────────────────────────────────────────────────────
class DistanciaRequest(BaseModel):
    origem: str
    destino: str

class DistanciaResponse(BaseModel):
    distancia_km: int
    origem: str
    destino: str

# ── Endpoint: estimar distância via Claude ─────────────────────────────────────
@app.post("/api/distancia", response_model=DistanciaResponse)
async def estimar_distancia(req: DistanciaRequest):
    if not ANTHROPIC_API_KEY:
        raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY não configurada no servidor.")

    prompt = (
        f'Qual a distância rodoviária aproximada em km entre "{req.origem}" e "{req.destino}" no Brasil? '
        'Responda APENAS com o número inteiro de km, sem texto, sem unidade, sem pontuação.'
    )

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "Content-Type": "application/json",
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
            },
            json={
                "model": "claude-haiku-4-5-20251001",
                "max_tokens": 60,
                "messages": [{"role": "user", "content": prompt}],
            },
        )

    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail=f"Erro na API Anthropic: {resp.text}")

    data = resp.json()
    raw = data.get("content", [{}])[0].get("text", "").strip()

    # extrai só dígitos
    digits = "".join(c for c in raw if c.isdigit())
    if not digits:
        raise HTTPException(status_code=422, detail=f"Resposta inesperada do modelo: '{raw}'")

    return DistanciaResponse(
        distancia_km=int(digits),
        origem=req.origem,
        destino=req.destino,
    )

# ── Servir o frontend ──────────────────────────────────────────────────────────
@app.get("/", include_in_schema=False)
async def root():
    return FileResponse("index.html")

# Fallback para arquivos estáticos (se quiser separar logo etc. futuramente)
# app.mount("/static", StaticFiles(directory="static"), name="static")

# ── Rodar direto com: python server.py ────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
