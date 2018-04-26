"""Python package description."""
import os
from setuptools import setup, find_packages


def readme():
    """Load the readme file."""
    readme_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'README.md')
    listing = os.listdir(os.path.dirname(readme_path))
    if not os.path.exists(readme_path):
        raise Exception('Could not find readme file in {}. Listing:\n{}'.format(readme_path, '\n'.join(sorted(listing))))
    with open(readme_path, 'r') as readme_file:
        return readme_file.read()


setup(
    name='miflora',
    version='0.4',
    description='Library to read data from Mi Flora sensor',
    long_description=readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/open-homeautomation/miflora',
    author='Daniel Matuschek',
    author_email='daniel@matuschek.net',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: System :: Hardware :: Hardware Drivers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5'
    ],
    packages=find_packages(),
    keywords='plant sensor bluetooth low-energy ble',
    zip_safe=False,
    install_requires=['btlewrap==0.0.2'],
    extras_require={'testing': ['pytest']}
)
