from setuptools import setup, find_packages
import sys
import platform

base_requires = [
    "PyQt5>=5.15.0",
    "pyaudio>=0.2.13",
    "psutil>=5.9.0",
    "openai-whisper @ git+https://github.com/openai/whisper.git",
    "Pillow>=9.0.0",
    "smolagents>=0.1.0",
    "ollama>=0.1.0",
    "transformers>=4.30.0",
    "aiohttp>=3.8.0",
    "chromadb>=0.4.0",
    "sentence-transformers>=2.2.0",
    "numpy>=1.24.0",
    "pandas>=2.0.0",
    "scikit-learn>=1.0.0",
    "colorama>=0.4.6",
    # ... add other core agentic dependencies here ...
]

# Platform-specific dependencies
platform_requires = []
if sys.platform.startswith("linux"):
    platform_requires += [
        "python-xlib>=0.33",
        "screen-brightness-control>=0.16.0",
    ]
elif sys.platform == "darwin":
    platform_requires += [
        "pyobjc-framework-Quartz>=9.2",
    ]
elif sys.platform == "win32":
    platform_requires += [
        "pywin32>=306",
    ]

dev_requires = [
    "black>=22.0.0",
    "isort>=5.0.0",
    "flake8>=6.0.0",
    "mypy>=1.0.0",
    "python-json-logger>=2.0.7",
    "colorlog>=6.7.0",
]

test_requires = [
    "pytest>=7.4.3",
    "pytest-selenium>=4.0.2",
    "pytest-html>=4.1.1",
    "pytest-cov>=4.0.0",
    "pytest-xdist>=3.0.0",
]

setup(
    name="uaibot",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=base_requires + platform_requires,
    extras_require={
        "dev": dev_requires,
        "test": test_requires,
        "all": dev_requires + test_requires,
    },
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "uaibot=uaibot.start_uaibot:main",
        ],
    },
    author="UaiBot Team",
    author_email="contact@uaibot.com",
    description="AI-powered agentic command processor with GUI interface",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/uaibot/uaibot",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
) 