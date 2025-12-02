"""
Core module containing plagiarism detection algorithms and utilities.
"""

from .preprocessor import TextPreprocessor
from .algorithms import SimilarityAlgorithms
from .checker import PlagiarismChecker

__all__ = ["TextPreprocessor", "SimilarityAlgorithms", "PlagiarismChecker"]
