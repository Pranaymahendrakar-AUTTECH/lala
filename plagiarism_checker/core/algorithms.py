"""
Similarity algorithms for plagiarism detection.
"""

import math
from typing import List, Set, Dict, Tuple
from collections import Counter


class SimilarityAlgorithms:
    """Collection of text similarity algorithms."""

    @staticmethod
    def jaccard_similarity(set1: Set, set2: Set) -> float:
        """
        Calculate Jaccard similarity between two sets.

        Args:
            set1: First set
            set2: Second set

        Returns:
            Jaccard similarity score (0.0 to 1.0)
        """
        if not set1 and not set2:
            return 1.0
        if not set1 or not set2:
            return 0.0

        intersection = len(set1 & set2)
        union = len(set1 | set2)

        return intersection / union if union > 0 else 0.0

    @staticmethod
    def cosine_similarity(tokens1: List[str], tokens2: List[str]) -> float:
        """
        Calculate cosine similarity between two token lists.

        Args:
            tokens1: First list of tokens
            tokens2: Second list of tokens

        Returns:
            Cosine similarity score (0.0 to 1.0)
        """
        if not tokens1 and not tokens2:
            return 1.0
        if not tokens1 or not tokens2:
            return 0.0

        # Create frequency vectors
        freq1 = Counter(tokens1)
        freq2 = Counter(tokens2)

        # Get all unique terms
        all_terms = set(freq1.keys()) | set(freq2.keys())

        # Calculate dot product and magnitudes
        dot_product = sum(freq1.get(term, 0) * freq2.get(term, 0) for term in all_terms)
        magnitude1 = math.sqrt(sum(v ** 2 for v in freq1.values()))
        magnitude2 = math.sqrt(sum(v ** 2 for v in freq2.values()))

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)

    @staticmethod
    def dice_coefficient(set1: Set, set2: Set) -> float:
        """
        Calculate Dice coefficient between two sets.

        Args:
            set1: First set
            set2: Second set

        Returns:
            Dice coefficient (0.0 to 1.0)
        """
        if not set1 and not set2:
            return 1.0
        if not set1 or not set2:
            return 0.0

        intersection = len(set1 & set2)
        return (2 * intersection) / (len(set1) + len(set2))

    @staticmethod
    def overlap_coefficient(set1: Set, set2: Set) -> float:
        """
        Calculate overlap coefficient between two sets.

        Args:
            set1: First set
            set2: Second set

        Returns:
            Overlap coefficient (0.0 to 1.0)
        """
        if not set1 and not set2:
            return 1.0
        if not set1 or not set2:
            return 0.0

        intersection = len(set1 & set2)
        min_size = min(len(set1), len(set2))

        return intersection / min_size if min_size > 0 else 0.0

    @staticmethod
    def levenshtein_distance(s1: str, s2: str) -> int:
        """
        Calculate Levenshtein (edit) distance between two strings.

        Args:
            s1: First string
            s2: Second string

        Returns:
            Edit distance (number of operations)
        """
        if len(s1) < len(s2):
            return SimilarityAlgorithms.levenshtein_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)

        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                # Cost is 0 if characters match, 1 otherwise
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

    @staticmethod
    def levenshtein_similarity(s1: str, s2: str) -> float:
        """
        Calculate normalized Levenshtein similarity.

        Args:
            s1: First string
            s2: Second string

        Returns:
            Similarity score (0.0 to 1.0)
        """
        if not s1 and not s2:
            return 1.0
        if not s1 or not s2:
            return 0.0

        distance = SimilarityAlgorithms.levenshtein_distance(s1, s2)
        max_len = max(len(s1), len(s2))

        return 1 - (distance / max_len) if max_len > 0 else 1.0

    @staticmethod
    def lcs_length(s1: str, s2: str) -> int:
        """
        Calculate the length of Longest Common Subsequence.

        Args:
            s1: First string
            s2: Second string

        Returns:
            Length of LCS
        """
        m, n = len(s1), len(s2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if s1[i - 1] == s2[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1] + 1
                else:
                    dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

        return dp[m][n]

    @staticmethod
    def lcs_similarity(s1: str, s2: str) -> float:
        """
        Calculate LCS-based similarity.

        Args:
            s1: First string
            s2: Second string

        Returns:
            Similarity score (0.0 to 1.0)
        """
        if not s1 and not s2:
            return 1.0
        if not s1 or not s2:
            return 0.0

        lcs_len = SimilarityAlgorithms.lcs_length(s1, s2)
        max_len = max(len(s1), len(s2))

        return lcs_len / max_len if max_len > 0 else 0.0

    @staticmethod
    def ngram_similarity(ngrams1: List[str], ngrams2: List[str]) -> float:
        """
        Calculate n-gram based similarity.

        Args:
            ngrams1: First list of n-grams
            ngrams2: Second list of n-grams

        Returns:
            Similarity score (0.0 to 1.0)
        """
        return SimilarityAlgorithms.jaccard_similarity(set(ngrams1), set(ngrams2))

    @staticmethod
    def find_matching_passages(
        text1: str,
        text2: str,
        min_length: int = 20
    ) -> List[Tuple[str, int, int]]:
        """
        Find matching passages between two texts.

        Args:
            text1: First text (source)
            text2: Second text (to check)
            min_length: Minimum length of matching passage

        Returns:
            List of tuples (matching_text, start_pos_in_text1, start_pos_in_text2)
        """
        matches = []
        text1_lower = text1.lower()
        text2_lower = text2.lower()

        # Use sliding window approach
        words1 = text1_lower.split()
        words2 = text2_lower.split()

        if len(words1) < 3 or len(words2) < 3:
            return matches

        # Find matching word sequences
        for i in range(len(words2)):
            for j in range(len(words1)):
                if words2[i] == words1[j]:
                    # Found a potential match, extend it
                    match_len = 0
                    while (i + match_len < len(words2) and
                           j + match_len < len(words1) and
                           words2[i + match_len] == words1[j + match_len]):
                        match_len += 1

                    if match_len >= 3:  # At least 3 words
                        match_text = ' '.join(words2[i:i + match_len])
                        if len(match_text) >= min_length:
                            # Calculate approximate character positions
                            pos1 = len(' '.join(words1[:j]))
                            pos2 = len(' '.join(words2[:i]))
                            matches.append((match_text, pos1, pos2))

        # Remove duplicate/overlapping matches
        unique_matches = []
        seen_texts = set()
        for match in sorted(matches, key=lambda x: -len(x[0])):
            if match[0] not in seen_texts:
                seen_texts.add(match[0])
                unique_matches.append(match)

        return unique_matches[:10]  # Return top 10 matches
