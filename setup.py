import os
import sys
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

cdir = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(cdir, 'readme.rst')).read()
CHANGELOG = open(os.path.join(cdir, 'changelog.rst')).read()

import basebwa
version = basebwa.VERSION

setup(
    name = "BaseBWA",
    version = version,
    description = "A supporting application for BlazeWeb applications.",
    long_description=README + '\n\n' + CHANGELOG,
    author = "Randy Syring",
    author_email = "rsyring@gmail.com",
    url='http://pypi.python.org/pypi/BaseBWA/',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP'
      ],
    license='BSD',
    packages=find_packages(exclude=['ez_setup', 'tests']),
    include_package_data=True,
    install_requires = [
        'AuthBWC>=0.1',
    ],
    entry_points="""
    [console_scripts]
    basebwa = basebwa.application:script_entry
    """,
    zip_safe=False
)
