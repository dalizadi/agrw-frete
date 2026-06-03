import os
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

app = FastAPI(title="AGRW Calculadora de Frete")

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

class DistanciaRequest(BaseModel):
    origem: str
    destino: str

class DistanciaResponse(BaseModel):
    distancia_km: int
    origem: str
    destino: str

@app.post("/api/distancia", response_model=DistanciaResponse)
async def estimar_distancia(req: DistanciaRequest):
    if not ANTHROPIC_API_KEY:
        raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY não configurada.")

    prompt = (
        f'Qual a distância rodoviária aproximada em km entre "{req.origem}" e "{req.destino}" no Brasil? '
        'Responda APENAS com o número inteiro de km, sem texto, sem unidade.'
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
        raise HTTPException(status_code=502, detail=f"Erro na API: {resp.text}")

    data = resp.json()
    raw = data.get("content", [{}])[0].get("text", "").strip()
    digits = "".join(c for c in raw if c.isdigit())

    if not digits:
        raise HTTPException(status_code=422, detail=f"Resposta inesperada: '{raw}'")

    return DistanciaResponse(distancia_km=int(digits), origem=req.origem, destino=req.destino)

@app.get("/")
async def root():
    return FileResponse("index.html")
