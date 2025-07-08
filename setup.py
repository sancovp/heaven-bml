from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="heaven-bml",
    version="1.4.0",
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
        # No external dependencies - uses GitHub CLI and standard library
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
