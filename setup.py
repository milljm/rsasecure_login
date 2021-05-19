import os
import os.path

from setuptools import setup, find_packages

from rsasecure_login.version import version_str

def read(*paths):
    """Build a file path from *paths* and return the contents."""
    with open(os.path.join(*paths), 'r') as f:
        return f.read()

setup(
    name = "rsasecure_login",
    version = version_str,

    author = "Jason Miller",
    author_email = "m.jason.miller@gmail.com",
    description = "Helper script to facilitate RSA SecurID Conda channel access",
    long_description = read("README.md"),
    license = "LGPL 2.1",
    keywords = "RSA SecurID Token Conda Channel",
    url = "https://github.com/milljm/rsasecure_login",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering',
    ],

    # files
    packages = find_packages(),
    entry_points = {
        'console_scripts': [
            'rsasecure_login=rsasecure_login.__main__:main',
        ],
    },
    install_requires = [],
    package_data = {
    },
)
