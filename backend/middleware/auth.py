"""JWT authentication middleware para o Kanban.

Responsabilidades:
- hash_password / verify_password (bcrypt)
- create_access_token (python-jose)
- get_current_user dependency (decodifica JWT → CurrentUser)
- require_role dependency factory (checa role por rota)
"""

import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "kanban-dev-secret-change-me")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = 24

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
_bearer_scheme = HTTPBearer()


# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------
def hash_password(password: str) -> str:
    """Gera hash bcrypt da senha."""
    return _pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    """Verifica senha contra hash bcrypt."""
    return _pwd_context.verify(password, hashed)


# ---------------------------------------------------------------------------
# JWT
# ---------------------------------------------------------------------------
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Cria JWT com payload data + exp."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(hours=JWT_EXPIRE_HOURS))
    to_encode["exp"] = expire
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


# ---------------------------------------------------------------------------
# CurrentUser dataclass
# ---------------------------------------------------------------------------
@dataclass
class CurrentUser:
    user_id: str
    tenant_id: str
    role: str
    email: str
    name: str


# ---------------------------------------------------------------------------
# Dependencies
# ---------------------------------------------------------------------------
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
) -> CurrentUser:
    """Dependency que decodifica JWT e retorna CurrentUser.

    Espera header: Authorization: Bearer <token>
    """
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id: str | None = payload.get("user_id")
        tenant_id: str | None = payload.get("tenant_id")
        role: str | None = payload.get("role")
        email: str | None = payload.get("email")
        name: str | None = payload.get("name")

        if not all([user_id, tenant_id, role, email]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalido: campos obrigatorios ausentes",
            )

        return CurrentUser(
            user_id=user_id,
            tenant_id=tenant_id,
            role=role,
            email=email,
            name=name or "",
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido ou expirado",
        )


def require_role(*allowed_roles: str):
    """Dependency factory que checa se o usuario tem um dos roles permitidos.

    Uso:
        @router.post("/users", dependencies=[Depends(require_role("admin"))])
        async def criar_usuario(...): ...

    Ou como param:
        current_user: CurrentUser = Depends(require_role("admin", "copywriter"))
    """

    def _check(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acesso negado. Roles permitidos: {', '.join(allowed_roles)}",
            )
        return current_user

    return _check
