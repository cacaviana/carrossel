"""Popula descricao das tasks em qa com caminho do codigo."""
import urllib.request
import json

TOKEN = "pk_101154796_69OIHUE9GGY4TV8ST4RPHPI2LNRRW0G4"
TEAM = "9007160573"

code_map = {
    "Listar Agentes": ("GET /api/agentes", ["backend/dtos/agentes/listar_agentes/", "backend/routers/agentes.py", "backend/factories/agente_factory.py"]),
    "Obter Prompt Agente": ("GET /api/agentes/{slug}", ["backend/routers/agentes.py::buscar_agente", "backend/factories/agente_factory.py::carregar_system_prompt"]),
    "Salvar Claude ApiKey": ("POST /api/config", ["backend/services/config_service.py::save_api_key", "backend/routers/config.py::salvar_config"]),
    "Salvar Gemini ApiKey": ("POST /api/config", ["backend/services/config_service.py::save_api_key", "backend/routers/config.py::salvar_config"]),
    "Salvar Google Drive Credentials": ("POST /api/config", ["backend/services/config_service.py", "backend/routers/config.py::salvar_config"]),
    "Salvar Google Drive Folder": ("POST /api/config", ["backend/services/config_service.py", "backend/routers/config.py::salvar_config"]),
    "Obter ApiKeys": ("GET /api/config", ["backend/routers/config.py::status_config"]),
    "Criar Carrossel": ("POST /api/gerar-conteudo + POST /api/pipelines/", ["backend/dtos/conteudo/gerar_conteudo/", "backend/services/conteudo_service.py", "backend/services/pipeline_service.py"]),
    "Listar Carrosseis": ("GET /api/historico?formato=carrossel", ["backend/routers/historico.py::listar_historico", "backend/dtos/historico/listar_historico/"]),
    "Obter Carrossel": ("GET /api/historico/{id}", ["backend/routers/historico.py::buscar_historico"]),
    "Excluir Carrossel": ("DELETE /api/historico/{id}", ["backend/routers/historico.py::deletar_historico"]),
    "Regerar Carrossel": ("POST /api/pipelines/{id}/regerar-imagens", ["backend/routers/pipeline.py::regerar_imagens", "backend/services/pipeline_service.py"]),
    "Exportar Carrossel PDF": ("POST /api/config/editor/salvar-pdf", ["backend/services/pdf_service.py", "backend/services/editor_service.py::salvar_pdf"]),
    "Criar PostUnico": ("POST /api/gerar-conteudo + POST /api/gerar-imagem (formato=post_unico)", ["backend/dtos/conteudo/gerar_conteudo/", "backend/dtos/imagem/gerar_imagem/"]),
    "Listar PostsUnicos": ("GET /api/historico?formato=post_unico", ["backend/routers/historico.py"]),
    "Obter PostUnico": ("GET /api/historico/{id} (formato=post_unico)", ["backend/routers/historico.py::buscar_historico"]),
    "Excluir PostUnico": ("DELETE /api/historico/{id}", ["backend/routers/historico.py::deletar_historico"]),
    "Regerar PostUnico": ("POST /api/pipelines/{id}/regerar-imagens", ["backend/routers/pipeline.py"]),
    "Criar CapaReels": ("POST /api/gerar-conteudo + POST /api/gerar-imagem (formato=capa_reels)", ["backend/dtos/conteudo/gerar_conteudo/", "backend/dtos/imagem/gerar_imagem/"]),
    "Listar CapasReels": ("GET /api/historico?formato=capa_reels", ["backend/routers/historico.py"]),
    "Obter CapaReels": ("GET /api/historico/{id} (formato=capa_reels)", ["backend/routers/historico.py::buscar_historico"]),
    "Excluir CapaReels": ("DELETE /api/historico/{id}", ["backend/routers/historico.py::deletar_historico"]),
    "Regerar CapaReels": ("POST /api/pipelines/{id}/regerar-imagens", ["backend/routers/pipeline.py"]),
    "Criar Thumbnail": ("POST /api/gerar-conteudo + POST /api/gerar-imagem (formato=thumbnail_youtube)", ["backend/dtos/conteudo/gerar_conteudo/", "backend/dtos/imagem/gerar_imagem/"]),
    "Listar Thumbnails": ("GET /api/historico?formato=thumbnail_youtube", ["backend/routers/historico.py"]),
    "Obter Thumbnail": ("GET /api/historico/{id} (formato=thumbnail_youtube)", ["backend/routers/historico.py::buscar_historico"]),
    "Excluir Thumbnail": ("DELETE /api/historico/{id}", ["backend/routers/historico.py::deletar_historico"]),
    "Regerar Thumbnail": ("POST /api/pipelines/{id}/regerar-imagens", ["backend/routers/pipeline.py"]),
    "Adicionar Creator": ("POST /api/config/creator-registry", ["backend/dtos/config/salvar_creator_registry/", "backend/services/config_service.py::save_creator_registry"]),
    "Listar Creators": ("GET /api/config/creator-registry", ["backend/dtos/config/buscar_creator_registry/"]),
    "Remover Creator": ("POST /api/config/creator-registry (lote sem o creator)", ["backend/services/config_service.py::save_creator_registry"]),
    "Salvar Creators Lote": ("POST /api/config/creator-registry", ["backend/services/config_service.py::save_creator_registry"]),
    "Listar Historico Lista": ("GET /api/historico (tab Lista)", ["backend/routers/historico.py::listar_historico", "frontend/src/routes/historico/+page.svelte"]),
    "Listar Historico Kanban": ("GET /api/kanban/board + GET /api/historico", ["backend/routers/kanban_board.py", "frontend/src/routes/historico (tab=kanban)"]),
    "Atribuir Prazo Publicacao": ("PATCH /api/kanban/cards/{id} (campo deadline)", ["backend/routers/kanban_card.py", "frontend/src/lib/components/DeadlinePicker.svelte"]),
    "Criar Marca": ("POST /api/config/brands", ["backend/routers/config.py::criar_brand", "backend/services/brand_service.py::criar_brand"]),
    "Listar Marcas": ("GET /api/config/brands", ["backend/routers/config.py::listar_brands", "backend/services/brand_service.py::listar_brands"]),
    "Obter Marca": ("GET /api/config/brands/{slug}", ["backend/routers/config.py::buscar_brand", "backend/services/brand_prompt_builder.py::carregar_brand"]),
    "Atualizar Marca": ("PATCH /api/config/brands/{slug}", ["backend/routers/config.py::atualizar_brand", "backend/services/brand_service.py::atualizar_brand"]),
    "Excluir Marca": ("DELETE /api/config/brands/{slug}", ["backend/routers/config.py::deletar_brand", "backend/services/brand_prompt_builder.py::deletar_brand"]),
    "Atualizar DNA Marca": ("PATCH /api/config/brands/{slug} (campo dna)", ["backend/services/brand_service.py::atualizar_brand"]),
    "Regerar DNA Marca com IA": ("POST /api/config/brands/{slug}/dna/regenerate", ["backend/services/dna_generator.py::regenerar_dna", "backend/routers/config.py::regenerate_dna"]),
    "Atualizar Paleta Cores": ("POST /api/config/brand-palette", ["backend/dtos/config/salvar_brand_palette/", "backend/services/config_service.py::save_brand_palette"]),
    "Atualizar Fontes": ("POST /api/config/brand-palette (campo fonte)", ["backend/services/config_service.py::save_brand_palette"]),
    "Atualizar Voz Marca": ("PATCH /api/config/brands/{slug} (campo voz)", ["backend/services/brand_service.py::atualizar_brand"]),
    "Enviar Logo Marca": ("POST /api/config/brands/{slug}/foto", ["backend/routers/config.py::salvar_foto_brand", "backend/services/brand_service.py::salvar_foto"]),
    "Enviar Referencia Com Avatar": ("POST /api/visual-preferences (pool=com_avatar)", ["backend/dtos/visual_preference/salvar_preferencia/", "backend/services/brand_service.py::upload_asset"]),
    "Enviar Referencia Sem Avatar": ("POST /api/visual-preferences (pool=sem_avatar)", ["backend/dtos/visual_preference/salvar_preferencia/", "backend/services/brand_service.py::upload_asset"]),
    "Remover Referencia Com Avatar": ("DELETE /api/config/brands/{slug}/assets/{nome}", ["backend/services/brand_service.py::deletar_asset"]),
    "Remover Referencia Sem Avatar": ("DELETE /api/config/brands/{slug}/assets/{nome}", ["backend/services/brand_service.py::deletar_asset"]),
    "Gerenciar Avatar Pessoa": ("POST /api/foto-overlay/aplicar", ["backend/dtos/foto_overlay/aplicar_foto/", "backend/services/foto_overlay.py"]),
    "Analisar Padrao Visual Pool": ("POST /api/config/analisar-referencias", ["backend/dtos/brand/analisar_referencias/", "backend/factories/brand_analyzer.py", "backend/services/brand_analyzer_service.py"]),
    "Executar Pipeline Conteudo": ("POST /api/pipelines/ + /executar", ["backend/routers/pipeline.py::criar", "backend/services/pipeline_service.py::criar", "backend/services/pipeline_executor.py"]),
    "Cancelar Pipeline": ("POST /api/pipelines/{id}/cancelar", ["backend/routers/pipeline.py::cancelar_pipeline", "backend/services/pipeline_service.py::cancelar"]),
    "Listar Skills": ("GET /api/agentes (tipo=skill)", ["backend/factories/agente_factory.py::listar_todos", "backend/skills/"]),
    "Autenticar Usuario": ("POST /api/auth/login", ["backend/dtos/auth/login/", "backend/services/auth_service.py::login", "backend/routers/auth.py::login"]),
    "Logout Usuario": ("Client-side clear", ["frontend/src/lib/stores/auth.svelte.ts::logout", "frontend/src/lib/services/AuthService.ts::logout"]),
    "Listar Usuarios": ("GET /api/auth/users", ["backend/dtos/auth/listar_usuarios/", "backend/routers/auth.py::listar_usuarios"]),
    "Editar Usuario": ("PATCH /api/auth/users/{id}", ["backend/dtos/auth/atualizar_usuario/", "backend/routers/auth.py::atualizar_usuario"]),
    "Desativar Usuario": ("DELETE /api/auth/users/{id}", ["backend/routers/auth.py::desativar_usuario"]),
    "Ativar Usuario": ("POST /api/auth/users/{id}/reativar", ["backend/routers/auth.py::reativar_usuario"]),
    "Convidar Usuario": ("POST /api/auth/users/invite + /invite/accept", ["backend/dtos/auth/convidar_usuario/", "backend/dtos/auth/aceitar_convite/", "backend/routers/auth.py::convidar_usuario", "backend/services/auth_service.py::aceitar_convite"]),
    "Atribuir Perfil Usuario": ("PATCH /api/auth/users/{id} (campo role)", ["backend/routers/auth.py::atualizar_usuario"]),
}


def main():
    all_tasks = []
    page = 0
    while True:
        url = f"https://api.clickup.com/api/v2/team/{TEAM}/task?assignees%5B%5D=101154796&include_closed=true&subtasks=true&page={page}"
        req = urllib.request.Request(url, headers={"Authorization": TOKEN})
        data = json.loads(urllib.request.urlopen(req).read())
        tasks = data.get("tasks", [])
        if not tasks:
            break
        all_tasks.extend(tasks)
        page += 1
        if len(tasks) < 100:
            break

    qa_tasks = [t for t in all_tasks if t["status"]["status"] == "qa"]
    print(f"Total em qa: {len(qa_tasks)}")

    updated = 0
    missing = []
    for t in qa_tasks:
        name = t["name"].split(" (")[0]
        if name not in code_map:
            missing.append(name)
            continue
        endpoint, paths = code_map[name]
        existing = (t.get("description") or "").strip()
        parts = []
        if existing:
            parts.append(existing)
            parts.append("---")
        parts.append(f"Endpoint: {endpoint}")
        parts.append("Implementado em:")
        parts.extend(f"- {p}" for p in paths)
        parts.append("QA: unit + integracao + e2e (ver tests/ e frontend/e2e/)")
        desc = "\n\n".join(parts)

        payload = json.dumps({"description": desc}).encode()
        url = f"https://api.clickup.com/api/v2/task/{t['id']}"
        req = urllib.request.Request(
            url, data=payload, method="PUT",
            headers={"Authorization": TOKEN, "Content-Type": "application/json"}
        )
        try:
            urllib.request.urlopen(req).read()
            updated += 1
        except Exception as e:
            print(f"ERR {name}: {e}")

    print(f"{updated}/{len(qa_tasks)} descriptions atualizadas")
    if missing:
        print(f"\nSem mapeamento ({len(missing)}):")
        for m in missing:
            print(f"  - {m}")


if __name__ == "__main__":
    main()
