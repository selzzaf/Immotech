"""
Setup script for Immotech - Plateforme de Gestion Immobilière
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="immotech",
    version="1.0.0",
    author="Developer",
    author_email="developer@example.com",
    description="Plateforme complète de gestion immobilière développée avec Flask et MongoDB",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/username/immotech",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Real Estate",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Office/Business :: Financial :: Real Estate",
        "Framework :: Flask",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "immotech=Immotech.app:main",
        ],
    },
    include_package_data=True,
    package_data={
        "Immotech": [
            "templates/*",
            "static/*",
            "static/uploads/.gitkeep",
            "static/contracts/.gitkeep",
        ],
    },
    keywords="real estate, property management, flask, mongodb, web application",
    project_urls={
        "Bug Reports": "https://github.com/username/immotech/issues",
        "Source": "https://github.com/username/immotech",
        "Documentation": "https://github.com/username/immotech#readme",
    },
) 