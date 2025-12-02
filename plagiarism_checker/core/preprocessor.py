"""
Text preprocessing utilities for plagiarism detection.
"""

import re
import string
from typing import List, Set


class TextPreprocessor:
    """Handles text preprocessing for plagiarism detection."""

    # Common English stop words
    STOP_WORDS: Set[str] = {
        'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you',
        "you're", "you've", "you'll", "you'd", 'your', 'yours', 'yourself',
        'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her',
        'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them',
        'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom',
        'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are',
        'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having',
        'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if',
        'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for',
        'with', 'about', 'against', 'between', 'into', 'through', 'during',
        'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down',
        'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further',
        'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how',
        'all', 'each', 'few', 'more', 'most', 'other', 'some', 'such',
        'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too',
        'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should',
        "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain',
        'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn',
        "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't",
        'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't",
        'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't",
        'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn',
        "wouldn't"
    }

    def __init__(self, remove_stopwords: bool = True, lowercase: bool = True):
        """
        Initialize the preprocessor.

        Args:
            remove_stopwords: Whether to remove stop words
            lowercase: Whether to convert text to lowercase
        """
        self.remove_stopwords = remove_stopwords
        self.lowercase = lowercase

    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text.

        Args:
            text: Input text to clean

        Returns:
            Cleaned text string
        """
        if not text:
            return ""

        # Convert to lowercase if enabled
        if self.lowercase:
            text = text.lower()

        # Remove URLs
        text = re.sub(r'https?://\S+|www\.\S+', '', text)

        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)

        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)

        return text.strip()

    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into words.

        Args:
            text: Input text to tokenize

        Returns:
            List of tokens
        """
        # Clean the text first
        text = self.clean_text(text)

        # Remove punctuation and split
        translator = str.maketrans('', '', string.punctuation)
        text = text.translate(translator)

        # Split into words
        tokens = text.split()

        # Remove stop words if enabled
        if self.remove_stopwords:
            tokens = [t for t in tokens if t not in self.STOP_WORDS]

        return tokens

    def get_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences.

        Args:
            text: Input text

        Returns:
            List of sentences
        """
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]

    def get_ngrams(self, text: str, n: int = 3) -> List[str]:
        """
        Generate n-grams from text.

        Args:
            text: Input text
            n: Size of n-grams

        Returns:
            List of n-gram strings
        """
        tokens = self.tokenize(text)
        if len(tokens) < n:
            return [' '.join(tokens)] if tokens else []

        ngrams = []
        for i in range(len(tokens) - n + 1):
            ngram = ' '.join(tokens[i:i + n])
            ngrams.append(ngram)

        return ngrams

    def get_shingles(self, text: str, k: int = 5) -> Set[str]:
        """
        Generate k-shingles (character-level n-grams) from text.

        Args:
            text: Input text
            k: Size of shingles

        Returns:
            Set of shingle strings
        """
        text = self.clean_text(text)
        text = re.sub(r'\s+', ' ', text)  # Normalize whitespace

        if len(text) < k:
            return {text} if text else set()

        shingles = set()
        for i in range(len(text) - k + 1):
            shingles.add(text[i:i + k])

        return shingles

    def fingerprint(self, text: str, n: int = 3) -> Set[int]:
        """
        Generate a fingerprint (set of hash values) for text.

        Args:
            text: Input text
            n: Size of n-grams for fingerprinting

        Returns:
            Set of hash values
        """
        ngrams = self.get_ngrams(text, n)
        return {hash(ngram) for ngram in ngrams}
