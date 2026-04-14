# Arquitetura Backend -- Kanban Pipeline

Documento produzido pelo Agente 03 (Arquiteto IT Valley Backend).
Base: PRD (`docs/prd-kanban-pipeline.md`) + Telas (`docs/telas-kanban-pipeline.md`) + Backend existente.

---

## 1. Decisoes de Arquitetura

### 1.1 Banco de dados
MongoDB (pymongo sincrono), mesmo database `content_factory` ja em uso. O projeto usa pymongo (NAO Motor), portanto os repositories sao sincronos. Os services usam `@staticmethod` como padrao do projeto.

### 1.2 Autenticacao
- Email+senha: bcrypt hash + JWT (python-jose + passlib)
- SSO Google/Microsoft: OAuth2 authorization code flow (httpx para callback)
- InviteToken: `secrets.token_urlsafe(32)`, expira 48h, usuario define senha ao aceitar
- JWT payload: `{ sub: user_id, tenant_id, role, exp }`
- Expiracao: 24h (RN-018)

### 1.3 Multitenancia
Todo documento MongoDB tem `tenant_id`. Toda query filtra por `tenant_id`. O `tenant_id` vem do JWT decodificado, nunca do request body.

### 1.4 Colunas fixas do MVP
6 colunas pre-definidas, criadas automaticamente no board padrao:
`Copy`, `Design`, `Revisao`, `Aprovado`, `Publicado`, `Cancelado`

IDs fixos (uuid4 gerados uma vez) para referenciar sem ambiguidade.

### 1.5 Padrao do projeto existente
O backend existente usa `@staticmethod` em services/repositories e pymongo sincrono. O Kanban segue o mesmo padrao para consistencia.

---

## 2. Dominios e Casos de Uso

### 2.1 Dominio: auth

| Caso de Uso | Metodo HTTP | Rota | Descricao |
|-------------|-------------|------|-----------|
| login | POST | /api/auth/login | Email+senha, retorna JWT |
| login_google | POST | /api/auth/google | Recebe authorization code Google, retorna JWT |
| login_microsoft | POST | /api/auth/microsoft | Recebe authorization code Microsoft, retorna JWT |
| criar_usuario | POST | /api/auth/users | Admin cria usuario (com senha inicial) |
| convidar_usuario | POST | /api/auth/users/invite | Admin gera InviteToken |
| aceitar_convite | POST | /api/auth/users/invite/accept | Usuario define senha via token |
| listar_usuarios | GET | /api/auth/users | Lista usuarios do tenant |
| buscar_usuario | GET | /api/auth/users/{user_id} | Busca usuario por ID |
| atualizar_usuario | PATCH | /api/auth/users/{user_id} | Admin edita nome, role, avatar |
| desativar_usuario | DELETE | /api/auth/users/{user_id} | Soft delete |
| reativar_usuario | POST | /api/auth/users/{user_id}/reativar | Remove soft delete |
| me | GET | /api/auth/me | Retorna dados do usuario logado |

### 2.2 Dominio: kanban_board

| Caso de Uso | Metodo HTTP | Rota | Descricao |
|-------------|-------------|------|-----------|
| buscar_board | GET | /api/kanban/boards/{board_id} | Board com colunas e cards |
| buscar_board_padrao | GET | /api/kanban/boards/default | Board padrao do tenant |
| criar_board | POST | /api/kanban/boards | Admin cria board (pos-MVP) |

### 2.3 Dominio: kanban_card

| Caso de Uso | Metodo HTTP | Rota | Descricao |
|-------------|-------------|------|-----------|
| criar_card | POST | /api/kanban/cards | Cria card na coluna Copy |
| buscar_card | GET | /api/kanban/cards/{card_id} | Detalhe completo do card |
| atualizar_card | PATCH | /api/kanban/cards/{card_id} | Edita campos do card |
| mover_card | POST | /api/kanban/cards/{card_id}/mover | Move card entre colunas |
| listar_cards | GET | /api/kanban/cards | Lista cards com filtros |
| atribuir_responsaveis | PATCH | /api/kanban/cards/{card_id}/responsaveis | Atribui usuarios |
| vincular_artefato | PATCH | /api/kanban/cards/{card_id}/artefatos | Vincula PDF/Drive |

### 2.4 Dominio: kanban_comment

| Caso de Uso | Metodo HTTP | Rota | Descricao |
|-------------|-------------|------|-----------|
| criar_comentario | POST | /api/kanban/cards/{card_id}/comments | Adiciona comentario |
| listar_comentarios | GET | /api/kanban/cards/{card_id}/comments | Lista comentarios do card |
| editar_comentario | PATCH | /api/kanban/comments/{comment_id} | Edita texto |
| deletar_comentario | DELETE | /api/kanban/comments/{comment_id} | Soft delete |

### 2.5 Dominio: kanban_activity

| Caso de Uso | Metodo HTTP | Rota | Descricao |
|-------------|-------------|------|-----------|
| listar_atividades | GET | /api/kanban/cards/{card_id}/activity | Timeline do card |

### 2.6 Dominio: kanban_notification

| Caso de Uso | Metodo HTTP | Rota | Descricao |
|-------------|-------------|------|-----------|
| listar_notificacoes | GET | /api/kanban/notifications | Notificacoes do usuario |
| contar_nao_lidas | GET | /api/kanban/notifications/count | Contador de nao-lidas |
| marcar_como_lida | PATCH | /api/kanban/notifications/{id}/read | Marca 1 como lida |
| marcar_todas_lidas | POST | /api/kanban/notifications/read-all | Marca todas como lidas |

---

## 3. Estrutura de Pastas

```
backend/
  middleware/
    auth.py                                    # get_current_user, require_role
    rate_limiter.py                            # (existente)

  dtos/
    auth/
      login/
        request.py                             # LoginRequest
        response.py                            # LoginResponse
      login_google/
        request.py                             # LoginGoogleRequest
        response.py                            # LoginResponse (reutiliza)
      login_microsoft/
        request.py                             # LoginMicrosoftRequest
        response.py                            # LoginResponse (reutiliza)
      criar_usuario/
        request.py                             # CriarUsuarioRequest
        response.py                            # UsuarioResponse
      convidar_usuario/
        request.py                             # ConvidarUsuarioRequest
        response.py                            # ConviteResponse
      aceitar_convite/
        request.py                             # AceitarConviteRequest
        response.py                            # LoginResponse
      atualizar_usuario/
        request.py                             # AtualizarUsuarioRequest
        response.py                            # UsuarioResponse
      listar_usuarios/
        response.py                            # ListarUsuariosResponse
      buscar_usuario/
        response.py                            # UsuarioResponse
      me/
        response.py                            # MeResponse
      base.py                                  # UsuarioBase

    kanban_board/
      buscar_board/
        response.py                            # BoardResponse
      base.py                                  # BoardBase, ColunaBase

    kanban_card/
      criar_card/
        request.py                             # CriarCardRequest
        response.py                            # CardResponse
      buscar_card/
        response.py                            # CardDetalheResponse
      atualizar_card/
        request.py                             # AtualizarCardRequest
        response.py                            # CardResponse
      mover_card/
        request.py                             # MoverCardRequest
        response.py                            # CardResponse
      listar_cards/
        request.py                             # ListarCardsFiltros
        response.py                            # ListarCardsResponse
      atribuir_responsaveis/
        request.py                             # AtribuirResponsaveisRequest
        response.py                            # CardResponse
      vincular_artefato/
        request.py                             # VincularArtefatoRequest
        response.py                            # CardResponse
      base.py                                  # CardBase

    kanban_comment/
      criar_comentario/
        request.py                             # CriarComentarioRequest
        response.py                            # ComentarioResponse
      listar_comentarios/
        response.py                            # ListarComentariosResponse
      editar_comentario/
        request.py                             # EditarComentarioRequest
        response.py                            # ComentarioResponse
      base.py                                  # ComentarioBase

    kanban_activity/
      listar_atividades/
        response.py                            # ListarAtividadesResponse
      base.py                                  # AtividadeBase

    kanban_notification/
      listar_notificacoes/
        response.py                            # ListarNotificacoesResponse
      contar_nao_lidas/
        response.py                            # ContadorNaoLidasResponse
      base.py                                  # NotificacaoBase

  factories/
    auth_factory.py
    kanban_board_factory.py
    kanban_card_factory.py
    kanban_comment_factory.py
    kanban_activity_factory.py
    kanban_notification_factory.py

  mappers/
    auth_mapper.py
    kanban_board_mapper.py
    kanban_card_mapper.py
    kanban_comment_mapper.py
    kanban_activity_mapper.py
    kanban_notification_mapper.py

  services/
    auth_service.py
    kanban_board_service.py
    kanban_card_service.py
    kanban_comment_service.py
    kanban_activity_service.py
    kanban_notification_service.py

  routers/
    auth.py
    kanban_board.py
    kanban_card.py
    kanban_comment.py
    kanban_notification.py

  data/
    repositories/
      mongo/
        auth_repository.py
        kanban_board_repository.py
        kanban_card_repository.py
        kanban_comment_repository.py
        kanban_activity_repository.py
        kanban_notification_repository.py
```

---

## 4. Codigo por Dominio

---

### 4.1 Middleware de Autenticacao

```python
# middleware/auth.py
from datetime import datetime, timezone, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from passlib.context import CryptContext
import os

security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "changeme-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24


class CurrentUser:
    """Dados do usuario extraidos do JWT."""
    def __init__(self, user_id: str, tenant_id: str, role: str, email: str, name: str):
        self.user_id = user_id
        self.tenant_id = tenant_id
        self.role = role
        self.email = email
        self.name = name


def create_access_token(user_id: str, tenant_id: str, role: str, email: str, name: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    payload = {
        "sub": user_id,
        "tenant_id": tenant_id,
        "role": role,
        "email": email,
        "name": name,
        "exp": expire,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> CurrentUser:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        tenant_id = payload.get("tenant_id")
        role = payload.get("role")
        email = payload.get("email")
        name = payload.get("name")
        if not user_id or not tenant_id or not role:
            raise HTTPException(status_code=401, detail="Token invalido")
        return CurrentUser(
            user_id=user_id,
            tenant_id=tenant_id,
            role=role,
            email=email or "",
            name=name or "",
        )
    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalido ou expirado")


def require_role(*allowed_roles: str):
    """Dependency factory: checa se o role do usuario esta na lista permitida."""
    async def _check(current_user: CurrentUser = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail=f"Perfil '{current_user.role}' nao tem permissao para esta acao",
            )
        return current_user
    return _check
```

---

### 4.2 Dominio: auth

#### DTOs

```python
# dtos/auth/base.py
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UsuarioBase(BaseModel):
    name: str
    email: EmailStr
    role: str  # admin, copywriter, designer, reviewer, viewer
    avatar_url: Optional[str] = None
```

```python
# dtos/auth/login/request.py
from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
```

```python
# dtos/auth/login/response.py
from pydantic import BaseModel


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    tenant_id: str
    role: str
    name: str
    email: str
```

```python
# dtos/auth/login_google/request.py
from pydantic import BaseModel


class LoginGoogleRequest(BaseModel):
    code: str  # authorization code do OAuth2
    redirect_uri: str
```

```python
# dtos/auth/login_microsoft/request.py
from pydantic import BaseModel


class LoginMicrosoftRequest(BaseModel):
    code: str
    redirect_uri: str
```

```python
# dtos/auth/criar_usuario/request.py
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
import re


class CriarUsuarioRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str  # admin, copywriter, designer, reviewer, viewer
    avatar_url: Optional[str] = None

    @field_validator("role")
    @classmethod
    def role_valido(cls, v: str) -> str:
        roles_validos = {"admin", "copywriter", "designer", "reviewer", "viewer"}
        if v.lower() not in roles_validos:
            raise ValueError(f"Role invalido. Valores aceitos: {roles_validos}")
        return v.lower()

    @field_validator("password")
    @classmethod
    def senha_forte(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Senha deve ter no minimo 8 caracteres")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Senha deve conter pelo menos 1 letra maiuscula")
        if not re.search(r"[0-9]", v):
            raise ValueError("Senha deve conter pelo menos 1 numero")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Senha deve conter pelo menos 1 caractere especial")
        return v

    @field_validator("name")
    @classmethod
    def nome_minimo(cls, v: str) -> str:
        if len(v.strip()) < 2:
            raise ValueError("Nome deve ter no minimo 2 caracteres")
        return v.strip()
```

```python
# dtos/auth/criar_usuario/response.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UsuarioResponse(BaseModel):
    id: str
    tenant_id: str
    name: str
    email: str
    role: str
    avatar_url: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
```

```python
# dtos/auth/convidar_usuario/request.py
from pydantic import BaseModel, EmailStr


class ConvidarUsuarioRequest(BaseModel):
    email: EmailStr
    name: str
    role: str  # perfil que o convidado tera
```

```python
# dtos/auth/convidar_usuario/response.py
from pydantic import BaseModel
from datetime import datetime


class ConviteResponse(BaseModel):
    invite_token: str
    email: str
    role: str
    expires_at: datetime
    invite_url: str  # URL completa para o frontend
```

```python
# dtos/auth/aceitar_convite/request.py
from pydantic import BaseModel, field_validator
import re


class AceitarConviteRequest(BaseModel):
    token: str
    password: str

    @field_validator("password")
    @classmethod
    def senha_forte(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Senha deve ter no minimo 8 caracteres")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Senha deve conter pelo menos 1 letra maiuscula")
        if not re.search(r"[0-9]", v):
            raise ValueError("Senha deve conter pelo menos 1 numero")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Senha deve conter pelo menos 1 caractere especial")
        return v
```

```python
# dtos/auth/atualizar_usuario/request.py
from pydantic import BaseModel, field_validator
from typing import Optional


class AtualizarUsuarioRequest(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    avatar_url: Optional[str] = None

    @field_validator("role")
    @classmethod
    def role_valido(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        roles_validos = {"admin", "copywriter", "designer", "reviewer", "viewer"}
        if v.lower() not in roles_validos:
            raise ValueError(f"Role invalido. Valores aceitos: {roles_validos}")
        return v.lower()
```

```python
# dtos/auth/atualizar_usuario/response.py
# Reutiliza UsuarioResponse de criar_usuario/response.py
```

```python
# dtos/auth/listar_usuarios/response.py
from pydantic import BaseModel
from dtos.auth.criar_usuario.response import UsuarioResponse


class ListarUsuariosResponse(BaseModel):
    users: list[UsuarioResponse]
    total: int
```

```python
# dtos/auth/buscar_usuario/response.py
# Reutiliza UsuarioResponse de criar_usuario/response.py
```

```python
# dtos/auth/me/response.py
from pydantic import BaseModel
from typing import Optional


class MeResponse(BaseModel):
    id: str
    tenant_id: str
    name: str
    email: str
    role: str
    avatar_url: Optional[str] = None
```

#### Factory

```python
# factories/auth_factory.py
import re
import secrets
from datetime import datetime, timezone, timedelta
from middleware.auth import hash_password


class AuthFactory:
    """Cria documentos de usuario e convite + regras de negocio."""

    VALID_ROLES = {"admin", "copywriter", "designer", "reviewer", "viewer"}

    @staticmethod
    def to_user_doc(dto, tenant_id: str) -> dict:
        """Cria documento MongoDB para kanban_users."""
        AuthFactory._validar_role(dto.role)
        return {
            "tenant_id": tenant_id,
            "email": dto.email.lower(),
            "name": dto.name,
            "avatar_url": getattr(dto, "avatar_url", None),
            "password_hash": hash_password(dto.password),
            "role": dto.role.lower(),
            "created_at": datetime.now(timezone.utc),
            "updated_at": None,
            "deleted_at": None,
        }

    @staticmethod
    def to_invite_doc(dto, tenant_id: str, created_by: str) -> dict:
        """Cria documento de convite com token seguro."""
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=48)
        return {
            "tenant_id": tenant_id,
            "email": dto.email.lower(),
            "name": dto.name,
            "role": dto.role.lower(),
            "token": token,
            "created_by": created_by,
            "expires_at": expires_at,
            "used": False,
            "created_at": datetime.now(timezone.utc),
        }

    @staticmethod
    def to_user_from_invite(invite_doc: dict, password: str) -> dict:
        """Cria documento de usuario a partir de convite aceito."""
        return {
            "tenant_id": invite_doc["tenant_id"],
            "email": invite_doc["email"],
            "name": invite_doc["name"],
            "avatar_url": None,
            "password_hash": hash_password(password),
            "role": invite_doc["role"],
            "created_at": datetime.now(timezone.utc),
            "updated_at": None,
            "deleted_at": None,
        }

    @staticmethod
    def to_update_fields(dto) -> dict:
        """Extrai campos nao-nulos do DTO para update parcial."""
        fields = {}
        if dto.name is not None:
            fields["name"] = dto.name
        if dto.role is not None:
            AuthFactory._validar_role(dto.role)
            fields["role"] = dto.role.lower()
        if dto.avatar_url is not None:
            fields["avatar_url"] = dto.avatar_url
        if fields:
            fields["updated_at"] = datetime.now(timezone.utc)
        return fields

    @staticmethod
    def _validar_role(role: str):
        if role.lower() not in AuthFactory.VALID_ROLES:
            raise ValueError(f"Role invalido: {role}")
```

#### Mapper

```python
# mappers/auth_mapper.py
from dtos.auth.criar_usuario.response import UsuarioResponse
from dtos.auth.login.response import LoginResponse
from dtos.auth.me.response import MeResponse
from dtos.auth.convidar_usuario.response import ConviteResponse
from dtos.auth.listar_usuarios.response import ListarUsuariosResponse


class AuthMapper:

    @staticmethod
    def to_usuario_response(doc: dict) -> UsuarioResponse:
        return UsuarioResponse(
            id=str(doc["_id"]),
            tenant_id=doc["tenant_id"],
            name=doc["name"],
            email=doc["email"],
            role=doc["role"],
            avatar_url=doc.get("avatar_url"),
            created_at=doc["created_at"],
            updated_at=doc.get("updated_at"),
        )

    @staticmethod
    def to_login_response(doc: dict, access_token: str) -> LoginResponse:
        return LoginResponse(
            access_token=access_token,
            user_id=str(doc["_id"]),
            tenant_id=doc["tenant_id"],
            role=doc["role"],
            name=doc["name"],
            email=doc["email"],
        )

    @staticmethod
    def to_me_response(doc: dict) -> MeResponse:
        return MeResponse(
            id=str(doc["_id"]),
            tenant_id=doc["tenant_id"],
            name=doc["name"],
            email=doc["email"],
            role=doc["role"],
            avatar_url=doc.get("avatar_url"),
        )

    @staticmethod
    def to_convite_response(doc: dict, base_url: str) -> ConviteResponse:
        return ConviteResponse(
            invite_token=doc["token"],
            email=doc["email"],
            role=doc["role"],
            expires_at=doc["expires_at"],
            invite_url=f"{base_url}/invite?token={doc['token']}",
        )

    @staticmethod
    def to_listar_response(docs: list[dict]) -> ListarUsuariosResponse:
        return ListarUsuariosResponse(
            users=[AuthMapper.to_usuario_response(d) for d in docs],
            total=len(docs),
        )
```

#### Repository

```python
# data/repositories/mongo/auth_repository.py
from bson import ObjectId
from datetime import datetime, timezone
from data.connections.mongo_connection import get_mongo_db


class AuthRepository:
    """CRUD kanban_users + kanban_invites no MongoDB."""

    # ---- Users ----

    @staticmethod
    def buscar_por_email(email: str, tenant_id: str) -> dict | None:
        db = get_mongo_db()
        if db is None:
            return None
        return db.kanban_users.find_one({
            "email": email.lower(),
            "tenant_id": tenant_id,
            "deleted_at": None,
        })

    @staticmethod
    def buscar_por_id(user_id: str, tenant_id: str) -> dict | None:
        db = get_mongo_db()
        if db is None:
            return None
        return db.kanban_users.find_one({
            "_id": ObjectId(user_id),
            "tenant_id": tenant_id,
            "deleted_at": None,
        })

    @staticmethod
    def listar(tenant_id: str, incluir_inativos: bool = False) -> list[dict]:
        db = get_mongo_db()
        if db is None:
            return []
        filtro = {"tenant_id": tenant_id}
        if not incluir_inativos:
            filtro["deleted_at"] = None
        return list(db.kanban_users.find(filtro).sort("name", 1))

    @staticmethod
    def criar(doc: dict) -> dict:
        db = get_mongo_db()
        if db is None:
            raise RuntimeError("MongoDB nao configurado")
        result = db.kanban_users.insert_one(doc)
        doc["_id"] = result.inserted_id
        return doc

    @staticmethod
    def atualizar(user_id: str, tenant_id: str, fields: dict) -> dict | None:
        db = get_mongo_db()
        if db is None:
            return None
        db.kanban_users.update_one(
            {"_id": ObjectId(user_id), "tenant_id": tenant_id},
            {"$set": fields},
        )
        return db.kanban_users.find_one({"_id": ObjectId(user_id)})

    @staticmethod
    def soft_delete(user_id: str, tenant_id: str) -> bool:
        db = get_mongo_db()
        if db is None:
            return False
        result = db.kanban_users.update_one(
            {"_id": ObjectId(user_id), "tenant_id": tenant_id},
            {"$set": {"deleted_at": datetime.now(timezone.utc)}},
        )
        return result.modified_count > 0

    @staticmethod
    def reativar(user_id: str, tenant_id: str) -> bool:
        db = get_mongo_db()
        if db is None:
            return False
        result = db.kanban_users.update_one(
            {"_id": ObjectId(user_id), "tenant_id": tenant_id},
            {"$set": {"deleted_at": None, "updated_at": datetime.now(timezone.utc)}},
        )
        return result.modified_count > 0

    # ---- Invites ----

    @staticmethod
    def criar_convite(doc: dict) -> dict:
        db = get_mongo_db()
        if db is None:
            raise RuntimeError("MongoDB nao configurado")
        result = db.kanban_invites.insert_one(doc)
        doc["_id"] = result.inserted_id
        return doc

    @staticmethod
    def buscar_convite(token: str) -> dict | None:
        db = get_mongo_db()
        if db is None:
            return None
        return db.kanban_invites.find_one({"token": token, "used": False})

    @staticmethod
    def marcar_convite_usado(token: str) -> bool:
        db = get_mongo_db()
        if db is None:
            return False
        result = db.kanban_invites.update_one(
            {"token": token},
            {"$set": {"used": True}},
        )
        return result.modified_count > 0

    @staticmethod
    def email_ja_existe(email: str, tenant_id: str) -> bool:
        db = get_mongo_db()
        if db is None:
            return False
        return db.kanban_users.find_one({
            "email": email.lower(),
            "tenant_id": tenant_id,
        }) is not None
```

#### Service

```python
# services/auth_service.py
from datetime import datetime, timezone
from fastapi import HTTPException
from factories.auth_factory import AuthFactory
from mappers.auth_mapper import AuthMapper
from data.repositories.mongo.auth_repository import AuthRepository
from middleware.auth import verify_password, create_access_token


class AuthService:
    """Orquestra autenticacao e CRUD de usuarios. Camada opaca."""

    @staticmethod
    def login(dto, tenant_id: str):
        user = AuthRepository.buscar_por_email(dto.email, tenant_id)
        if not user:
            raise HTTPException(status_code=401, detail="Email ou senha incorretos")
        if not verify_password(dto.password, user["password_hash"]):
            raise HTTPException(status_code=401, detail="Email ou senha incorretos")
        token = create_access_token(
            user_id=str(user["_id"]),
            tenant_id=user["tenant_id"],
            role=user["role"],
            email=user["email"],
            name=user["name"],
        )
        return AuthMapper.to_login_response(user, token)

    @staticmethod
    def criar_usuario(dto, tenant_id: str):
        if AuthRepository.email_ja_existe(dto.email, tenant_id):
            raise HTTPException(status_code=409, detail="Email ja cadastrado")
        doc = AuthFactory.to_user_doc(dto, tenant_id)
        saved = AuthRepository.criar(doc)
        return AuthMapper.to_usuario_response(saved)

    @staticmethod
    def convidar_usuario(dto, tenant_id: str, created_by: str, base_url: str):
        if AuthRepository.email_ja_existe(dto.email, tenant_id):
            raise HTTPException(status_code=409, detail="Email ja cadastrado")
        doc = AuthFactory.to_invite_doc(dto, tenant_id, created_by)
        saved = AuthRepository.criar_convite(doc)
        return AuthMapper.to_convite_response(saved, base_url)

    @staticmethod
    def aceitar_convite(dto):
        invite = AuthRepository.buscar_convite(dto.token)
        if not invite:
            raise HTTPException(status_code=404, detail="Convite nao encontrado ou ja utilizado")
        if invite["expires_at"] < datetime.now(timezone.utc):
            raise HTTPException(status_code=410, detail="Convite expirado")
        if AuthRepository.email_ja_existe(invite["email"], invite["tenant_id"]):
            raise HTTPException(status_code=409, detail="Email ja cadastrado")
        user_doc = AuthFactory.to_user_from_invite(invite, dto.password)
        saved = AuthRepository.criar(user_doc)
        AuthRepository.marcar_convite_usado(dto.token)
        token = create_access_token(
            user_id=str(saved["_id"]),
            tenant_id=saved["tenant_id"],
            role=saved["role"],
            email=saved["email"],
            name=saved["name"],
        )
        return AuthMapper.to_login_response(saved, token)

    @staticmethod
    def listar_usuarios(tenant_id: str):
        docs = AuthRepository.listar(tenant_id)
        return AuthMapper.to_listar_response(docs)

    @staticmethod
    def buscar_usuario(user_id: str, tenant_id: str):
        doc = AuthRepository.buscar_por_id(user_id, tenant_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Usuario nao encontrado")
        return AuthMapper.to_usuario_response(doc)

    @staticmethod
    def atualizar_usuario(user_id: str, dto, tenant_id: str):
        fields = AuthFactory.to_update_fields(dto)
        if not fields:
            raise HTTPException(status_code=400, detail="Nenhum campo para atualizar")
        updated = AuthRepository.atualizar(user_id, tenant_id, fields)
        if not updated:
            raise HTTPException(status_code=404, detail="Usuario nao encontrado")
        return AuthMapper.to_usuario_response(updated)

    @staticmethod
    def desativar_usuario(user_id: str, tenant_id: str):
        success = AuthRepository.soft_delete(user_id, tenant_id)
        if not success:
            raise HTTPException(status_code=404, detail="Usuario nao encontrado")
        return {"detail": "Usuario desativado"}

    @staticmethod
    def reativar_usuario(user_id: str, tenant_id: str):
        success = AuthRepository.reativar(user_id, tenant_id)
        if not success:
            raise HTTPException(status_code=404, detail="Usuario nao encontrado")
        return {"detail": "Usuario reativado"}

    @staticmethod
    def me(user_id: str, tenant_id: str):
        doc = AuthRepository.buscar_por_id(user_id, tenant_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Usuario nao encontrado")
        return AuthMapper.to_me_response(doc)
```

#### Router

```python
# routers/auth.py
from fastapi import APIRouter, HTTPException, Depends, Request

from dtos.auth.login.request import LoginRequest
from dtos.auth.login.response import LoginResponse
from dtos.auth.login_google.request import LoginGoogleRequest
from dtos.auth.login_microsoft.request import LoginMicrosoftRequest
from dtos.auth.criar_usuario.request import CriarUsuarioRequest
from dtos.auth.criar_usuario.response import UsuarioResponse
from dtos.auth.convidar_usuario.request import ConvidarUsuarioRequest
from dtos.auth.convidar_usuario.response import ConviteResponse
from dtos.auth.aceitar_convite.request import AceitarConviteRequest
from dtos.auth.atualizar_usuario.request import AtualizarUsuarioRequest
from dtos.auth.listar_usuarios.response import ListarUsuariosResponse
from dtos.auth.me.response import MeResponse
from middleware.auth import get_current_user, require_role, CurrentUser
from middleware.rate_limiter import limiter
from services.auth_service import AuthService
from config import settings

router = APIRouter(prefix="/auth", tags=["Autenticacao"])


@router.post("/login", response_model=LoginResponse)
@limiter.limit("5/minute")
async def login(request: Request, dto: LoginRequest):
    return AuthService.login(dto, tenant_id=settings.TENANT_ID)


@router.post("/google", response_model=LoginResponse)
async def login_google(dto: LoginGoogleRequest):
    # SSO Google: trocar authorization code por user info, buscar/criar usuario
    raise HTTPException(status_code=501, detail="SSO Google: implementar OAuth2 callback")


@router.post("/microsoft", response_model=LoginResponse)
async def login_microsoft(dto: LoginMicrosoftRequest):
    # SSO Microsoft: trocar authorization code por user info, buscar/criar usuario
    raise HTTPException(status_code=501, detail="SSO Microsoft: implementar OAuth2 callback")


@router.post("/users", response_model=UsuarioResponse, status_code=201)
async def criar_usuario(
    dto: CriarUsuarioRequest,
    current_user: CurrentUser = Depends(require_role("admin")),
):
    return AuthService.criar_usuario(dto, tenant_id=current_user.tenant_id)


@router.post("/users/invite", response_model=ConviteResponse, status_code=201)
async def convidar_usuario(
    request: Request,
    dto: ConvidarUsuarioRequest,
    current_user: CurrentUser = Depends(require_role("admin")),
):
    base_url = str(request.base_url).rstrip("/")
    return AuthService.convidar_usuario(
        dto,
        tenant_id=current_user.tenant_id,
        created_by=current_user.user_id,
        base_url=base_url,
    )


@router.post("/users/invite/accept", response_model=LoginResponse)
async def aceitar_convite(dto: AceitarConviteRequest):
    return AuthService.aceitar_convite(dto)


@router.get("/users", response_model=ListarUsuariosResponse)
async def listar_usuarios(
    current_user: CurrentUser = Depends(require_role("admin")),
):
    return AuthService.listar_usuarios(tenant_id=current_user.tenant_id)


@router.get("/users/{user_id}", response_model=UsuarioResponse)
async def buscar_usuario(
    user_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    return AuthService.buscar_usuario(user_id, tenant_id=current_user.tenant_id)


@router.patch("/users/{user_id}", response_model=UsuarioResponse)
async def atualizar_usuario(
    user_id: str,
    dto: AtualizarUsuarioRequest,
    current_user: CurrentUser = Depends(require_role("admin")),
):
    return AuthService.atualizar_usuario(user_id, dto, tenant_id=current_user.tenant_id)


@router.delete("/users/{user_id}")
async def desativar_usuario(
    user_id: str,
    current_user: CurrentUser = Depends(require_role("admin")),
):
    return AuthService.desativar_usuario(user_id, tenant_id=current_user.tenant_id)


@router.post("/users/{user_id}/reativar")
async def reativar_usuario(
    user_id: str,
    current_user: CurrentUser = Depends(require_role("admin")),
):
    return AuthService.reativar_usuario(user_id, tenant_id=current_user.tenant_id)


@router.get("/me", response_model=MeResponse)
async def me(current_user: CurrentUser = Depends(get_current_user)):
    return AuthService.me(current_user.user_id, tenant_id=current_user.tenant_id)
```

---

### 4.3 Dominio: kanban_board

#### DTOs

```python
# dtos/kanban_board/base.py
from pydantic import BaseModel
from typing import Optional


class ColunaBase(BaseModel):
    id: str
    name: str
    order: int
    color: Optional[str] = None


class BoardBase(BaseModel):
    name: str
```

```python
# dtos/kanban_board/buscar_board/response.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from dtos.kanban_board.base import ColunaBase


class BoardResponse(BaseModel):
    id: str
    tenant_id: str
    name: str
    columns: list[ColunaBase]
    created_at: datetime
    updated_at: Optional[datetime] = None
```

#### Factory

```python
# factories/kanban_board_factory.py
import uuid
from datetime import datetime, timezone


# IDs fixos das colunas MVP — nunca mudam
COLUNAS_MVP = [
    {"id": "col-copy",      "name": "Copy",       "order": 0, "color": "#3B82F6"},
    {"id": "col-design",    "name": "Design",      "order": 1, "color": "#8B5CF6"},
    {"id": "col-revisao",   "name": "Revisao",     "order": 2, "color": "#EAB308"},
    {"id": "col-aprovado",  "name": "Aprovado",    "order": 3, "color": "#22C55E"},
    {"id": "col-publicado", "name": "Publicado",   "order": 4, "color": "#15803D"},
    {"id": "col-cancelado", "name": "Cancelado",   "order": 5, "color": "#6B7280"},
]

COLUNAS_TERMINAIS = {"col-publicado", "col-cancelado"}
COLUNA_COPY = "col-copy"
COLUNA_DESIGN = "col-design"
COLUNA_REVISAO = "col-revisao"
COLUNA_APROVADO = "col-aprovado"
COLUNA_PUBLICADO = "col-publicado"
COLUNA_CANCELADO = "col-cancelado"


class KanbanBoardFactory:

    @staticmethod
    def criar_board_padrao(tenant_id: str) -> dict:
        """Cria o board padrao do MVP com 6 colunas fixas."""
        return {
            "tenant_id": tenant_id,
            "name": "Pipeline de Carrosseis",
            "columns": [col.copy() for col in COLUNAS_MVP],
            "created_at": datetime.now(timezone.utc),
            "updated_at": None,
        }

    @staticmethod
    def validar_coluna_destino(column_id: str, column_origem_id: str):
        """RN-019: unica movimentacao manual permitida e para Cancelado.
           RN-007: colunas terminais nao podem mover para frente."""
        if column_origem_id in COLUNAS_TERMINAIS:
            raise ValueError(f"Card em coluna terminal nao pode ser movido")
        if column_id != COLUNA_CANCELADO:
            raise ValueError(
                "Movimentacao manual so e permitida para a coluna Cancelado. "
                "Demais movimentacoes sao automaticas via pipeline."
            )

    @staticmethod
    def validar_movimentacao_pipeline(column_destino: str):
        """Movimentacoes automaticas da pipeline aceitam qualquer coluna nao-terminal como origem."""
        colunas_validas = {c["id"] for c in COLUNAS_MVP}
        if column_destino not in colunas_validas:
            raise ValueError(f"Coluna destino invalida: {column_destino}")
```

#### Mapper

```python
# mappers/kanban_board_mapper.py
from dtos.kanban_board.buscar_board.response import BoardResponse
from dtos.kanban_board.base import ColunaBase


class KanbanBoardMapper:

    @staticmethod
    def to_response(doc: dict) -> BoardResponse:
        return BoardResponse(
            id=str(doc["_id"]),
            tenant_id=doc["tenant_id"],
            name=doc["name"],
            columns=[
                ColunaBase(
                    id=col["id"],
                    name=col["name"],
                    order=col["order"],
                    color=col.get("color"),
                )
                for col in doc.get("columns", [])
            ],
            created_at=doc["created_at"],
            updated_at=doc.get("updated_at"),
        )
```

#### Repository

```python
# data/repositories/mongo/kanban_board_repository.py
from bson import ObjectId
from data.connections.mongo_connection import get_mongo_db


class KanbanBoardRepository:

    @staticmethod
    def buscar_padrao(tenant_id: str) -> dict | None:
        db = get_mongo_db()
        if db is None:
            return None
        return db.kanban_boards.find_one({"tenant_id": tenant_id})

    @staticmethod
    def buscar_por_id(board_id: str, tenant_id: str) -> dict | None:
        db = get_mongo_db()
        if db is None:
            return None
        return db.kanban_boards.find_one({
            "_id": ObjectId(board_id),
            "tenant_id": tenant_id,
        })

    @staticmethod
    def criar(doc: dict) -> dict:
        db = get_mongo_db()
        if db is None:
            raise RuntimeError("MongoDB nao configurado")
        result = db.kanban_boards.insert_one(doc)
        doc["_id"] = result.inserted_id
        return doc

    @staticmethod
    def garantir_board_padrao(tenant_id: str) -> dict:
        """Retorna board existente ou cria o padrao."""
        from factories.kanban_board_factory import KanbanBoardFactory
        board = KanbanBoardRepository.buscar_padrao(tenant_id)
        if board:
            return board
        doc = KanbanBoardFactory.criar_board_padrao(tenant_id)
        return KanbanBoardRepository.criar(doc)
```

#### Service

```python
# services/kanban_board_service.py
from mappers.kanban_board_mapper import KanbanBoardMapper
from data.repositories.mongo.kanban_board_repository import KanbanBoardRepository


class KanbanBoardService:
    """Orquestra operacoes do board. Camada opaca."""

    @staticmethod
    def buscar_padrao(tenant_id: str):
        doc = KanbanBoardRepository.garantir_board_padrao(tenant_id)
        return KanbanBoardMapper.to_response(doc)

    @staticmethod
    def buscar(board_id: str, tenant_id: str):
        doc = KanbanBoardRepository.buscar_por_id(board_id, tenant_id)
        if not doc:
            return None
        return KanbanBoardMapper.to_response(doc)
```

#### Router

```python
# routers/kanban_board.py
from fastapi import APIRouter, HTTPException, Depends

from dtos.kanban_board.buscar_board.response import BoardResponse
from middleware.auth import get_current_user, CurrentUser
from services.kanban_board_service import KanbanBoardService

router = APIRouter(prefix="/kanban/boards", tags=["Kanban Board"])


@router.get("/default", response_model=BoardResponse)
async def buscar_board_padrao(
    current_user: CurrentUser = Depends(get_current_user),
):
    return KanbanBoardService.buscar_padrao(tenant_id=current_user.tenant_id)


@router.get("/{board_id}", response_model=BoardResponse)
async def buscar_board(
    board_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    result = KanbanBoardService.buscar(board_id, tenant_id=current_user.tenant_id)
    if not result:
        raise HTTPException(status_code=404, detail="Board nao encontrado")
    return result
```

---

### 4.4 Dominio: kanban_card

#### DTOs

```python
# dtos/kanban_card/base.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CardBase(BaseModel):
    title: str
    copy_text: Optional[str] = None
    disciplina: Optional[str] = None
    tecnologia: Optional[str] = None
    priority: str = "media"  # alta, media, baixa
```

```python
# dtos/kanban_card/criar_card/request.py
from pydantic import BaseModel, field_validator
from typing import Optional


class CriarCardRequest(BaseModel):
    title: str
    copy_text: Optional[str] = None
    disciplina: Optional[str] = None
    tecnologia: Optional[str] = None
    priority: str = "media"
    assigned_user_ids: list[str] = []
    pipeline_id: Optional[str] = None

    @field_validator("title")
    @classmethod
    def titulo_minimo(cls, v: str) -> str:
        if len(v.strip()) < 3:
            raise ValueError("Titulo deve ter no minimo 3 caracteres")
        return v.strip()

    @field_validator("priority")
    @classmethod
    def prioridade_valida(cls, v: str) -> str:
        if v.lower() not in {"alta", "media", "baixa"}:
            raise ValueError("Prioridade deve ser: alta, media ou baixa")
        return v.lower()
```

```python
# dtos/kanban_card/criar_card/response.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CardResponse(BaseModel):
    id: str
    board_id: str
    column_id: str
    title: str
    copy_text: Optional[str] = None
    disciplina: Optional[str] = None
    tecnologia: Optional[str] = None
    priority: str
    assigned_user_ids: list[str] = []
    created_by: str
    pipeline_id: Optional[str] = None
    drive_link: Optional[str] = None
    drive_folder_name: Optional[str] = None
    pdf_url: Optional[str] = None
    image_urls: list[str] = []
    created_at: datetime
    updated_at: Optional[datetime] = None
```

```python
# dtos/kanban_card/buscar_card/response.py
# Reutiliza CardResponse de criar_card/response.py
```

```python
# dtos/kanban_card/atualizar_card/request.py
from pydantic import BaseModel, field_validator
from typing import Optional


class AtualizarCardRequest(BaseModel):
    title: Optional[str] = None
    copy_text: Optional[str] = None
    disciplina: Optional[str] = None
    tecnologia: Optional[str] = None
    priority: Optional[str] = None

    @field_validator("title")
    @classmethod
    def titulo_minimo(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v.strip()) < 3:
            raise ValueError("Titulo deve ter no minimo 3 caracteres")
        return v.strip() if v else v

    @field_validator("priority")
    @classmethod
    def prioridade_valida(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v.lower() not in {"alta", "media", "baixa"}:
            raise ValueError("Prioridade deve ser: alta, media ou baixa")
        return v.lower() if v else v
```

```python
# dtos/kanban_card/atualizar_card/response.py
# Reutiliza CardResponse de criar_card/response.py
```

```python
# dtos/kanban_card/mover_card/request.py
from pydantic import BaseModel


class MoverCardRequest(BaseModel):
    column_id: str  # coluna destino (para movimentacao manual: sempre "col-cancelado")
```

```python
# dtos/kanban_card/mover_card/response.py
# Reutiliza CardResponse de criar_card/response.py
```

```python
# dtos/kanban_card/listar_cards/request.py
from pydantic import BaseModel
from typing import Optional


class ListarCardsFiltros(BaseModel):
    board_id: Optional[str] = None
    column_id: Optional[str] = None
    priority: Optional[str] = None
    assigned_user_id: Optional[str] = None
    search: Optional[str] = None
```

```python
# dtos/kanban_card/listar_cards/response.py
from pydantic import BaseModel
from dtos.kanban_card.criar_card.response import CardResponse


class ListarCardsResponse(BaseModel):
    cards: list[CardResponse]
    total: int
```

```python
# dtos/kanban_card/atribuir_responsaveis/request.py
from pydantic import BaseModel


class AtribuirResponsaveisRequest(BaseModel):
    user_ids: list[str]
```

```python
# dtos/kanban_card/atribuir_responsaveis/response.py
# Reutiliza CardResponse de criar_card/response.py
```

```python
# dtos/kanban_card/vincular_artefato/request.py
from pydantic import BaseModel
from typing import Optional


class VincularArtefatoRequest(BaseModel):
    drive_link: Optional[str] = None
    drive_folder_name: Optional[str] = None
    pdf_url: Optional[str] = None
    image_urls: Optional[list[str]] = None
```

```python
# dtos/kanban_card/vincular_artefato/response.py
# Reutiliza CardResponse de criar_card/response.py
```

#### Factory

```python
# factories/kanban_card_factory.py
from datetime import datetime, timezone
from factories.kanban_board_factory import COLUNA_COPY


class KanbanCardFactory:

    PRIORIDADES_VALIDAS = {"alta", "media", "baixa"}

    @staticmethod
    def to_doc(dto, board_id: str, tenant_id: str, created_by: str) -> dict:
        """Cria documento MongoDB para kanban_cards. Card sempre inicia na coluna Copy."""
        KanbanCardFactory._validar_prioridade(dto.priority)
        return {
            "tenant_id": tenant_id,
            "board_id": board_id,
            "column_id": COLUNA_COPY,
            "title": dto.title.strip(),
            "copy_text": getattr(dto, "copy_text", None),
            "disciplina": getattr(dto, "disciplina", None),
            "tecnologia": getattr(dto, "tecnologia", None),
            "priority": dto.priority.lower(),
            "assigned_user_ids": getattr(dto, "assigned_user_ids", []),
            "created_by": created_by,
            "pipeline_id": getattr(dto, "pipeline_id", None),
            "drive_link": None,
            "drive_folder_name": None,
            "pdf_url": None,
            "image_urls": [],
            "order_in_column": 0,
            "created_at": datetime.now(timezone.utc),
            "updated_at": None,
            "archived_at": None,
        }

    @staticmethod
    def to_update_fields(dto) -> dict:
        """Extrai campos nao-nulos do DTO para update parcial."""
        fields = {}
        for campo in ("title", "copy_text", "disciplina", "tecnologia", "priority"):
            valor = getattr(dto, campo, None)
            if valor is not None:
                if campo == "priority":
                    KanbanCardFactory._validar_prioridade(valor)
                    valor = valor.lower()
                fields[campo] = valor
        if fields:
            fields["updated_at"] = datetime.now(timezone.utc)
        return fields

    @staticmethod
    def to_artefato_fields(dto) -> dict:
        """Extrai campos de artefato para update."""
        fields = {}
        if dto.drive_link is not None:
            fields["drive_link"] = dto.drive_link
        if dto.drive_folder_name is not None:
            fields["drive_folder_name"] = dto.drive_folder_name
        if dto.pdf_url is not None:
            fields["pdf_url"] = dto.pdf_url
        if dto.image_urls is not None:
            fields["image_urls"] = dto.image_urls
        if fields:
            fields["updated_at"] = datetime.now(timezone.utc)
        return fields

    @staticmethod
    def _validar_prioridade(priority: str):
        if priority.lower() not in KanbanCardFactory.PRIORIDADES_VALIDAS:
            raise ValueError(f"Prioridade invalida: {priority}")
```

#### Mapper

```python
# mappers/kanban_card_mapper.py
from dtos.kanban_card.criar_card.response import CardResponse
from dtos.kanban_card.listar_cards.response import ListarCardsResponse


class KanbanCardMapper:

    @staticmethod
    def to_response(doc: dict) -> CardResponse:
        return CardResponse(
            id=str(doc["_id"]),
            board_id=doc["board_id"],
            column_id=doc["column_id"],
            title=doc["title"],
            copy_text=doc.get("copy_text"),
            disciplina=doc.get("disciplina"),
            tecnologia=doc.get("tecnologia"),
            priority=doc["priority"],
            assigned_user_ids=doc.get("assigned_user_ids", []),
            created_by=doc["created_by"],
            pipeline_id=doc.get("pipeline_id"),
            drive_link=doc.get("drive_link"),
            drive_folder_name=doc.get("drive_folder_name"),
            pdf_url=doc.get("pdf_url"),
            image_urls=doc.get("image_urls", []),
            created_at=doc["created_at"],
            updated_at=doc.get("updated_at"),
        )

    @staticmethod
    def to_list_response(docs: list[dict]) -> ListarCardsResponse:
        return ListarCardsResponse(
            cards=[KanbanCardMapper.to_response(d) for d in docs],
            total=len(docs),
        )
```

#### Repository

```python
# data/repositories/mongo/kanban_card_repository.py
import re
from bson import ObjectId
from datetime import datetime, timezone
from data.connections.mongo_connection import get_mongo_db


class KanbanCardRepository:

    @staticmethod
    def criar(doc: dict) -> dict:
        db = get_mongo_db()
        if db is None:
            raise RuntimeError("MongoDB nao configurado")
        result = db.kanban_cards.insert_one(doc)
        doc["_id"] = result.inserted_id
        return doc

    @staticmethod
    def buscar_por_id(card_id: str, tenant_id: str) -> dict | None:
        db = get_mongo_db()
        if db is None:
            return None
        return db.kanban_cards.find_one({
            "_id": ObjectId(card_id),
            "tenant_id": tenant_id,
            "archived_at": None,
        })

    @staticmethod
    def buscar_por_pipeline_id(pipeline_id: str, tenant_id: str) -> dict | None:
        """Busca card vinculado a um pipeline (para integracao automatica)."""
        db = get_mongo_db()
        if db is None:
            return None
        return db.kanban_cards.find_one({
            "pipeline_id": pipeline_id,
            "tenant_id": tenant_id,
            "archived_at": None,
        })

    @staticmethod
    def listar(tenant_id: str, filters: dict = {}) -> list[dict]:
        db = get_mongo_db()
        if db is None:
            return []
        query = {"tenant_id": tenant_id, "archived_at": None}
        if filters.get("board_id"):
            query["board_id"] = filters["board_id"]
        if filters.get("column_id"):
            query["column_id"] = filters["column_id"]
        if filters.get("priority"):
            query["priority"] = filters["priority"]
        if filters.get("assigned_user_id"):
            query["assigned_user_ids"] = filters["assigned_user_id"]
        if filters.get("search"):
            query["title"] = {"$regex": re.escape(filters["search"]), "$options": "i"}
        return list(
            db.kanban_cards.find(query).sort([("order_in_column", 1), ("created_at", -1)])
        )

    @staticmethod
    def atualizar(card_id: str, tenant_id: str, fields: dict) -> dict | None:
        db = get_mongo_db()
        if db is None:
            return None
        db.kanban_cards.update_one(
            {"_id": ObjectId(card_id), "tenant_id": tenant_id},
            {"$set": fields},
        )
        return db.kanban_cards.find_one({"_id": ObjectId(card_id)})

    @staticmethod
    def mover(card_id: str, tenant_id: str, column_id: str) -> dict | None:
        db = get_mongo_db()
        if db is None:
            return None
        db.kanban_cards.update_one(
            {"_id": ObjectId(card_id), "tenant_id": tenant_id},
            {"$set": {
                "column_id": column_id,
                "updated_at": datetime.now(timezone.utc),
            }},
        )
        return db.kanban_cards.find_one({"_id": ObjectId(card_id)})

    @staticmethod
    def atribuir_responsaveis(card_id: str, tenant_id: str, user_ids: list[str]) -> dict | None:
        db = get_mongo_db()
        if db is None:
            return None
        db.kanban_cards.update_one(
            {"_id": ObjectId(card_id), "tenant_id": tenant_id},
            {"$set": {
                "assigned_user_ids": user_ids,
                "updated_at": datetime.now(timezone.utc),
            }},
        )
        return db.kanban_cards.find_one({"_id": ObjectId(card_id)})
```

#### Service

```python
# services/kanban_card_service.py
from fastapi import HTTPException
from factories.kanban_card_factory import KanbanCardFactory
from factories.kanban_board_factory import KanbanBoardFactory, COLUNA_CANCELADO
from mappers.kanban_card_mapper import KanbanCardMapper
from data.repositories.mongo.kanban_card_repository import KanbanCardRepository
from data.repositories.mongo.kanban_board_repository import KanbanBoardRepository
from services.kanban_activity_service import KanbanActivityService
from services.kanban_notification_service import KanbanNotificationService


class KanbanCardService:
    """Orquestra operacoes de card. Camada opaca."""

    @staticmethod
    def criar(dto, tenant_id: str, created_by: str):
        board = KanbanBoardRepository.garantir_board_padrao(tenant_id)
        board_id = str(board["_id"])
        doc = KanbanCardFactory.to_doc(dto, board_id, tenant_id, created_by)
        saved = KanbanCardRepository.criar(doc)

        # Audit log
        KanbanActivityService.registrar(
            tenant_id=tenant_id,
            card_id=str(saved["_id"]),
            user_id=created_by,
            action="card_created",
            metadata={"title": saved["title"]},
        )

        # Notificar responsaveis atribuidos
        for uid in saved.get("assigned_user_ids", []):
            KanbanNotificationService.notificar(
                tenant_id=tenant_id,
                user_id=uid,
                card_id=str(saved["_id"]),
                type_="assigned",
                message=f"Voce foi atribuido ao card '{saved['title']}'",
            )

        return KanbanCardMapper.to_response(saved)

    @staticmethod
    def buscar(card_id: str, tenant_id: str):
        doc = KanbanCardRepository.buscar_por_id(card_id, tenant_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Card nao encontrado")
        return KanbanCardMapper.to_response(doc)

    @staticmethod
    def listar(tenant_id: str, filtros: dict):
        docs = KanbanCardRepository.listar(tenant_id, filtros)
        return KanbanCardMapper.to_list_response(docs)

    @staticmethod
    def atualizar(card_id: str, dto, tenant_id: str, user_id: str):
        fields = KanbanCardFactory.to_update_fields(dto)
        if not fields:
            raise HTTPException(status_code=400, detail="Nenhum campo para atualizar")
        updated = KanbanCardRepository.atualizar(card_id, tenant_id, fields)
        if not updated:
            raise HTTPException(status_code=404, detail="Card nao encontrado")

        # Audit log para cada campo editado
        for campo, valor in fields.items():
            if campo == "updated_at":
                continue
            KanbanActivityService.registrar(
                tenant_id=tenant_id,
                card_id=card_id,
                user_id=user_id,
                action="field_edited",
                metadata={"field_name": campo, "new_value": str(valor)},
            )

        return KanbanCardMapper.to_response(updated)

    @staticmethod
    def mover_manual(card_id: str, dto, tenant_id: str, user_id: str):
        """Movimentacao manual — RN-019: so para Cancelado."""
        card = KanbanCardRepository.buscar_por_id(card_id, tenant_id)
        if not card:
            raise HTTPException(status_code=404, detail="Card nao encontrado")
        KanbanBoardFactory.validar_coluna_destino(dto.column_id, card["column_id"])
        from_col = card["column_id"]
        moved = KanbanCardRepository.mover(card_id, tenant_id, dto.column_id)

        KanbanActivityService.registrar(
            tenant_id=tenant_id,
            card_id=card_id,
            user_id=user_id,
            action="column_changed",
            metadata={"from_column": from_col, "to_column": dto.column_id},
        )

        # Notificar responsaveis
        for uid in card.get("assigned_user_ids", []):
            KanbanNotificationService.notificar(
                tenant_id=tenant_id,
                user_id=uid,
                card_id=card_id,
                type_="column_changed",
                message=f"Card '{card['title']}' moveu para {dto.column_id}",
            )

        return KanbanCardMapper.to_response(moved)

    @staticmethod
    def mover_pipeline(card_id: str, column_destino: str, tenant_id: str):
        """Movimentacao automatica via pipeline (sem restricao manual)."""
        card = KanbanCardRepository.buscar_por_id(card_id, tenant_id)
        if not card:
            return None
        KanbanBoardFactory.validar_movimentacao_pipeline(column_destino)
        from_col = card["column_id"]
        moved = KanbanCardRepository.mover(card_id, tenant_id, column_destino)

        KanbanActivityService.registrar(
            tenant_id=tenant_id,
            card_id=card_id,
            user_id="sistema",
            action="column_changed",
            metadata={"from_column": from_col, "to_column": column_destino},
        )

        for uid in card.get("assigned_user_ids", []):
            KanbanNotificationService.notificar(
                tenant_id=tenant_id,
                user_id=uid,
                card_id=card_id,
                type_="column_changed",
                message=f"Card '{card['title']}' moveu automaticamente para {column_destino}",
            )

        return KanbanCardMapper.to_response(moved)

    @staticmethod
    def atribuir_responsaveis(card_id: str, dto, tenant_id: str, user_id: str):
        card = KanbanCardRepository.buscar_por_id(card_id, tenant_id)
        if not card:
            raise HTTPException(status_code=404, detail="Card nao encontrado")
        old_ids = set(card.get("assigned_user_ids", []))
        new_ids = set(dto.user_ids)
        updated = KanbanCardRepository.atribuir_responsaveis(card_id, tenant_id, dto.user_ids)

        KanbanActivityService.registrar(
            tenant_id=tenant_id,
            card_id=card_id,
            user_id=user_id,
            action="assignee_changed",
            metadata={"old": list(old_ids), "new": list(new_ids)},
        )

        # Notificar novos atribuidos
        for uid in new_ids - old_ids:
            KanbanNotificationService.notificar(
                tenant_id=tenant_id,
                user_id=uid,
                card_id=card_id,
                type_="assigned",
                message=f"Voce foi atribuido ao card '{card['title']}'",
            )

        return KanbanCardMapper.to_response(updated)

    @staticmethod
    def vincular_artefato(card_id: str, dto, tenant_id: str, user_id: str):
        fields = KanbanCardFactory.to_artefato_fields(dto)
        if not fields:
            raise HTTPException(status_code=400, detail="Nenhum artefato para vincular")
        updated = KanbanCardRepository.atualizar(card_id, tenant_id, fields)
        if not updated:
            raise HTTPException(status_code=404, detail="Card nao encontrado")

        KanbanActivityService.registrar(
            tenant_id=tenant_id,
            card_id=card_id,
            user_id=user_id,
            action="drive_linked" if "drive_link" in fields else "pdf_exported",
            metadata={k: v for k, v in fields.items() if k != "updated_at"},
        )

        return KanbanCardMapper.to_response(updated)
```

#### Router

```python
# routers/kanban_card.py
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional

from dtos.kanban_card.criar_card.request import CriarCardRequest
from dtos.kanban_card.criar_card.response import CardResponse
from dtos.kanban_card.atualizar_card.request import AtualizarCardRequest
from dtos.kanban_card.mover_card.request import MoverCardRequest
from dtos.kanban_card.listar_cards.response import ListarCardsResponse
from dtos.kanban_card.atribuir_responsaveis.request import AtribuirResponsaveisRequest
from dtos.kanban_card.vincular_artefato.request import VincularArtefatoRequest
from middleware.auth import get_current_user, require_role, CurrentUser
from services.kanban_card_service import KanbanCardService

router = APIRouter(prefix="/kanban/cards", tags=["Kanban Cards"])


@router.post("/", response_model=CardResponse, status_code=201)
async def criar_card(
    dto: CriarCardRequest,
    current_user: CurrentUser = Depends(require_role("admin", "copywriter")),
):
    return KanbanCardService.criar(
        dto,
        tenant_id=current_user.tenant_id,
        created_by=current_user.user_id,
    )


@router.get("/", response_model=ListarCardsResponse)
async def listar_cards(
    board_id: Optional[str] = Query(None),
    column_id: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    assigned_user_id: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: CurrentUser = Depends(get_current_user),
):
    filtros = {
        k: v for k, v in {
            "board_id": board_id,
            "column_id": column_id,
            "priority": priority,
            "assigned_user_id": assigned_user_id,
            "search": search,
        }.items() if v is not None
    }
    return KanbanCardService.listar(
        tenant_id=current_user.tenant_id,
        filtros=filtros,
    )


@router.get("/{card_id}", response_model=CardResponse)
async def buscar_card(
    card_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    return KanbanCardService.buscar(card_id, tenant_id=current_user.tenant_id)


@router.patch("/{card_id}", response_model=CardResponse)
async def atualizar_card(
    card_id: str,
    dto: AtualizarCardRequest,
    current_user: CurrentUser = Depends(
        require_role("admin", "copywriter", "designer", "reviewer")
    ),
):
    return KanbanCardService.atualizar(
        card_id, dto,
        tenant_id=current_user.tenant_id,
        user_id=current_user.user_id,
    )


@router.post("/{card_id}/mover", response_model=CardResponse)
async def mover_card(
    card_id: str,
    dto: MoverCardRequest,
    current_user: CurrentUser = Depends(
        require_role("admin", "copywriter", "designer", "reviewer")
    ),
):
    return KanbanCardService.mover_manual(
        card_id, dto,
        tenant_id=current_user.tenant_id,
        user_id=current_user.user_id,
    )


@router.patch("/{card_id}/responsaveis", response_model=CardResponse)
async def atribuir_responsaveis(
    card_id: str,
    dto: AtribuirResponsaveisRequest,
    current_user: CurrentUser = Depends(require_role("admin")),
):
    return KanbanCardService.atribuir_responsaveis(
        card_id, dto,
        tenant_id=current_user.tenant_id,
        user_id=current_user.user_id,
    )


@router.patch("/{card_id}/artefatos", response_model=CardResponse)
async def vincular_artefato(
    card_id: str,
    dto: VincularArtefatoRequest,
    current_user: CurrentUser = Depends(get_current_user),
):
    return KanbanCardService.vincular_artefato(
        card_id, dto,
        tenant_id=current_user.tenant_id,
        user_id=current_user.user_id,
    )
```

---

### 4.5 Dominio: kanban_comment

#### DTOs

```python
# dtos/kanban_comment/base.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ComentarioBase(BaseModel):
    text: str
    user_id: str
    user_name: str
    user_avatar_url: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
```

```python
# dtos/kanban_comment/criar_comentario/request.py
from pydantic import BaseModel, field_validator


class CriarComentarioRequest(BaseModel):
    text: str

    @field_validator("text")
    @classmethod
    def texto_nao_vazio(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Comentario nao pode ser vazio")
        return v.strip()
```

```python
# dtos/kanban_comment/criar_comentario/response.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ComentarioResponse(BaseModel):
    id: str
    card_id: str
    user_id: str
    user_name: str
    user_avatar_url: Optional[str] = None
    text: str
    created_at: datetime
    updated_at: Optional[datetime] = None
```

```python
# dtos/kanban_comment/listar_comentarios/response.py
from pydantic import BaseModel
from dtos.kanban_comment.criar_comentario.response import ComentarioResponse


class ListarComentariosResponse(BaseModel):
    comments: list[ComentarioResponse]
    total: int
```

```python
# dtos/kanban_comment/editar_comentario/request.py
from pydantic import BaseModel, field_validator


class EditarComentarioRequest(BaseModel):
    text: str

    @field_validator("text")
    @classmethod
    def texto_nao_vazio(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Comentario nao pode ser vazio")
        return v.strip()
```

#### Factory

```python
# factories/kanban_comment_factory.py
from datetime import datetime, timezone


class KanbanCommentFactory:

    @staticmethod
    def to_doc(dto, card_id: str, tenant_id: str, user_id: str) -> dict:
        """Cria documento MongoDB para kanban_comments."""
        return {
            "tenant_id": tenant_id,
            "card_id": card_id,
            "user_id": user_id,
            "text": dto.text.strip(),
            "parent_comment_id": None,  # thread pos-MVP
            "mentions": [],              # pos-MVP
            "created_at": datetime.now(timezone.utc),
            "updated_at": None,
            "deleted_at": None,
        }

    @staticmethod
    def validar_permissao_edicao(comment_doc: dict, user_id: str, user_role: str):
        """RN-005: so autor edita. Admin pode deletar (mas nao editar)."""
        if comment_doc["user_id"] != user_id:
            raise ValueError("Apenas o autor pode editar o comentario")

    @staticmethod
    def validar_permissao_exclusao(comment_doc: dict, user_id: str, user_role: str):
        """RN-005: autor ou Admin pode deletar."""
        if comment_doc["user_id"] != user_id and user_role != "admin":
            raise ValueError("Apenas o autor ou Admin pode deletar o comentario")
```

#### Mapper

```python
# mappers/kanban_comment_mapper.py
from dtos.kanban_comment.criar_comentario.response import ComentarioResponse
from dtos.kanban_comment.listar_comentarios.response import ListarComentariosResponse


class KanbanCommentMapper:

    @staticmethod
    def to_response(doc: dict, user_name: str = "", user_avatar_url: str = None) -> ComentarioResponse:
        return ComentarioResponse(
            id=str(doc["_id"]),
            card_id=doc["card_id"],
            user_id=doc["user_id"],
            user_name=user_name,
            user_avatar_url=user_avatar_url,
            text=doc["text"],
            created_at=doc["created_at"],
            updated_at=doc.get("updated_at"),
        )

    @staticmethod
    def to_list_response(docs: list[dict], users_map: dict) -> ListarComentariosResponse:
        """users_map: {user_id: {name, avatar_url}}"""
        comments = []
        for doc in docs:
            user_info = users_map.get(doc["user_id"], {})
            comments.append(KanbanCommentMapper.to_response(
                doc,
                user_name=user_info.get("name", "Desconhecido"),
                user_avatar_url=user_info.get("avatar_url"),
            ))
        return ListarComentariosResponse(comments=comments, total=len(comments))
```

#### Repository

```python
# data/repositories/mongo/kanban_comment_repository.py
from bson import ObjectId
from datetime import datetime, timezone
from data.connections.mongo_connection import get_mongo_db


class KanbanCommentRepository:

    @staticmethod
    def criar(doc: dict) -> dict:
        db = get_mongo_db()
        if db is None:
            raise RuntimeError("MongoDB nao configurado")
        result = db.kanban_comments.insert_one(doc)
        doc["_id"] = result.inserted_id
        return doc

    @staticmethod
    def listar_por_card(card_id: str, tenant_id: str) -> list[dict]:
        db = get_mongo_db()
        if db is None:
            return []
        return list(
            db.kanban_comments.find({
                "card_id": card_id,
                "tenant_id": tenant_id,
                "deleted_at": None,
            }).sort("created_at", 1)
        )

    @staticmethod
    def buscar_por_id(comment_id: str, tenant_id: str) -> dict | None:
        db = get_mongo_db()
        if db is None:
            return None
        return db.kanban_comments.find_one({
            "_id": ObjectId(comment_id),
            "tenant_id": tenant_id,
            "deleted_at": None,
        })

    @staticmethod
    def atualizar(comment_id: str, tenant_id: str, text: str) -> dict | None:
        db = get_mongo_db()
        if db is None:
            return None
        db.kanban_comments.update_one(
            {"_id": ObjectId(comment_id), "tenant_id": tenant_id},
            {"$set": {"text": text, "updated_at": datetime.now(timezone.utc)}},
        )
        return db.kanban_comments.find_one({"_id": ObjectId(comment_id)})

    @staticmethod
    def soft_delete(comment_id: str, tenant_id: str) -> bool:
        db = get_mongo_db()
        if db is None:
            return False
        result = db.kanban_comments.update_one(
            {"_id": ObjectId(comment_id), "tenant_id": tenant_id},
            {"$set": {"deleted_at": datetime.now(timezone.utc)}},
        )
        return result.modified_count > 0

    @staticmethod
    def contar_por_card(card_id: str, tenant_id: str) -> int:
        db = get_mongo_db()
        if db is None:
            return 0
        return db.kanban_comments.count_documents({
            "card_id": card_id,
            "tenant_id": tenant_id,
            "deleted_at": None,
        })
```

#### Service

```python
# services/kanban_comment_service.py
from fastapi import HTTPException
from factories.kanban_comment_factory import KanbanCommentFactory
from mappers.kanban_comment_mapper import KanbanCommentMapper
from data.repositories.mongo.kanban_comment_repository import KanbanCommentRepository
from data.repositories.mongo.auth_repository import AuthRepository
from services.kanban_activity_service import KanbanActivityService


class KanbanCommentService:
    """Orquestra comentarios. Camada opaca."""

    @staticmethod
    def criar(card_id: str, dto, tenant_id: str, user_id: str, user_name: str):
        doc = KanbanCommentFactory.to_doc(dto, card_id, tenant_id, user_id)
        saved = KanbanCommentRepository.criar(doc)

        KanbanActivityService.registrar(
            tenant_id=tenant_id,
            card_id=card_id,
            user_id=user_id,
            action="comment_added",
            metadata={"comment_id": str(saved["_id"])},
        )

        return KanbanCommentMapper.to_response(saved, user_name=user_name)

    @staticmethod
    def listar(card_id: str, tenant_id: str):
        docs = KanbanCommentRepository.listar_por_card(card_id, tenant_id)
        # Construir mapa de usuarios para enriquecer os comentarios
        user_ids = list({d["user_id"] for d in docs})
        users_map = {}
        for uid in user_ids:
            user = AuthRepository.buscar_por_id(uid, tenant_id)
            if user:
                users_map[uid] = {"name": user["name"], "avatar_url": user.get("avatar_url")}
        return KanbanCommentMapper.to_list_response(docs, users_map)

    @staticmethod
    def editar(comment_id: str, dto, tenant_id: str, user_id: str, user_role: str):
        comment = KanbanCommentRepository.buscar_por_id(comment_id, tenant_id)
        if not comment:
            raise HTTPException(status_code=404, detail="Comentario nao encontrado")
        try:
            KanbanCommentFactory.validar_permissao_edicao(comment, user_id, user_role)
        except ValueError as e:
            raise HTTPException(status_code=403, detail=str(e))
        updated = KanbanCommentRepository.atualizar(comment_id, tenant_id, dto.text)

        KanbanActivityService.registrar(
            tenant_id=tenant_id,
            card_id=comment["card_id"],
            user_id=user_id,
            action="comment_edited",
            metadata={"comment_id": comment_id},
        )

        user = AuthRepository.buscar_por_id(user_id, tenant_id)
        user_name = user["name"] if user else "Desconhecido"
        return KanbanCommentMapper.to_response(updated, user_name=user_name)

    @staticmethod
    def deletar(comment_id: str, tenant_id: str, user_id: str, user_role: str):
        comment = KanbanCommentRepository.buscar_por_id(comment_id, tenant_id)
        if not comment:
            raise HTTPException(status_code=404, detail="Comentario nao encontrado")
        try:
            KanbanCommentFactory.validar_permissao_exclusao(comment, user_id, user_role)
        except ValueError as e:
            raise HTTPException(status_code=403, detail=str(e))
        KanbanCommentRepository.soft_delete(comment_id, tenant_id)

        KanbanActivityService.registrar(
            tenant_id=tenant_id,
            card_id=comment["card_id"],
            user_id=user_id,
            action="comment_deleted",
            metadata={"comment_id": comment_id},
        )

        return {"detail": "Comentario deletado"}
```

#### Router

```python
# routers/kanban_comment.py
from fastapi import APIRouter, HTTPException, Depends

from dtos.kanban_comment.criar_comentario.request import CriarComentarioRequest
from dtos.kanban_comment.criar_comentario.response import ComentarioResponse
from dtos.kanban_comment.listar_comentarios.response import ListarComentariosResponse
from dtos.kanban_comment.editar_comentario.request import EditarComentarioRequest
from middleware.auth import get_current_user, require_role, CurrentUser
from services.kanban_comment_service import KanbanCommentService

router = APIRouter(tags=["Kanban Comentarios"])


@router.post(
    "/kanban/cards/{card_id}/comments",
    response_model=ComentarioResponse,
    status_code=201,
)
async def criar_comentario(
    card_id: str,
    dto: CriarComentarioRequest,
    current_user: CurrentUser = Depends(
        require_role("admin", "copywriter", "designer", "reviewer")
    ),
):
    return KanbanCommentService.criar(
        card_id, dto,
        tenant_id=current_user.tenant_id,
        user_id=current_user.user_id,
        user_name=current_user.name,
    )


@router.get(
    "/kanban/cards/{card_id}/comments",
    response_model=ListarComentariosResponse,
)
async def listar_comentarios(
    card_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    return KanbanCommentService.listar(card_id, tenant_id=current_user.tenant_id)


@router.patch("/kanban/comments/{comment_id}", response_model=ComentarioResponse)
async def editar_comentario(
    comment_id: str,
    dto: EditarComentarioRequest,
    current_user: CurrentUser = Depends(
        require_role("admin", "copywriter", "designer", "reviewer")
    ),
):
    return KanbanCommentService.editar(
        comment_id, dto,
        tenant_id=current_user.tenant_id,
        user_id=current_user.user_id,
        user_role=current_user.role,
    )


@router.delete("/kanban/comments/{comment_id}")
async def deletar_comentario(
    comment_id: str,
    current_user: CurrentUser = Depends(
        require_role("admin", "copywriter", "designer", "reviewer")
    ),
):
    return KanbanCommentService.deletar(
        comment_id,
        tenant_id=current_user.tenant_id,
        user_id=current_user.user_id,
        user_role=current_user.role,
    )
```

---

### 4.6 Dominio: kanban_activity

#### DTOs

```python
# dtos/kanban_activity/base.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AtividadeBase(BaseModel):
    action: str
    user_id: str
    user_name: str
    metadata: dict = {}
    created_at: datetime
```

```python
# dtos/kanban_activity/listar_atividades/response.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AtividadeResponse(BaseModel):
    id: str
    card_id: str
    user_id: str
    user_name: str
    action: str
    metadata: dict = {}
    created_at: datetime


class ListarAtividadesResponse(BaseModel):
    activities: list[AtividadeResponse]
    total: int
```

#### Factory

```python
# factories/kanban_activity_factory.py
from datetime import datetime, timezone


ACOES_VALIDAS = {
    "card_created",
    "column_changed",
    "assignee_changed",
    "field_edited",
    "comment_added",
    "comment_edited",
    "comment_deleted",
    "image_generated",
    "drive_linked",
    "pdf_exported",
}


class KanbanActivityFactory:

    @staticmethod
    def to_doc(tenant_id: str, card_id: str, user_id: str, action: str, metadata: dict = {}) -> dict:
        """Cria documento MongoDB para kanban_activity_log. Append-only (RN-013)."""
        if action not in ACOES_VALIDAS:
            raise ValueError(f"Acao invalida: {action}")
        return {
            "tenant_id": tenant_id,
            "card_id": card_id,
            "user_id": user_id,
            "action": action,
            "metadata": metadata or {},
            "created_at": datetime.now(timezone.utc),
        }
```

#### Mapper

```python
# mappers/kanban_activity_mapper.py
from dtos.kanban_activity.listar_atividades.response import (
    AtividadeResponse,
    ListarAtividadesResponse,
)


class KanbanActivityMapper:

    @staticmethod
    def to_response(doc: dict, user_name: str = "") -> AtividadeResponse:
        return AtividadeResponse(
            id=str(doc["_id"]),
            card_id=doc["card_id"],
            user_id=doc["user_id"],
            user_name=user_name,
            action=doc["action"],
            metadata=doc.get("metadata", {}),
            created_at=doc["created_at"],
        )

    @staticmethod
    def to_list_response(docs: list[dict], users_map: dict) -> ListarAtividadesResponse:
        activities = []
        for doc in docs:
            user_info = users_map.get(doc["user_id"], {})
            name = user_info.get("name", "Sistema") if doc["user_id"] != "sistema" else "Sistema"
            activities.append(KanbanActivityMapper.to_response(doc, user_name=name))
        return ListarAtividadesResponse(activities=activities, total=len(activities))
```

#### Repository

```python
# data/repositories/mongo/kanban_activity_repository.py
from data.connections.mongo_connection import get_mongo_db


class KanbanActivityRepository:
    """Append-only. Nunca edita ou deleta (RN-013)."""

    @staticmethod
    def criar(doc: dict) -> dict:
        db = get_mongo_db()
        if db is None:
            raise RuntimeError("MongoDB nao configurado")
        result = db.kanban_activity_log.insert_one(doc)
        doc["_id"] = result.inserted_id
        return doc

    @staticmethod
    def listar_por_card(card_id: str, tenant_id: str, limit: int = 50, skip: int = 0) -> list[dict]:
        db = get_mongo_db()
        if db is None:
            return []
        return list(
            db.kanban_activity_log.find({
                "card_id": card_id,
                "tenant_id": tenant_id,
            }).sort("created_at", -1).skip(skip).limit(limit)
        )
```

#### Service

```python
# services/kanban_activity_service.py
from factories.kanban_activity_factory import KanbanActivityFactory
from mappers.kanban_activity_mapper import KanbanActivityMapper
from data.repositories.mongo.kanban_activity_repository import KanbanActivityRepository
from data.repositories.mongo.auth_repository import AuthRepository


class KanbanActivityService:
    """Orquestra audit log. Camada opaca."""

    @staticmethod
    def registrar(tenant_id: str, card_id: str, user_id: str, action: str, metadata: dict = {}):
        """Registra acao no audit log. Chamado por outros services."""
        doc = KanbanActivityFactory.to_doc(tenant_id, card_id, user_id, action, metadata)
        KanbanActivityRepository.criar(doc)

    @staticmethod
    def listar(card_id: str, tenant_id: str, limit: int = 50, skip: int = 0):
        docs = KanbanActivityRepository.listar_por_card(card_id, tenant_id, limit, skip)
        user_ids = list({d["user_id"] for d in docs if d["user_id"] != "sistema"})
        users_map = {}
        for uid in user_ids:
            user = AuthRepository.buscar_por_id(uid, tenant_id)
            if user:
                users_map[uid] = {"name": user["name"], "avatar_url": user.get("avatar_url")}
        return KanbanActivityMapper.to_list_response(docs, users_map)
```

Router do activity e aninhado no router de cards (GET /api/kanban/cards/{card_id}/activity), definido abaixo.

---

### 4.7 Dominio: kanban_notification

#### DTOs

```python
# dtos/kanban_notification/base.py
from pydantic import BaseModel
from datetime import datetime


class NotificacaoBase(BaseModel):
    type: str  # assigned, column_changed
    message: str
    card_id: str
    is_read: bool
    created_at: datetime
```

```python
# dtos/kanban_notification/listar_notificacoes/response.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class NotificacaoResponse(BaseModel):
    id: str
    card_id: str
    type: str
    message: str
    is_read: bool
    created_at: datetime


class ListarNotificacoesResponse(BaseModel):
    notifications: list[NotificacaoResponse]
    total: int
```

```python
# dtos/kanban_notification/contar_nao_lidas/response.py
from pydantic import BaseModel


class ContadorNaoLidasResponse(BaseModel):
    count: int
```

#### Factory

```python
# factories/kanban_notification_factory.py
from datetime import datetime, timezone


TIPOS_VALIDOS = {"assigned", "mentioned", "column_changed"}


class KanbanNotificationFactory:

    @staticmethod
    def to_doc(tenant_id: str, user_id: str, card_id: str, type_: str, message: str) -> dict:
        if type_ not in TIPOS_VALIDOS:
            raise ValueError(f"Tipo de notificacao invalido: {type_}")
        return {
            "tenant_id": tenant_id,
            "user_id": user_id,
            "card_id": card_id,
            "type": type_,
            "message": message,
            "is_read": False,
            "created_at": datetime.now(timezone.utc),
        }
```

#### Mapper

```python
# mappers/kanban_notification_mapper.py
from dtos.kanban_notification.listar_notificacoes.response import (
    NotificacaoResponse,
    ListarNotificacoesResponse,
)
from dtos.kanban_notification.contar_nao_lidas.response import ContadorNaoLidasResponse


class KanbanNotificationMapper:

    @staticmethod
    def to_response(doc: dict) -> NotificacaoResponse:
        return NotificacaoResponse(
            id=str(doc["_id"]),
            card_id=doc["card_id"],
            type=doc["type"],
            message=doc["message"],
            is_read=doc["is_read"],
            created_at=doc["created_at"],
        )

    @staticmethod
    def to_list_response(docs: list[dict]) -> ListarNotificacoesResponse:
        return ListarNotificacoesResponse(
            notifications=[KanbanNotificationMapper.to_response(d) for d in docs],
            total=len(docs),
        )

    @staticmethod
    def to_contador_response(count: int) -> ContadorNaoLidasResponse:
        return ContadorNaoLidasResponse(count=count)
```

#### Repository

```python
# data/repositories/mongo/kanban_notification_repository.py
from bson import ObjectId
from datetime import datetime, timezone
from data.connections.mongo_connection import get_mongo_db


class KanbanNotificationRepository:

    @staticmethod
    def criar(doc: dict) -> dict:
        db = get_mongo_db()
        if db is None:
            raise RuntimeError("MongoDB nao configurado")
        result = db.kanban_notifications.insert_one(doc)
        doc["_id"] = result.inserted_id
        return doc

    @staticmethod
    def listar(user_id: str, tenant_id: str, limit: int = 20) -> list[dict]:
        db = get_mongo_db()
        if db is None:
            return []
        return list(
            db.kanban_notifications.find({
                "user_id": user_id,
                "tenant_id": tenant_id,
            }).sort("created_at", -1).limit(limit)
        )

    @staticmethod
    def contar_nao_lidas(user_id: str, tenant_id: str) -> int:
        db = get_mongo_db()
        if db is None:
            return 0
        return db.kanban_notifications.count_documents({
            "user_id": user_id,
            "tenant_id": tenant_id,
            "is_read": False,
        })

    @staticmethod
    def marcar_como_lida(notification_id: str, tenant_id: str) -> bool:
        db = get_mongo_db()
        if db is None:
            return False
        result = db.kanban_notifications.update_one(
            {"_id": ObjectId(notification_id), "tenant_id": tenant_id},
            {"$set": {"is_read": True}},
        )
        return result.modified_count > 0

    @staticmethod
    def marcar_todas_lidas(user_id: str, tenant_id: str) -> int:
        db = get_mongo_db()
        if db is None:
            return 0
        result = db.kanban_notifications.update_many(
            {"user_id": user_id, "tenant_id": tenant_id, "is_read": False},
            {"$set": {"is_read": True}},
        )
        return result.modified_count
```

#### Service

```python
# services/kanban_notification_service.py
from factories.kanban_notification_factory import KanbanNotificationFactory
from mappers.kanban_notification_mapper import KanbanNotificationMapper
from data.repositories.mongo.kanban_notification_repository import KanbanNotificationRepository


class KanbanNotificationService:
    """Orquestra notificacoes. Camada opaca."""

    @staticmethod
    def notificar(tenant_id: str, user_id: str, card_id: str, type_: str, message: str):
        """Cria notificacao. Chamado por outros services."""
        doc = KanbanNotificationFactory.to_doc(tenant_id, user_id, card_id, type_, message)
        KanbanNotificationRepository.criar(doc)

    @staticmethod
    def listar(user_id: str, tenant_id: str, limit: int = 20):
        docs = KanbanNotificationRepository.listar(user_id, tenant_id, limit)
        return KanbanNotificationMapper.to_list_response(docs)

    @staticmethod
    def contar_nao_lidas(user_id: str, tenant_id: str):
        count = KanbanNotificationRepository.contar_nao_lidas(user_id, tenant_id)
        return KanbanNotificationMapper.to_contador_response(count)

    @staticmethod
    def marcar_como_lida(notification_id: str, tenant_id: str):
        success = KanbanNotificationRepository.marcar_como_lida(notification_id, tenant_id)
        if not success:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Notificacao nao encontrada")
        return {"detail": "Marcada como lida"}

    @staticmethod
    def marcar_todas_lidas(user_id: str, tenant_id: str):
        count = KanbanNotificationRepository.marcar_todas_lidas(user_id, tenant_id)
        return {"detail": f"{count} notificacoes marcadas como lidas"}
```

#### Router

```python
# routers/kanban_notification.py
from fastapi import APIRouter, Depends, Query

from dtos.kanban_notification.listar_notificacoes.response import ListarNotificacoesResponse
from dtos.kanban_notification.contar_nao_lidas.response import ContadorNaoLidasResponse
from dtos.kanban_activity.listar_atividades.response import ListarAtividadesResponse
from middleware.auth import get_current_user, CurrentUser
from services.kanban_notification_service import KanbanNotificationService
from services.kanban_activity_service import KanbanActivityService

router = APIRouter(tags=["Kanban Notificacoes"])


# ---- Notificacoes ----

@router.get("/kanban/notifications", response_model=ListarNotificacoesResponse)
async def listar_notificacoes(
    current_user: CurrentUser = Depends(get_current_user),
):
    return KanbanNotificationService.listar(
        user_id=current_user.user_id,
        tenant_id=current_user.tenant_id,
    )


@router.get("/kanban/notifications/count", response_model=ContadorNaoLidasResponse)
async def contar_nao_lidas(
    current_user: CurrentUser = Depends(get_current_user),
):
    return KanbanNotificationService.contar_nao_lidas(
        user_id=current_user.user_id,
        tenant_id=current_user.tenant_id,
    )


@router.patch("/kanban/notifications/{notification_id}/read")
async def marcar_como_lida(
    notification_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    return KanbanNotificationService.marcar_como_lida(
        notification_id, tenant_id=current_user.tenant_id
    )


@router.post("/kanban/notifications/read-all")
async def marcar_todas_lidas(
    current_user: CurrentUser = Depends(get_current_user),
):
    return KanbanNotificationService.marcar_todas_lidas(
        user_id=current_user.user_id,
        tenant_id=current_user.tenant_id,
    )


# ---- Activity Log (aninhado em cards, mas registrado aqui por conveniencia) ----

@router.get("/kanban/cards/{card_id}/activity", response_model=ListarAtividadesResponse)
async def listar_atividades(
    card_id: str,
    limit: int = Query(50, le=200),
    skip: int = Query(0, ge=0),
    current_user: CurrentUser = Depends(get_current_user),
):
    return KanbanActivityService.listar(
        card_id, tenant_id=current_user.tenant_id, limit=limit, skip=skip
    )
```

---

## 5. Integracao com Pipeline Existente

O pipeline existente (conteudo/imagem/drive) precisa chamar o Kanban automaticamente. Pontos de integracao:

### 5.1 Gerar Conteudo --> Criar Card (RN-009)

Onde: `services/pipeline_service.py` ou `services/conteudo_service.py`, apos gerar conteudo com sucesso.

```python
# Inserir no final de PipelineService.criar() ou conteudo_service apos sucesso:
from services.kanban_card_service import KanbanCardService
from dtos.kanban_card.criar_card.request import CriarCardRequest

# Criar card automaticamente na coluna Copy
card_dto = CriarCardRequest(
    title=tema,  # titulo do carrossel
    copy_text=conteudo_gerado,  # texto gerado
    disciplina=disciplina,
    tecnologia=tecnologia,
    pipeline_id=pipeline_id,
    priority="media",
)
KanbanCardService.criar(
    card_dto,
    tenant_id=tenant_id,
    created_by="sistema",
)
```

### 5.2 Gerar Imagens --> Mover para Design (RN-010)

Onde: `services/imagem_service.py`, apos gerar imagens com sucesso.

```python
# Inserir apos geracao de imagens:
from services.kanban_card_service import KanbanCardService
from data.repositories.mongo.kanban_card_repository import KanbanCardRepository
from factories.kanban_board_factory import COLUNA_DESIGN

card = KanbanCardRepository.buscar_por_pipeline_id(pipeline_id, tenant_id)
if card:
    KanbanCardService.mover_pipeline(
        card_id=str(card["_id"]),
        column_destino=COLUNA_DESIGN,
        tenant_id=tenant_id,
    )
```

### 5.3 Exportar PDF --> Mover para Revisao

```python
from factories.kanban_board_factory import COLUNA_REVISAO

card = KanbanCardRepository.buscar_por_pipeline_id(pipeline_id, tenant_id)
if card:
    KanbanCardService.mover_pipeline(
        card_id=str(card["_id"]),
        column_destino=COLUNA_REVISAO,
        tenant_id=tenant_id,
    )
```

### 5.4 Salvar Google Drive --> Vincular Link (RN-011)

Onde: `services/drive_service.py`, apos salvar no Drive.

```python
from services.kanban_card_service import KanbanCardService
from dtos.kanban_card.vincular_artefato.request import VincularArtefatoRequest

card = KanbanCardRepository.buscar_por_pipeline_id(pipeline_id, tenant_id)
if card:
    artefato_dto = VincularArtefatoRequest(
        drive_link=drive_link,
        drive_folder_name=folder_name,
    )
    KanbanCardService.vincular_artefato(
        card_id=str(card["_id"]),
        dto=artefato_dto,
        tenant_id=tenant_id,
        user_id="sistema",
    )
```

---

## 6. Registro de Routers no main.py

```python
# Adicionar ao main.py:
from routers import auth, kanban_board, kanban_card, kanban_comment, kanban_notification

app.include_router(auth.router, prefix="/api")
app.include_router(kanban_board.router, prefix="/api")
app.include_router(kanban_card.router, prefix="/api")
app.include_router(kanban_comment.router, prefix="/api")
app.include_router(kanban_notification.router, prefix="/api")
```

---

## 7. Variaveis de Ambiente Novas

Adicionar ao `config.py` (Settings):

```python
JWT_SECRET_KEY: str = "changeme-in-production"
GOOGLE_OAUTH_CLIENT_ID: str = ""
GOOGLE_OAUTH_CLIENT_SECRET: str = ""
MICROSOFT_OAUTH_CLIENT_ID: str = ""
MICROSOFT_OAUTH_CLIENT_SECRET: str = ""
MICROSOFT_OAUTH_TENANT_ID: str = ""
```

Adicionar ao `.env`:

```
JWT_SECRET_KEY=<gerar com: python -c "import secrets; print(secrets.token_hex(32))">
GOOGLE_OAUTH_CLIENT_ID=
GOOGLE_OAUTH_CLIENT_SECRET=
MICROSOFT_OAUTH_CLIENT_ID=
MICROSOFT_OAUTH_CLIENT_SECRET=
MICROSOFT_OAUTH_TENANT_ID=
```

---

## 8. Dependencias Novas (requirements.txt)

```
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
httpx>=0.27.0
```

- `python-jose`: encode/decode JWT
- `passlib[bcrypt]`: hash de senhas
- `httpx`: chamadas HTTP para OAuth2 callbacks (Google/Microsoft)

---

## 9. Indices MongoDB

Criar ao inicializar o sistema (script ou startup):

```python
# scripts/create_indexes.py
from data.connections.mongo_connection import get_mongo_db

def criar_indices():
    db = get_mongo_db()
    if db is None:
        return

    db.kanban_users.create_index(
        [("tenant_id", 1), ("email", 1)], unique=True
    )
    db.kanban_cards.create_index(
        [("tenant_id", 1), ("board_id", 1), ("column_id", 1)]
    )
    db.kanban_cards.create_index(
        [("tenant_id", 1), ("assigned_user_ids", 1)]
    )
    db.kanban_cards.create_index(
        [("tenant_id", 1), ("pipeline_id", 1)]
    )
    db.kanban_activity_log.create_index(
        [("tenant_id", 1), ("card_id", 1), ("created_at", -1)]
    )
    db.kanban_comments.create_index(
        [("tenant_id", 1), ("card_id", 1), ("created_at", 1)]
    )
    db.kanban_notifications.create_index(
        [("tenant_id", 1), ("user_id", 1), ("is_read", 1)]
    )
    db.kanban_invites.create_index(
        [("token", 1)], unique=True
    )
```

---

## 10. Tabela Consolidada de Endpoints

| Metodo | Rota | Auth | Role Minimo | Descricao |
|--------|------|------|-------------|-----------|
| POST | /api/auth/login | N | -- | Login email+senha |
| POST | /api/auth/google | N | -- | Login SSO Google |
| POST | /api/auth/microsoft | N | -- | Login SSO Microsoft |
| POST | /api/auth/users | S | admin | Criar usuario |
| POST | /api/auth/users/invite | S | admin | Gerar convite |
| POST | /api/auth/users/invite/accept | N | -- | Aceitar convite |
| GET | /api/auth/users | S | admin | Listar usuarios |
| GET | /api/auth/users/{id} | S | any | Buscar usuario |
| PATCH | /api/auth/users/{id} | S | admin | Editar usuario |
| DELETE | /api/auth/users/{id} | S | admin | Desativar usuario |
| POST | /api/auth/users/{id}/reativar | S | admin | Reativar usuario |
| GET | /api/auth/me | S | any | Dados do logado |
| GET | /api/kanban/boards/default | S | any | Board padrao |
| GET | /api/kanban/boards/{id} | S | any | Board por ID |
| POST | /api/kanban/cards | S | admin, copywriter | Criar card |
| GET | /api/kanban/cards | S | any | Listar cards (filtros) |
| GET | /api/kanban/cards/{id} | S | any | Detalhe card |
| PATCH | /api/kanban/cards/{id} | S | admin, copy, design, review | Editar card |
| POST | /api/kanban/cards/{id}/mover | S | admin, copy, design, review | Mover card (so Cancelado) |
| PATCH | /api/kanban/cards/{id}/responsaveis | S | admin | Atribuir responsaveis |
| PATCH | /api/kanban/cards/{id}/artefatos | S | any | Vincular PDF/Drive |
| POST | /api/kanban/cards/{id}/comments | S | admin, copy, design, review | Criar comentario |
| GET | /api/kanban/cards/{id}/comments | S | any | Listar comentarios |
| PATCH | /api/kanban/comments/{id} | S | autor | Editar comentario |
| DELETE | /api/kanban/comments/{id} | S | autor ou admin | Deletar comentario |
| GET | /api/kanban/cards/{id}/activity | S | any | Timeline audit log |
| GET | /api/kanban/notifications | S | any | Minhas notificacoes |
| GET | /api/kanban/notifications/count | S | any | Contador nao-lidas |
| PATCH | /api/kanban/notifications/{id}/read | S | any | Marcar 1 como lida |
| POST | /api/kanban/notifications/read-all | S | any | Marcar todas lidas |

---

## 11. Regras de Negocio por Camada

### Na Factory (onde vivem as regras)

| Factory | Regra | PRD |
|---------|-------|-----|
| AuthFactory | Senha forte: 8+ chars, maiuscula, numero, especial | RN-021 |
| AuthFactory | Role valido: admin/copywriter/designer/reviewer/viewer | RN-008 |
| AuthFactory | InviteToken: token_urlsafe(32), expira 48h | DT-001 |
| KanbanBoardFactory | Colunas MVP fixas, IDs constantes | RN-020 |
| KanbanBoardFactory | Movimentacao manual so para Cancelado | RN-019 |
| KanbanBoardFactory | Colunas terminais nao movem | RN-007 |
| KanbanCardFactory | Prioridade aceita: alta/media/baixa. Default: media | RN-014 |
| KanbanCardFactory | Card sempre inicia na coluna Copy | RN-001 |
| KanbanCommentFactory | Edicao: so autor | RN-005 |
| KanbanCommentFactory | Exclusao: autor ou Admin | RN-005 |
| KanbanActivityFactory | Acoes validas (enum restrito) | RN-013 |

### Nas camadas opacas (Service/Router) = ZERO regras

Service e Router nao conhecem campos, nao validam, nao decidem. Delegam para Factory (regras) e Mapper (conversao).

---

## 12. Duvidas Tecnicas Finais

| ID | Duvida | Impacto |
|----|--------|---------|
| DT-B01 | SSO Google/Microsoft: os Client IDs e Secrets ja foram criados nos consoles Google/Microsoft? | Bloqueia implementacao de `POST /api/auth/google` e `/microsoft`. Os endpoints estao com `501 Not Implemented` como placeholder. |
| DT-B02 | O `tenant_id` atual e fixo em `config.py` (`TENANT_ID = "itvalley"`). Com multiusuario, cada usuario tera tenant_id no JWT. O tenant_id do login inicial (primeiro Admin) precisa ser definido: sera criado por seed/script ou autogerado no primeiro registro? | Afeta bootstrap do sistema. Sugestao: seed script que cria o primeiro Admin + tenant. |
| DT-B03 | Rate limiting do login (5/min) e por IP (atual). Com SSO, o rate limit aplica so ao email+senha ou tambem ao SSO? | Sugestao: so email+senha (SSO tem rate limit no provedor). |
| DT-B04 | Cards cancelados ocultos apos 7 dias (DT-006): implementar via query filter no repository ou via job periodico de archival? | Sugestao: query filter (archived_at preenchido por job noturno, ou filtro por created_at no column Cancelado). |
