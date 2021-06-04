from setuptools import setup, find_packages

from codecs import open
from os import path

__VERSION__='0.0.0' # CodePipeline will populate this when building

here = path.abspath(path.dirname(__file__))

setup(
    name='buddha',

    version=__VERSION__,

    description='',
    long_description="",

    # The project's main homepage.
    url='',

    # Author details
    author='Csaba Zagoni',
    author_email='csabi.zagoni@gmail.com',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 5 - Production/Stable',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],

    # What does your project relate to?

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=['buddha'],

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=[
        'selenium==3.141.0',
        'django==3.1.9',
        'whoosh==2.7.4',
        'tqdm==4.47.0'
    ],

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    extras_require={
        'dev': [
        ],
        'test': [
            'pyflakes==2.1.1',
            'pytest==5.4.1',
            'pytest-mock==1.10.4',
            'pytest-cov==2.8.1',
            'pytest-django==3.9.0'
        ],
    },

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
    },

    include_package_data=True
)
