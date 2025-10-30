"""
ArqSysIA - Iterative Software Architecture with AI
Setup configuration for package distribution.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

# Read requirements
requirements = []
with open("requirements.txt") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

# Version
VERSION = "1.0.1"

setup(
    # Basic Information
    name="arqsysia",
    version=VERSION,
    description="Iterative Software Architecture with AI - AI-assisted iterative architecture design system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    
    # Author Information
    author="Carlos",
    author_email="carlos@arqsysia.example.com",
    
    # URLs
    url="https://github.com/Krl05oP11/ArqSysIA",
    project_urls={
        "Bug Reports": "https://github.com/Krl05oP11/ArqSysIA/issues",
        "Source": "https://github.com/Krl05oP11/ArqSysIA",
        "Documentation": "https://github.com/Krl05oP11/ArqSysIA#readme",
        "Changelog": "https://github.com/Krl05oP11/ArqSysIA/blob/main/CHANGELOG.md",
    },
    
    # Package Configuration
    packages=find_packages(exclude=["tests", "tests.*", "docs", "*.egg-info"]),
    include_package_data=True,
    
    # Python Version Requirement
    python_requires=">=3.11",
    
    # Dependencies
    install_requires=requirements,
    
    # Optional Dependencies
    extras_require={
        "dev": [
            "pytest>=8.4.0",
            "pytest-cov>=7.0.0",
            "black>=24.0.0",
            "flake8>=7.0.0",
            "mypy>=1.8.0",
        ],
        "docs": [
            "sphinx>=7.0.0",
            "sphinx-rtd-theme>=2.0.0",
        ],
    },
    
    # Entry Points (CLI commands)
    entry_points={
        "console_scripts": [
            "arqsysia=arqsysia.cli.main:main",
        ],
    },
    
    # Package Data
    package_data={
        "arqsysia": [
            "py.typed",  # PEP 561 marker for type hints
        ],
    },
    
    # Classifiers for PyPI
    classifiers=[
        # Development Status
        "Development Status :: 4 - Beta",
        
        # Intended Audience
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        
        # Topics
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        
        # License
        "License :: OSI Approved :: MIT License",
        
        # Programming Language
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3 :: Only",
        
        # Operating System
        "Operating System :: OS Independent",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        
        # Framework
        "Framework :: Pytest",
        
        # Natural Language
        "Natural Language :: English",
        "Natural Language :: Spanish",
        
        # Typing
        "Typing :: Typed",
    ],
    
    # Keywords for PyPI search
    keywords=[
        "ai",
        "architecture",
        "software-design",
        "llm",
        "code-generation",
        "iterative-design",
        "ollama",
        "deepseek",
        "software-engineering",
    ],
    
    # Zip Safe
    zip_safe=False,
    
    # License
    license="MIT",
    
    # Platforms
    platforms=["any"],
)
