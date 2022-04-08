from setuptools import setup

setup(
    name='sdig',
    version='0.2',
    description='Simple module for reading ERDDAP metadata',
    author='Roland Schweitzer',
    author_email='roland.schweitzer@noaa.gov',
    packages=['sdig'],  # same as name
    install_requires=['pandas', 'dateutil', 'datetime', 're'],  # external packages as dependencies
)