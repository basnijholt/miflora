from setuptools import setup, find_packages

setup(name='miflora',
      version='0.1.14',
      description='Library to read data from Mi Flora sensor',
      url='https://github.com/open-homeautomation/miflora',
      author='Daniel Matuschek',
      author_email='daniel@matuschek.net',
      license='MIT',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'Topic :: System :: Hardware :: Hardware Drivers',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5'
      ],
      packages=find_packages(),
      keywords='plant sensor bluetooth low-energy ble',
      zip_safe=False)
