#!/usr/bin/env python3
"""
Setup script for VacationPlaner.
"""

from setuptools import setup, find_packages

setup(
    name="vacationplaner",
    version="1.0.0",
    description="A tool for managing and visualizing holidays and vacation days",
    author="Heinrich Krupp",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "matplotlib>=3.7.0",
        "numpy>=1.24.0",
        "icalendar>=5.0.0",
        "Pillow",
        "python-dateutil",
        "tzdata",
    ],
    entry_points={
        "console_scripts": [
            "vacationplaner=vacationplaner.app:main",
        ],
    },
    python_requires=">=3.8",
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business :: Scheduling",
        "Topic :: Utilities"
    ],
)
