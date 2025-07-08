from setuptools import setup, find_packages
import subprocess
import re

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

def get_version():
    import os
    # In GitHub Actions, use GITHUB_REF_NAME environment variable
    if 'GITHUB_REF_NAME' in os.environ:
        tag = os.environ['GITHUB_REF_NAME']
        # Convert v1.6.0 or public-1.6.0 to 1.6.0
        version = re.sub(r'^(v|public-)', '', tag)
        return version
    
    try:
        # Get version from git tag
        result = subprocess.run(['git', 'describe', '--tags', '--abbrev=0'], 
                              capture_output=True, text=True, check=True)
        tag = result.stdout.strip()
        # Convert v1.6.0 or public-1.6.0 to 1.6.0
        version = re.sub(r'^(v|public-)', '', tag)
        return version
    except:
        # Fallback version if git not available
        return "1.6.2"

setup(
    name="heaven-bml",
    version=get_version(),
    author="HEAVEN Development Team",
    author_email="team@heaven-dev.com",
    description="Build-Measure-Learn GitHub project management for AI agents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sancovp/heaven-bml",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Version Control :: Git",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests",  # Required for GitHub API calls in BML functions
        "mcp",       # Required for MCP server functionality
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black",
            "flake8",
        ],
    },
    entry_points={
        "console_scripts": [
            "install-bml-workflows=setup_scripts.install_bml_workflows:main",
        ],
    },
    include_package_data=True,
    package_data={
        "heaven_bml_system": [
            "github_workflows/*.yml",
            "examples/*.py",
            "docs/*.md",
        ],
    },
)
