# Background Agent 任務指令

> 這是給各 Background Agent 的任務說明。
> 主 Terminal 的 Agent 會提供這些指令，用戶複製到各 Background Terminal 執行。

---

## 🔴 Background 1: MCP Server Agent

### 任務摘要
你負責 **MCP Server 框架** 的開發。

### 工作目錄
```bash
cd /root/workspace251215/MedRAX
# 或使用 worktree:
# git worktree add ../medrax-mcp-server -b feature/mcp-server
# cd ../medrax-mcp-server
```

### Phase 1 任務清單

1. **安裝 MCP 依賴**
   ```bash
   uv add mcp fastmcp
   ```

2. **實作 SQLite Session 管理**
   - 檔案：`medrax/mcp_server/database.py`
   - 表格：sessions, images, annotations
   - 使用 SQLAlchemy + aiosqlite

3. **完善 MCP Tools**
   - 檔案：`medrax/mcp_server/server.py` (已有框架)
   - 將 mock 回傳改為真實 DB 操作
   - 工具：`create_session`, `add_image`, `get_session_status`

4. **測試 MCP Server**
   ```bash
   python -m medrax.mcp_server
   # 或
   npx @anthropic/mcp-cli dev medrax/mcp_server/server.py
   ```

### 介面契約
遵守 `contracts/mcp_tools.py` 中的定義：
- `CreateSessionRequest/Response`
- `AddImageRequest/Response`
- `SessionStatus`

### 驗收標準
- [ ] MCP Server 可啟動
- [ ] `create_session` 回傳有效 session_id
- [ ] Session 資料持久化到 SQLite
- [ ] Claude Desktop 可連接測試

### 不要做
- ❌ 不要實作真實 AI 模型推理（用 mock）
- ❌ 不要做 Canvas UI
- ❌ 不要改 `contracts/` 介面

---

## 🟢 Background 2: Canvas UI Agent

### 任務摘要
你負責 **React Canvas UI** 的開發。

### 工作目錄
```bash
# 建立前端專案
mkdir -p /root/workspace251215/medrax-ui
cd /root/workspace251215/medrax-ui
npm create vite@latest . -- --template react-ts
npm install
```

### Phase 1 任務清單

1. **專案設置**
   ```bash
   npm install fabric zustand @tanstack/react-query tailwindcss postcss autoprefixer
   npx tailwindcss init -p
   ```

2. **基本 UI 結構**
   - `src/components/Canvas.tsx` - Fabric.js 畫板
   - `src/components/ImageViewer.tsx` - 影像顯示
   - `src/components/Toolbar.tsx` - 繪圖工具列

3. **繪圖功能**
   - BBox 繪製
   - Polygon 繪製
   - Point 標記

4. **Mock MCP Client**
   - `src/lib/mcpClient.ts` - 介面實作
   - `src/mocks/mcpClient.ts` - Mock 回傳

### 介面契約
遵守 `contracts/mcp-client.ts` 中的定義：
- `MCPClient` interface
- `CanvasEventHandlers` interface
- 所有 Request/Response types

### 驗收標準
- [ ] `npm run dev` 可啟動
- [ ] 能上傳並顯示影像
- [ ] 能繪製 BBox 並取得座標
- [ ] Mock 分析結果可顯示

### 不要做
- ❌ 不要實作真實 MCP 連接（先用 mock）
- ❌ 不要做後端邏輯
- ❌ 不要改 Python 代碼

---

## 🔵 Background 3: Models Agent

### 任務摘要
你負責 **AI 模型封裝** 的開發。

### 工作目錄
```bash
cd /root/workspace251215/MedRAX
# 或使用 worktree:
# git worktree add ../medrax-models -b feature/models
# cd ../medrax-models
```

### Phase 1 任務清單

1. **建立 Model Registry**
   - 檔案：`medrax/models/registry.py`
   - 實作 `ModelRegistryInterface`

2. **封裝 DenseNet 分類器**
   - 檔案：`medrax/models/classification.py`
   - 使用 torchxrayvision 的 DenseNet
   - 實作 `ClassifierModel` 介面

3. **統一輸入/輸出格式**
   - 使用 `contracts/models.py` 定義的 schema
   - `ImageInput` → 模型 → `ClassificationOutput`

4. **測試模型**
   ```python
   from medrax.models import ModelRegistry
   from contracts.models import ImageInput
   
   registry = ModelRegistry()
   registry.load_model("densenet")
   result = registry.get("densenet").predict(ImageInput(path="test.png"))
   print(result.predictions)
   ```

### 介面契約
遵守 `contracts/models.py` 中的定義：
- `ClassifierModel` 抽象類
- `ImageInput`, `ClassificationOutput`
- `ModelRegistryInterface`

### 驗收標準
- [ ] Model Registry 可初始化
- [ ] DenseNet 可載入
- [ ] 輸入影像回傳分類結果
- [ ] 符合 `ClassificationOutput` 格式

### 不要做
- ❌ 不要做 MCP Server
- ❌ 不要做 VQA/Segmentation（Phase 2）
- ❌ 不要改 `contracts/` 介面

---

## 🟡 主 Terminal: Integration Agent（你 + 我）

### 任務摘要
我們負責 **協調和整合**。

### 工作目錄
```bash
cd /root/workspace251215/MedRAX
```

### 任務清單

1. **監控各 Agent 進度**
2. **處理介面契約問題**
3. **整合測試**
4. **解決 merge 衝突**
5. **規劃下一 Phase**

---

## 溝通協議

### 各 Agent 完成任務後
回報格式：
```
✅ 完成：[任務名稱]
📁 修改的檔案：
  - file1.py
  - file2.ts
🧪 測試結果：[通過/失敗]
❓ 問題/疑問：[如果有]
```

### 遇到問題時
```
❌ 阻塞：[問題描述]
📍 檔案/位置：[相關檔案]
💡 可能解法：[如果有想法]
```

### 需要改介面契約時
```
🔄 請求修改契約：
  - 檔案：contracts/xxx.py
  - 原因：[為什麼需要改]
  - 提議：[新的定義]
```
等待主 Terminal 確認後才能改。
