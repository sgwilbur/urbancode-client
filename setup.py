from distutils.core import setup

setup(name='ucclient',
      version='0.1',
      description='UrbanCode Client modules for Python',
      url='http://github.com/sgwilbur/urbancode-clients',
      author='Sean Wilbur',
      author_email='sgwilbur@gmail.com',
      license='MIT',
      packages=['ucclient', 'ucclient/ucd', 'ucclient/release'],
      install_requires=[
          'requests',
      ],
      zip_safe=False)
