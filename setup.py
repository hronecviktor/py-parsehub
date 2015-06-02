from setuptools import find_packages, setup

setup(name="py-parsehub",
      version="0.1",
      description="Python3 module for interaction with Parsehub API",
      author="Viktor Hronec",
      author_email='zamr666@gmail.com',
      platforms=["linux"],
      license="BSD",
      url="https://github.com/hronecviktor/py-parsehub",
      packages=find_packages(), install_requires=['urllib3']
      )
