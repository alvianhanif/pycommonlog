from setuptools import setup, find_packages
import subprocess
import os

def get_latest_git_tag():
    # In GitHub Actions, use GITHUB_REF for release tags
    if 'GITHUB_REF' in os.environ and os.environ['GITHUB_REF'].startswith('refs/tags/'):
        tag = os.environ['GITHUB_REF'].replace('refs/tags/', '')
    else:
        try:
            tag = subprocess.check_output(["git", "describe", "--tags", "--abbrev=0"]).decode().strip()
        except Exception:
            return "0.0.0"
    
    # Clean up invalid version formats
    if tag.startswith('v'):
        tag = tag[1:]  # Remove leading 'v'
    if '-v' in tag:
        # Extract base version from tags like 0.1.7-v24
        base_version = tag.split('-v')[0]
        return base_version
    return tag

setup(
    name="pycommonlog",
    version=get_latest_git_tag(),
    description="Unified logging and alerting library for Python.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Alvian Rahman Hanif",
    author_email="alvian.hanif@pasarpolis.com",
    url="https://github.com/alvianhanif/pycommonlog",
    packages=find_packages(),
    install_requires=["requests"],
    extras_require={
        "redis": ["redis>=4.0.0"],
    },
    license="MIT",
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
)