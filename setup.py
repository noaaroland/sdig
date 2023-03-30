from setuptools import setup, find_packages

setup(
    name='sdig',
    version='0.7',
    description='Simple class for reading ERDDAP metadata and utility class for get zoom and center for Mapbox map.',
    author='Roland Schweitzer',
    author_email='roland.schweitzer@noaa.gov',
    packages=find_packages(),  # same as name
    install_requires=['pandas','numpy'],  # external packages as dependencies
)
