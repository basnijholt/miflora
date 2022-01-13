"""Python package description."""
import os
from importlib.util import module_from_spec, spec_from_file_location

from setuptools import find_packages, setup


def readme():
    """Load the readme file."""
    with open("README.md") as readme_file:
        return readme_file.read()


def get_version_and_cmdclass(package_path):
    """Load version.py module without importing the whole package.

    Template code from miniver
    """
    spec = spec_from_file_location("version", os.path.join(package_path, "_version.py"))
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.__version__, module.cmdclass


version, cmdclass = get_version_and_cmdclass("miflora")


setup(
    name="miflora",
    version=version,
    cmdclass=cmdclass,
    description="Library to read data from Mi Flora sensor",
    long_description=readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/basnijholt/miflora",
    author="Daniel Matuschek",
    author_email="daniel@matuschek.net",
    maintainer="Bas Nijholt",
    maintainer_email="bas@nijho.lt",
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
    packages=find_packages(exclude=["test", "test.*"]),
    keywords="plant sensor bluetooth low-energy ble",
    zip_safe=False,
    install_requires=["btlewrap>=0.0.10,<0.2"],
    extras_require={"testing": ["pytest"]},
    include_package_data=True,
)
