"""
Setup script pour Cursor Browser Control
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="cursor-browser-control",
    version="1.0.0",
    author="Cursor Browser Control Team",
    author_email="contact@example.com",
    description="Contrôle du curseur dans le navigateur via les touches directionnelles",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/cursor-browser-control",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Hardware :: Input Devices",
        "Topic :: Internet :: WWW/HTTP :: Browsers",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "cursor-browser-control=src.main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="browser automation playwright cursor control keyboard",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/cursor-browser-control/issues",
        "Source": "https://github.com/yourusername/cursor-browser-control",
        "Documentation": "https://github.com/yourusername/cursor-browser-control#readme",
    },
) 