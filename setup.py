from setuptools import setup, find_packages  # Always prefer setuptools over distutils
import codecs  # To use a consistent encoding
from os import path

# Get the long description from the relevant file                               
with codecs.open('DESCRIPTION.rst', encoding='utf-8') as f:
    long_description = f.read()

setup(
  name='nvpnsxapi',
  version='0.1.3.dev1',
  description='An NSX / NVP API Binding for Python',
  long_description=long_description,
  url='https://github.com/wallnerryan/nvpnsxapi',
  author='Ryan Wallner',
  author_email='wallnerryan@gmail.com',
  license='Apache 2.0',
  classifiers=[

    'Development Status :: 2 - Pre-Alpha',

    'Intended Audience :: Developers',
    'Topic :: Software Development :: Libraries :: Python Modules',

    'License :: OSI Approved :: Apache Software License',

    # Python versions supported 
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
  ],
  keywords='nsx nvp api python',
  packages=find_packages(exclude=['tests*']),
  install_requires = ['simplejson', 'paramiko','m2crypto',
                      'swigibpy', 'configparser', 'pyOpenSSL',
                      'pexpect'],
  data_files=[('/etc/nvp/', ['etc/nvp.conf']),
              ('/etc/nvp/configs/',['automation/configs/nvp-config-example.json'])
  ],
  package_data = {
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.json', '*.conf'],
  },
  entry_points={
    'console_scripts': [
        'transportnode=automation.transportnode:main',
    ],
}
)
