import os
import sys
from setuptools import setup, find_packages
from app.platform_core.platform_manager import PlatformManager

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
    'build>=1.0.3'
]

# Platform-specific dependencies
platform_requires = []
if platform_info['name'] == 'ubuntu':
    platform_requires += [
        'python-xlib>=0.33',
        'python-evdev>=1.6.1',
        'dbus-python>=1.3.2'
    ]
elif platform_info['name'] == 'mac':
    platform_requires += [
        'pyobjc-framework-Quartz>=9.2',
        'pyobjc-framework-CoreServices>=9.2',
        'pyobjc-framework-CoreWLAN>=9.2'
    ]
elif platform_info['name'] == 'windows':
    platform_requires += [
        'pywin32>=306',
        'wmi>=1.5.1',
        'pywinauto>=0.6.8'
    ]

setup(
    name="labeeb",
    version="1.0.0",
    description="Intelligent, cross-platform AI agent framework",
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
            'labeeb=app.start_Labeeb:main',
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
    ],
) 