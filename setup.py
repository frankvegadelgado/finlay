from pathlib import Path

import setuptools

VERSION = "0.1.9"

NAME = "aegypti"

INSTALL_REQUIRES = [
    "numpy>=2.2.1",
    "scipy>=1.15.0",  
]

setuptools.setup(
    name=NAME,
    version=VERSION,
    description="Solve the Triangle-Free Problem for an undirected graph represented by a Boolean Adjacency Matrix given in a File.",
    url="https://github.com/frankvegadelgado/finlay",
    project_urls={
        "Source Code": "https://github.com/frankvegadelgado/finlay",
        "Documentation Research": "https://www.researchgate.net/publication/387698746_The_Triangle_Finding_Problem",
    },
    author="Frank Vega",
    author_email="vega.frank@gmail.com",
    license="MIT License",
    classifiers=[
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.12",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "Natural Language :: English",
    ],
    python_requires=">=3.12",
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