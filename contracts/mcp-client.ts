/**
 * MedRAX Canvas UI Interface Contracts
 * 
 * Canvas UI 必須遵守的介面定義。
 * 與 Python 端的 contracts/mcp_tools.py 對應。
 */

// === Enums ===

export type ImageType = 'CXR' | 'KUB' | 'EKG' | 'CT' | 'MRI' | 'DICOM' | 'Other';
export type RegionType = 'bbox' | 'polygon' | 'point' | 'mask';
export type AnnotationSource = 'ai' | 'user' | 'system';
export type CanvasAction = 'add_layer' | 'update_layer' | 'remove_layer' | 'highlight';
export type AnalysisAction = 'describe' | 'segment' | 'measure' | 'compare';

// === Core Types ===

export interface Region {
  type: RegionType;
  coordinates: number[] | number[][];  // bbox: [x1,y1,x2,y2], polygon: [[x,y],...], point: [x,y]
  format: 'pixel' | 'relative';
}

export interface CanvasLayer {
  id: string;
  type: 'segmentation' | 'bbox' | 'annotation' | 'user_drawing' | 'measurement';
  visible: boolean;
  opacity: number;
  color?: string;
  label?: string;
  data: Record<string, any>;
}

// === Session Management ===

export interface CreateSessionRequest {
  name?: string;
  metadata?: Record<string, any>;
}

export interface CreateSessionResponse {
  session_id: string;
  ui_url?: string;
  created_at: string;
}

export interface AddImageRequest {
  session_id: string;
  image_path: string;
  image_type?: ImageType;
  auto_analyze?: boolean;
  analysis_config?: Record<string, any>;
}

export interface AddImageResponse {
  image_id: string;
  detected_type: ImageType;
  width: number;
  height: number;
  auto_analysis?: Record<string, any>;
}

export interface SessionStatus {
  session_id: string;
  name?: string;
  image_count: number;
  current_image_id?: string;
  annotation_count: number;
  created_at: string;
  updated_at: string;
}

// === Analysis ===

export interface AnalyzeImageRequest {
  session_id: string;
  image_id?: string;
  classify?: boolean;
  detect?: boolean;
  segment?: boolean;
  generate_report?: boolean;
  classification_threshold?: number;
  detection_phrases?: string[];
}

export interface ClassificationResult {
  label: string;
  confidence: number;
  category?: string;
}

export interface DetectionResult {
  label: string;
  confidence: number;
  bbox: [number, number, number, number];
  annotation_id?: string;
}

export interface AnalyzeImageResponse {
  image_id: string;
  classification?: ClassificationResult[];
  detections?: DetectionResult[];
  segmentation?: Record<string, any>;
  report?: string;
  processing_time_ms: number;
}

export interface AnalyzeRegionRequest {
  session_id: string;
  region: Region;
  question?: string;
  actions?: AnalysisAction[];
  image_id?: string;
}

export interface AnalyzeRegionResponse {
  description?: string;
  segmentation?: Record<string, any>;
  measurements?: Record<string, any>;
  annotation_id?: string;
  confidence?: number;
}

export interface AskImageRequest {
  session_id: string;
  question: string;
  image_id?: string;
  include_context?: boolean;
}

export interface AskImageResponse {
  answer: string;
  confidence?: number;
  references?: string[];
}

// === Canvas Sync ===

export interface PushToCanvasPayload {
  layer?: CanvasLayer;
  region?: Region;
  style?: 'pulse' | 'glow' | 'outline';
  duration_ms?: number;
  layer_id?: string;
}

export interface PushToCanvasRequest {
  session_id: string;
  action: CanvasAction;
  payload: PushToCanvasPayload;
}

export interface CanvasStateSync {
  session_id: string;
  viewport: {
    zoom: number;
    pan_x: number;
    pan_y: number;
  };
  active_tool?: string;
  user_drawings: Array<{
    id: string;
    type: RegionType;
    coordinates: any;
    temporary: boolean;
  }>;
  pending_selection?: Region;
}

// === Annotations ===

export interface CreateAnnotationRequest {
  session_id: string;
  image_id?: string;
  type: RegionType;
  coordinates: any;
  label: string;
  notes?: string;
  source?: AnnotationSource;
}

export interface AnnotationResponse {
  annotation_id: string;
  image_id: string;
  type: RegionType;
  coordinates: any;
  label: string;
  confidence?: number;
  source: AnnotationSource;
  created_at: string;
}

// === Agent (A2A) ===

export interface InvokeAgentRequest {
  session_id: string;
  task: string;
  context?: Record<string, any>;
  mode?: 'auto' | 'interactive' | 'step_by_step';
}

export interface AgentActionTaken {
  tool: string;
  params: Record<string, any>;
  result_summary: string;
}

export interface InvokeAgentResponse {
  status: 'completed' | 'need_input' | 'in_progress' | 'error';
  result?: Record<string, any>;
  actions_taken: AgentActionTaken[];
  follow_up_suggestions: string[];
  error_message?: string;
}

// === MCP Resources (Subscription) ===

export interface ResourceUpdate {
  resource_uri: string;
  event_type: 'created' | 'updated' | 'deleted';
  data: Record<string, any>;
  timestamp: string;
}

// === Error ===

export interface MCPError {
  code: string;
  message: string;
  details?: Record<string, any>;
}

// === MCP Client Interface ===

/**
 * Canvas UI 必須實作的 MCP Client
 */
export interface MCPClient {
  // Connection
  connect(serverUrl: string): Promise<void>;
  disconnect(): Promise<void>;
  isConnected(): boolean;
  
  // Session Management
  createSession(params?: CreateSessionRequest): Promise<CreateSessionResponse>;
  getSessionStatus(sessionId: string): Promise<SessionStatus>;
  addImage(params: AddImageRequest): Promise<AddImageResponse>;
  
  // Analysis
  analyzeImage(params: AnalyzeImageRequest): Promise<AnalyzeImageResponse>;
  analyzeRegion(params: AnalyzeRegionRequest): Promise<AnalyzeRegionResponse>;
  askImage(params: AskImageRequest): Promise<AskImageResponse>;
  
  // Canvas Sync
  syncCanvasState(params: CanvasStateSync): Promise<void>;
  pushToCanvas(params: PushToCanvasRequest): Promise<void>;
  
  // Annotations
  createAnnotation(params: CreateAnnotationRequest): Promise<AnnotationResponse>;
  getAnnotations(sessionId: string, imageId?: string): Promise<AnnotationResponse[]>;
  deleteAnnotation(sessionId: string, annotationId: string): Promise<void>;
  
  // Agent (A2A)
  invokeAgent(params: InvokeAgentRequest): Promise<InvokeAgentResponse>;
  
  // Subscriptions (MCP Resources)
  subscribe(resourceUri: string, callback: (update: ResourceUpdate) => void): () => void;
}

/**
 * Canvas 事件處理器 - Canvas 組件必須實作
 */
export interface CanvasEventHandlers {
  // 用戶繪製區域完成
  onRegionDrawn: (region: Region) => void;
  
  // 用戶上傳影像
  onImageUploaded: (file: File) => void;
  
  // 收到 Server 推送的圖層
  onLayerReceived: (layer: CanvasLayer) => void;
  
  // 收到高亮請求
  onHighlightRequested: (region: Region, style: string) => void;
  
  // 用戶點擊標註
  onAnnotationClicked: (annotationId: string) => void;
  
  // 分析結果更新
  onAnalysisUpdated: (response: AnalyzeImageResponse) => void;
}

/**
 * Canvas 狀態管理 - 建議使用 Zustand
 */
export interface CanvasStore {
  // State
  sessionId: string | null;
  currentImageId: string | null;
  layers: CanvasLayer[];
  annotations: AnnotationResponse[];
  activeTool: string;
  isLoading: boolean;
  error: MCPError | null;
  
  // Actions
  setSession: (sessionId: string) => void;
  setCurrentImage: (imageId: string) => void;
  addLayer: (layer: CanvasLayer) => void;
  updateLayer: (layerId: string, updates: Partial<CanvasLayer>) => void;
  removeLayer: (layerId: string) => void;
  setActiveTool: (tool: string) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: MCPError | null) => void;
  reset: () => void;
}
