from distutils.core import setup
import sys

if sys.version_info.major < 3:
    print("Pants requires Python version >= 3, please upgrade")
    sys.exit(1)

setup(
    name="ACO-Pants",
    version="0.5.0",
    author="Robert Grant",
    author_email="rhgrant10@gmail.com",
    packages=["pants", "pants.test"],
    scripts=["bin/pants-demo"],
    url="http://pypi.python.org/pypi/ACO-Pants",
    license="LICENSE.txt",
    description="A Python3 implementation of the ACO Meta-Heuristic",
    long_description=open("README.rst").read()
)