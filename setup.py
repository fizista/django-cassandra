#-*- encoding: utf-8 -*-
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import sys


install_requires = [
    'django >= 1.6, < 1.7',
    #'djangotoolbox >= 1.6, < 1.7',
    'cql >= 1.4, < 1.5',
    'cqlsh >= 4.1.0, < 5.0.0',
    #'readline >= 6.2',  # Tab completion in cqlsh for MAC OS
]


tests_requires = [
    'tox >= 1.6.0',
    'django-extensions',
    'werkzeug',
    'django-pdb',
    'pycallgraph',
    'pycassa',
    'ipdb',
    'django-pdb',
    'pyprof2calltree',
    'guppy',
]


dependency_links = [
]


class Tox(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import tox
        errno = tox.cmdline(self.test_args)
        sys.exit(errno)


setup(
    name="django-cassandra",
    version=__import__('django_cassandra').get_version(limit=3),
    description="A Django database backend for Cassandra",
    #url="",
    maintainer='Wojciech Banaś',
    maintainer_email='wojciech.banas@dataexoand.pl',
    packages=find_packages(),
    install_requires=install_requires,
    platforms=['Any'],
    keywords=[
        'django',
        'cassandra',
        'backend',
        'database'],
    #package_dir={"": ""},
    #cmdclass=cmdclass,
    classifiers=[
        "Development Status :: 1 - Planning",
        #"Development Status :: 2 - Pre-Alpha",
        #"Development Status :: 3 - Alpha",
        #"Development Status :: 4 - Beta",
        #"Development Status :: 5 - Production/Stable",
        #"Development Status :: 6 - Mature",
        #"Development Status :: 7 - Inactive",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Framework :: Django", ],
    extras_require={'tests': tests_requires},
    tests_require=tests_requires,
    cmdclass={'test': Tox},
)
