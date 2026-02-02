"""MedVision MCP Server - Main entry point.

Visual RAG Mode B: RAD-DINO + FAISS + DenseNet
"""

import os
from pathlib import Path
from typing import Optional

from mcp.server import FastMCP

from .tools.visual_rag import VisualRAGEngine

# Initialize MCP Server
mcp = FastMCP("medvision-mcp")

# Global Visual RAG engine (lazy loaded)
_rag_engine: Optional[VisualRAGEngine] = None


def get_rag_engine() -> VisualRAGEngine:
    """Get or create Visual RAG engine (singleton)."""
    global _rag_engine
    if _rag_engine is None:
        # Check for pre-built index
        index_path = os.environ.get("MEDVISION_INDEX_PATH", None)
        _rag_engine = VisualRAGEngine(index_path=index_path)
    return _rag_engine


# ============================================================================
# Core Visual RAG Tools
# ============================================================================


@mcp.tool()
async def analyze_xray(
    image_path: str,
    mode: str = "full",
    top_k: int = 5,
    threshold: float = 0.5,
) -> dict:
    """Analyze chest X-ray using Visual RAG (DenseNet + RAD-DINO + FAISS).
    
    Args:
        image_path: Path to X-ray image (DICOM, PNG, JPG)
        mode: Analysis mode:
            - 'quick': Only DenseNet classification (fastest)
            - 'full': Classification + RAG similarity search
            - 'rag_only': Only RAG search (no classification)
        top_k: Number of similar cases to retrieve
        threshold: Probability threshold for positive findings
    
    Returns:
        Analysis results including:
        - classification: DenseNet pathology predictions
        - similar_cases: Similar historical cases from RAG
        - aggregated_labels: Weighted labels from similar cases
        - confidence_summary: Human-readable summary
    
    Example:
        >>> result = await analyze_xray("chest.png", mode="full")
        >>> print(result["confidence_summary"])
        "DenseNet: Infiltration (85%) | RAG Top-1: mimic-001 (92%)"
    """
    if not Path(image_path).exists():
        return {"error": f"Image not found: {image_path}"}
    
    engine = get_rag_engine()
    result = engine.analyze(
        image_path,
        mode=mode,
        top_k=top_k,
        classification_threshold=threshold,
    )
    
    return result


@mcp.tool()
async def search_similar_cases(
    image_path: str,
    top_k: int = 5,
    include_reports: bool = True,
) -> dict:
    """Search for similar historical cases using Visual RAG.
    
    Uses RAD-DINO to encode the image and FAISS for similarity search.
    
    Args:
        image_path: Path to X-ray image
        top_k: Number of similar cases to return
        include_reports: Whether to include full reports in results
    
    Returns:
        similar_cases: List of similar cases with:
            - case_id: Case identifier
            - similarity: Similarity score (0-1)
            - report: Report text (if include_reports=True)
            - labels: Pathology labels
        aggregated_labels: Weighted labels from all similar cases
    
    Example:
        >>> result = await search_similar_cases("chest.png", top_k=3)
        >>> for case in result["similar_cases"]:
        ...     print(f"{case['case_id']}: {case['similarity']:.0%}")
    """
    if not Path(image_path).exists():
        return {"error": f"Image not found: {image_path}"}
    
    engine = get_rag_engine()
    
    if engine.index is None or engine.index_size == 0:
        return {
            "warning": "No reference index loaded. Use build_rag_index first.",
            "similar_cases": [],
            "aggregated_labels": [],
        }
    
    similar = engine.search_similar(image_path, top_k=top_k)
    
    # Optionally filter out reports
    if not include_reports:
        for case in similar:
            case.pop("report", None)
    
    # Aggregate labels
    aggregated = engine._aggregate_labels(similar)
    
    return {
        "similar_cases": similar,
        "aggregated_labels": aggregated,
        "index_size": engine.index_size,
    }


@mcp.tool()
async def classify_xray(
    image_path: str,
    threshold: float = 0.5,
) -> dict:
    """Quick X-ray classification using DenseNet-121.
    
    Classifies chest X-ray for 18 pathology types.
    
    Args:
        image_path: Path to X-ray image
        threshold: Probability threshold for positive findings
    
    Returns:
        predictions: All pathology probabilities
        positive_findings: Findings above threshold
        top_finding: Most likely pathology
        top_probability: Probability of top finding
    
    Example:
        >>> result = await classify_xray("chest.png")
        >>> print(f"Top finding: {result['top_finding']} ({result['top_probability']:.0%})")
    """
    if not Path(image_path).exists():
        return {"error": f"Image not found: {image_path}"}
    
    engine = get_rag_engine()
    return engine.classify_image(image_path, threshold=threshold)


@mcp.tool()
async def build_rag_index(
    image_dir: str,
    metadata_file: Optional[str] = None,
    output_path: str = "./rag_index",
) -> dict:
    """Build Visual RAG index from image directory.
    
    Encodes images with RAD-DINO and builds FAISS index.
    
    Args:
        image_dir: Directory containing X-ray images
        metadata_file: Optional JSON file with metadata (case_id, labels, report)
        output_path: Path to save the index
    
    Returns:
        status: Build status
        index_size: Number of indexed images
        output_path: Path to saved index
    
    Example:
        >>> result = await build_rag_index("./images", "./metadata.json", "./my_index")
        >>> print(f"Indexed {result['index_size']} images")
    """
    import json
    
    image_dir = Path(image_dir)
    if not image_dir.exists():
        return {"error": f"Directory not found: {image_dir}"}
    
    # Find images
    image_extensions = {".png", ".jpg", ".jpeg", ".dcm", ".dicom"}
    images = [
        p for p in image_dir.iterdir()
        if p.suffix.lower() in image_extensions
    ]
    
    if not images:
        return {"error": "No images found in directory"}
    
    # Load metadata
    metadata = []
    if metadata_file and Path(metadata_file).exists():
        with open(metadata_file) as f:
            metadata_list = json.load(f)
            # Index by filename
            metadata_map = {
                Path(m.get("image_path", m.get("filename", ""))).name: m
                for m in metadata_list
            }
    else:
        metadata_map = {}
    
    # Build metadata list
    for img in images:
        if img.name in metadata_map:
            meta = metadata_map[img.name]
        else:
            meta = {
                "case_id": img.stem,
                "image_path": str(img),
                "labels": [],
            }
        meta["image_path"] = str(img)
        metadata.append(meta)
    
    # Build index
    engine = get_rag_engine()
    engine.build_index(
        images=[str(p) for p in images],
        metadata=metadata,
        save_path=output_path,
    )
    
    return {
        "status": "success",
        "index_size": engine.index_size,
        "output_path": str(Path(output_path).absolute()),
    }


@mcp.tool()
async def load_rag_index(index_path: str) -> dict:
    """Load a pre-built Visual RAG index.
    
    Args:
        index_path: Path to index directory
    
    Returns:
        status: Load status
        index_size: Number of entries in index
    """
    if not Path(index_path).exists():
        return {"error": f"Index not found: {index_path}"}
    
    engine = get_rag_engine()
    engine.load_index(index_path)
    
    return {
        "status": "success",
        "index_size": engine.index_size,
    }


@mcp.tool()
async def get_engine_status() -> dict:
    """Get Visual RAG engine status.
    
    Returns:
        encoder_loaded: Whether RAD-DINO is loaded
        classifier_loaded: Whether DenseNet is loaded
        index_size: Number of entries in FAISS index
        device: Current device (cuda/cpu)
    """
    engine = get_rag_engine()
    
    return {
        "encoder_loaded": engine.encoder.is_loaded,
        "classifier_loaded": engine.classifier.is_loaded,
        "index_size": engine.index_size,
        "device": engine.device,
    }


# ============================================================================
# Legacy placeholder tools (for backward compatibility)
# ============================================================================


@mcp.tool()
async def segment_region(image_path: str, region: str) -> dict:
    """Segment anatomical region in medical image.
    
    Args:
        image_path: Path to medical image
        region: Anatomical region to segment (lung, heart, etc.)
    
    Returns:
        Segmentation mask and metadata
    
    Note: Requires Medical-SAM3, not yet implemented.
    """
    return {
        "status": "not_implemented",
        "message": "SAM3 segmentation will be added in Phase 3",
        "image_path": image_path,
        "region": region,
    }


@mcp.tool()
async def medical_vqa(image_path: str, question: str) -> dict:
    """Answer questions about medical images.
    
    Args:
        image_path: Path to medical image
        question: Question about the image
    
    Returns:
        Answer and confidence score
    
    Note: For now, use analyze_xray + LLM for Q&A.
    """
    # Use Visual RAG to provide context, then suggest LLM completion
    if not Path(image_path).exists():
        return {"error": f"Image not found: {image_path}"}
    
    engine = get_rag_engine()
    analysis = engine.analyze(image_path, mode="full", top_k=3)
    
    return {
        "status": "partial",
        "message": "Use this context with LLM to answer questions",
        "question": question,
        "context": {
            "classification": analysis.get("classification"),
            "similar_cases": analysis.get("similar_cases"),
            "confidence_summary": analysis.get("confidence_summary"),
        },
    }


def main():
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
