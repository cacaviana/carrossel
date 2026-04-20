"""Valida chave de API fazendo um ping trivial no provider, sem salvar.

Providers suportados:
- claude  — POST /v1/messages com max_tokens=1
- openai  — GET /v1/models (lista modelos, nao consome tokens)
- gemini  — GET /v1/models (lista modelos)
- drive   — valida credenciais JSON da service account + files.list limitado
"""

from __future__ import annotations

import json as _json
from typing import Optional

import httpx


CLAUDE_URL = "https://api.anthropic.com/v1/messages"
OPENAI_MODELS_URL = "https://api.openai.com/v1/models"
GEMINI_MODELS_URL = "https://generativelanguage.googleapis.com/v1beta/models"

DEFAULT_TIMEOUT = 8.0


async def validar(provider: str, api_key: str) -> dict:
    """Retorna {ok: bool, provider, erro?, detalhe?}."""
    if not api_key or not api_key.strip():
        return {"ok": False, "provider": provider, "erro": "chave_vazia"}

    if provider == "claude":
        return await _validar_claude(api_key)
    if provider == "openai":
        return await _validar_openai(api_key)
    if provider == "gemini":
        return await _validar_gemini(api_key)
    if provider == "drive":
        return await _validar_drive(api_key)
    return {"ok": False, "provider": provider, "erro": "provider_desconhecido"}


async def _validar_claude(api_key: str) -> dict:
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    body = {
        "model": "claude-3-5-haiku-20241022",
        "max_tokens": 1,
        "messages": [{"role": "user", "content": "hi"}],
    }
    return await _ping_post("claude", CLAUDE_URL, headers, body)


async def _validar_openai(api_key: str) -> dict:
    headers = {"Authorization": f"Bearer {api_key}"}
    return await _ping_get("openai", OPENAI_MODELS_URL, headers)


async def _validar_gemini(api_key: str) -> dict:
    url = f"{GEMINI_MODELS_URL}?key={api_key}"
    return await _ping_get("gemini", url, {})


async def _validar_drive(api_key_json: str) -> dict:
    """api_key_json e o JSON completo da service account. Valida parse + auth."""
    try:
        creds_dict = _json.loads(api_key_json)
    except Exception as e:
        return {"ok": False, "provider": "drive", "erro": "json_invalido", "detalhe": str(e)}

    required = {"type", "project_id", "private_key", "client_email"}
    faltando = required - set(creds_dict.keys())
    if faltando:
        return {"ok": False, "provider": "drive", "erro": "campos_faltando", "detalhe": ",".join(sorted(faltando))}

    try:
        from google.oauth2 import service_account
        creds = service_account.Credentials.from_service_account_info(
            creds_dict,
            scopes=["https://www.googleapis.com/auth/drive.readonly"],
        )
        creds.refresh(_GoogleAuthRequest())
        return {"ok": True, "provider": "drive", "detalhe": creds_dict.get("client_email", "")}
    except Exception as e:
        return {"ok": False, "provider": "drive", "erro": "auth_falhou", "detalhe": str(e)}


class _GoogleAuthRequest:
    """Wrapper minimalista sobre requests — usado so no refresh do service_account."""
    def __call__(self, *args, **kwargs):
        from google.auth.transport.requests import Request
        return Request()(*args, **kwargs)


async def _ping_get(provider: str, url: str, headers: dict) -> dict:
    try:
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            resp = await client.get(url, headers=headers)
        return _interpretar_resposta(provider, resp.status_code, resp.text)
    except httpx.TimeoutException:
        return {"ok": False, "provider": provider, "erro": "timeout"}
    except Exception as e:
        return {"ok": False, "provider": provider, "erro": "falha_rede", "detalhe": str(e)}


async def _ping_post(provider: str, url: str, headers: dict, body: dict) -> dict:
    try:
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            resp = await client.post(url, headers=headers, json=body)
        return _interpretar_resposta(provider, resp.status_code, resp.text)
    except httpx.TimeoutException:
        return {"ok": False, "provider": provider, "erro": "timeout"}
    except Exception as e:
        return {"ok": False, "provider": provider, "erro": "falha_rede", "detalhe": str(e)}


def _interpretar_resposta(provider: str, status: int, body: str) -> dict:
    if 200 <= status < 300:
        return {"ok": True, "provider": provider}
    if status == 401:
        return {"ok": False, "provider": provider, "erro": "chave_invalida"}
    if status == 403:
        return {"ok": False, "provider": provider, "erro": "acesso_negado"}
    if status == 429:
        return {"ok": False, "provider": provider, "erro": "quota_excedida"}
    return {"ok": False, "provider": provider, "erro": f"http_{status}", "detalhe": body[:200]}
