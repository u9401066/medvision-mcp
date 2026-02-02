# MedRAX v2 開發啟動檢查清單

## 開發前必做

### 1. 環境設置 ✅/❌

- [ ] Python 3.12+ 已安裝
- [ ] Node.js 20+ 已安裝 (Canvas UI)
- [ ] CUDA 12.x 已安裝 (GPU 推理)
- [ ] Git Worktree 支援確認

```bash
# 檢查版本
python --version    # >= 3.12
node --version      # >= 20
nvcc --version      # >= 12.0
git --version       # >= 2.20 (worktree support)
```

### 2. 依賴安裝

```bash
# Python 環境
cd /root/workspace251215/MedRAX
uv sync --all-extras

# 確認 MCP 套件
uv add mcp fastmcp

# Canvas UI (在 canvas-ui worktree)
cd ../medrax-canvas-ui
npm create vite@latest medrax-ui -- --template react-ts
cd medrax-ui
npm install fabric zustand @tanstack/react-query tailwindcss
```

### 3. 建立 Worktrees

```bash
cd /root/workspace251215/MedRAX

# 建立 worktrees
git worktree add ../medrax-mcp-server -b feature/mcp-server
git worktree add ../medrax-canvas-ui -b feature/canvas-ui
git worktree add ../medrax-models -b feature/models
git worktree add ../medrax-integration -b feature/integration

# 確認
git worktree list
```

### 4. 環境變數 (.env)

```bash
# 複製到各 worktree
cp .env ../medrax-mcp-server/
cp .env ../medrax-models/
```

需要的環境變數：
```env
# Model paths
MODEL_CACHE_DIR=/model-cache
HUGGINGFACE_HUB_CACHE=/model-cache/huggingface

# MCP Server
MCP_SERVER_PORT=8000
MCP_LOG_LEVEL=INFO

# Database
SQLITE_DB_PATH=./data/medrax.db

# GPU
CUDA_VISIBLE_DEVICES=0

# (Optional) 外部 API
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

---

## 開發分工確認

### Agent A: MCP Server (`medrax-mcp-server`)

**Week 1-2 任務：**
- [ ] FastMCP Server 基本設置
- [ ] SQLite 連接與 Session 表
- [ ] `create_session` tool
- [ ] `add_image` tool (Mock 分析)
- [ ] `get_session_status` tool

**驗收標準：**
```bash
# 能啟動 MCP Server
python -m medrax.mcp_server

# Claude Desktop 能連接
# 或用 mcp dev 測試
npx @anthropic/mcp-cli dev medrax/mcp_server/server.py
```

### Agent B: Canvas UI (`medrax-canvas-ui`)

**Week 1-2 任務：**
- [ ] Vite + React + TypeScript 設置
- [ ] Fabric.js Canvas 組件
- [ ] 影像上傳 + 顯示
- [ ] BBox 繪圖工具
- [ ] Mock MCP Client

**驗收標準：**
```bash
# 能啟動 UI
npm run dev

# 瀏覽器開啟 http://localhost:5173
# 能上傳影像、繪製 BBox
```

### Agent C: Models (`medrax-models`)

**Week 1-2 任務：**
- [ ] Model Registry 架構
- [ ] DenseNet 分類器封裝
- [ ] 統一 ImageInput/ClassificationOutput
- [ ] PyTorch 推理後端

**驗收標準：**
```python
from medrax.models import ModelRegistry
from contracts.models import ImageInput

registry = ModelRegistry()
registry.load_model("densenet")
result = registry.get("densenet").predict(ImageInput(path="test.png"))
assert len(result.predictions) > 0
```

### Agent D: Integration (`medrax-integration`)

**Week 3-4 任務：**
- [ ] Docker Compose 設置
- [ ] MCP Server + Models 整合
- [ ] E2E 測試框架
- [ ] CI Pipeline (GitHub Actions)

---

## 關鍵決策確認

開發前請確認以下決策：

| 項目 | 選項 A | 選項 B | 決定 |
|:-----|:-------|:-------|:-----|
| MCP Transport | stdio | HTTP/SSE | ❓ |
| MVP 模型 | DenseNet + Mock VQA | CheXagent-2 | ❓ |
| Canvas 框架 | Fabric.js | Konva.js | Fabric.js ✅ |
| 狀態管理 | Zustand | Redux | Zustand ✅ |
| 整合頻率 | 每日 | 每 PR | ❓ |

---

## 第一週目標 (Milestone 1)

**完成標準：各模組可獨立運行 + Mock 互通**

```
┌─────────────────┐     Mock      ┌─────────────────┐
│  MCP Server     │◄─────────────►│  Canvas UI      │
│  (能接收請求)    │               │  (能發送請求)    │
└────────┬────────┘               └─────────────────┘
         │ Mock
         ▼
┌─────────────────┐
│  Models         │
│  (DenseNet OK)  │
└─────────────────┘
```

---

## 問題回報

如果開發過程遇到問題：

1. **介面不相容**：在 `contracts/` 目錄開 PR 討論
2. **依賴衝突**：在 `feature/integration` 解決
3. **架構疑問**：更新 `docs/spec.md` 待討論區

---

## 啟動！

確認上述項目後，各 Agent 可以開始開發。

```bash
# 各 Agent 進入自己的 worktree
cd ../medrax-{your-module}

# 開始開發
git status
# ... code ...
git add .
git commit -m "feat(module): description"
git push origin feature/{your-module}
```

祝開發順利！🚀
