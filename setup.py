"""
Introduction
---------------

BaseBWA is a library designed as a "supporting application" for
`BlazeWeb <http://pypi.python.org/pypi/BlazeWeb/>`_ applications.

It incorporates sqlalchemy, auth, forms, and other basic functionality needed
for most web applications.

Questions & Comments
---------------------

Please visit: http://groups.google.com/group/blazelibs

Current Status
---------------

The code stays pretty stable, but the API is likely to change in the future.

The `BaseBWA tip <http://bitbucket.org/rsyring/basebwa/get/tip.zip#egg=BaseBWA-dev>`_
is installable via `easy_install` with ``easy_install BaseBWA==dev``
"""
import sys
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

import basebwa
version = basebwa.VERSION

setup(
    name = "BaseBWA",
    version = version,
    description = "A supporting application for BlazeWeb applications.",
    long_description = __doc__,
    author = "Randy Syring",
    author_email = "rsyring@gmail.com",
    url='http://pypi.python.org/pypi/BaseBWA/',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
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
