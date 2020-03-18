from setuptools import setup

from certcheck import __version__

setup(name='certcheck',
      version=__version__,
      description='The http/https redirect, http response checker',
      url='http://github.com/youmee/certcheck',
      author='Al Fi',
      author_email='job@youmee.co',
      license='MIT',
      packages=['certcheck'],
      scripts=['bin/certcheck'],
      python_requires='~=3.6',
      install_requires=[
          'aiohttp==3.6.2',
          'colored==1.4.2'
      ],
      zip_safe=False)
