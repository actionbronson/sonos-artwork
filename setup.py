# Always prefer setuptools over distutils
import pathlib

from setuptools import find_packages, setup

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / "README.md").read_text(encoding="utf-8")

requirements = [
    'requests==2.32.3',
    'flet==0.25.2',
    'pyaml==24.12.1',
    'flet-timer==0.0.13',
    'typer==0.15.1',
]

setup(
    name="sonos-artwork",
    version="1.1.1",
    description="Displays Sonos Artwork playing in a zone",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/actionbronson/sonos-artwork",
    author="Philippe Legault",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords="sonos",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.10, <4",
    install_requires=requirements,
    extras_require={
        "dev": ["pytest", "black", "ruff", "twine"],
    },
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "sonos=sonos.main:app",
        ],
    },
)
