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
│  │              Visual RAG Engine                     │ │
│  │      RAD-DINO + FAISS + DenseNet (Mode B)          │ │
│  └───────────────────────┬────────────────────────────┘ │
│                          │                              │
│  ┌───────────────────────▼────────────────────────────┐ │
│  │                 Model Registry                     │ │
│  │   DenseNet │ RAD-DINO │ LLaVA-Med │ SAM3 │ ...    │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────┐
│                    Canvas UI                            │
│  ┌────────────────────────────────────────────────────┐ │
│  │  React + Fabric.js Interactive Workspace           │ │
│  │  - DICOM/Image Display                             │ │
│  │  - Annotation Tools (Draw, Box, Polygon)           │ │
│  │  - AI Overlay (Segmentation, Heatmaps)             │ │
│  │  - Visual RAG Region Selection                     │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

## 核心整合：Visual RAG × Canvas

> **User 圈選區域 → RAD-DINO 編碼 → FAISS 檢索 → External Agent 判斷 → push_to_canvas**

```
Canvas (圈選) → MCP Server (RAG) → Claude (判斷) → Canvas (標記)
     │                 │                 │               │
     ▼                 ▼                 ▼               ▼
  region          embedding          回答+標記      顯示結果
  + question      + similar_cases    指令
```

## 模組依賴

```
presentation/server.py
    ↓
application/tools/*.py
application/tools/visual_rag.py  ← NEW
    ↓
domain/services/*.py
    ↓
infrastructure/models/*.py
               /persistence/*.py
               /faiss_index/      ← NEW
```

## 技術選型

### MCP Server
- **FastMCP**: 簡化 MCP 實作
- **Transport**: stdio (Claude Desktop), SSE (web)

### Database
- **SQLAlchemy**: ORM
- **aiosqlite**: Async SQLite
- 表: sessions, images, annotations, analysis_results, **cases, reports, diagnoses**

### AI Models (已驗證)

| Model | 狀態 | Format | 用途 |
|-------|------|--------|------|
| RAD-DINO | ✅ Ready | HF/PyTorch | 768-dim 編碼 |
| DenseNet-121 | ✅ Ready | PyTorch | 18 種病理分類 |
| FAISS | ✅ Ready | faiss-cpu | 向量檢索 |
| PSPNet | ✅ Ready | PyTorch | 器官分割 |
| LLaVA-Med | ❓ 未測試 | HF/vLLM | VQA |
| SAM3 | ❓ 未測試 | PyTorch | 互動分割 |

### Visual RAG 元件

| 元件 | 規格 | 性能 |
|------|------|------|
| RAD-DINO | microsoft/rad-dino, 346MB | ~2s/img (GPU) |
| FAISS | L2 距離, 768-dim | <1ms 檢索 |
| DenseNet | torchxrayvision | ~0.1s/img |
| Reference DB | SQLite + FAISS Index | 100K+ cases |

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

3. **Visual RAG Tools** (NEW)
   - `search_similar_cases(image, region, top_k)` → similar_cases[]
   - `analyze_with_rag(image, region, question)` → RAG context
   - `analyze_selected_region(session_id, region, question, actions)` → comprehensive result

4. **Canvas Tools**
   - `sync_canvas_state(session_id, state)` → ack
   - `push_to_canvas(session_id, overlay)` → ack
   - `request_user_input(session_id, prompt)` → user_input

5. **Agent Tools**
   - `invoke_medical_agent(instruction)` → result
   - `get_agent_capabilities()` → capabilities[]

---
*Last Updated: 2026-02-02*
