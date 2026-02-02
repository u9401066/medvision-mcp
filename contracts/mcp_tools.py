"""
MedRAX MCP Tools Interface Contracts

這些是 MCP Server 與 Canvas UI 之間的介面契約。
所有 Worktree 必須遵守這些定義。

變更規則：
- 變更前必須在 PR 中討論
- 所有 Agent 必須同意
- 變更後各 Worktree 需同步更新
"""

from pydantic import BaseModel, Field
from typing import Literal, Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# === Enums ===

class ImageType(str, Enum):
    CXR = "CXR"
    KUB = "KUB"
    EKG = "EKG"
    CT = "CT"
    MRI = "MRI"
    DICOM = "DICOM"
    OTHER = "Other"


class RegionType(str, Enum):
    BBOX = "bbox"
    POLYGON = "polygon"
    POINT = "point"
    MASK = "mask"


class AnnotationSource(str, Enum):
    AI = "ai"
    USER = "user"
    SYSTEM = "system"


class CanvasAction(str, Enum):
    ADD_LAYER = "add_layer"
    UPDATE_LAYER = "update_layer"
    REMOVE_LAYER = "remove_layer"
    HIGHLIGHT = "highlight"


class AnalysisAction(str, Enum):
    DESCRIBE = "describe"
    SEGMENT = "segment"
    MEASURE = "measure"
    COMPARE = "compare"


# === Core Models ===

class Region(BaseModel):
    """區域定義 - Canvas 繪圖與分析共用"""
    type: RegionType
    coordinates: Any  # bbox: [x1,y1,x2,y2], polygon: [[x,y],...], point: [x,y]
    format: Literal["pixel", "relative"] = "pixel"
    
    class Config:
        json_schema_extra = {
            "examples": [
                {"type": "bbox", "coordinates": [100, 200, 300, 400], "format": "pixel"},
                {"type": "polygon", "coordinates": [[100, 100], [200, 100], [200, 200]], "format": "pixel"},
                {"type": "point", "coordinates": [150, 150], "format": "pixel"},
            ]
        }


class CanvasLayer(BaseModel):
    """Canvas 圖層 - Server 推送到 UI"""
    id: str
    type: Literal["segmentation", "bbox", "annotation", "user_drawing", "measurement"]
    visible: bool = True
    opacity: float = 0.7
    color: Optional[str] = None  # hex color
    label: Optional[str] = None
    data: Dict[str, Any]  # 具體內容依 type 不同


# === Session Management ===

class CreateSessionRequest(BaseModel):
    """建立新 Session"""
    name: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class CreateSessionResponse(BaseModel):
    """建立 Session 回應"""
    session_id: str
    ui_url: Optional[str] = None
    created_at: datetime


class AddImageRequest(BaseModel):
    """加入影像到 Session"""
    session_id: str
    image_path: str  # 本地路徑或 URL
    image_type: Optional[ImageType] = None  # None = 自動偵測
    auto_analyze: bool = True
    analysis_config: Optional[Dict[str, Any]] = None


class AddImageResponse(BaseModel):
    """加入影像回應"""
    image_id: str
    detected_type: ImageType
    width: int
    height: int
    auto_analysis: Optional[Dict[str, Any]] = None  # 如果啟用 auto_analyze


class SessionStatus(BaseModel):
    """Session 狀態"""
    session_id: str
    name: Optional[str] = None
    image_count: int
    current_image_id: Optional[str] = None
    annotation_count: int
    created_at: datetime
    updated_at: datetime


# === Analysis Tools ===

class AnalyzeImageRequest(BaseModel):
    """分析影像請求"""
    session_id: str
    image_id: Optional[str] = None  # None = 當前影像
    
    # 分析開關
    classify: bool = True
    detect: bool = False
    segment: bool = False
    generate_report: bool = False
    
    # 配置
    classification_threshold: float = 0.5
    detection_phrases: Optional[List[str]] = None  # 自定義偵測目標


class ClassificationResult(BaseModel):
    """分類結果"""
    label: str
    confidence: float
    category: Optional[str] = None  # 疾病類別


class DetectionResult(BaseModel):
    """偵測結果"""
    label: str
    confidence: float
    bbox: List[float]  # [x1, y1, x2, y2]
    annotation_id: Optional[str] = None


class AnalyzeImageResponse(BaseModel):
    """分析影像回應"""
    image_id: str
    classification: Optional[List[ClassificationResult]] = None
    detections: Optional[List[DetectionResult]] = None
    segmentation: Optional[Dict[str, Any]] = None  # mask 資訊
    report: Optional[str] = None
    processing_time_ms: int


# === Interactive Analysis ===

class AnalyzeRegionRequest(BaseModel):
    """分析選定區域請求"""
    session_id: str
    region: Region
    question: Optional[str] = None  # VQA 問題
    actions: List[AnalysisAction] = [AnalysisAction.DESCRIBE]
    image_id: Optional[str] = None  # None = 當前影像


class AnalyzeRegionResponse(BaseModel):
    """分析區域回應"""
    description: Optional[str] = None
    segmentation: Optional[Dict[str, Any]] = None
    measurements: Optional[Dict[str, Any]] = None
    annotation_id: Optional[str] = None
    confidence: Optional[float] = None


class AskImageRequest(BaseModel):
    """VQA 請求"""
    session_id: str
    question: str
    image_id: Optional[str] = None
    include_context: bool = True  # 包含先前分析結果


class AskImageResponse(BaseModel):
    """VQA 回應"""
    answer: str
    confidence: Optional[float] = None
    references: Optional[List[str]] = None  # 參考的區域 ID


# === Canvas Sync ===

class PushToCanvasRequest(BaseModel):
    """推送視覺化到 Canvas"""
    session_id: str
    action: CanvasAction
    payload: Dict[str, Any]
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "session_id": "abc123",
                    "action": "add_layer",
                    "payload": {
                        "layer": {
                            "id": "seg_001",
                            "type": "segmentation",
                            "data": {"mask_url": "/masks/seg_001.png"}
                        }
                    }
                },
                {
                    "session_id": "abc123",
                    "action": "highlight",
                    "payload": {
                        "region": {"type": "bbox", "coordinates": [100, 200, 300, 400]},
                        "style": "pulse",
                        "duration_ms": 2000
                    }
                }
            ]
        }


class CanvasStateSync(BaseModel):
    """Canvas 狀態同步 (UI → Server)"""
    session_id: str
    viewport: Dict[str, Any]  # zoom, pan position
    active_tool: Optional[str] = None
    user_drawings: List[Dict[str, Any]] = []
    pending_selection: Optional[Region] = None


# === Annotations ===

class CreateAnnotationRequest(BaseModel):
    """建立標註"""
    session_id: str
    image_id: Optional[str] = None
    type: RegionType
    coordinates: Any
    label: str
    notes: Optional[str] = None
    source: AnnotationSource = AnnotationSource.USER


class AnnotationResponse(BaseModel):
    """標註回應"""
    annotation_id: str
    image_id: str
    type: RegionType
    coordinates: Any
    label: str
    confidence: Optional[float] = None
    source: AnnotationSource
    created_at: datetime


# === Agent Tools (A2A) ===

class InvokeAgentRequest(BaseModel):
    """委託 MedRAX Agent 執行任務"""
    session_id: str
    task: str  # 自然語言任務描述
    context: Optional[Dict[str, Any]] = None
    mode: Literal["auto", "interactive", "step_by_step"] = "auto"


class AgentActionTaken(BaseModel):
    """Agent 執行的動作"""
    tool: str
    params: Dict[str, Any]
    result_summary: str


class InvokeAgentResponse(BaseModel):
    """Agent 執行結果"""
    status: Literal["completed", "need_input", "in_progress", "error"]
    result: Optional[Dict[str, Any]] = None
    actions_taken: List[AgentActionTaken] = []
    follow_up_suggestions: List[str] = []
    error_message: Optional[str] = None


# === MCP Resources (Server → Client 訂閱) ===

class ResourceUpdate(BaseModel):
    """MCP Resource 更新通知"""
    resource_uri: str  # e.g., "session/{id}/annotations"
    event_type: Literal["created", "updated", "deleted"]
    data: Dict[str, Any]
    timestamp: datetime


# === Error Responses ===

class MCPError(BaseModel):
    """MCP 錯誤回應"""
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    
    class Config:
        json_schema_extra = {
            "examples": [
                {"code": "SESSION_NOT_FOUND", "message": "Session abc123 not found"},
                {"code": "INVALID_REGION", "message": "Region coordinates are invalid"},
                {"code": "MODEL_LOAD_ERROR", "message": "Failed to load CheXagent model"},
            ]
        }
