import asyncio
import json
import os

from factories.conteudo_factory import build_system_prompt, build_user_prompt
from utils.json_parser import parse_llm_json


async def gerar_conteudo_cli(
    disciplina: str | None = None,
    tecnologia: str | None = None,
    tema_custom: str | None = None,
    texto_livre: str | None = None,
    total_slides: int = 10,
) -> dict:
    system_prompt = build_system_prompt()
    user_prompt = build_user_prompt(disciplina, tecnologia, tema_custom, texto_livre, total_slides)

    env = os.environ.copy()
    env.pop("CLAUDECODE", None)

    proc = await asyncio.create_subprocess_exec(
        "claude",
        "--dangerously-skip-permissions",
        "--system-prompt", system_prompt,
        "--output-format", "json",
        "--tools", "",
        "-p", user_prompt,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env=env,
    )

    try:
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=180)
    except asyncio.TimeoutError:
        proc.kill()
        await proc.wait()
        raise Exception("Timeout: Claude Code CLI demorou mais de 3 minutos.")

    if proc.returncode != 0:
        raise Exception(f"Claude Code CLI falhou: {stderr.decode()}")

    raw = stdout.decode()
    try:
        outer = json.loads(raw)
        response_text = outer.get("result", raw)
    except json.JSONDecodeError:
        response_text = raw

    return parse_llm_json(response_text)
