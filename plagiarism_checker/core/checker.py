"""
Main plagiarism checker module.
"""

import os
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field

from .preprocessor import TextPreprocessor
from .algorithms import SimilarityAlgorithms


@dataclass
class PlagiarismResult:
    """Result of plagiarism check."""
    similarity_score: float
    is_plagiarized: bool
    algorithm_scores: Dict[str, float]
    matching_passages: List[Tuple[str, int, int]]
    source_file: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            'similarity_score': round(self.similarity_score * 100, 2),
            'is_plagiarized': self.is_plagiarized,
            'algorithm_scores': {k: round(v * 100, 2) for k, v in self.algorithm_scores.items()},
            'matching_passages': [
                {'text': m[0], 'source_pos': m[1], 'target_pos': m[2]}
                for m in self.matching_passages
            ],
            'source_file': self.source_file,
            'details': self.details
        }


class PlagiarismChecker:
    """
    Main plagiarism checker class that combines preprocessing and algorithms.
    """

    # Plagiarism threshold (percentage)
    DEFAULT_THRESHOLD = 0.3  # 30%

    def __init__(
        self,
        threshold: float = DEFAULT_THRESHOLD,
        remove_stopwords: bool = True,
        ngram_size: int = 3
    ):
        """
        Initialize the plagiarism checker.

        Args:
            threshold: Similarity threshold for plagiarism detection (0.0 to 1.0)
            remove_stopwords: Whether to remove stop words during preprocessing
            ngram_size: Size of n-grams for comparison
        """
        self.threshold = threshold
        self.ngram_size = ngram_size
        self.preprocessor = TextPreprocessor(remove_stopwords=remove_stopwords)
        self.algorithms = SimilarityAlgorithms()
        self.source_documents: Dict[str, str] = {}

    def add_source(self, name: str, text: str) -> None:
        """
        Add a source document to compare against.

        Args:
            name: Name/identifier for the source
            text: Source text content
        """
        self.source_documents[name] = text

    def add_source_file(self, filepath: str) -> None:
        """
        Add a source document from a file.

        Args:
            filepath: Path to the source file
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Source file not found: {filepath}")

        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        name = os.path.basename(filepath)
        self.add_source(name, content)

    def add_sources_from_directory(self, directory: str, extensions: Optional[List[str]] = None) -> int:
        """
        Add all text files from a directory as sources.

        Args:
            directory: Path to directory
            extensions: List of file extensions to include (e.g., ['.txt', '.md'])

        Returns:
            Number of files added
        """
        if extensions is None:
            extensions = ['.txt', '.md', '.py', '.java', '.cpp', '.c', '.js', '.html', '.css']

        count = 0
        for root, _, files in os.walk(directory):
            for filename in files:
                ext = os.path.splitext(filename)[1].lower()
                if ext in extensions:
                    filepath = os.path.join(root, filename)
                    try:
                        self.add_source_file(filepath)
                        count += 1
                    except Exception:
                        pass  # Skip files that can't be read

        return count

    def clear_sources(self) -> None:
        """Clear all source documents."""
        self.source_documents.clear()

    def compare_texts(self, text1: str, text2: str) -> Dict[str, float]:
        """
        Compare two texts using multiple algorithms.

        Args:
            text1: First text
            text2: Second text

        Returns:
            Dictionary of algorithm scores
        """
        # Preprocess texts
        tokens1 = self.preprocessor.tokenize(text1)
        tokens2 = self.preprocessor.tokenize(text2)

        # Generate n-grams
        ngrams1 = self.preprocessor.get_ngrams(text1, self.ngram_size)
        ngrams2 = self.preprocessor.get_ngrams(text2, self.ngram_size)

        # Generate shingles
        shingles1 = self.preprocessor.get_shingles(text1)
        shingles2 = self.preprocessor.get_shingles(text2)

        # Calculate various similarity scores
        scores = {
            'cosine': self.algorithms.cosine_similarity(tokens1, tokens2),
            'jaccard': self.algorithms.jaccard_similarity(set(tokens1), set(tokens2)),
            'dice': self.algorithms.dice_coefficient(set(tokens1), set(tokens2)),
            'ngram': self.algorithms.ngram_similarity(ngrams1, ngrams2),
            'shingle': self.algorithms.jaccard_similarity(shingles1, shingles2),
        }

        # Add LCS for shorter texts (it's computationally expensive for long texts)
        clean1 = self.preprocessor.clean_text(text1)
        clean2 = self.preprocessor.clean_text(text2)
        if len(clean1) < 5000 and len(clean2) < 5000:
            scores['lcs'] = self.algorithms.lcs_similarity(clean1, clean2)

        return scores

    def check(self, text: str, source_text: Optional[str] = None) -> PlagiarismResult:
        """
        Check text for plagiarism against a single source or all loaded sources.

        Args:
            text: Text to check for plagiarism
            source_text: Optional specific source text to compare against

        Returns:
            PlagiarismResult object
        """
        if source_text is not None:
            # Compare against specific source
            scores = self.compare_texts(text, source_text)
            matches = self.algorithms.find_matching_passages(source_text, text)

            # Calculate weighted average score
            weights = {'cosine': 0.25, 'jaccard': 0.2, 'dice': 0.15, 'ngram': 0.25, 'shingle': 0.15}
            avg_score = sum(scores.get(k, 0) * w for k, w in weights.items())

            return PlagiarismResult(
                similarity_score=avg_score,
                is_plagiarized=avg_score >= self.threshold,
                algorithm_scores=scores,
                matching_passages=matches,
                details={'comparison_type': 'direct'}
            )

        # Compare against all loaded sources
        if not self.source_documents:
            return PlagiarismResult(
                similarity_score=0.0,
                is_plagiarized=False,
                algorithm_scores={},
                matching_passages=[],
                details={'error': 'No source documents loaded'}
            )

        best_result = None
        best_score = 0.0
        all_results = []

        for name, source in self.source_documents.items():
            result = self.check(text, source)
            result.source_file = name
            all_results.append(result)

            if result.similarity_score > best_score:
                best_score = result.similarity_score
                best_result = result

        if best_result is None:
            return PlagiarismResult(
                similarity_score=0.0,
                is_plagiarized=False,
                algorithm_scores={},
                matching_passages=[],
                details={'error': 'No valid comparisons'}
            )

        best_result.details['all_comparisons'] = [
            {'source': r.source_file, 'score': round(r.similarity_score * 100, 2)}
            for r in sorted(all_results, key=lambda x: -x.similarity_score)
        ]

        return best_result

    def check_file(self, filepath: str) -> PlagiarismResult:
        """
        Check a file for plagiarism.

        Args:
            filepath: Path to file to check

        Returns:
            PlagiarismResult object
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")

        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        result = self.check(content)
        result.details['checked_file'] = filepath
        return result

    def compare_files(self, file1: str, file2: str) -> PlagiarismResult:
        """
        Compare two files for similarity.

        Args:
            file1: Path to first file
            file2: Path to second file

        Returns:
            PlagiarismResult object
        """
        if not os.path.exists(file1):
            raise FileNotFoundError(f"File not found: {file1}")
        if not os.path.exists(file2):
            raise FileNotFoundError(f"File not found: {file2}")

        with open(file1, 'r', encoding='utf-8', errors='ignore') as f:
            content1 = f.read()
        with open(file2, 'r', encoding='utf-8', errors='ignore') as f:
            content2 = f.read()

        result = self.check(content1, content2)
        result.details['file1'] = file1
        result.details['file2'] = file2
        return result

    def get_detailed_report(self, result: PlagiarismResult) -> str:
        """
        Generate a detailed text report from plagiarism result.

        Args:
            result: PlagiarismResult object

        Returns:
            Formatted report string
        """
        lines = [
            "=" * 60,
            "PLAGIARISM CHECK REPORT",
            "=" * 60,
            "",
            f"Overall Similarity: {result.similarity_score * 100:.1f}%",
            f"Plagiarism Detected: {'YES' if result.is_plagiarized else 'NO'}",
            f"Threshold: {self.threshold * 100:.1f}%",
            "",
        ]

        if result.source_file:
            lines.append(f"Most Similar Source: {result.source_file}")
            lines.append("")

        lines.append("-" * 60)
        lines.append("Algorithm Breakdown:")
        lines.append("-" * 60)

        for algo, score in result.algorithm_scores.items():
            bar_length = int(score * 30)
            bar = "█" * bar_length + "░" * (30 - bar_length)
            lines.append(f"  {algo.capitalize():12} [{bar}] {score * 100:5.1f}%")

        if result.matching_passages:
            lines.append("")
            lines.append("-" * 60)
            lines.append("Matching Passages Found:")
            lines.append("-" * 60)

            for i, (text, _, _) in enumerate(result.matching_passages[:5], 1):
                preview = text[:100] + "..." if len(text) > 100 else text
                lines.append(f"\n  {i}. \"{preview}\"")

        if 'all_comparisons' in result.details:
            lines.append("")
            lines.append("-" * 60)
            lines.append("All Source Comparisons:")
            lines.append("-" * 60)

            for comp in result.details['all_comparisons'][:10]:
                lines.append(f"  {comp['source']}: {comp['score']:.1f}%")

        lines.append("")
        lines.append("=" * 60)

        return "\n".join(lines)
