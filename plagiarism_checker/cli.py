"""
Command-line interface for the plagiarism checker.
"""

import sys
import argparse
from typing import Optional

from .core.checker import PlagiarismChecker


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog='plagiarism-checker',
        description='Check text or files for plagiarism',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Compare two files
  plagiarism-checker --file1 document.txt --file2 source.txt

  # Check a file against a directory of sources
  plagiarism-checker --check document.txt --sources ./sources/

  # Compare two text strings
  plagiarism-checker --text1 "Hello world" --text2 "Hello world!"

  # Check text against sources with custom threshold
  plagiarism-checker --check document.txt --sources ./sources/ --threshold 0.4
        """
    )

    # Input options
    input_group = parser.add_argument_group('Input Options')
    input_group.add_argument(
        '--file1', '-f1',
        help='First file to compare'
    )
    input_group.add_argument(
        '--file2', '-f2',
        help='Second file to compare'
    )
    input_group.add_argument(
        '--text1', '-t1',
        help='First text string to compare'
    )
    input_group.add_argument(
        '--text2', '-t2',
        help='Second text string to compare'
    )
    input_group.add_argument(
        '--check', '-c',
        help='File to check for plagiarism'
    )
    input_group.add_argument(
        '--sources', '-s',
        help='Directory containing source files to compare against'
    )

    # Configuration options
    config_group = parser.add_argument_group('Configuration')
    config_group.add_argument(
        '--threshold', '-th',
        type=float,
        default=0.3,
        help='Plagiarism detection threshold (0.0-1.0, default: 0.3)'
    )
    config_group.add_argument(
        '--ngram-size', '-n',
        type=int,
        default=3,
        help='N-gram size for comparison (default: 3)'
    )
    config_group.add_argument(
        '--keep-stopwords',
        action='store_true',
        help='Keep stop words (default: remove them)'
    )

    # Output options
    output_group = parser.add_argument_group('Output Options')
    output_group.add_argument(
        '--json',
        action='store_true',
        help='Output results as JSON'
    )
    output_group.add_argument(
        '--brief',
        action='store_true',
        help='Show only similarity percentage'
    )
    output_group.add_argument(
        '--no-color',
        action='store_true',
        help='Disable colored output'
    )

    return parser


def colorize(text: str, color: str, no_color: bool = False) -> str:
    """Add ANSI color codes to text."""
    if no_color:
        return text

    colors = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'magenta': '\033[95m',
        'cyan': '\033[96m',
        'reset': '\033[0m',
        'bold': '\033[1m'
    }

    return f"{colors.get(color, '')}{text}{colors['reset']}"


def print_result(checker: PlagiarismChecker, result, args) -> None:
    """Print the plagiarism check result."""
    import json

    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
        return

    if args.brief:
        score = result.similarity_score * 100
        status = "PLAGIARIZED" if result.is_plagiarized else "ORIGINAL"
        print(f"{score:.1f}% - {status}")
        return

    # Full report
    report = checker.get_detailed_report(result)

    # Add colors if enabled
    if not args.no_color:
        if result.is_plagiarized:
            status_color = 'red'
        elif result.similarity_score > checker.threshold * 0.7:
            status_color = 'yellow'
        else:
            status_color = 'green'

        # Colorize key parts
        if result.is_plagiarized:
            report = report.replace('Plagiarism Detected: YES',
                                   colorize('Plagiarism Detected: YES', 'red'))
        else:
            report = report.replace('Plagiarism Detected: NO',
                                   colorize('Plagiarism Detected: NO', 'green'))

    print(report)


def main(argv: Optional[list] = None) -> int:
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args(argv)

    # Validate arguments
    has_compare = args.file1 and args.file2
    has_text_compare = args.text1 and args.text2
    has_check = args.check and args.sources

    if not (has_compare or has_text_compare or has_check):
        parser.print_help()
        print("\nError: Please specify either:")
        print("  - Two files to compare (--file1 and --file2)")
        print("  - Two text strings to compare (--text1 and --text2)")
        print("  - A file to check against sources (--check and --sources)")
        return 1

    # Create checker
    checker = PlagiarismChecker(
        threshold=args.threshold,
        remove_stopwords=not args.keep_stopwords,
        ngram_size=args.ngram_size
    )

    try:
        if has_compare:
            # Compare two files
            result = checker.compare_files(args.file1, args.file2)

        elif has_text_compare:
            # Compare two text strings
            result = checker.check(args.text1, args.text2)

        elif has_check:
            # Check file against source directory
            count = checker.add_sources_from_directory(args.sources)
            if count == 0:
                print(f"Error: No valid source files found in {args.sources}")
                return 1

            print(f"Loaded {count} source files from {args.sources}")
            print()

            result = checker.check_file(args.check)

        print_result(checker, result, args)

        # Return non-zero if plagiarism detected
        return 1 if result.is_plagiarized else 0

    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
