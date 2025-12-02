#!/usr/bin/env python3
"""
Setup script for Plagiarism Checker.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="plagiarism-checker",
    version="1.0.0",
    author="Plagiarism Checker Team",
    description="A comprehensive tool for detecting text similarity and plagiarism",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/example/plagiarism-checker",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "plagiarism_checker.web": ["templates/*.html", "static/*"],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Text Processing :: General",
        "Topic :: Education",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "plagiarism-checker=plagiarism_checker.cli:main",
        ],
    },
)
