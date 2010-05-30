"""
Introduction
---------------

pysapp is a library designed as a "supporting application" for
`pysmvt <http://pypi.python.org/pypi/pysmvt/>`_ applications.

Example applications will be avilable soon, for now, please follow the steps
below to get your own default application up and running.

Steps for Installation
----------------------

#. Install Python
#. install setuptools (includes easy_install)
#. install virtualenv `easy_install virtualenv`
#. Create a new virtual environement `virtualenv myproj-staging --no-site-packages`
#. `Activate the virtual environment (os dependent) <http://pypi.python.org/pypi/virtualenv#activate-script>`_
#. install pysapp & dependencies `easy_install pysapp`

Steps for creating a working application
-----------------------------------------

Note: the `pysmvt` command is installed when you install pysapp, which has
pysmvt as a requirement.

#. `cd myproj-staging`
#. `mkdir src`
#. `cd src`
#. `pysmvt project -t pysapp <myapp>` replace <myapp> with your project name
#. answer the questions that come up
#. write down "Login Details", referred to hereafter as <user> & <pass>
#. `cd <myapp>-dist`
#. `python setup.py -q develop`
#. `cd <myapp>`
#. `pysmvt broadcast initdb` setup the database tables
#. `pysmvt broadcast initdata <user>` put basic data in the database, use the 
   settings profile for your user
#. `pysmvt serve <user>` run a development http server with the user's settings 
   profile
#. point your browser at http://localhost:5000/
    
Creating a New Application Module
---------------------------------
This step creates a Application Module directory structure in <myapp>/modules/<mymod>:

`pysmvt module <mymod>`

where <mymod> is the name of the module you want to create

Questions & Comments
---------------------

Please visit: http://groups.google.com/group/pyslibs

Current Status
---------------

The code stays pretty stable, but the API is likely to change in the future.

The `pysapp tip <http://bitbucket.org/rsyring/pysapp/get/tip.zip#egg=pysapp-dev>`_
is installable via `easy_install` with ``easy_install pysapp==dev``
"""
import sys
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

version = '0.2'

setup(
    name = "pysapp",
    version = version,
    description = "A pysmvt supporting application",
    long_description = __doc__,
    author = "Randy Syring",
    author_email = "rsyring@gmail.com",
    url='http://pypi.python.org/pypi/pysapp/',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
      ],
    license='BSD',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    install_requires = [
        "Elixir>=0.6.1",
        "pysmvt>=0.2",
        "pysform>=0.2",
        "SQLiteFKTG4SA>=0.1.1",
        "python-dateutil>=1.4.1"
    ],
    entry_points="""
    [pysmvt.pysmvt_project_template]
    pysapp = pysapp.lib.paster_tpl:ProjectTemplate

    [pysmvt.pysmvt_module_template]
    pysapp = pysapp.lib.paster_tpl:ModuleTemplate
    """,
    zip_safe=False
)