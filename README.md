# Althia MCP Bridge

Servidor MCP (Streamable HTTP) que expõe a API de debate-prep da Althia como ferramentas para o Claude — sem guardar a chave do cliente. Cada chamador informa sua própria chave via header (`Authorization: Bearer althia_dbt_...` ou `x-api-key`) na configuração do Connector; o servidor só repassa esse header para a Althia em cada chamada.

## Ferramentas expostas

`list_dossiers`, `get_dossier`, `list_briefings`, `get_briefing`, `generate_briefing`, `get_painel`, `get_social_mentions`, `get_findings` — mapeiam 1:1 os endpoints documentados em `https://althia.pro/docs/api/debates/`.

## Deploy

Docker, deployado como serviço isolado no EasyPanel (projeto `infra-core`), expondo a porta 8000.

## Configurar no Claude do cliente

1. Settings → Connectors → Add custom connector.
2. Cole a URL do serviço (ex.: `https://infra-core-althia-mcp.kxryyk.easypanel.host/mcp`).
3. Adicione um header customizado: `Authorization` com valor `Bearer <sua chave althia_dbt_...>`.
4. Pronto — peça um briefing de debate no Claude.

A chave nunca é armazenada por este servidor — vive só na configuração do Connector do próprio cliente.
