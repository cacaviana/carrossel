"""Serviço de publicação em redes sociais — Instagram e LinkedIn."""

import asyncio
import base64
import os

import httpx

GRAPH_API = "https://graph.facebook.com/v21.0"
LINKEDIN_API = "https://api.linkedin.com/v2"
LINKEDIN_REST_API = "https://api.linkedin.com/rest"


async def _get_page_token_and_ig_id(page_id: str, user_token: str) -> tuple[str, str | None]:
    """Retorna (page_access_token, instagram_business_account_id) para uma Page."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        res = await client.get(
            f"{GRAPH_API}/{page_id}",
            params={
                "fields": "instagram_business_account,access_token,name",
                "access_token": user_token,
            },
        )
        res.raise_for_status()
        data = res.json()
        page_token = data.get("access_token", user_token)
        ig = data.get("instagram_business_account")
        ig_id = ig["id"] if ig else None
        return page_token, ig_id


async def _upload_photo_get_url(
    client: httpx.AsyncClient, page_id: str, img_bytes: bytes, page_token: str
) -> str:
    """Upload foto não-publicada no Facebook e retorna URL pública."""
    res = await client.post(
        f"{GRAPH_API}/{page_id}/photos",
        data={"published": "false", "access_token": page_token},
        files={"source": ("slide.png", img_bytes, "image/png")},
    )
    res.raise_for_status()
    photo_id = res.json()["id"]

    res = await client.get(
        f"{GRAPH_API}/{photo_id}",
        params={"fields": "images", "access_token": page_token},
    )
    res.raise_for_status()
    images = res.json().get("images", [])
    if not images:
        raise ValueError("Não conseguiu URL da foto no Facebook")
    return images[0]["source"]


async def publicar_instagram(
    images_base64: list[str],
    caption: str,
    conta: str = "carlosviana",
) -> dict:
    """Publica carrossel no Instagram via Meta Graph API."""
    user_token = os.getenv("META_ACCESS_TOKEN")
    if not user_token:
        raise ValueError("META_ACCESS_TOKEN não configurado")

    # Tentar ambas as pages para achar a que tem Instagram vinculado
    page_ids = [
        os.getenv("META_PAGE_ID_CARLOSVIANA"),
        os.getenv("META_PAGE_ID_ITVALLEY"),
    ]

    # Descobrir qual page tem Instagram Business Account
    page_token = None
    ig_account_id = None
    page_id_used = None

    for pid in page_ids:
        pt, ig_id = await _get_page_token_and_ig_id(pid, user_token)
        if ig_id and conta == "itvalley":
            page_token, ig_account_id, page_id_used = pt, ig_id, pid
            break
        if not ig_id and conta == "carlosviana":
            # Page sem IG vinculado — pode ser que carlosviana é perfil pessoal
            page_token = pt
            page_id_used = pid

    # Se não achou IG para esta conta, tentar todas
    if not ig_account_id:
        for pid in page_ids:
            pt, ig_id = await _get_page_token_and_ig_id(pid, user_token)
            if ig_id:
                page_token, ig_account_id, page_id_used = pt, ig_id, pid
                break

    if not ig_account_id:
        raise ValueError(f"Nenhuma Page tem Instagram Business Account vinculada para '{conta}'")

    async with httpx.AsyncClient(timeout=120.0) as client:
        # 1. Upload cada imagem no Facebook e criar container IG
        children_ids = []
        for i, img_b64 in enumerate(images_base64):
            img_data = img_b64.split(",", 1)[1] if "," in img_b64 else img_b64
            img_bytes = base64.b64decode(img_data)

            # Upload no Facebook pra obter URL pública
            photo_url = await _upload_photo_get_url(client, page_id_used, img_bytes, page_token)

            # Criar container no Instagram com URL pública
            res = await client.post(
                f"{GRAPH_API}/{ig_account_id}/media",
                data={
                    "image_url": photo_url,
                    "is_carousel_item": "true",
                    "access_token": page_token,
                },
            )
            res.raise_for_status()
            children_ids.append(res.json()["id"])
            print(f"  IG slide {i+1}/{len(images_base64)} uploaded", flush=True)

            # Rate limit
            if i < len(images_base64) - 1:
                await asyncio.sleep(1)

        # 2. Criar container do carrossel
        res = await client.post(
            f"{GRAPH_API}/{ig_account_id}/media",
            data={
                "media_type": "CAROUSEL",
                "caption": caption,
                "children": ",".join(children_ids),
                "access_token": page_token,
            },
        )
        res.raise_for_status()
        carousel_id = res.json()["id"]
        print(f"  Carousel container: {carousel_id}", flush=True)

        # 3. Aguardar processamento e publicar
        # Instagram precisa de tempo para processar
        await asyncio.sleep(5)

        res = await client.post(
            f"{GRAPH_API}/{ig_account_id}/media_publish",
            data={"creation_id": carousel_id, "access_token": page_token},
        )
        res.raise_for_status()

        return {"platform": "instagram", "conta": conta, "post_id": res.json().get("id")}


async def publicar_linkedin(
    images_base64: list[str],
    text: str,
    conta: str = "pessoal",
) -> dict:
    """Publica post multi-imagem no LinkedIn."""
    access_token = os.getenv("LINKEDIN_ACCESS_TOKEN")
    if not access_token:
        raise ValueError("LINKEDIN_ACCESS_TOKEN não configurado")

    headers = {
        "Authorization": f"Bearer {access_token}",
        "LinkedIn-Version": "202601",
        "X-Restli-Protocol-Version": "2.0.0",
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        # Determinar author URN
        if conta == "pessoal":
            res = await client.get(
                f"{LINKEDIN_API}/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            res.raise_for_status()
            member_sub = res.json().get("sub")
            author_urn = f"urn:li:person:{member_sub}"
        else:
            org_id = os.getenv("LINKEDIN_ORGANIZATION_ID")
            author_urn = f"urn:li:organization:{org_id}"

        # Upload cada imagem
        image_urns = []
        for img_b64 in images_base64:
            img_data = img_b64.split(",", 1)[1] if "," in img_b64 else img_b64
            img_bytes = base64.b64decode(img_data)

            res = await client.post(
                f"{LINKEDIN_REST_API}/images?action=initializeUpload",
                json={"initializeUploadRequest": {"owner": author_urn}},
                headers=headers,
            )
            res.raise_for_status()
            up = res.json()["value"]

            await client.put(
                up["uploadUrl"],
                content=img_bytes,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/octet-stream",
                },
            )
            image_urns.append(up["image"])

        # Criar post multi-imagem
        post_body = {
            "author": author_urn,
            "commentary": text,
            "visibility": "PUBLIC",
            "distribution": {
                "feedDistribution": "MAIN_FEED",
                "targetEntities": [],
                "thirdPartyDistributionChannels": [],
            },
            "content": {
                "multiImage": {
                    "images": [{"id": urn} for urn in image_urns],
                }
            },
            "lifecycleState": "PUBLISHED",
            "isReshareDisabledByAuthor": False,
        }

        res = await client.post(
            f"{LINKEDIN_REST_API}/posts",
            json=post_body,
            headers={**headers, "Content-Type": "application/json"},
        )
        res.raise_for_status()

        post_id = res.headers.get("x-restli-id", "published")
        return {"platform": "linkedin", "conta": conta, "post_id": post_id}


async def publicar_todas(
    images_base64: list[str],
    legenda_instagram: str,
    texto_linkedin: str,
) -> list[dict]:
    """Publica em todas as 4 contas: 2 Instagram + 2 LinkedIn."""
    resultados = []

    # Instagram carlosviana.ca
    try:
        r = await publicar_instagram(images_base64, legenda_instagram, "carlosviana")
        resultados.append(r)
    except Exception as e:
        resultados.append({"platform": "instagram", "conta": "carlosviana", "error": str(e)})

    # Instagram itvalleybr
    try:
        r = await publicar_instagram(images_base64, legenda_instagram, "itvalley")
        resultados.append(r)
    except Exception as e:
        resultados.append({"platform": "instagram", "conta": "itvalley", "error": str(e)})

    # LinkedIn pessoal (carlosaraujoviana)
    try:
        r = await publicar_linkedin(images_base64, texto_linkedin, "pessoal")
        resultados.append(r)
    except Exception as e:
        resultados.append({"platform": "linkedin", "conta": "pessoal", "error": str(e)})

    # LinkedIn IT Valley (organização)
    try:
        r = await publicar_linkedin(images_base64, texto_linkedin, "organizacao")
        resultados.append(r)
    except Exception as e:
        resultados.append({"platform": "linkedin", "conta": "organizacao", "error": str(e)})

    return resultados
