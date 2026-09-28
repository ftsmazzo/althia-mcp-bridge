"""MCP bridge for the Althia debate-prep API.

Exposes Althia's REST API (https://althia.pro) as MCP tools over Streamable HTTP.
The Althia API key is never stored here: each caller supplies it via the
`Authorization` or `x-api-key` header on their MCP connector, and every tool
call simply forwards that header upstream to Althia.
"""

from typing import Optional

import httpx
from mcp.server.fastmcp import Context, FastMCP

ALTHIA_BASE_URL = "https://pxqdpteehqidgomixfre.supabase.co/functions/v1/debate-api/v1"

mcp = FastMCP("althia-debate-api", stateless_http=True)


def _auth_headers(ctx: Context) -> dict:
    request = ctx.request_context.request
    auth = request.headers.get("authorization")
    api_key = request.headers.get("x-api-key")
    headers = {}
    if auth:
        headers["Authorization"] = auth
    if api_key:
        headers["x-api-key"] = api_key
    if not headers:
        raise ValueError(
            "Nenhuma chave da Althia recebida. Configure o header "
            "'Authorization: Bearer althia_dbt_...' (ou 'x-api-key') "
            "no seu Connector do Claude."
        )
    return headers


async def _get(ctx: Context, path: str, params: Optional[dict] = None) -> dict:
    headers = _auth_headers(ctx)
    async with httpx.AsyncClient(base_url=ALTHIA_BASE_URL, timeout=30) as client:
        resp = await client.get(path, headers=headers, params=params or {})
        resp.raise_for_status()
        return resp.json()


async def _post(ctx: Context, path: str) -> dict:
    headers = _auth_headers(ctx)
    async with httpx.AsyncClient(base_url=ALTHIA_BASE_URL, timeout=30) as client:
        resp = await client.post(path, headers=headers)
        resp.raise_for_status()
        return resp.json() if resp.content else {"status": resp.status_code}


@mcp.tool()
async def list_dossiers(ctx: Context) -> dict:
    """Lista os dossies (candidatos/campanhas) acessiveis com a chave da Althia."""
    return await _get(ctx, "/dossiers")


@mcp.tool()
async def get_dossier(ctx: Context, dossier_id: str) -> dict:
    """Detalhe de um dossie e seus adversarios."""
    return await _get(ctx, f"/dossiers/{dossier_id}")


@mcp.tool()
async def list_briefings(ctx: Context, dossier_id: str) -> dict:
    """Resumo dos briefings de todos os adversarios de um dossie."""
    return await _get(ctx, f"/dossiers/{dossier_id}/briefings")


@mcp.tool()
async def get_briefing(ctx: Context, dossier_id: str, opponent_key: str) -> dict:
    """Briefing completo de um adversario: perguntas antecipadas, respostas sugeridas, fontes, analise Cortex."""
    return await _get(ctx, f"/dossiers/{dossier_id}/briefings/{opponent_key}")


@mcp.tool()
async def generate_briefing(ctx: Context, dossier_id: str, opponent_key: str) -> dict:
    """Dispara a geracao de um novo briefing para um adversario (assincrono - consulte get_briefing depois)."""
    return await _post(ctx, f"/dossiers/{dossier_id}/briefings/{opponent_key}/generate")


@mcp.tool()
async def get_painel(ctx: Context, dossier_id: str) -> dict:
    """Indicadores de prontidao, risco/oportunidade por tema, pendencias e confianca das fontes."""
    return await _get(ctx, f"/dossiers/{dossier_id}/painel")


@mcp.tool()
async def get_social_mentions(ctx: Context, dossier_id: str, opponent_key: str) -> dict:
    """Mencoes em redes sociais (Instagram) citando o candidato, com transcricao de video quando houver."""
    return await _get(ctx, f"/dossiers/{dossier_id}/opponents/{opponent_key}/social")


@mcp.tool()
async def get_findings(
    ctx: Context,
    dossier_id: str,
    topic: Optional[str] = None,
    kind: Optional[str] = None,
    offset: Optional[int] = None,
) -> dict:
    """Arquivo de perguntas de debates com evidencia de transcricao. kind: esclarecimento | possivel_contradicao | verificacao."""
    params: dict = {}
    if topic:
        params["topic"] = topic
    if kind:
        params["kind"] = kind
    if offset is not None:
        params["offset"] = offset
    return await _get(ctx, f"/dossiers/{dossier_id}/findings", params)


app = mcp.streamable_http_app()
