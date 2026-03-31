# Agentic Campaign Builder — Future State

A multi-agent Python architecture for automating campaign builds across TTD, DV360, and Amazon DSP.

## Architecture

```
main.py
└── orchestrator/orchestrator.py
    ├── agents/media_plan_translator/       → Parses Excel inputs, maps to DSP formats
    ├── agents/placement_name_generator/    → Generates placement names (TBD)
    ├── agents/ttd_campaign_builder/        → Creates TTD campaigns via API
    │   ├── subagents/campaign_subagent.py
    │   ├── subagents/ad_group_subagent.py
    │   └── subagents/budget_flight_subagent.py
    ├── agents/dv360_campaign_builder/      → Creates DV360 insertion orders via API
    │   └── subagents/insertion_order_subagent.py
    └── agents/amazon_campaign_builder/     → Creates Amazon DSP campaigns via API (stub)
```

Shared data models live in `shared/models.py`.

## MCP Server

`mcp_server.py` exposes each agent as a separate MCP tool. It can be used two ways:

### From Claude Code (stdio)

Add to your Claude Code MCP settings or use the `.mcp.json` in this repo:

```json
{
  "mcpServers": {
    "campaign-builder": {
      "command": "python3",
      "args": ["mcp_server.py"],
      "cwd": "/path/to/agentic-campaign-builder"
    }
  }
}
```

Available tools:
| Tool | Description |
|---|---|
| `build_campaign` | Full pipeline — translate → name → build in each DSP |
| `translate_media_plan` | Parse Excel files and map to DSP-specific formats |
| `generate_placement_names` | Generate placement names from translated campaign |
| `build_ttd_campaign` | Create TTD campaigns (Campaign Sets, Ad Groups, Budget Flights) |
| `build_dv360_campaign` | Create DV360 Insertion Orders |
| `build_amazon_campaign` | Create Amazon DSP campaigns (stub) |

### From FastAPI

```python
from fastapi import FastAPI
from mcp_server import create_mcp_app

app = FastAPI()
app.mount("/mcp", create_mcp_app())
# MCP endpoint: http://localhost:8000/mcp/sse
```

## Running the CLI

```bash
cd /path/to/agentic-campaign-builder
pip install -r requirements.txt

python3 main.py \
  --brief   /path/to/media_brief.xlsx \
  --plan    /path/to/media_plan.xlsx \
  --audience /path/to/audience_matrix.xlsx \
  --trafficking /path/to/trafficking_sheet.xlsx
```

## Environment Variables

Copy `.env.example` to `.env` and fill in credentials when available:

```
TTD_API_KEY=
TTD_ADVERTISER_ID=
DV360_ACCESS_TOKEN=
DV360_ADVERTISER_ID=
AMAZON_CLIENT_ID=
AMAZON_ACCESS_TOKEN=
AMAZON_PROFILE_ID=
```

## Status

| Component | Status |
|---|---|
| Media Plan Translator | ✅ Implemented (rule-based, imports Campaign Builder repo) |
| Placement Name Generator | 🔲 Placeholder (naming convention TBD) |
| TTD Campaign Builder | 🔲 Stubbed (API calls commented out) |
| DV360 Campaign Builder | 🔲 Stubbed (API calls commented out) |
| Amazon Campaign Builder | 🔲 Not yet implemented |
| MCP Server | ✅ Implemented |

## Future: Amazon Bedrock

This project is designed to migrate to Amazon Bedrock as the LLM runtime. Python was chosen over TypeScript for better `boto3` support.
