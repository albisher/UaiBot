import os
import sys
from setuptools import setup, find_packages
from labeeb.platform_services.common.platform_manager import PlatformManager

# Initialize platform manager
platform_manager = PlatformManager()
platform_info = platform_manager.get_platform_info()

# Base dependencies
base_requires = [
    'requests>=2.31.0',
    'pyyaml>=6.0.1',
    'python-dotenv>=1.0.0',
    'psutil>=5.9.0',
    'pyautogui>=0.9.54',
    'pyttsx3>=2.90',
    'openai-whisper>=20231117',
    'pynput>=1.7.6',
    'keyboard>=0.13.5',
    'mouse>=0.7.1',
    'screen-brightness-control>=0.16.0',
    'pygetwindow>=0.0.9',
    'pyperclip>=1.8.2',
    'pillow>=10.0.0',
    'numpy>=1.24.0',
    'pandas>=2.0.0',
    'scikit-learn>=1.3.0',
    'matplotlib>=3.7.0',
    'seaborn>=0.12.0',
    'plotly>=5.18.0',
    'pyqt5>=5.15.0',
    'pytest>=7.4.0',
    'pytest-cov>=4.1.0',
    'black>=23.7.0',
    'isort>=5.12.0',
    'flake8>=6.1.0',
    'mypy>=1.5.0',
    'sphinx>=7.1.0',
    'sphinx-rtd-theme>=1.3.0',
    'twine>=4.0.2',
    'build>=1.0.3',
    'arabic-reshaper>=3.0.0',
    'python-bidi>=0.4.2',
    'selenium>=4.18.1',
    'aiohttp>=3.12.0',
    'websockets>=12.0',
    'ollama>=0.1.7',
    'transformers>=4.40.0',
    'pyjwt>=2.8.0',
    'bcrypt>=4.1.2',
    'orjson>=3.9.10',
    'cryptography>=41.0.0',
    'toml>=0.10.2',
    'colorama>=0.4.6',
    'beautifulsoup4>=4.12.2',
    'python-dateutil>=2.8.2',
    'smolagents>=0.1.0',
    'langchain>=0.1.0',
    'langchain-core>=0.1.0',
    'langchain-community>=0.1.0',
    'sentence-transformers>=2.2.2',
    'torch>=2.2.0',
    'chromadb>=0.4.22',
    'playwright>=1.42.0',
    'gettext>=0.21.0',
    'pyaudio>=0.2.13',
    'opencv-python>=4.8.0',
    'pytesseract>=0.3.10',
    'asyncio>=3.4.3',
    'typing-extensions>=4.8.0',
    'pydantic>=2.5.0',
    'fastapi>=0.104.0',
    'uvicorn>=0.24.0',
    'python-multipart>=0.0.6',
    'jinja2>=3.1.2',
    'markdown>=3.5.0',
    'pygments>=2.16.0',
    'watchdog>=3.0.0',
    'ffmpeg-python>=0.2.0',
    'soundfile>=0.12.1',
    'sentencepiece>=0.1.99',
    'protobuf>=4.24.0',
    'networkx>=3.2.0',
    'spacy>=3.7.0',
    'langdetect>=1.0.9',
    'aiomysql>=0.2.0',
    'aioimaplib>=2.0.0',
    'aiosmtplib>=3.0.0',
    'dnspython>=2.6.0'
]

# Platform-specific dependencies
platform_requires = []
if platform_info['name'] == 'ubuntu':
    platform_requires += [
        'python-xlib>=0.33',
        'python-evdev>=1.6.1',
        'dbus-python>=1.3.2',
        'pyalsaaudio>=0.10.0',
        'alsaaudio>=0.10.0',
        'pyudev>=0.24.0',
        'distro>=1.9.0',
        'sounddevice>=0.4.6'
    ]
elif platform_info['name'] == 'mac':
    platform_requires += [
        'pyobjc>=9.2',
        'pyobjc-framework-Quartz>=9.2',
        'pyobjc-framework-CoreServices>=9.2',
        'pyobjc-framework-CoreWLAN>=9.2',
        'pyobjc-framework-AVFoundation>=9.2',
        'pyobjc-framework-AppKit>=9.2',
        'pyobjc-framework-CoreAudio>=9.2',
        'pyobjc-framework-Foundation>=9.2',
        'pyobjc-framework-IOBluetooth>=9.2',
        'pyobjc-framework-IOKit>=9.2',
        'objc>=0.1.0'
    ]
elif platform_info['name'] == 'windows':
    platform_requires += [
        'pywin32>=306',
        'wmi>=1.5.1',
        'pywinauto>=0.6.8',
        'comtypes>=1.2.0',
        'win32api',
        'win32clipboard',
        'win32com',
        'win32con',
        'win32file',
        'win32gui',
        'win32process',
        'win32security'
    ]

setup(
    name="labeeb",
    version="1.0.0",
    description="Intelligent, cross-platform AI agent framework with RTL and Arabic language support",
    author="Labeeb Team",
    author_email="contact@labeeb.ai",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=base_requires + platform_requires,
    extras_require={
        'dev': [
            'pytest>=7.4.0',
            'pytest-cov>=4.1.0',
            'black>=23.7.0',
            'isort>=5.12.0',
            'flake8>=6.1.0',
            'mypy>=1.5.0',
            'sphinx>=7.1.0',
            'sphinx-rtd-theme>=1.3.0',
            'twine>=4.0.2',
            'build>=1.0.3'
        ]
    },
    entry_points={
        'console_scripts': [
            'labeeb=labeeb.main:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
        'Natural Language :: Arabic',
    ],
) 