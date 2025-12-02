#!/usr/bin/env python3
"""
Plagiarism Checker - Main entry point.

This module provides the main entry point for running the plagiarism checker
either as a CLI tool or as a web application.
"""

import sys
import argparse


def main():
    """Main entry point that routes to CLI or web server."""
    parser = argparse.ArgumentParser(
        description='Plagiarism Checker - Detect text similarity and plagiarism',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # CLI command
    cli_parser = subparsers.add_parser('check', help='Run plagiarism check from command line')
    cli_parser.add_argument('--file1', '-f1', help='First file to compare')
    cli_parser.add_argument('--file2', '-f2', help='Second file to compare')
    cli_parser.add_argument('--text1', '-t1', help='First text string')
    cli_parser.add_argument('--text2', '-t2', help='Second text string')
    cli_parser.add_argument('--check', '-c', help='File to check')
    cli_parser.add_argument('--sources', '-s', help='Source directory')
    cli_parser.add_argument('--threshold', '-th', type=float, default=0.3)
    cli_parser.add_argument('--json', action='store_true')
    cli_parser.add_argument('--brief', action='store_true')

    # Web server command
    web_parser = subparsers.add_parser('web', help='Start web interface')
    web_parser.add_argument('--host', default='0.0.0.0', help='Host to bind (default: 0.0.0.0)')
    web_parser.add_argument('--port', '-p', type=int, default=5000, help='Port to listen (default: 5000)')
    web_parser.add_argument('--debug', '-d', action='store_true', help='Enable debug mode')

    # Quick compare command
    quick_parser = subparsers.add_parser('compare', help='Quick comparison of two texts')
    quick_parser.add_argument('text1', help='First text or file path')
    quick_parser.add_argument('text2', help='Second text or file path')
    quick_parser.add_argument('--threshold', '-t', type=float, default=0.3)

    args = parser.parse_args()

    if args.command == 'check':
        # Run CLI
        from plagiarism_checker.cli import main as cli_main
        cli_args = []
        if args.file1:
            cli_args.extend(['--file1', args.file1])
        if args.file2:
            cli_args.extend(['--file2', args.file2])
        if args.text1:
            cli_args.extend(['--text1', args.text1])
        if args.text2:
            cli_args.extend(['--text2', args.text2])
        if args.check:
            cli_args.extend(['--check', args.check])
        if args.sources:
            cli_args.extend(['--sources', args.sources])
        cli_args.extend(['--threshold', str(args.threshold)])
        if args.json:
            cli_args.append('--json')
        if args.brief:
            cli_args.append('--brief')
        return cli_main(cli_args)

    elif args.command == 'web':
        # Start web server
        from plagiarism_checker.web.app import run_server
        print(f"Starting Plagiarism Checker web server on http://{args.host}:{args.port}")
        run_server(host=args.host, port=args.port, debug=args.debug)

    elif args.command == 'compare':
        # Quick compare
        import os
        from plagiarism_checker.core.checker import PlagiarismChecker

        text1 = args.text1
        text2 = args.text2

        # Check if inputs are file paths
        if os.path.isfile(text1):
            with open(text1, 'r', encoding='utf-8') as f:
                text1 = f.read()
        if os.path.isfile(text2):
            with open(text2, 'r', encoding='utf-8') as f:
                text2 = f.read()

        checker = PlagiarismChecker(threshold=args.threshold)
        result = checker.check(text1, text2)
        print(checker.get_detailed_report(result))
        return 1 if result.is_plagiarized else 0

    else:
        parser.print_help()
        return 0

    return 0


if __name__ == '__main__':
    sys.exit(main())
