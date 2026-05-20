"""
Semantic Analysis Service for Obsidian Graph
Creates logical-semantic connections between markdown content
"""

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Any, Tuple
import re
from collections import Counter
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SemanticAnalysisService:
    """Service for semantic analysis of markdown content"""

    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words="english")
        logger.info("Semantic analysis service initialized (TF-IDF based)")

    def extract_text_from_markdown(self, markdown_content: str) -> str:
        """Extract clean text from markdown content"""
        # Remove markdown syntax
        text = re.sub(r"#+\s*", "", markdown_content)  # Headers
        text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)  # Bold
        text = re.sub(r"\*([^*]+)\*", r"\1", text)  # Italic
        text = re.sub(r"`([^`]+)`", r"\1", text)  # Inline code
        text = re.sub(r"```[\s\S]*?```", "", text)  # Code blocks
        text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)  # Links
        text = re.sub(r"!\[([^\]]*)\]\([^)]+\)", "", text)  # Images
        text = re.sub(r"[-*_]{3,}", "", text)  # Horizontal rules
        text = re.sub(r"^>\s+", "", text, flags=re.MULTILINE)  # Blockquotes
        text = re.sub(r"^[-*+]\s+", "", text, flags=re.MULTILINE)  # Lists
        text = re.sub(r"^\d+\.\s+", "", text, flags=re.MULTILINE)  # Numbered lists

        # Clean up whitespace
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def extract_keywords(self, text: str, top_n: int = 10) -> List[str]:
        """Extract top keywords from text"""
        # Simple keyword extraction based on word frequency
        words = re.findall(r"\b[a-zA-Z]{4,}\b", text.lower())

        # Filter out common words (basic stoplist)
        stop_words = {
            "that",
            "this",
            "with",
            "from",
            "have",
            "been",
            "were",
            "they",
            "what",
            "when",
            "where",
            "will",
            "would",
            "could",
            "should",
            "about",
            "after",
            "before",
            "being",
            "doing",
            "going",
            "know",
            "think",
            "take",
            "come",
        }

        words = [w for w in words if w not in stop_words and len(w) > 3]
        word_freq = Counter(words)

        return [word for word, _ in word_freq.most_common(top_n)]

    def create_embeddings(self, texts: List[str]) -> np.ndarray:
        """Create embeddings for a list of texts using TF-IDF"""
        try:
            if not texts:
                return np.zeros((0, 1000))

            # Fit and transform texts to TF-IDF vectors
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            return tfidf_matrix.toarray()
        except Exception as e:
            logger.error(f"Failed to create embeddings: {e}")
            return np.zeros((len(texts), 1000))

    def calculate_similarity_matrix(self, embeddings: np.ndarray) -> np.ndarray:
        """Calculate cosine similarity matrix"""
        return cosine_similarity(embeddings)

    def find_semantic_connections(
        self, documents: List[Dict[str, Any]], similarity_threshold: float = 0.6
    ) -> List[Dict[str, Any]]:
        """
        Find semantic connections between documents

        Args:
            documents: List of documents with 'id', 'content', and 'metadata'
            similarity_threshold: Minimum similarity score to consider as connection

        Returns:
            List of semantic connections with similarity scores
        """
        if not documents:
            return []

        # Extract and clean text from documents
        texts = []
        doc_ids = []

        for doc in documents:
            cleaned_text = self.extract_text_from_markdown(doc.get("content", ""))
            if cleaned_text:
                texts.append(cleaned_text)
                doc_ids.append(doc.get("id", "unknown"))

        if not texts:
            return []

        # Create embeddings
        embeddings = self.create_embeddings(texts)

        # Calculate similarity matrix
        similarity_matrix = self.calculate_similarity_matrix(embeddings)

        # Find connections above threshold
        connections = []

        for i in range(len(doc_ids)):
            for j in range(i + 1, len(doc_ids)):
                similarity = similarity_matrix[i][j]
                if similarity >= similarity_threshold:
                    connections.append(
                        {
                            "source": doc_ids[i],
                            "target": doc_ids[j],
                            "type": "semantic",
                            "weight": float(similarity),
                            "label": f"{similarity:.2f}",
                        }
                    )

        # Sort by similarity (descending)
        connections.sort(key=lambda x: x["weight"], reverse=True)

        return connections

    def extract_topics(self, documents: List[Dict[str, Any]], top_n: int = 5) -> List[str]:
        """Extract main topics from a collection of documents"""
        all_text = ""
        for doc in documents:
            cleaned_text = self.extract_text_from_markdown(doc.get("content", ""))
            all_text += cleaned_text + " "

        keywords = self.extract_keywords(all_text, top_n * 2)

        # Group related keywords (simple clustering)
        topics = []
        for i, keyword in enumerate(keywords[:top_n]):
            topics.append(f"{keyword.capitalize()}")

        return topics

    def analyze_document(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a single document for semantic insights

        Returns:
            Dictionary with keywords, topics, and semantic summary
        """
        cleaned_text = self.extract_text_from_markdown(document.get("content", ""))

        if not cleaned_text:
            return {
                "id": document.get("id"),
                "keywords": [],
                "topics": [],
                "summary": "No content available",
            }

        keywords = self.extract_keywords(cleaned_text)
        topics = keywords[:5]  # Use top keywords as topics

        # Generate simple summary (first few sentences)
        sentences = re.split(r"[.!?]+", cleaned_text)
        summary = ". ".join(sentences[:3]) if sentences else cleaned_text[:200]

        return {
            "id": document.get("id"),
            "keywords": keywords,
            "topics": topics,
            "summary": summary[:300],
            "word_count": len(cleaned_text.split()),
        }


# Global service instance
semantic_service = SemanticAnalysisService()
