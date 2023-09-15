"""Packaging settings."""

VERSION = '0.1.0'

from codecs import open
from os.path import abspath, dirname, join
from subprocess import call

from setuptools import Command, find_packages, setup


# this_dir = abspath(dirname(__file__))
# with open(join(this_dir, 'README.md'), encoding='utf-8') as file:
#     long_description = file.read()


class RunTests(Command):
    """ Run all tests. """
    description = 'run tests'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        """Run all tests!"""
        err = call(['py.test'])
        raise SystemExit(err)


setup(
    name='pip-ascent',
    use_scm_version=True,
    # version=VERSION,
    setup_requires=['setuptools_scm'],
    description='A dynamic tool for upgrading pip requirements that seamlessly synchronizes the version changes within your requirements.txt file.',
    # long_description=long_description,
    # long_description_content_type="text/markdown",
    url='https://github.com/thisisazeez/pip-ascent',
    author='Abdulazeez Sherif',
    author_email='abdoulazeezx@gmail.com',
    license='The MIT License (MIT)',
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Utilities',
        'License :: Public Domain',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    keywords='cli,pip,pypi,requirements,upgrade',
    packages=find_packages(exclude=['docs', 'tests*']),
    install_requires=['docopt', 'packaging', 'requests', 'terminaltables', 'colorclass'],
    extras_require={
        'test': ['coverage', 'pytest', 'pytest-cov', 'pytest-pep8', 'mock', 'responses'],
    },
    entry_points={
        'console_scripts': [
            'pip-ascent=pip_ascent.cli:main',
        ],
    },
    # cmdclass={'test': RunTests},
)