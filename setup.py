from setuptools import setup, find_packages

setup(
    name="uaibot",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "PyQt5>=5.15.0",
        "pyaudio>=0.2.11",
        "psutil>=5.8.0",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "uaibot=uaibot.start_uaibot:main",
        ],
    },
    author="UaiBot Team",
    author_email="contact@uaibot.com",
    description="AI-powered command processor with GUI interface",
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
    ],
) 