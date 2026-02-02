```instructions
# Copilot 自定義指令

此文件為 VS Code GitHub Copilot 及 Claude Code 提供專案上下文與操作規範。

---

## 專案概述

**MedVision MCP** - 透過 Model Context Protocol 提供醫療影像 AI 分析工具。

核心架構：
- **MCP Server**: FastMCP 實現，提供醫療 AI 工具給 LLM Agents
- **Internal Agent**: 內部代理器，協調多步驟分析流程 (A2A-like)
- **Canvas UI**: React + Fabric.js 互動式醫療影像標註工作區
- **Model Registry**: 多模型管理（CheXagent、LLaVA-Med、SAM3 等）

---

## 開發哲學 💡

> **「想要寫文件的時候，就更新 Memory Bank 吧！」**
> 
> **「想要零散測試的時候，就寫測試檔案進 tests/ 資料夾吧！」**

- 不要另開檔案寫筆記，直接寫進 Memory Bank
- 今天的零散測試，就是明天的回歸測試

---

## 法規層級

```
CONSTITUTION.md          ← 最高原則（不可違反）
  │
  ├── .github/bylaws/    ← 子法（細則規範）
  │     ├── ddd-architecture.md
  │     ├── git-workflow.md
  │     ├── python-environment.md
  │     └── memory-bank.md
  │
  └── .claude/skills/    ← 實施細則（操作程序）
```

你必須遵守以下法規層級：
1. **憲法**：`CONSTITUTION.md` - 最高原則，不可違反
2. **子法**：`.github/bylaws/*.md` - 細則規範
3. **技能**：`.claude/skills/*/SKILL.md` - 操作程序

---

## 專案架構

### 目錄結構

```
medvision-mcp/
├── src/medvision_mcp/      # Python MCP Server
│   ├── server.py           # FastMCP 入口
│   ├── tools/              # MCP Tool 實作
│   ├── models/             # AI Model Registry
│   └── agent/              # Internal Agent
├── canvas-ui/              # React + Fabric.js 前端
│   ├── src/
│   │   ├── components/     # React 組件
│   │   ├── hooks/          # Custom Hooks
│   │   └── mcp-client/     # MCP Client 封裝
│   └── package.json
├── contracts/              # 介面合約 (Python + TypeScript)
├── docs/                   # 規格文檔
└── tests/                  # 測試
```

### DDD 架構
- **Domain Layer**: 核心醫療影像分析邏輯
- **Application Layer**: MCP Tools 編排、Agent 流程
- **Infrastructure Layer**: Model Registry、外部服務 (vLLM, Ollama)
- **Presentation Layer**: MCP Server、Canvas UI

詳見：`.github/bylaws/ddd-architecture.md`

---

## 技術棧

### Backend (Python)
- **MCP**: mcp, fastmcp
- **Database**: SQLAlchemy + aiosqlite
- **Inference**: vLLM, Ollama, PyTorch
- **Medical AI**: CheXagent, LLaVA-Med, MAIRA-2, SAM3

### Frontend (TypeScript)
- **Framework**: React 18+
- **Canvas**: Fabric.js
- **MCP Client**: @modelcontextprotocol/sdk

---

## Python 環境（uv 優先）

```bash
# 初始化環境
uv venv
uv sync --all-extras

# 安裝依賴
uv add package-name
uv add --dev pytest ruff mypy
```

詳見：`.github/bylaws/python-environment.md`

---

## Memory Bank 同步

每次重要操作必須更新 Memory Bank：

| 操作 | 更新文件 |
|------|----------|
| 完成任務 | `progress.md` (Done) |
| 開始任務 | `progress.md` (Doing), `activeContext.md` |
| 重大決策 | `decisionLog.md` |
| 架構變更 | `architect.md` |

詳見：`.github/bylaws/memory-bank.md`

---

## Git 工作流

提交前必須執行檢查清單：
1. ✅ Memory Bank 同步（必要）
2. 📖 README 更新（如需要）
3. 📋 CHANGELOG 更新（如需要）
4. 🗺️ ROADMAP 標記（如需要）

詳見：`.github/bylaws/git-workflow.md`

---

## 💸 Memory Checkpoint 規則

為避免對話被 Summarize 壓縮時遺失重要上下文：

### 主動觸發時機
1. 對話超過 **10 輪**
2. 累積修改超過 **5 個檔案**
3. 完成一個 **重要功能/修復**
4. 使用者說要 **離開/等等**

### 必須記錄
- 當前工作焦點
- 變更的檔案列表（完整路徑）
- 待解決事項
- 下一步計畫

---

## 常用指令

```
「準備 commit」       → 執行完整提交流程
「快速 commit」       → 只同步 Memory Bank
「建立新功能 X」      → 生成 DDD 結構
「review 程式碼」     → 程式碼審查
「更新 memory bank」  → 同步專案記憶
「checkpoint」        → 記憶檢查點
```

---

## 回應風格

- 使用**繁體中文**
- 提供清晰的步驟說明
- 引用相關法規條文
- 執行操作後更新 Memory Bank

---

## 相關文檔

- `docs/spec.md` - 完整技術規格
- `contracts/` - 介面合約定義
- `README.md` - 專案說明

```
