#!/usr/bin/env python
"""
Setup script for TodoApp Django project
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="django-todo-app",
    version="1.0.0",
    author="TodoApp Team",
    author_email="team@todoapp.com",
    description="A modern Django todo management application with comprehensive testing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/django-todo-app",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Framework :: Django",
        "Framework :: Django :: 4.2",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-django>=4.7.0",
            "factory-boy>=3.3.0",
            "coverage>=7.3.2",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
