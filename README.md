# gcs-wm-marketplace

Marketplace de plugins do Claude para o **Wealth & Migration Summit 2026** (Lisboa, 5–6 de novembro de 2026, convocado pela Global Citizen Solutions).

## Plugin: `wm-summit`

| Skill | Faz |
|---|---|
| `wm-presentations` | Decks PowerPoint (.pptx) editáveis do Summit |
| `wm-social-media` | Carrosséis, posts, Stories e posts de LinkedIn |
| `wm-reels` | Roteiro de Reel do Instagram: gancho em 3s, tabela de beats, textos em tela, falas, legenda, capa, alt text e checklist antes de publicar (só o script, não gera vídeo) |
| `wm-letterhead` | Papel timbrado A4 em Word (.docx) |
| `wm-web-banners` | Banners web em PNG ou GIF animado, em qualquer WxH |
| `wm-paid-ads` | Pacotes de anúncios pagos para Google Ads (RSA, Display, Performance Max, Demand Gen) e Meta Ads (Feed, Stories/Reels, carrossel): textos dentro dos limites de cada plataforma, criativos PNG nos tamanhos e zonas seguras certos, lint de preço e fatos |
| `wm-assets` | Entrega assets que já existem: logos (W&M, GCS, CNN Portugal, parceiros), fotos dos 26 palestrantes, imagens e fontes |

As que criam peças usam a identidade própria do Summit e puxam os fatos (programa, 26 palestrantes, três faixas de preço, teto de 200 participantes) dos dados confirmados do site, nunca de texto digitado à mão.

### Instalar

```
/plugin marketplace add <owner>/gcs-wm-marketplace
/plugin install wm-summit@gcs-wm-marketplace
```

Para testar localmente, sem publicar: `/plugin marketplace add "/caminho/para/gcs-wm-marketplace"`.

### Requisitos na máquina

- Python 3 com `python-pptx`, `python-docx`, `Pillow`, `lxml`, `beautifulsoup4`, `playwright` (+ Chromium)
- LibreOffice (`soffice`) e `pdftoppm` (poppler) para renderizar as prévias
- As fontes da marca (Caladea, Archivo) já vão dentro de cada skill

## Estrutura

```
.claude-plugin/marketplace.json     catálogo do marketplace
plugins/wm-summit/
  .claude-plugin/plugin.json        manifesto do plugin
  skills/<skill>/SKILL.md           uma pasta por skill (assets, scripts, references, evals)
```

## Manutenção

- Edite as skills direto em `plugins/wm-summit/skills/`.
- A cada mudança publicada, suba `version` em `plugins/wm-summit/.claude-plugin/plugin.json` **e** em `.claude-plugin/marketplace.json` (as duas juntas), senão quem já instalou não recebe a atualização.
- Valide antes de publicar: `claude plugin validate .` e `claude plugin validate plugins/wm-summit/skills`.
