# MedVision MCP

Medical Vision AI Tools via Model Context Protocol (MCP)

## Overview

MedVision MCP provides AI-powered medical image analysis tools accessible through the [Model Context Protocol](https://modelcontextprotocol.io/). It enables LLM agents (like Claude, GitHub Copilot) to analyze X-rays, CT scans, and other medical images.

## Features (Roadmap)

- 🔬 **X-ray Analysis**: Classification, detection, and findings extraction
- 🎯 **Interactive Segmentation**: SAM-based region segmentation
- 💬 **Medical VQA**: Visual question answering for medical images
- 🖼️ **Canvas Workspace**: Interactive drawing/annotation interface
- 🤖 **Internal Agent**: Orchestrates multi-step analysis workflows

## Quick Start

```bash
# Install
pip install medvision-mcp

# Run MCP server
medvision-mcp
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    MCP Client (Claude, Copilot)         │
└─────────────────────────┬───────────────────────────────┘
                          │ stdio/SSE
┌─────────────────────────▼───────────────────────────────┐
│                   MedVision MCP Server                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │
│  │ Session     │  │ Analysis    │  │ Canvas          │  │
│  │ Tools       │  │ Tools       │  │ Tools           │  │
│  └─────────────┘  └─────────────┘  └─────────────────┘  │
│                          │                              │
│  ┌───────────────────────▼────────────────────────────┐ │
│  │              Internal Medical Agent                │ │
│  │         (Multi-step reasoning & planning)          │ │
│  └───────────────────────┬────────────────────────────┘ │
│                          │                              │
│  ┌───────────────────────▼────────────────────────────┐ │
│  │                 Model Registry                     │ │
│  │   CheXagent │ MAIRA-2 │ LLaVA-Med │ SAM3 │ ...    │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

## Development

```bash
# Clone
git clone https://github.com/u9401066/medvision-mcp.git
cd medvision-mcp

# Install dev dependencies  
pip install -e ".[dev]"

# Run tests
pytest
```

## License

MIT
