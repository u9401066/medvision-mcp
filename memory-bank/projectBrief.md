# Project Brief

> 📌 此檔案描述專案的高層級目標和範圍，建立後很少更改。

## 🎯 專案目的

**MedVision MCP** - 透過 Model Context Protocol (MCP) 提供醫療影像 AI 分析工具。

核心功能：
- 讓 LLM Agent (Claude, Copilot) 能分析 X-ray、CT 等醫療影像
- 提供互動式 Canvas 工作區讓醫師標註與互動
- 整合多種醫療 AI 模型 (CheXagent, LLaVA-Med, SAM3)
- 內部 Agent 協調複雜的多步驟分析流程

## 👥 目標用戶

- **醫師/放射科醫師**: 使用 Canvas UI 分析影像
- **AI 開發者**: 透過 MCP 整合醫療 AI 能力
- **LLM Agent**: Claude, Copilot CLI 等 AI 助手

## 🏆 成功指標

- [ ] Claude Desktop 可連接並使用 MCP Tools
- [ ] 能正確分類 X-ray 影像 (14 類疾病)
- [ ] Canvas UI 可顯示 DICOM 並進行標註
- [ ] Agent 可執行多步驟分析流程

## 🚫 範圍限制

- 不用於臨床診斷決策（僅供研究輔助）
- 初期僅支援 X-ray，CT/MRI 為後續目標
- 不包含 PACS 整合

## 📝 技術決策

- **MCP Server**: FastMCP (Python)
- **Canvas UI**: React + Fabric.js
- **Database**: SQLite + SQLAlchemy
- **Inference**: vLLM / Ollama

---
*Created: 2026-02-02*
