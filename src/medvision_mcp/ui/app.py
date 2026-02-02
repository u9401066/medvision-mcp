"""MedVision Gradio Canvas UI.

Phase 1B: Interactive X-ray analysis with Visual RAG.
"""

import json
from pathlib import Path
from typing import Optional

import gradio as gr
import numpy as np
from PIL import Image

from ..tools.visual_rag import VisualRAGEngine

# Global engine (lazy loaded)
_engine: Optional[VisualRAGEngine] = None


def get_engine() -> VisualRAGEngine:
    """Get or create Visual RAG engine."""
    global _engine
    if _engine is None:
        _engine = VisualRAGEngine(device="cuda")
    return _engine


# ============================================================================
# Analysis Functions
# ============================================================================


def analyze_image(
    image: np.ndarray | Image.Image | None,
    mode: str,
    threshold: float,
    top_k: int,
) -> tuple[str, str, str]:
    """Analyze uploaded X-ray image.
    
    Returns:
        (classification_result, rag_result, summary)
    """
    if image is None:
        return "請先上傳影像", "", ""
    
    engine = get_engine()
    
    # Convert to PIL if numpy
    if isinstance(image, np.ndarray):
        image = Image.fromarray(image)
    
    # Run analysis
    result = engine.analyze(
        image,
        mode=mode.lower(),
        top_k=top_k,
        classification_threshold=threshold,
    )
    
    # Format classification results
    classification_text = ""
    if result.get("classification"):
        c = result["classification"]
        classification_text = f"**Top Finding:** {c.get('top_finding', 'N/A')} ({c.get('top_probability', 0):.1%})\n\n"
        
        if c.get("positive_findings"):
            classification_text += "### Positive Findings\n"
            for f in c["positive_findings"][:8]:
                prob = f["probability"]
                bar = "█" * int(prob * 20) + "░" * (20 - int(prob * 20))
                classification_text += f"- **{f['label']}**: {prob:.1%} `{bar}`\n"
    
    # Format RAG results
    rag_text = ""
    if result.get("similar_cases"):
        rag_text = "### Similar Historical Cases\n\n"
        for i, case in enumerate(result["similar_cases"], 1):
            sim = case.get("similarity", 0)
            case_id = case.get("case_id", "unknown")
            rag_text += f"{i}. **{case_id}** - Similarity: {sim:.1%}\n"
            if case.get("labels"):
                labels = ", ".join(str(l) for l in case["labels"][:5])
                rag_text += f"   Labels: {labels}\n"
            if case.get("report"):
                report_preview = case["report"][:200] + "..." if len(case["report"]) > 200 else case["report"]
                rag_text += f"   > {report_preview}\n"
            rag_text += "\n"
        
        if result.get("aggregated_labels"):
            rag_text += "\n### Aggregated Labels (Weighted)\n"
            for agg in result["aggregated_labels"][:5]:
                rag_text += f"- {agg['label']}: {agg['confidence']:.1%} ({agg['supporting_cases']} cases)\n"
    elif mode.lower() in ("full", "rag_only"):
        rag_text = "⚠️ No index loaded. Use 'Build Index' tab to create one."
    
    # Summary
    summary = result.get("confidence_summary", "Analysis complete")
    
    return classification_text, rag_text, summary


def classify_only(
    image: np.ndarray | Image.Image | None,
    threshold: float,
) -> str:
    """Quick classification only."""
    if image is None:
        return "請先上傳影像"
    
    engine = get_engine()
    
    if isinstance(image, np.ndarray):
        image = Image.fromarray(image)
    
    result = engine.classify_image(image, threshold=threshold)
    
    # Format as markdown table
    text = "| Pathology | Probability |\n|-----------|-------------|\n"
    for label, prob in result.get("predictions", {}).items():
        marker = "✓" if prob >= threshold else ""
        text += f"| {label} {marker} | {prob:.1%} |\n"
    
    return text


def build_index_handler(
    image_dir: str,
    metadata_file: str,
    output_path: str,
    progress: gr.Progress = gr.Progress(),
) -> str:
    """Build FAISS index from directory."""
    if not image_dir:
        return "❌ 請輸入影像目錄路徑"
    
    image_dir_path = Path(image_dir)
    if not image_dir_path.exists():
        return f"❌ 目錄不存在: {image_dir}"
    
    # Find images
    image_extensions = {".png", ".jpg", ".jpeg", ".dcm", ".dicom"}
    images = [p for p in image_dir_path.iterdir() if p.suffix.lower() in image_extensions]
    
    if not images:
        return "❌ 目錄中沒有找到影像檔案"
    
    progress(0, desc=f"Found {len(images)} images...")
    
    # Load metadata if provided
    metadata = []
    if metadata_file and Path(metadata_file).exists():
        with open(metadata_file) as f:
            metadata_list = json.load(f)
            metadata_map = {
                Path(m.get("image_path", m.get("filename", ""))).name: m
                for m in metadata_list
            }
    else:
        metadata_map = {}
    
    for img in images:
        if img.name in metadata_map:
            meta = metadata_map[img.name].copy()
        else:
            meta = {"case_id": img.stem, "labels": []}
        meta["image_path"] = str(img)
        metadata.append(meta)
    
    progress(0.1, desc="Loading models...")
    
    engine = get_engine()
    
    progress(0.3, desc="Encoding images...")
    
    # Build index
    engine.build_index(
        images=[str(p) for p in images],
        metadata=metadata,
        save_path=output_path or "./rag_index",
    )
    
    progress(1.0, desc="Complete!")
    
    return f"✅ 成功建立索引\n- 影像數量: {len(images)}\n- 儲存路徑: {output_path or './rag_index'}"


def load_index_handler(index_path: str) -> str:
    """Load existing index."""
    if not index_path:
        return "❌ 請輸入索引路徑"
    
    if not Path(index_path).exists():
        return f"❌ 索引不存在: {index_path}"
    
    engine = get_engine()
    engine.load_index(index_path)
    
    return f"✅ 索引載入成功\n- 索引大小: {engine.index_size} entries"


def get_status() -> str:
    """Get engine status."""
    engine = get_engine()
    
    return f"""### Engine Status
- **RAD-DINO Encoder:** {'✅ Loaded' if engine.encoder.is_loaded else '⏳ Not loaded'}
- **DenseNet Classifier:** {'✅ Loaded' if engine.classifier.is_loaded else '⏳ Not loaded'}
- **FAISS Index:** {engine.index_size} entries
- **Device:** {engine.device}
"""


# ============================================================================
# Gradio App
# ============================================================================


def create_app() -> gr.Blocks:
    """Create Gradio application."""
    
    with gr.Blocks(
        title="MedVision - Visual RAG for CXR",
        theme=gr.themes.Soft(),
        css="""
        .gradio-container { max-width: 1400px !important; }
        .analysis-result { min-height: 300px; }
        """,
    ) as app:
        gr.Markdown(
            """
            # 🏥 MedVision - Visual RAG for Chest X-Ray
            
            **Phase 1B**: DenseNet classification + RAD-DINO similarity search
            """
        )
        
        with gr.Tabs():
            # ================================================================
            # Tab 1: Analysis
            # ================================================================
            with gr.TabItem("📊 Analysis", id="analysis"):
                with gr.Row():
                    # Left: Image input
                    with gr.Column(scale=1):
                        image_input = gr.Image(
                            label="Upload X-Ray",
                            type="pil",
                            height=400,
                        )
                        
                        with gr.Accordion("Analysis Options", open=True):
                            mode_select = gr.Radio(
                                choices=["Quick", "Full", "RAG_only"],
                                value="Quick",
                                label="Mode",
                                info="Quick=Classification only, Full=Classification+RAG, RAG_only=Similarity only",
                            )
                            threshold_slider = gr.Slider(
                                minimum=0.1, maximum=0.9, value=0.3, step=0.05,
                                label="Classification Threshold",
                            )
                            topk_slider = gr.Slider(
                                minimum=1, maximum=20, value=5, step=1,
                                label="Top-K Similar Cases",
                            )
                        
                        analyze_btn = gr.Button("🔍 Analyze", variant="primary", size="lg")
                    
                    # Right: Results
                    with gr.Column(scale=1):
                        summary_output = gr.Textbox(
                            label="Summary",
                            interactive=False,
                            lines=1,
                        )
                        
                        with gr.Tabs():
                            with gr.TabItem("Classification"):
                                classification_output = gr.Markdown(
                                    label="Classification Results",
                                    elem_classes=["analysis-result"],
                                )
                            with gr.TabItem("Similar Cases (RAG)"):
                                rag_output = gr.Markdown(
                                    label="RAG Results",
                                    elem_classes=["analysis-result"],
                                )
                
                # Event handlers
                analyze_btn.click(
                    fn=analyze_image,
                    inputs=[image_input, mode_select, threshold_slider, topk_slider],
                    outputs=[classification_output, rag_output, summary_output],
                )
            
            # ================================================================
            # Tab 2: Quick Classification
            # ================================================================
            with gr.TabItem("⚡ Quick Classify", id="classify"):
                with gr.Row():
                    with gr.Column(scale=1):
                        classify_image_input = gr.Image(
                            label="Upload X-Ray",
                            type="pil",
                            height=350,
                        )
                        classify_threshold = gr.Slider(
                            minimum=0.1, maximum=0.9, value=0.3, step=0.05,
                            label="Threshold",
                        )
                        classify_btn = gr.Button("⚡ Classify", variant="primary")
                    
                    with gr.Column(scale=1):
                        classify_output = gr.Markdown(label="Results")
                
                classify_btn.click(
                    fn=classify_only,
                    inputs=[classify_image_input, classify_threshold],
                    outputs=[classify_output],
                )
            
            # ================================================================
            # Tab 3: Build Index
            # ================================================================
            with gr.TabItem("🔧 Build Index", id="build"):
                gr.Markdown(
                    """
                    ### Build Visual RAG Index
                    
                    Encode images with RAD-DINO and build FAISS index for similarity search.
                    """
                )
                
                with gr.Row():
                    with gr.Column():
                        index_image_dir = gr.Textbox(
                            label="Image Directory",
                            placeholder="/path/to/images",
                        )
                        index_metadata_file = gr.Textbox(
                            label="Metadata JSON (optional)",
                            placeholder="/path/to/metadata.json",
                        )
                        index_output_path = gr.Textbox(
                            label="Output Path",
                            value="./rag_index",
                        )
                        build_btn = gr.Button("🔨 Build Index", variant="primary")
                    
                    with gr.Column():
                        build_output = gr.Markdown(label="Status")
                
                with gr.Row():
                    gr.Markdown(
                        """
                        #### Metadata Format
                        ```json
                        [
                          {"filename": "image1.png", "case_id": "case-001", "labels": ["Pneumonia"], "report": "..."},
                          {"filename": "image2.dcm", "case_id": "case-002", "labels": ["Cardiomegaly"]}
                        ]
                        ```
                        """
                    )
                
                build_btn.click(
                    fn=build_index_handler,
                    inputs=[index_image_dir, index_metadata_file, index_output_path],
                    outputs=[build_output],
                )
            
            # ================================================================
            # Tab 4: Load Index
            # ================================================================
            with gr.TabItem("📂 Load Index", id="load"):
                with gr.Row():
                    with gr.Column():
                        load_index_path = gr.Textbox(
                            label="Index Path",
                            placeholder="./rag_index",
                        )
                        load_btn = gr.Button("📂 Load Index", variant="primary")
                    
                    with gr.Column():
                        load_output = gr.Markdown(label="Status")
                
                load_btn.click(
                    fn=load_index_handler,
                    inputs=[load_index_path],
                    outputs=[load_output],
                )
            
            # ================================================================
            # Tab 5: Status
            # ================================================================
            with gr.TabItem("ℹ️ Status", id="status"):
                status_output = gr.Markdown()
                refresh_btn = gr.Button("🔄 Refresh Status")
                
                refresh_btn.click(
                    fn=get_status,
                    outputs=[status_output],
                )
                
                # Auto-refresh on tab load
                app.load(fn=get_status, outputs=[status_output])
        
        gr.Markdown(
            """
            ---
            **MedVision MCP** | Phase 1B | [GitHub](https://github.com/u9401066/medvision-mcp)
            """
        )
    
    return app


def launch(
    share: bool = False,
    server_name: str = "0.0.0.0",
    server_port: int = 7860,
    **kwargs,
) -> None:
    """Launch Gradio app.
    
    Args:
        share: Create public Gradio link
        server_name: Server hostname
        server_port: Server port
        **kwargs: Additional Gradio launch arguments
    """
    app = create_app()
    app.launch(
        share=share,
        server_name=server_name,
        server_port=server_port,
        **kwargs,
    )


if __name__ == "__main__":
    launch()
