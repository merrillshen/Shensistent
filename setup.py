#!/usr/bin/env python3
"""
Setup script for Shensistent Personal Assistant.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

# Read requirements
requirements = []
if (this_directory / "requirements.txt").exists():
    with open(this_directory / "requirements.txt", "r") as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="shensistent",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A hyperpersonalized personal assistant agent that offers advice and guidance",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/Shensistent",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/Shensistent/issues",
        "Source": "https://github.com/yourusername/Shensistent",
        "Documentation": "https://github.com/yourusername/Shensistent/wiki",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development",
        "Topic :: Text Processing :: Linguistic",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
            "pre-commit>=3.0.0",
        ],
        "docs": [
            "sphinx>=6.0.0",
            "sphinx-rtd-theme>=1.2.0",
            "myst-parser>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "shensistent=main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords=[
        "ai",
        "artificial-intelligence",
        "personal-assistant",
        "career-development",
        "github",
        "linkedin",
        "twitter",
        "openai",
        "recommendations",
        "career-insights",
    ],
)
