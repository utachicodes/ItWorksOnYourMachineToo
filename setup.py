#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LexWorksEverywhere - Cross-Platform Development Environment Manager
Setup Script for Deployment
"""

from setuptools import setup, find_packages
import pathlib

# Read the long description from README
here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="lexworkseverywhere",
    version="2.1.0",
    author="Alexandre Albert Ndour",
    author_email="alexandre.albert.ndour@example.com",
    description="LexWorksEverywhere: Cross-platform development environment manager that ensures code works everywhere without manual configuration.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/alexandrealbertndour/lexworkseverywhere",
    project_urls={
        "Bug Reports": "https://github.com/alexandrealbertndour/lexworkseverywhere/issues",
        "Source": "https://github.com/alexandrealbertndour/lexworkseverywhere",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "."},
    packages=find_packages(),
    python_requires=">=3.9, <4",
    install_requires=[
        "click>=8.0.0",
        "psutil>=5.8.0",
        "rich>=10.0.0",
        "requests>=2.25.0",
        "pyyaml>=6.0",
        "toml>=0.10.0",
    ],
    entry_points={
        "console_scripts": [
            "lexworks=lexworkseverywhere.cli.main:main",
            "lex=lexworkseverywhere.cli.main:main",
        ],
    },
    keywords="development, environment, cross-platform, deployment, tool",
    zip_safe=True,
)