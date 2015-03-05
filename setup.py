from setuptools import setup, find_packages  # Always prefer setuptools over distutils
from codecs import open  # To use a consistent encoding
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, 'DESCRIPTION.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
  name='nvpnsxapi',
  version='0.1.0.dev1',
  description='An NSX / NVP API Binding for Python',
  long_description=long_description,
  url='https://github.com/wallnerryan/nsxnvpapi',
  author='Ryan Wallner',
  author_email='wallnerryan@gmail.com',
  license='Apache 2.0',
  classifiers=[

    'Development Status :: 1 - Alpha',

    'Intended Audience :: Developers',
    'Topic :: Software Development :: API Bindings',

     'License :: OSI Approved :: Apache 2.0 License',

    # Python versions supported 
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
  ],
  keywords='nsx nvp api python',
  packages=find_packages(exclude=['tests*']),
  install_requires = ['python-simplejson', 'python-m2crypto', 'python-pexpect'],
  data_files=[('confs', ['etc/nvp.conf', 'automation/configs/nvp-config-example.json'])],
  entry_points={
    'console_scripts': [
        'transportnode=automation:transportnode:main',
    ],
}
)
