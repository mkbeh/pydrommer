from setuptools import setup, find_packages
from src import __version__


setup(
    name='pydrommer',
    version=__version__,
    description='Simple asynchronous Internet-scale port scanner.',
    author='mkbeh',
    license='GPLv3',
    platforms='linux',
    install_requires=[
        'uvloop==0.12.2',
        'aiofiles==0.4.0',
        'netaddr==0.7.19',
        'termcolor==1.1.0',
    ],
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'pydrommer = src.pydrommer:main'
        ],
    },
)
