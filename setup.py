"""Python package description."""
from setuptools import find_packages, setup


def readme():
    """Load the readme file."""
    with open("README.md", "r") as readme_file:
        return readme_file.read()


setup(
    name="miflora",
    version="0.7dev",
    description="Library to read data from Mi Flora sensor",
    long_description=readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/open-homeautomation/miflora",
    author="Daniel Matuschek",
    author_email="daniel@matuschek.net",
    license="MIT",
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: System :: Hardware :: Hardware Drivers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    packages=find_packages(),
    keywords="plant sensor bluetooth low-energy ble",
    zip_safe=False,
    install_requires=["btlewrap==0.0.10"],
    extras_require={"testing": ["pytest"]},
    include_package_data=True,
)
