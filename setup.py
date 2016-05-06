#!/usr/bin/env python
from os.path import dirname, join
from setuptools import setup, find_packages


with open(join(dirname(__file__), 'VERSION'), 'rb') as f:
    version = f.read().decode('ascii').strip()


setup(
    name='Mosquito',
    version=version,
    url='?',
    description='A high-level Distributed Web Crawling and Web Scraping framework',
    long_description=open('README.md').read(),
    author='Mikkel Vilstrup',
    maintainer='Mikkel Vilstrup',
    maintainer_email='mikkel@vilstrup.dk',
    license='BSD',
    packages=find_packages(exclude=('tests', 'tests.*')),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Framework :: Mosquito',
        'Development Status :: 0.1 - Beta/Unstable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires=[
        'lxml',
        'cssselect>=0.9',
        'pyzmq',
        'msgpack-python',
    ],
)
