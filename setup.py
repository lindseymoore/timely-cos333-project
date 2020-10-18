"""Set up Flask app."""

from setuptools import setup

setup(
    name='timely',
    packages=['timely'],
    include_package_data=True,
    install_requires=['flask'],
)
