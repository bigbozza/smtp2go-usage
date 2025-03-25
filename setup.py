#!/usr/bin/env python
"""Setup script for SMTP2GO Monthly Usage Reporter."""

from setuptools import setup, find_packages

setup(
    name="smtp2go-usage",
    version="0.1.0",
    description="Generate and email monthly usage reports for SMTP2GO subaccounts",
    author="SMTP2GO User",
    author_email="user@example.com",
    url="https://github.com/user/smtp2go-usage",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
        "matplotlib>=3.3.0",
        "pandas>=1.0.0",
        "numpy>=1.19.0",
    ],
    entry_points={
        "console_scripts": [
            "smtp2go-usage=smtp2go_usage.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
)