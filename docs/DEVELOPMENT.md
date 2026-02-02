# MedRAX 多 Agent 協作開發指南

> 本文件說明如何使用 Git Worktree 進行多 Copilot Agent 並行開發

## 快速開始

### 1. 建立 Worktrees

```bash
# 在 MedRAX 根目錄執行
cd /root/workspace251215/MedRAX

# 建立各模組的 worktree
git worktree add ../medrax-mcp-server -b feature/mcp-server
git worktree add ../medrax-canvas-ui -b feature/canvas-ui  
git worktree add ../medrax-models -b feature/models
git worktree add ../medrax-integration -b feature/integration

# 查看所有 worktrees
git worktree list
```

### 2. 各 Agent 分工

| Worktree | Agent 職責 | 主要目錄 |
|:---------|:-----------|:---------|
| `medrax-mcp-server` | MCP Server 框架、Session 管理、工具註冊 | `medrax/mcp_server/` |
| `medrax-canvas-ui` | React Canvas UI、MCP Client | `medrax-ui/` |
| `medrax-models` | AI 模型封裝、推理後端 | `medrax/models/` |
| `medrax-integration` | 整合測試、E2E、CI/CD | `tests/` |

---

## 介面契約

**重要：所有 Agent 必須遵守 `contracts/` 目錄中的介面定義**

```
contracts/
├── __init__.py
├── mcp_tools.py      # Python: MCP Server 與工具介面
├── models.py         # Python: AI 模型介面
└── mcp-client.ts     # TypeScript: Canvas UI MCP Client 介面
```

### 變更介面的流程

1. 在 `main` 或 `feature/integration` branch 修改 `contracts/`
2. 開 PR 並 @mention 所有相關 Agent
3. 討論並確認後 merge
4. 各 worktree 執行 `git pull origin main` 同步

---

## 開發流程

### 日常開發

```bash
# 進入自己的 worktree
cd ../medrax-mcp-server

# 開發...
# 確保 import 介面契約
from contracts.mcp_tools import AnalyzeImageRequest, AnalyzeImageResponse

# 提交
git add .
git commit -m "feat(mcp-server): implement analyze_image tool"
git push origin feature/mcp-server
```

### 每日整合

```bash
# Integration Agent 執行
cd ../medrax-integration

# 從各 feature branch 拉取
git fetch origin
git merge origin/feature/mcp-server origin/feature/models --no-edit

# 解決衝突後執行測試
pytest tests/integration/

# 測試通過後
git push origin feature/integration
```

### Merge 到 Main

```bash
# 當 integration 穩定後
cd /root/workspace251215/MedRAX
git checkout main
git merge feature/integration
git push origin main

# 通知所有 worktree 同步
# 各 Agent 執行:
git fetch origin
git merge origin/main
```

---

## Mock 開發策略

當其他模組尚未完成時，使用 mock 替代：

### MCP Server Mock Models

```python
# medrax/mcp_server/mocks.py
from contracts.mcp_tools import AnalyzeImageResponse, ClassificationResult

def mock_analyze_image(request) -> AnalyzeImageResponse:
    """Mock 分析結果 - 在 models 模組完成前使用"""
    return AnalyzeImageResponse(
        image_id=request.image_id or "mock_001",
        classification=[
            ClassificationResult(label="Cardiomegaly", confidence=0.85),
            ClassificationResult(label="Effusion", confidence=0.72),
        ],
        processing_time_ms=100
    )
```

### Canvas UI Mock MCP Client

```typescript
// medrax-ui/src/mocks/mcpClient.ts
import type { MCPClient, AnalyzeImageResponse } from '@/contracts/mcp-client';

export const mockMCPClient: MCPClient = {
  async analyzeImage(params) {
    await new Promise(r => setTimeout(r, 500)); // 模擬延遲
    return {
      image_id: params.image_id || 'mock_001',
      classification: [
        { label: 'Cardiomegaly', confidence: 0.85 },
        { label: 'Effusion', confidence: 0.72 },
      ],
      processing_time_ms: 500,
    };
  },
  // ... 其他 mock 方法
};
```

---

## 目錄結構

```
medrax/
├── contracts/                 # 📑 介面契約 (所有 Agent 共享)
│   ├── __init__.py
│   ├── mcp_tools.py          # MCP 工具介面
│   ├── models.py             # 模型介面
│   └── mcp-client.ts         # Canvas UI 介面
│
├── mcp_server/               # 🔧 Agent A: MCP Server
│   ├── __init__.py
│   ├── server.py             # FastMCP Server 入口
│   ├── tools/                # MCP Tools 實作
│   │   ├── session.py
│   │   ├── analysis.py
│   │   ├── interactive.py
│   │   └── canvas.py
│   ├── database.py           # SQLite 連接
│   └── mocks.py              # Mock 模型回傳
│
├── models/                   # 🧠 Agent C: AI 模型封裝
│   ├── __init__.py
│   ├── registry.py           # Model Registry
│   ├── classification.py     # 分類模型
│   ├── vqa.py                # VQA 模型
│   ├── segmentation.py       # 分割模型
│   └── backends/
│       ├── pytorch.py
│       ├── vllm.py
│       └── ollama.py
│
├── core/                     # 共用核心
│   ├── session.py
│   └── database.py
│
└── tests/                    # 🧪 Agent D: Integration
    ├── unit/
    ├── integration/
    └── e2e/

medrax-ui/                    # 🎨 Agent B: Canvas UI
├── package.json
├── src/
│   ├── App.tsx
│   ├── components/
│   │   ├── Canvas.tsx
│   │   ├── ImageViewer.tsx
│   │   └── AnalysisPanel.tsx
│   ├── hooks/
│   │   └── useMCPClient.ts
│   ├── lib/
│   │   └── mcpClient.ts      # 實作 MCPClient 介面
│   ├── mocks/
│   │   └── mcpClient.ts      # Mock 實作
│   └── types/                # 從 contracts/ 複製或 import
└── vite.config.ts
```

---

## 通訊協議

### MCP Server ↔ Canvas UI

```
                MCP Protocol (stdio/SSE)
Canvas UI  ◄──────────────────────────────►  MCP Server
    │                                              │
    │  call_tool("analyze_image", {...})           │
    │  ─────────────────────────────────────────►  │
    │                                              │
    │  {result: {...}}                             │
    │  ◄─────────────────────────────────────────  │
    │                                              │
    │  subscribe("session/123/annotations")       │
    │  ─────────────────────────────────────────►  │
    │                                              │
    │  resource_update({...})                      │
    │  ◄─────────────────────────────────────────  │
```

### MCP Server ↔ Model Registry

```python
# MCP Tool 內部調用 Model Registry
@mcp.tool
async def analyze_image(request: AnalyzeImageRequest) -> AnalyzeImageResponse:
    # 取得模型
    classifier = model_registry.get("densenet")
    
    # 確保載入
    if not classifier.is_loaded:
        await model_registry.load_model("densenet")
    
    # 執行推理
    result = classifier.predict(image_input)
    
    return AnalyzeImageResponse(
        classification=result.predictions,
        processing_time_ms=result.processing_time_ms
    )
```

---

## 測試策略

### 單元測試 (各 Worktree 自行負責)

```bash
# MCP Server
cd ../medrax-mcp-server
pytest medrax/mcp_server/tests/

# Models
cd ../medrax-models
pytest medrax/models/tests/

# Canvas UI
cd ../medrax-canvas-ui
npm test
```

### 整合測試 (Integration Agent)

```bash
cd ../medrax-integration
pytest tests/integration/ -v
```

### E2E 測試

```bash
# 需要先啟動 MCP Server
python -m medrax.mcp_server &

# 啟動 Canvas UI
cd medrax-ui && npm run dev &

# 執行 E2E
npx playwright test
```

---

## Checklist

### Phase 1 完成標準

- [ ] MCP Server 可啟動，回應 tool 列表
- [ ] `create_session` 工具可用
- [ ] `add_image` 工具可用 (回傳 mock 分析)
- [ ] SQLite Session 持久化
- [ ] 至少 1 個真實模型可載入 (DenseNet)
- [ ] Canvas UI 可顯示影像
- [ ] Canvas UI 可繪製 BBox
- [ ] Canvas UI MCP Client 連接成功
- [ ] 整合測試通過

### Phase 2 完成標準

- [ ] `analyze_selected_region` 工具可用
- [ ] Canvas 區域選擇 → 分析 → 結果顯示 完整流程
- [ ] VQA 模型整合 (CheXagent 或 mock)
- [ ] 標註 CRUD 可用
- [ ] E2E 測試通過

---

## 疑難排解

### Worktree 衝突

```bash
# 如果 merge 衝突，優先保留 contracts/ 的變更
git checkout --theirs contracts/
git add contracts/
```

### 介面不相容

```bash
# 回到最後的 integration 穩定版本
git checkout feature/integration -- contracts/
```

### 清理 Worktree

```bash
git worktree remove ../medrax-mcp-server
git branch -D feature/mcp-server
```
