# Roadmap

MedVision MCP 發展路線圖。

## 版本規劃

### Phase 1: Foundation (MVP) 🚧
*Target: 2026 Q1*

- [ ] **MCP Server 骨架**
  - [ ] FastMCP 設定與啟動
  - [ ] Session 管理 Tool
  - [ ] SQLite 資料持久化
  
- [ ] **基礎 AI Tool**
  - [ ] DenseNet X-ray 分類 (14 classes)
  - [ ] 影像載入與預處理
  
- [ ] **Canvas UI 骨架**
  - [ ] React + Vite 專案初始化
  - [ ] Fabric.js Canvas 整合
  - [ ] 基礎 DICOM 渲染

### Phase 2: Core Analysis
*Target: 2026 Q2*

- [ ] **進階 AI Tools**
  - [ ] CheXagent-2-3b 整合
  - [ ] Medical VQA (LLaVA-Med)
  - [ ] 結果 Overlay 渲染
  
- [ ] **Canvas 增強**
  - [ ] Window/Level 控制
  - [ ] 繪圖工具 (ROI 選擇)
  - [ ] 標註圖層管理

### Phase 3: Interactive Segmentation
*Target: 2026 Q3*

- [ ] **SAM3 整合**
  - [ ] 點擊式分割
  - [ ] 框選分割
  - [ ] 多區域管理
  
- [ ] **Canvas 互動**
  - [ ] 即時分割預覽
  - [ ] 編輯分割結果
  - [ ] 匯出遮罩

### Phase 4: Internal Agent
*Target: 2026 Q3-Q4*

- [ ] **Agent 框架**
  - [ ] LangGraph 整合
  - [ ] 多步驟規劃
  - [ ] 工具調用編排
  
- [ ] **Agent Tools**
  - [ ] invoke_medical_agent
  - [ ] 上下文管理
  - [ ] 使用者確認流程

### Phase 5: Advanced VLM
*Target: 2026 Q4*

- [ ] **MAIRA-2 整合**
  - [ ] 結構化報告生成
  - [ ] Grounded 發現標註
  
- [ ] **多模態推理**
  - [ ] 影像比較分析
  - [ ] 時序追蹤

### Phase 6: Production Ready
*Target: 2027 Q1*

- [ ] **部署優化**
  - [ ] Docker Compose 配置
  - [ ] vLLM 生產設定
  - [ ] 安全性強化
  
- [ ] **整合測試**
  - [ ] Claude Desktop 整合
  - [ ] Copilot CLI 整合
  - [ ] 端到端測試

---

## 已完成 ✅

### v0.0.1 (2026-02-02)
- [x] 專案初始化
- [x] GitHub Repo 建立
- [x] 基礎 pyproject.toml
- [x] MCP Server 骨架 (server.py)
- [x] 介面合約定義 (contracts/)
- [x] 規格文檔 (docs/spec.md)
- [x] Template 整合

---

## MVP 定義

**MVP 目標**：能在 Claude Desktop 中使用基本 X-ray 分類功能

**MVP 範圍**：
1. ✅ MCP Server 可啟動並被 Claude 連接
2. ⬜ 載入 X-ray 影像 (DICOM/PNG)
3. ⬜ 執行 DenseNet 分類
4. ⬜ 返回分類結果給 Claude

**MVP 排除**：
- Canvas UI（但骨架可以同步開發）
- 進階 VLM（CheXagent, LLaVA-Med）
- Internal Agent
- 互動式分割

---

## 開發策略

### Worktree 分工

| Agent | 負責 | 分支 |
|-------|------|------|
| Main | 整合、協調、Memory Bank | main |
| Background 1 | MCP Server + SQLite | feature/mcp-server |
| Background 2 | Canvas UI (React) | feature/canvas-ui |
| Background 3 | Model Registry | feature/models |
