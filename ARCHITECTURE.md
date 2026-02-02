# Architecture

MedVision MCP 系統架構說明文檔。

## 系統概覽

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
                          │
┌─────────────────────────▼───────────────────────────────┐
│                    Canvas UI                            │
│  ┌────────────────────────────────────────────────────┐ │
│  │  React + Fabric.js Interactive Workspace           │ │
│  │  - DICOM/Image Display                             │ │
│  │  - Annotation Tools (Draw, Box, Polygon)           │ │
│  │  - AI Overlay (Segmentation, Heatmaps)             │ │
│  │  - Chat Interface                                  │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

## 組件說明

### 1. MCP Server (`src/medvision_mcp/`)

FastMCP 實現的 Model Context Protocol 伺服器。

**Tool 類別：**

| 類別 | 功能 | 範例 |
|------|------|------|
| Session Tools | 會話管理 | `create_session`, `load_image` |
| Analysis Tools | AI 分析 | `classify_xray`, `detect_findings`, `medical_vqa` |
| Canvas Tools | UI 互動 | `push_to_canvas`, `request_user_input` |
| Agent Tools | Agent 調用 | `invoke_medical_agent`, `get_agent_capabilities` |

### 2. Internal Agent (`src/medvision_mcp/agent/`)

內部 AI Agent，處理複雜的多步驟分析任務。

**特性：**
- 接收高階指令，自動規劃分析步驟
- 調用多個 AI 模型協同工作
- 維護分析上下文和中間結果
- 支援與使用者的 Canvas 互動

### 3. Model Registry (`src/medvision_mcp/models/`)

統一管理多種醫療 AI 模型。

**支援模型：**

| 類型 | 模型 | 用途 |
|------|------|------|
| Classification | CheXagent-2-3b | X-ray 疾病分類 |
| VQA | LLaVA-Med, MAIRA-2 | 醫療問答 |
| Segmentation | Medical-SAM3 | 互動式分割 |
| Report | CheXagent | 報告生成 |

### 4. Canvas UI (`canvas-ui/`)

React + Fabric.js 的互動式醫療影像工作區。

**功能：**
- DICOM 渲染 (Window/Level 調整)
- 繪圖工具 (自由繪、矩形、多邊形)
- AI 結果疊加 (分割遮罩、熱力圖、標註)
- 與 MCP Server 雙向通訊

## 資料流

1. **使用者上傳影像** → Canvas UI → MCP Server → Session 建立
2. **AI 分析請求** → MCP Client → MCP Server → Model Registry → 結果
3. **互動標註** → Canvas UI → MCP Server → Agent 處理 → 更新 Canvas
4. **Agent 規劃** → MCP Client → invoke_medical_agent → 多步驟執行 → 彙整結果

## DDD 分層

```
src/medvision_mcp/
├── domain/           # 核心領域（無外部依賴）
│   ├── entities/     # 實體 (Session, Image, Finding)
│   ├── value_objects/# 值物件 (BoundingBox, SegmentMask)
│   └── services/     # 領域服務
├── application/      # 應用層（用例編排）
│   ├── tools/        # MCP Tool 實作
│   └── agent/        # Agent 編排
├── infrastructure/   # 基礎設施
│   ├── models/       # Model Registry 實作
│   ├── persistence/  # SQLite DAL
│   └── external/     # vLLM, Ollama 連接器
└── presentation/     # 呈現層
    └── server.py     # FastMCP Server
```

## Memory Bank (`memory-bank/`)

跨對話的專案記憶系統，保持上下文連續性。

| 文件 | 用途 |
|------|------|
| `activeContext.md` | 當前工作焦點 |
| `progress.md` | 進度追蹤 |
| `decisionLog.md` | 決策記錄 |
| `productContext.md` | 專案上下文 |
| `projectBrief.md` | 專案簡介 |
| `systemPatterns.md` | 系統模式 |
| `architect.md` | 架構設計 |
