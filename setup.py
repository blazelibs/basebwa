"""
Introduction
---------------

pysapp is a library designed as a "supporting application" for
`pysmvt <http://pypi.python.org/pypi/pysmvt/>`_ applications.

Documentation and example applications are not yet available.

Steps for Installation
----------------------

#. Install Python
#. install setuptools (includes easy_install)
#. install virtualenv `easy_install virtualenv`
#. make a staging area `mkdir myproj-staging`
#. `cd myproj-staging`
#. Create a new virtual environement `virtualenv ENV --no-site-packages`
#. `Activate the virtual environment <http://pypi.python.org/pypi/virtualenv#activate-script>`
#. install pysapp & dependencies `easy_install pysapp`

Steps for creating a working application
-----------------------------------------

#. `pysmvt project -t pysapp <myapp>` replace <myapp> with your project name
#. answer the questions that come up
#. write down "Login Details", referred to hereafter as <user> & <pass>
#. `cd <myapp>-dist`
#. `python setup.py -q develop`
#. `cd <myapp>`
#. `pysmvt broadcast initdb` setup the database tables
#. `pysmvt broadcast initmod -p <user>` let modules set themselves up, use the 
   settings profile for your user
#. `pysmvt serve <user>` run a development http server with the user's settings 
   profile
    
Creating a new application module
---------------------------------
`pysmvt module <mymod>` where <mymod> is the name of the module you want to create


Current Status
---------------

We are currently in an alpha phase which means lots of stuff can change, maybe rapidly, and we are not interested in backwards compatibility at this point.

I am currently using this library for some production websites, but I wouldn't recommend you do that unless you **really** know what you are doing.

The unstable `development version
<https://svn.rcslocal.com:8443/svn/pysmvt/pysapp/trunk/#egg=pysapp-dev>`_.
"""
import sys
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name = "pysapp",
    version = "0.1dev",
    description = "A pysmvt supporting application",
    long_description = __doc__,
    author = "Randy Syring",
    author_email = "randy@rcs-comp.com",
    url='http://pypi.python.org/pypi/pysapp/',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
      ],
    license='BSD',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    install_requires = [
        "Elixir>=0.6.1",
        "pysmvt>=dev",
        "pyhtmlquickform>=dev",
        "SQLiteFKTG4SA>=dev",
    ],
    entry_points="""
    [pysmvt.pysmvt_project_template]
    pysapp = pysapp.lib.paster_tpl:ProjectTemplate

    [pysmvt.pysmvt_module_template]
    pysapp = pysapp.lib.paster_tpl:ModuleTemplate
    """,
    zip_safe=False
)