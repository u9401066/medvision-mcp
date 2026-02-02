"""
MedRAX AI Models Interface Contracts

這些是 AI 模型封裝層必須遵守的介面。
Model Registry 與各模型實作都需要符合這些規範。
"""

from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Union
from enum import Enum
import numpy as np
from pathlib import Path


# === Enums ===

class ModelType(str, Enum):
    CLASSIFIER = "classifier"
    SEGMENTER = "segmenter"
    VQA = "vqa"
    REPORT_GENERATOR = "report_generator"
    GROUNDING = "grounding"
    ENCODER = "encoder"
    INTERACTIVE_SEGMENTER = "interactive_segmenter"


class InferenceBackend(str, Enum):
    PYTORCH = "pytorch"
    VLLM = "vllm"
    OLLAMA = "ollama"
    ONNX = "onnx"


# === Input/Output Schemas ===

class ImageInput(BaseModel):
    """統一影像輸入格式"""
    path: Optional[str] = None  # 檔案路徑
    array: Optional[Any] = None  # numpy array (序列化時忽略)
    base64: Optional[str] = None  # base64 編碼
    url: Optional[str] = None  # 遠端 URL
    
    class Config:
        arbitrary_types_allowed = True


class ClassificationOutput(BaseModel):
    """分類模型輸出"""
    predictions: List[Dict[str, float]]  # [{"label": "Cardiomegaly", "confidence": 0.85}, ...]
    model_name: str
    processing_time_ms: int


class SegmentationOutput(BaseModel):
    """分割模型輸出"""
    mask_path: Optional[str] = None  # 遮罩檔案路徑
    mask_base64: Optional[str] = None  # 遮罩 base64
    labels: Dict[int, str]  # {1: "lung_left", 2: "lung_right", ...}
    model_name: str
    processing_time_ms: int


class VQAOutput(BaseModel):
    """VQA 模型輸出"""
    answer: str
    confidence: Optional[float] = None
    model_name: str
    processing_time_ms: int


class ReportOutput(BaseModel):
    """報告生成輸出"""
    report_text: str
    findings: Optional[List[str]] = None
    impressions: Optional[List[str]] = None
    model_name: str
    processing_time_ms: int


class GroundingOutput(BaseModel):
    """Grounding 模型輸出"""
    detections: List[Dict[str, Any]]  # [{"label": "nodule", "bbox": [...], "confidence": 0.9}, ...]
    model_name: str
    processing_time_ms: int


class EncoderOutput(BaseModel):
    """編碼器輸出"""
    embedding: List[float]  # 特徵向量
    embedding_dim: int
    model_name: str
    processing_time_ms: int


class InteractiveSegmentOutput(BaseModel):
    """互動分割輸出"""
    masks: List[str]  # 多個候選遮罩路徑或 base64
    scores: List[float]  # 各遮罩信心度
    best_mask_idx: int
    model_name: str
    processing_time_ms: int


# === Abstract Base Classes ===

class BaseModel_(ABC):
    """所有模型的基類"""
    
    @property
    @abstractmethod
    def model_name(self) -> str:
        """模型名稱"""
        pass
    
    @property
    @abstractmethod
    def model_type(self) -> ModelType:
        """模型類型"""
        pass
    
    @property
    @abstractmethod
    def backend(self) -> InferenceBackend:
        """推理後端"""
        pass
    
    @abstractmethod
    def load(self) -> None:
        """載入模型到記憶體"""
        pass
    
    @abstractmethod
    def unload(self) -> None:
        """從記憶體卸載模型"""
        pass
    
    @property
    @abstractmethod
    def is_loaded(self) -> bool:
        """模型是否已載入"""
        pass


class ClassifierModel(BaseModel_):
    """分類模型介面"""
    
    @abstractmethod
    def predict(
        self, 
        image: ImageInput,
        threshold: float = 0.5,
        top_k: Optional[int] = None
    ) -> ClassificationOutput:
        """執行分類預測"""
        pass


class SegmentationModel(BaseModel_):
    """分割模型介面"""
    
    @abstractmethod
    def segment(
        self,
        image: ImageInput,
        target_organs: Optional[List[str]] = None
    ) -> SegmentationOutput:
        """執行分割"""
        pass


class VQAModel(BaseModel_):
    """VQA 模型介面"""
    
    @abstractmethod
    def answer(
        self,
        image: ImageInput,
        question: str,
        context: Optional[str] = None
    ) -> VQAOutput:
        """回答問題"""
        pass


class ReportGeneratorModel(BaseModel_):
    """報告生成模型介面"""
    
    @abstractmethod
    def generate(
        self,
        image: ImageInput,
        findings_only: bool = False,
        template: Optional[str] = None
    ) -> ReportOutput:
        """生成報告"""
        pass


class GroundingModel(BaseModel_):
    """Grounding 模型介面"""
    
    @abstractmethod
    def ground(
        self,
        image: ImageInput,
        phrases: List[str],
        threshold: float = 0.5
    ) -> GroundingOutput:
        """執行短語定位"""
        pass


class EncoderModel(BaseModel_):
    """編碼器模型介面"""
    
    @abstractmethod
    def encode(
        self,
        image: ImageInput
    ) -> EncoderOutput:
        """產生影像嵌入"""
        pass


class InteractiveSegmentModel(BaseModel_):
    """互動分割模型介面 (如 SAM)"""
    
    @abstractmethod
    def segment_point(
        self,
        image: ImageInput,
        points: List[List[int]],  # [[x, y], ...]
        labels: Optional[List[int]] = None,  # 1=foreground, 0=background
        multimask: bool = True
    ) -> InteractiveSegmentOutput:
        """點擊分割"""
        pass
    
    @abstractmethod
    def segment_box(
        self,
        image: ImageInput,
        box: List[int]  # [x1, y1, x2, y2]
    ) -> InteractiveSegmentOutput:
        """框選分割"""
        pass
    
    @abstractmethod
    def segment_text(
        self,
        image: ImageInput,
        text_prompt: str
    ) -> InteractiveSegmentOutput:
        """文字提示分割"""
        pass


# === Model Registry Interface ===

class ModelRegistryInterface(ABC):
    """Model Registry 必須實作的介面"""
    
    @abstractmethod
    def register(self, model: BaseModel_) -> None:
        """註冊模型"""
        pass
    
    @abstractmethod
    def get(self, model_name: str) -> BaseModel_:
        """取得模型實例"""
        pass
    
    @abstractmethod
    def list_models(self, model_type: Optional[ModelType] = None) -> List[str]:
        """列出可用模型"""
        pass
    
    @abstractmethod
    def load_model(self, model_name: str) -> None:
        """載入指定模型"""
        pass
    
    @abstractmethod
    def unload_model(self, model_name: str) -> None:
        """卸載指定模型"""
        pass
    
    @abstractmethod
    def get_loaded_models(self) -> List[str]:
        """取得目前已載入的模型"""
        pass
    
    @abstractmethod
    def get_memory_usage(self) -> Dict[str, int]:
        """取得各模型記憶體使用量 (bytes)"""
        pass


# === Model Configuration ===

class ModelConfig(BaseModel):
    """模型配置"""
    name: str
    type: ModelType
    backend: InferenceBackend
    model_path: str  # HuggingFace ID 或本地路徑
    device: str = "cuda"
    quantization: Optional[str] = None  # "awq", "gptq", "int8"
    max_batch_size: int = 1
    lazy_load: bool = True  # 延遲載入
    priority: int = 0  # 載入優先順序 (越高越優先)
    vram_estimate_mb: int = 0  # 預估 VRAM 使用量


class ModelRegistryConfig(BaseModel):
    """Model Registry 配置"""
    models: List[ModelConfig]
    max_loaded_models: int = 5
    auto_unload: bool = True  # VRAM 不足時自動卸載低優先順序模型
    cache_dir: str = "/model-cache"
