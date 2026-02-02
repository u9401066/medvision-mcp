# Architect

> 🏗️ 架構設計細節與技術決策。

## 系統架構圖

```
┌─────────────────────────────────────────────────────────┐
│              MCP Client (Claude, Copilot CLI)           │
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

## 模組依賴

```
presentation/server.py
    ↓
application/tools/*.py
    ↓
domain/services/*.py
    ↓
infrastructure/models/*.py
               /persistence/*.py
```

## 技術選型

### MCP Server
- **FastMCP**: 簡化 MCP 實作
- **Transport**: stdio (Claude Desktop), SSE (web)

### Database
- **SQLAlchemy**: ORM
- **aiosqlite**: Async SQLite
- 表: sessions, images, annotations, analysis_results

### AI Models

| Model | Format | Inference |
|-------|--------|-----------|
| DenseNet | PyTorch | Direct |
| CheXagent | HF | vLLM |
| LLaVA-Med | HF | vLLM/Ollama |
| SAM3 | PyTorch | Direct |

### Canvas UI
- **React 18**: Framework
- **Fabric.js 6**: Canvas
- **Vite**: Build tool
- **TailwindCSS**: Styling

## API 設計

### MCP Tool 分類

1. **Session Tools**
   - `create_session` → `session_id`
   - `load_image(session_id, path)` → `image_id`
   - `get_session_info(session_id)` → session state

2. **Analysis Tools**
   - `classify_xray(image_id)` → findings[]
   - `medical_vqa(image_id, question)` → answer
   - `segment_region(image_id, prompt)` → mask

3. **Canvas Tools**
   - `sync_canvas_state(session_id, state)` → ack
   - `push_to_canvas(session_id, overlay)` → ack
   - `request_user_input(session_id, prompt)` → user_input

4. **Agent Tools**
   - `invoke_medical_agent(instruction)` → result
   - `get_agent_capabilities()` → capabilities[]

---
*Last Updated: 2026-02-02*
