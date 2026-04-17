# RELATORIO DE CONFORMIDADE ARQUITETURAL - Kanban Pipeline

**Data:** 2026-04-14
**Agente:** 15 - Guardiao de Arquitetura
**Modulo:** Kanban Pipeline (Auth + Board + Card + Comments + Activity + Notifications)
**Status Geral:** REPROVADO

---

## VIOLACOES ENCONTRADAS

### BACKEND

#### BLOCKER-001: Service acessa campos do DTO diretamente
**Severidade:** BLOQUEANTE
**Arquivo:** `backend/services/auth_service.py`
**Linhas:** 31, 34, 64, 85, 94, 112, 120, 130

O `AuthService` acessa campos do DTO diretamente em multiplos metodos, violando a regra fundamental de que Service e camada opaca e NUNCA conhece campos do DTO.

Trechos:
- Linha 31: `dto.email` no metodo `login()`
- Linha 34: `dto.email, dto.password` passados para Factory
- Linha 64: `dto.email` no metodo `criar_usuario()`
- Linha 85: `dto.email` no metodo `convidar_usuario()`
- Linha 94: `dto.email` no metodo `convidar_usuario()`
- Linha 112: `dto.token` no metodo `aceitar_convite()`
- Linha 120: `dto.password` no metodo `aceitar_convite()`
- Linha 130: `dto.token` no metodo `aceitar_convite()`

**Correcao exigida:** O Service deve delegar TODA manipulacao de campos para a Factory. Exemplos:
- `login()`: Factory deve receber o DTO inteiro e extrair email/password internamente
- `criar_usuario()`: Factory deve validar email duplicado (recebendo tenant_id e DTO, usando Repository via interface)
- `aceitar_convite()`: Factory deve receber o DTO e extrair token/password
- Alternativa minima: Factory deve expor metodos de extracao como `AuthFactory.extract_email(dto)`, `AuthFactory.extract_credentials(dto)` para manter o Service opaco

#### BLOCKER-002: Service acessa banco sem interface (Repository concreto)
**Severidade:** BLOQUEANTE
**Arquivo:** `backend/services/auth_service.py`
**Linhas:** 4-5

O Service importa diretamente as classes concretas `AuthRepository` e `InviteRepository`:
```python
from data.repositories.mongo.auth_repository import AuthRepository
from data.repositories.mongo.invite_repository import InviteRepository
```

**Correcao exigida:** Service deve receber `BaseRepository` via interface, nunca instanciar o concreto diretamente. Criar interfaces `AuthRepositoryInterface` e `InviteRepositoryInterface` em `data/interfaces/`.

#### BLOCKER-003: Ausencia de coluna "Revisao" no board mock (RN-020)
**Severidade:** BLOQUEANTE
**Arquivo:** `frontend/src/lib/mocks/kanban/board.mock.ts`
**Linha:** 8-14

O PRD (RN-020) define 6 colunas fixas: Copy, Design, Revisao, Aprovado, Publicado, Cancelado.
O board mock tem apenas 5 colunas e a coluna "Design" foi renomeada para "Diretor de Arte". Falta a coluna "Revisao".

**Correcao exigida:** Adicionar coluna `{ id: 'col-revisao', name: 'Revisao', order: 3, color: '...' }` e renomear "Diretor de Arte" de volta para "Design".

#### BLOCKER-004: Movimentacao manual para "Publicado" viola RN-019
**Severidade:** BLOQUEANTE
**Arquivo:** `frontend/src/lib/components/kanban/KanbanBoard.svelte`
**Linha:** 22

O componente permite drop (movimentacao manual) tanto para Cancelado quanto para Publicado:
```
isDropTarget={column.id === 'col-cancelado' || column.id === 'col-publicado'}
```

O PRD (RN-019) define que a UNICA movimentacao MANUAL permitida e para "Cancelado". Movimentacao para "Publicado" deve ser automatica via pipeline.

**Correcao exigida:** Remover `|| column.id === 'col-publicado'` do KanbanBoard.svelte. Publicado so deve ser alcancado via integracao automatica com pipeline.

---

### WARNING-001: login mock aceita qualquer email com senha fixa
**Severidade:** MEDIA
**Arquivo:** `frontend/src/lib/mocks/kanban/users.mock.ts`
**Linhas:** 67-87

O `loginMock` aceita qualquer email (inclusive nao cadastrado) e usa `usersMock[0]` como fallback. Deveria retornar erro para emails nao encontrados, simulando comportamento real.

### WARNING-002: Repositorios frontend sem token de autenticacao
**Severidade:** ALTA
**Arquivo:** `frontend/src/lib/repositories/BoardRepository.ts`, `CardRepository.ts`, `CommentRepository.ts`, `ActivityRepository.ts`, `NotificationRepository.ts`

Os repositorios Board, Card, Comment, Activity e Notification fazem fetch SEM enviar o header `Authorization: Bearer`. Somente `AuthRepository.ts` e `UserRepository.ts` enviam o token JWT.

**Correcao exigida:** Todos os repositorios de rotas protegidas devem incluir `Authorization: Bearer <token>` no header.

### WARNING-003: Falta data-testid nos componentes Kanban
**Severidade:** MEDIA
**Arquivos:** `frontend/src/lib/components/kanban/KanbanBoard.svelte`, `KanbanColumn.svelte`, `KanbanCard.svelte`, `CardDetailModal.svelte`, `CardCreateModal.svelte`

Os componentes do dominio Kanban nao possuem `data-testid` nos elementos interativos (botoes de drag, cards, colunas, tabs). Os componentes Auth e User tem `data-testid` corretamente.

**Correcao exigida:** Adicionar `data-testid` em: cards (`data-testid="card-{id}"`), colunas, botao criar, tabs do modal, botao fechar.

### WARNING-004: notifications.svelte.ts usa cast inseguro
**Severidade:** BAIXA
**Arquivo:** `frontend/src/lib/stores/notifications.svelte.ts`
**Linhas:** 16-17, 22-24

Usa `as unknown as NotificationDTO` para fazer spread de DTOs imutaveis. Isso quebra a imutabilidade do readonly e cria objetos que nao sao instancias reais de NotificationDTO (sem metodos).

**Correcao exigida:** Criar nova instancia via `new NotificationDTO({...n, is_read: true})` em vez de cast.

### WARNING-005: kanban.svelte.ts acessa campos do DTO diretamente nos filtros
**Severidade:** MEDIA
**Arquivo:** `frontend/src/lib/stores/kanban.svelte.ts`
**Linhas:** 65, 70, 74, 78

O store acessa `c.title`, `c.assigned_user_ids`, `c.priority`, `c.column_id` diretamente nos filtros. No padrao IT Valley, stores podem acessar getters/metodos publicos do DTO, mas os campos sao `readonly` entao e aceitavel. Porem, seria mais consistente se o CardDTO expusesse metodos de filtragem.

**Nota:** Aceito como WARNING pois stores sao a UI (fabrica de DTOs), e o acesso e via readonly fields.

### WARNING-006: CardDTO e BoardDTO tem campos extras nao definidos no PRD
**Severidade:** BAIXA
**Arquivo:** `frontend/src/lib/dtos/CardDTO.ts`
**Linhas:** 17, 26-27

Os campos `formato` (CardFormato) e `deadline` nao estao no modelo de dados do PRD (secao 10). Sao extensoes que podem causar inconsistencia com o backend.

**Nota:** Aceito como extensao se documentado. Deadline esta listado como fora do MVP (DA-006).

---

## CONFORMIDADE VERIFICADA (OK)

### Backend - OK
- [x] DTOs organizados em `dtos/auth/[caso_de_uso]/request.py` e `response.py`
- [x] NAO existe pasta `schemas/`
- [x] NAO existe pasta `app/` no backend
- [x] Factory presente em `factories/auth_factory.py` com regras de negocio
- [x] Mapper presente em `mappers/auth_mapper.py` (so conversao, sem validacao)
- [x] Repository NAO chama `commit()` (pymongo auto-commit)
- [x] Repository NAO contem regra de negocio
- [x] tenant_id em TODA query do AuthRepository
- [x] JWT aplicado em rotas protegidas (via `get_current_user` e `require_role`)
- [x] Rate limiting na rota de login (5/minuto) - RN seguranca
- [x] Senha forte validada no DTO (RN-021)
- [x] JWT expira em 24h (RN-018)
- [x] Router sem regra de negocio (so recebe DTO e delega para Service)
- [x] Imports explicitos, sem barrel exports (\_\_init\_\_.py vazios)
- [x] `base.py` compartilhado no dominio auth

### Frontend DTOs - OK
- [x] Todos os DTOs tem `readonly` em todos os campos
- [x] Todos os DTOs tem `constructor(data: Record<string, any>)`
- [x] Todos os DTOs tem `isValid()` e `toPayload()`
- [x] AuthDTO, LoginRequestDTO, CardDTO, BoardDTO, UserDTO, CriarUsuarioDTO, CriarCardDTO, CommentDTO, ActivityDTO, NotificationDTO, EditarUsuarioDTO - todos conformes

### Frontend Services - OK
- [x] Todos usam metodos `static`
- [x] NENHUM Service acessa campos do DTO diretamente (usam `isValid()`, `toPayload()`, `getUserId()`)
- [x] Services chamam Repository, nunca fazem fetch

### Frontend Repositories - OK
- [x] Todos alternam mock/real via `VITE_USE_MOCK`
- [x] Repositories criam o DTO (`new AuthDTO(data)`, `new CardDTO(data)`, etc.)
- [x] Mocks simulam delay de rede
- [x] Mocks NAO sao importados direto pelo componente

### Frontend Mocks - OK
- [x] Nomes brasileiros realistas (Poliana Cardoso, Joao Mendes, Ana Beatriz Silva, Carlos Viana, Maria Fernanda Costa)
- [x] Variedade de cenarios (cards em todas as colunas, prioridades variadas, com/sem deadline, com/sem drive link, cancelado)
- [x] 5 usuarios com todos os 5 roles diferentes

### Frontend Componentes - OK
- [x] Organizados por dominio (kanban/, auth/, user/)
- [x] NAO existe atoms/, molecules/, organisms/, shared/
- [x] Props tipadas com `$props()`
- [x] Logica derivada com `$derived()`
- [x] Sem logica de negocio no componente
- [x] Imports diretos dos arquivos
- [x] auth/ e user/ tem data-testid nos elementos interativos

### Frontend Stores - OK
- [x] Separacao correta: auth.svelte.ts, kanban.svelte.ts, notifications.svelte.ts
- [x] Persistencia JWT no localStorage com `toPayload()`
- [x] Validacao de sessao via `isValid()`

---

## RESUMO DE ACOES

| # | Violacao | Severidade | Status |
|---|----------|-----------|--------|
| BLOCKER-001 | Service acessa campos do DTO | BLOQUEANTE | Correcao obrigatoria |
| BLOCKER-002 | Service importa Repository concreto | BLOQUEANTE | Correcao obrigatoria |
| BLOCKER-003 | Falta coluna Revisao no board mock | BLOQUEANTE | Correcao obrigatoria |
| BLOCKER-004 | Drop manual em Publicado viola RN-019 | BLOQUEANTE | Correcao obrigatoria |
| WARNING-001 | Mock login aceita qualquer email | MEDIA | Correcao recomendada |
| WARNING-002 | Repos frontend sem token JWT | ALTA | Correcao obrigatoria antes de QA |
| WARNING-003 | Falta data-testid nos componentes Kanban | MEDIA | Correcao antes de E2E |
| WARNING-004 | Cast inseguro no notifications store | BAIXA | Correcao recomendada |
| WARNING-005 | Store acessa campos do DTO nos filtros | MEDIA | Aceito (UI e fabrica de DTOs) |
| WARNING-006 | Campos extras nao no PRD | BAIXA | Aceito se documentado |

---

## DECISAO

**REPROVADO** - 4 violacoes BLOQUEANTES impedem avanco para QA.

Apos correcao dos 4 BLOCKERs, revalidar e atualizar este relatorio.
