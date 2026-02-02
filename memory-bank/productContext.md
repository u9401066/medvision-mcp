# Product Context

> 🧭 此檔案描述產品定位、使用流程與商業邏輯。

## 產品定位

MedVision MCP 是一個 **醫療影像 AI 基礎設施**，透過 MCP 協議讓 LLM Agent 能夠分析醫療影像。

## 核心使用流程

### 流程 1: Claude Desktop 分析
```
醫師 → Claude Desktop → 上傳 X-ray 
     → Claude 調用 MCP Tool → 分類/VQA
     → 返回分析結果 → 醫師確認
```

### 流程 2: Canvas 互動分析
```
醫師 → Canvas UI → 上傳 DICOM
     → 選擇區域 → 請求 AI 分析
     → AI 返回分割結果 → 醫師編輯
     → 確認並儲存
```

### 流程 3: Agent 多步驟分析
```
醫師 → "分析這張 X-ray 並產生報告"
     → Agent 規劃步驟:
        1. 載入影像
        2. 執行分類
        3. 執行 VQA 細節
        4. 生成報告
     → 彙整結果 → 返回報告
```

## 差異化優勢

| 特性 | MedVision MCP | 傳統 AI API |
|------|---------------|-------------|
| 整合方式 | MCP 標準協議 | REST API |
| Agent 支援 | 原生支援 | 需額外封裝 |
| 互動模式 | Canvas + Chat | 僅 API |
| 多模型協調 | 內建 Agent | 需自行實作 |

## 技術約束

- HIPAA/隱私考量：資料不離開本地
- 計算資源：需 GPU 進行推理
- 響應時間：分析 < 30 秒

---
*Last Updated: 2026-02-02*
