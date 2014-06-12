from distutils.core import setup

setup(
    name="ACO-Pants",
    version="0.3.3",
    author="Robert Grant",
    author_email="rhgrant10@gmail.com",
    packages=["pants", "pants.test"],
    scripts=["bin/demo"],
    url="http://pypi.python.org/pypi/ACO-Pants",
    license="LICENSE.txt",
    description="A Python3 implementation of the ACO Meta-Heuristic",
    long_description=open("README.md").read()
)