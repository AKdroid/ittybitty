import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "ittybitty",
    version = "1.0.0",
    author = "Mercion Wilathgamuwage",
    author_email = "mercion@mwilathg.com",
    description = ("A simple extendible python web framework"),
    license = "BSD",
    url = "http://packages.python",
    install_requires = ['pycrash', 'docutils'],
    dependency_links = ['https://github.com/mercion/pycrash/tarball/master#egg=PyCrash-1.0PreAlpha1'],
    packages=['ittybitty', 'tests'],
    long_description=read('README.txt'),
)
