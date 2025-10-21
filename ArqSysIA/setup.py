from setuptools import setup, find_packages

setup(
    name="arqsysia",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "pytest>=8.0.0",
        "rich>=13.0.0",
    ],
    python_requires=">=3.8",
)

