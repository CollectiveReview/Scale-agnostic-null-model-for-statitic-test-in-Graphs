"""
SciBERT-based relevance scoring module.

This module uses SciBERT embeddings to compute semantic similarity
between papers and a reference query/context.
"""

import logging
from typing import List, Dict, Tuple, Optional
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SciBERTRelevanceScorer:
    """
    Relevance scorer using SciBERT embeddings for semantic similarity.
    """
    
    def __init__(self, model_name: str = "allenai/scibert_scivocab_uncased"):
        """
        Initialize the SciBERT relevance scorer.
        
        Args:
            model_name: HuggingFace model name for SciBERT
        """
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        
    def _lazy_load_model(self):
        """Lazy load the model to avoid initialization overhead."""
        if self.model is None:
            try:
                from transformers import AutoTokenizer, AutoModel
                import torch
                
                logger.info(f"Loading SciBERT model: {self.model_name}")
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                self.model = AutoModel.from_pretrained(self.model_name)
                self.model.eval()  # Set to evaluation mode
                logger.info("SciBERT model loaded successfully")
                
            except ImportError:
                logger.error("transformers or torch not installed. Install with: pip install transformers torch")
                raise
            except Exception as e:
                logger.error(f"Error loading SciBERT model: {e}")
                raise
    
    def encode_text(self, text: str) -> np.ndarray:
        """
        Encode text into SciBERT embeddings.
        
        Args:
            text: Text to encode
            
        Returns:
            Numpy array of embeddings
        """
        self._lazy_load_model()
        
        try:
            import torch
            
            # Tokenize and encode
            inputs = self.tokenizer(
                text,
                padding=True,
                truncation=True,
                max_length=512,
                return_tensors="pt"
            )
            
            # Get embeddings
            with torch.no_grad():
                outputs = self.model(**inputs)
                # Use mean pooling over token embeddings
                embeddings = outputs.last_hidden_state.mean(dim=1)
            
            return embeddings.numpy()[0]
            
        except Exception as e:
            logger.error(f"Error encoding text: {e}")
            raise
    
    def compute_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Compute cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Cosine similarity score (0-1)
        """
        # Normalize vectors
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        # Cosine similarity
        similarity = np.dot(embedding1, embedding2) / (norm1 * norm2)
        
        # Convert to 0-1 range (from -1 to 1)
        similarity = (similarity + 1) / 2
        
        return float(similarity)
    
    def score_papers(
        self,
        papers: List[Dict],
        query: str,
        context: Optional[str] = None,
        top_k: Optional[int] = None
    ) -> List[Tuple[Dict, float]]:
        """
        Score papers based on relevance to query and optional context.
        
        Args:
            papers: List of paper dictionaries
            query: Search query or topic
            context: Optional context text for relevance
            top_k: Return only top k papers
            
        Returns:
            List of (paper, score) tuples sorted by score
        """
        if not papers:
            return []
        
        # Encode query
        query_embedding = self.encode_text(query)
        
        # Encode context if provided
        context_embedding = None
        if context:
            context_embedding = self.encode_text(context)
        
        # Score each paper
        scored_papers = []
        for paper in papers:
            # Create paper text from title and abstract
            paper_text = f"{paper.get('title', '')} {paper.get('abstract', '')}"
            
            if not paper_text.strip():
                # Skip papers without text
                continue
            
            # Encode paper
            paper_embedding = self.encode_text(paper_text)
            
            # Compute similarity with query
            query_sim = self.compute_similarity(paper_embedding, query_embedding)
            
            # Compute similarity with context if provided
            if context_embedding is not None:
                context_sim = self.compute_similarity(paper_embedding, context_embedding)
                # Weighted combination (70% query, 30% context)
                score = 0.7 * query_sim + 0.3 * context_sim
            else:
                score = query_sim
            
            scored_papers.append((paper, score))
        
        # Sort by score (descending)
        scored_papers.sort(key=lambda x: x[1], reverse=True)
        
        # Return top k if specified
        if top_k is not None:
            scored_papers = scored_papers[:top_k]
        
        logger.info(f"Scored {len(scored_papers)} papers")
        if scored_papers:
            logger.info(f"Top score: {scored_papers[0][1]:.3f}, Lowest score: {scored_papers[-1][1]:.3f}")
        
        return scored_papers
    
    def batch_encode(self, texts: List[str], batch_size: int = 8) -> List[np.ndarray]:
        """
        Encode multiple texts in batches for efficiency.
        
        Args:
            texts: List of texts to encode
            batch_size: Batch size for encoding
            
        Returns:
            List of embeddings
        """
        self._lazy_load_model()
        
        try:
            import torch
            
            embeddings = []
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                
                # Tokenize batch
                inputs = self.tokenizer(
                    batch_texts,
                    padding=True,
                    truncation=True,
                    max_length=512,
                    return_tensors="pt"
                )
                
                # Get embeddings
                with torch.no_grad():
                    outputs = self.model(**inputs)
                    batch_embeddings = outputs.last_hidden_state.mean(dim=1)
                
                embeddings.extend(batch_embeddings.numpy())
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Error in batch encoding: {e}")
            raise


class SimpleRelevanceScorer:
    """
    Simple relevance scorer using keyword matching and metadata.
    Fallback when SciBERT is not available.
    """
    
    def score_papers(
        self,
        papers: List[Dict],
        query: str,
        context: Optional[str] = None,
        top_k: Optional[int] = None
    ) -> List[Tuple[Dict, float]]:
        """
        Score papers using simple keyword matching.
        
        Args:
            papers: List of paper dictionaries
            query: Search query or topic
            context: Optional context text
            top_k: Return only top k papers
            
        Returns:
            List of (paper, score) tuples sorted by score
        """
        query_terms = set(query.lower().split())
        context_terms = set(context.lower().split()) if context else set()
        
        scored_papers = []
        for paper in papers:
            # Get paper text
            title = paper.get('title', '').lower()
            abstract = paper.get('abstract', '').lower()
            paper_text = f"{title} {abstract}"
            paper_terms = set(paper_text.split())
            
            # Compute keyword overlap
            query_overlap = len(query_terms & paper_terms) / max(len(query_terms), 1)
            
            if context_terms:
                context_overlap = len(context_terms & paper_terms) / max(len(context_terms), 1)
                score = 0.7 * query_overlap + 0.3 * context_overlap
            else:
                score = query_overlap
            
            # Boost score based on citation count
            citations = paper.get('citations', 0) or 0
            citation_boost = min(citations / 100, 1.0) * 0.1
            score += citation_boost
            
            # Boost recent papers
            year = paper.get('year')
            if year and year >= 2020:
                score += 0.05
            
            scored_papers.append((paper, score))
        
        # Sort by score
        scored_papers.sort(key=lambda x: x[1], reverse=True)
        
        if top_k is not None:
            scored_papers = scored_papers[:top_k]
        
        logger.info(f"Scored {len(scored_papers)} papers using simple scorer")
        return scored_papers
