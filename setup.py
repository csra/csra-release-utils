from setuptools import find_packages
from setuptools import setup

setup (
       name='CSRAReleaseScripts',
       version='0.1',
       packages=find_packages(),

       # Fill in these to make your Egg ready for upload to
       # PyPI
       author='DivineThreepwood',
       author_email='divine@openbase.org',

       #summary = 'Just another Python package for the cheese shop',
       url='http://www.openbase .org',
       license="LGPLv3",
       long_description='CSRA release scripts is a script collection to simpliefy the release process. This includes the automated generation of component branches and distribution files.',
       
       scripts=['citec/csra/release-csra-rc.py'],
       # could also include long_description, download_url, classifiers, etc.
       
       # Declare your packages' dependencies here, for eg:
       install_requires = ['gitpython'],
)
