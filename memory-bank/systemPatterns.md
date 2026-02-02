# System Patterns

> 🔧 系統層級的設計模式與約定。

## 架構模式

### 1. MCP Tool Pattern
每個 MCP Tool 遵循統一結構：

```python
@mcp.tool()
async def tool_name(param: str) -> dict:
    """Tool 說明
    
    Args:
        param: 參數說明
    
    Returns:
        結果字典
    """
    # 1. 驗證輸入
    # 2. 執行業務邏輯
    # 3. 返回標準化結果
    return {"status": "success", "data": {...}}
```

### 2. Model Registry Pattern
統一的模型管理介面：

```python
class ModelRegistry:
    def get(self, model_id: str) -> BaseModel
    def list_available() -> List[ModelInfo]
    def load(self, model_id: str) -> None
    def unload(self, model_id: str) -> None
```

### 3. Session Pattern
會話管理確保狀態一致：

```python
session = await create_session(user_id)
session.load_image(path)
session.add_annotation(...)
result = await session.analyze()
```

## 命名約定

| 類型 | 約定 | 範例 |
|------|------|------|
| MCP Tool | snake_case 動詞開頭 | `classify_xray`, `load_image` |
| Python 模組 | snake_case | `model_registry.py` |
| React 組件 | PascalCase | `CanvasWorkspace.tsx` |
| TypeScript 介面 | I 前綴 | `ICanvasState` |

## 錯誤處理

```python
# MCP Tool 錯誤返回格式
return {
    "status": "error",
    "error_code": "INVALID_IMAGE",
    "message": "Cannot load image: format not supported"
}
```

## 資料流

```
User Input → MCP Tool → Validation → Business Logic → Model Call → Result Format → Response
```

---
*Last Updated: 2026-02-02*
