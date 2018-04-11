from setuptools import find_packages
from setuptools import setup

setup (
    name='csra_release_utils',
    version='0.2',

    # Fill in these to make your Egg ready for upload to
    # PyPI
    author='DivineThreepwood',
    author_email='divine@openbase.org',

    description='A collection of util scripts to support and '
            'to simplify the csra release process.',
    url='https://github.com/csra/csra-release-utils',
    license="LGPLv3",
    long_description='CSRA release utils is a script collection to simpliefy the release process of your release candidate distribution. '
                     'This includes the automated generation of component branches and distribution files.',

    packages=find_packages('src'),
    package_dir={'': 'src'},
    zip_safe=True,

    # Declare your packages' dependencies here, for eg:
    install_requires=['GitPython', 'termcolor', 'coloredlogs', 'logging'],
    entry_points={
        "console_scripts": [
            "release-csra-rc = csra_release_utils.release:entry_point",
        ]
    },
)
