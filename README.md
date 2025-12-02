# Plagiarism Checker

A comprehensive Python application for detecting text similarity and plagiarism using multiple algorithms.

## Features

- **Multiple Similarity Algorithms**: Cosine similarity, Jaccard index, Dice coefficient, N-gram analysis, and more
- **Matching Passage Detection**: Identifies specific text passages that match between documents
- **Flexible Input**: Compare text strings, files, or entire directories
- **Web Interface**: Modern, responsive web UI for easy plagiarism checking
- **CLI Tool**: Command-line interface for batch processing and automation
- **Configurable Threshold**: Adjust sensitivity for plagiarism detection

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Usage

### Command Line Interface

**Compare two files:**
```bash
python main.py check --file1 document1.txt --file2 document2.txt
```

**Compare two text strings:**
```bash
python main.py check --text1 "Hello world" --text2 "Hello world!"
```

**Check a file against a directory of sources:**
```bash
python main.py check --check document.txt --sources ./source_documents/
```

**Quick comparison:**
```bash
python main.py compare "First text to compare" "Second text to compare"
python main.py compare file1.txt file2.txt
```

**Additional options:**
```bash
# Set custom threshold (default: 0.3 = 30%)
python main.py check --file1 doc1.txt --file2 doc2.txt --threshold 0.5

# Output as JSON
python main.py check --file1 doc1.txt --file2 doc2.txt --json

# Brief output (just percentage)
python main.py check --file1 doc1.txt --file2 doc2.txt --brief
```

### Web Interface

Start the web server:
```bash
python main.py web
```

Then open your browser to `http://localhost:5000`

**Options:**
```bash
# Custom port
python main.py web --port 8080

# Enable debug mode
python main.py web --debug
```

### Python API

```python
from plagiarism_checker import PlagiarismChecker

# Create checker instance
checker = PlagiarismChecker(threshold=0.3)

# Compare two texts
result = checker.check("Original text content", "Text to check for plagiarism")

# Check result
print(f"Similarity: {result.similarity_score * 100:.1f}%")
print(f"Plagiarized: {result.is_plagiarized}")

# Get detailed scores
for algo, score in result.algorithm_scores.items():
    print(f"  {algo}: {score * 100:.1f}%")

# Get matching passages
for passage, pos1, pos2 in result.matching_passages:
    print(f"Match: {passage}")

# Compare files
result = checker.compare_files("source.txt", "check.txt")

# Check against multiple sources
checker.add_sources_from_directory("./sources/")
result = checker.check_file("document_to_check.txt")

# Get formatted report
print(checker.get_detailed_report(result))
```

## Algorithms

The checker uses multiple algorithms for accurate plagiarism detection:

| Algorithm | Description |
|-----------|-------------|
| **Cosine Similarity** | Measures the cosine of the angle between word frequency vectors |
| **Jaccard Index** | Calculates the intersection over union of word sets |
| **Dice Coefficient** | Similar to Jaccard but with double weight on intersection |
| **N-gram Analysis** | Compares sequences of N consecutive words |
| **Shingle Similarity** | Uses character-level n-grams for fine-grained comparison |
| **LCS** | Longest Common Subsequence for sequential matching |

## Project Structure

```
plagiarism_checker/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── preprocessor.py    # Text preprocessing utilities
│   ├── algorithms.py      # Similarity algorithms
│   └── checker.py         # Main plagiarism checker class
├── web/
│   ├── __init__.py
│   ├── app.py             # Flask web application
│   └── templates/
│       └── index.html     # Web interface
├── cli.py                 # Command-line interface
├── main.py                # Main entry point
├── requirements.txt
└── README.md
```

## Configuration

### Threshold Settings

The plagiarism threshold determines when text is flagged as potentially plagiarized:

- `0.0 - 0.2`: Very strict, flags low similarity
- `0.3` (default): Balanced detection
- `0.4 - 0.6`: Moderate, requires higher similarity
- `0.7+`: Lenient, only flags very similar content

### Preprocessing Options

```python
checker = PlagiarismChecker(
    threshold=0.3,           # Plagiarism detection threshold
    remove_stopwords=True,   # Remove common words (the, is, at, etc.)
    ngram_size=3             # Size of n-grams for comparison
)
```

## License

MIT License
