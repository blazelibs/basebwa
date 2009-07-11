from setuptools import setup, find_packages

version = '0.1'

setup(name='pysappexample',
      version=version,
      description="Example application based on pysapp",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='matt',
      author_email='matt@rcs-comp.com',
      url='',
      license='',
      packages= find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'pysapp>=dev'
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      [nose.plugins]
      testsfrompackage = pysmvt.test:TestsFromPackagePlugin
      """,
      )
