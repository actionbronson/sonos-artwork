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
    name="sonos-artwork",  # Required
    version="1.0.0",  # Required
    description="Displays Sonos Artwork playing in a zone",  # Optional
    long_description=long_description,  # Optional
    long_description_content_type="text/markdown",  # Optional (see note above)
    url="https://github.com/pypa/sampleproject",  # Optional
    author="Philippe Legault",  # Optional
    classifiers=[  # Optional
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate you support Python 3. These classifiers are *not*
        # checked by 'pip install'. See instead 'python_requires' below.
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
        "dev": ["pytest", "black", "ruff"],
    },
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "sonos=sonos.main:app",
        ],
    },
)
