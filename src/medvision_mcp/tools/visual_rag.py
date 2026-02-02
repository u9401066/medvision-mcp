"""Visual RAG Engine for medical image analysis."""

from pathlib import Path
from typing import Optional, Union

import numpy as np
from PIL import Image

from ..models.densenet import DenseNetClassifier
from ..models.faiss_index import FaissIndex
from ..models.rad_dino import RadDinoEncoder


class VisualRAGEngine:
    """Visual RAG Engine: RAD-DINO + FAISS + DenseNet.
    
    Combines image encoding, similarity search, and classification
    for comprehensive medical image analysis.
    """
    
    def __init__(
        self,
        index_path: Optional[str | Path] = None,
        device: str = "auto",
    ):
        """Initialize Visual RAG Engine.
        
        Args:
            index_path: Path to pre-built FAISS index (optional)
            device: Device to use ('auto', 'cuda', 'cpu')
        """
        self.device = device
        self.encoder = RadDinoEncoder(device=device)
        self.classifier = DenseNetClassifier(device=device)
        self.index: Optional[FaissIndex] = None
        
        if index_path and Path(index_path).exists():
            self.index = FaissIndex.load(index_path)
    
    def encode_image(
        self, 
        image: Union[str, Path, Image.Image, np.ndarray]
    ) -> np.ndarray:
        """Encode image to embedding vector.
        
        Args:
            image: Input image
            
        Returns:
            768-dim embedding vector
        """
        return self.encoder.encode(image)
    
    def classify_image(
        self,
        image: Union[str, Path, Image.Image, np.ndarray],
        threshold: float = 0.5,
    ) -> dict:
        """Classify image for pathologies.
        
        Args:
            image: Input image
            threshold: Probability threshold for positive findings
            
        Returns:
            Classification results
        """
        return self.classifier.classify(image, threshold=threshold)
    
    def search_similar(
        self,
        image: Union[str, Path, Image.Image, np.ndarray],
        top_k: int = 5,
    ) -> list[dict]:
        """Search for similar images in index.
        
        Args:
            image: Input image
            top_k: Number of results to return
            
        Returns:
            List of similar cases with metadata
        """
        if self.index is None or len(self.index) == 0:
            return []
        
        embedding = self.encode_image(image)
        return self.index.search(embedding, top_k=top_k)
    
    def analyze(
        self,
        image: Union[str, Path, Image.Image, np.ndarray],
        mode: str = "full",
        top_k: int = 5,
        classification_threshold: float = 0.5,
    ) -> dict:
        """Full Visual RAG analysis.
        
        Args:
            image: Input image
            mode: Analysis mode ('quick', 'full', 'rag_only')
                - quick: Only classification
                - full: Classification + RAG + embedding
                - rag_only: Only RAG search (no classification)
            top_k: Number of similar cases to retrieve
            classification_threshold: Threshold for positive findings
            
        Returns:
            Complete analysis results
        """
        result = {
            "mode": mode,
            "classification": None,
            "similar_cases": [],
            "embedding": None,
            "aggregated_labels": [],
        }
        
        # Classification (quick or full mode)
        if mode in ("quick", "full"):
            result["classification"] = self.classify_image(
                image, threshold=classification_threshold
            )
        
        # RAG search (full or rag_only mode)
        if mode in ("full", "rag_only"):
            similar = self.search_similar(image, top_k=top_k)
            result["similar_cases"] = similar
            
            # Aggregate labels from similar cases
            if similar:
                result["aggregated_labels"] = self._aggregate_labels(similar)
        
        # Include embedding for full mode
        if mode == "full":
            embedding = self.encode_image(image)
            result["embedding_dim"] = len(embedding)
            # Don't return raw embedding by default (too large for JSON)
        
        # Build confidence summary
        result["confidence_summary"] = self._build_summary(result)
        
        return result
    
    def _aggregate_labels(self, similar_cases: list[dict]) -> list[dict]:
        """Aggregate labels from similar cases with weighted voting.
        
        Args:
            similar_cases: List of similar cases with metadata
            
        Returns:
            Aggregated labels with confidence scores
        """
        label_scores: dict[str, float] = {}
        label_counts: dict[str, int] = {}
        
        for case in similar_cases:
            labels = case.get("labels", [])
            similarity = case.get("similarity", 0.5)
            
            for label in labels:
                if isinstance(label, dict):
                    label_name = label.get("name", label.get("label", str(label)))
                else:
                    label_name = str(label)
                
                label_scores[label_name] = label_scores.get(label_name, 0) + similarity
                label_counts[label_name] = label_counts.get(label_name, 0) + 1
        
        # Normalize and sort
        aggregated = []
        for label, score in label_scores.items():
            count = label_counts[label]
            avg_confidence = score / count if count > 0 else 0
            aggregated.append({
                "label": label,
                "confidence": avg_confidence,
                "supporting_cases": count,
            })
        
        return sorted(aggregated, key=lambda x: x["confidence"], reverse=True)
    
    def _build_summary(self, result: dict) -> str:
        """Build human-readable confidence summary.
        
        Args:
            result: Analysis result dictionary
            
        Returns:
            Summary string
        """
        parts = []
        
        # Classification summary
        if result.get("classification"):
            top = result["classification"].get("top_finding")
            prob = result["classification"].get("top_probability", 0)
            if top:
                parts.append(f"DenseNet: {top} ({prob:.0%})")
        
        # RAG summary
        if result.get("similar_cases"):
            top_case = result["similar_cases"][0]
            sim = top_case.get("similarity", 0)
            case_id = top_case.get("case_id", "unknown")
            parts.append(f"RAG Top-1: {case_id} ({sim:.0%})")
        
        return " | ".join(parts) if parts else "No analysis performed"
    
    def build_index(
        self,
        images: list[Union[str, Path]],
        metadata: list[dict],
        save_path: Optional[str | Path] = None,
    ) -> FaissIndex:
        """Build FAISS index from images.
        
        Args:
            images: List of image paths
            metadata: List of metadata dicts (must include case_id, labels, etc.)
            save_path: Path to save index (optional)
            
        Returns:
            Built FaissIndex
        """
        # Encode all images
        embeddings = self.encoder.encode_batch(images)
        
        # Build index
        self.index = FaissIndex(dimension=768, metric="L2")
        self.index.build()
        self.index.add(embeddings, metadata)
        
        # Save if path provided
        if save_path:
            self.index.save(save_path)
        
        return self.index
    
    def load_index(self, path: str | Path) -> None:
        """Load FAISS index from disk.
        
        Args:
            path: Path to index directory
        """
        self.index = FaissIndex.load(path)
    
    @property
    def index_size(self) -> int:
        """Return number of entries in index."""
        return len(self.index) if self.index else 0
    
    def unload(self) -> None:
        """Unload all models to free memory."""
        self.encoder.unload()
        self.classifier.unload()
