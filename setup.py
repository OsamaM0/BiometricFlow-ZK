"""
Setup configuration for BiometricFlow-ZK
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

# Read requirements
requirements = []
requirements_file = this_directory / "requirements.txt"
if requirements_file.exists():
    requirements = requirements_file.read_text().strip().split('\n')

setup(
    name="biometric-flow-zk",
    version="1.0.0",
    author="Osama Mohamed",
    author_email="osamamohamedmohamed30@gmail.com",
    description="Multi-Place Fingerprint Attendance System",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/BiometricFlow-ZK",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
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
        "Topic :: Office/Business",
        "Topic :: System :: Monitoring",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "isort>=5.12.0",
            "mypy>=1.0.0",
        ],
        "test": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "httpx>=0.24.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "biometric-flow-place-backend=biometric_flow.backend.place_backend:main",
            "biometric-flow-unified-gateway=biometric_flow.backend.unified_gateway:main",
            "biometric-flow-frontend=biometric_flow.frontend.app:main",
        ],
    },
    include_package_data=True,
    package_data={
        "biometric_flow": ["py.typed"],
    },
)
