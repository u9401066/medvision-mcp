# MedVision MCP

Medical Vision AI Tools via Model Context Protocol (MCP)

## Overview

MedVision MCP provides AI-powered medical image analysis tools accessible through the [Model Context Protocol](https://modelcontextprotocol.io/). It enables LLM agents (like Claude, GitHub Copilot) to analyze chest X-rays using Visual RAG (RAD-DINO + FAISS + DenseNet).

## Features

- ✅ **DenseNet Classification**: 18 pathology detection (Lung Opacity, Pneumonia, etc.)
- ✅ **RAD-DINO Embeddings**: 768-dim visual embeddings for similarity search
- ✅ **FAISS Index**: Fast similarity search for similar historical cases
- ✅ **DICOM Support**: Native DICOM file reading
- 🔜 **Interactive Segmentation**: SAM-based region segmentation
- 🔜 **Gradio Canvas**: Interactive drawing/annotation interface

## Quick Start

```bash
# Clone
git clone https://github.com/u9401066/medvision-mcp.git
cd medvision-mcp

# Install with uv
uv sync

# Test classification
uv run python -c "
import asyncio
from src.medvision_mcp.server import classify_xray

async def main():
    result = await classify_xray('path/to/xray.dcm')
    print(result)
asyncio.run(main())
"
```

## MCP Tools

| Tool | Description |
|------|-------------|
| `analyze_xray` | Full Visual RAG analysis (classification + similarity) |
| `classify_xray` | Quick DenseNet-121 classification (18 pathologies) |
| `search_similar_cases` | RAG similarity search |
| `build_rag_index` | Build FAISS index from image directory |
| `load_rag_index` | Load pre-built index |
| `get_engine_status` | Check model loading status |

## Claude Desktop Configuration

Add to `~/.config/claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "medvision": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/medvision-mcp", "python", "-m", "src.medvision_mcp.server"]
    }
  }
}
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    MCP Client (Claude, Copilot)         │
└─────────────────────────┬───────────────────────────────┘
                          │ stdio
┌─────────────────────────▼───────────────────────────────┐
│                   MedVision MCP Server                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │
│  │ classify    │  │ search      │  │ analyze         │  │
│  │ _xray       │  │ _similar    │  │ _xray           │  │
│  └─────────────┘  └─────────────┘  └─────────────────┘  │
│                          │                              │
│  ┌───────────────────────▼────────────────────────────┐ │
│  │               Visual RAG Engine                    │ │
│  │         RAD-DINO │ FAISS │ DenseNet-121            │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

## Development

```bash
# Install dev dependencies  
uv sync --dev

# Run tests
uv run pytest

# Check types
uv run pyright
```

## License

MIT
