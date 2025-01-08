from pathlib import Path

import setuptools

VERSION = "0.1.1"

NAME = "aegypti"

INSTALL_REQUIRES = [
    "numpy>=2.2.1",
    "scipy>=1.15.0" 
]

setuptools.setup(
    name=NAME,
    version=VERSION,
    description="Solve the Triangle-Free Problem for an undirected graph represented by a Boolean adjacency matrix given in a file.",
    url="https://github.com/frankvegadelgado/finlay",
    project_urls={
        "Source Code": "https://github.com/frankvegadelgado/finlay",
    },
    author="Frank Vega",
    author_email="vega.frank@gmail.com",
    license="MIT License",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
    ],
    # Snowpark requires Python 3.8
    python_requires=">=3.8",
    # Requirements
    install_requires=INSTALL_REQUIRES,
    packages=["aegypti"],
    long_description=Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    entry_points={
        'console_scripts': [
            'triangle = aegypti.app:main',
            'test_triangle = aegypti.test:main'
        ]
    }
)
