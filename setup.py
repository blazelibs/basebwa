import sys
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name = "pysapp",
    version = "0.1.0",
    description = "A pysmvt supporting application",
    long_description = "Coming eventually",
    author = "Randy Syring",
    author_email = "randy@rcs-comp.com",
    url='http://pypi.python.org/pypi/pysapp',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
      ],
    license='BSD',
    packages=['pysapp'],
    install_requires = [
        "Elixir>=0.6.1",
        "pysmvt>=dev",
        "pysform>=dev",
        "SQLiteFKTG4SA>=dev",
    ],
    dependency_links = [
        "https://svn.rcslocal.com:8443/svn/pysmvt/pysmvt/trunk/#egg=pysmvt-dev",
        "https://svn.rcslocal.com:8443/svn/pysmvt/pysform/trunk/#egg=pysform-dev"
    ],
    zip_safe=False
)