from setuptools import setup, find_packages

setup(
    name='sdig',
    version='0.4',
    description='Simple class for reading ERDDAP metadata',
    author='Roland Schweitzer',
    author_email='roland.schweitzer@noaa.gov',
    packages=find_packages(),  # same as name
    install_requires=['pandas'],  # external packages as dependencies
)