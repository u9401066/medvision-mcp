# Decision Log

> 📝 重要決策記錄。

## 2026-02-02

### 決策 1: 專案名稱
- **決定**: `medvision-mcp`
- **原因**: 
  - GitHub/PyPI/npm 未被使用
  - 清楚表達 Medical Vision + MCP 定位
- **替代方案**: medrax-mcp (放棄，因為 MedRAX 是 fork 的)

### 決策 2: 獨立專案 vs Fork
- **決定**: 創建全新專案，不繼承 MedRAX git history
- **原因**:
  - MedRAX 是 fork 別人的專案
  - 架構完全重寫 (MCP-based)
  - 乾淨的 git history 更好維護
- **影響**: 需要重新設定所有 git config

### 決策 3: UI 技術選型
- **決定**: React + Fabric.js
- **原因**:
  - 需要真正的 Canvas 互動（繪圖、標註）
  - Streamlit canvas 功能有限
  - MCP ext-apps 官方支援 React
  - 適合 Copilot CLI SDK 整合
- **替代方案**: 
  - Streamlit (放棄: Canvas 限制)
  - Gradio (放棄: 客製化困難)

### 決策 4: 開發策略
- **決定**: Multi-worktree 平行開發
- **分工**:
  - Main: 整合協調
  - Background 1: MCP Server
  - Background 2: Canvas UI (React)
  - Background 3: Models
- **原因**: 加速開發，介面合約已定義

---
