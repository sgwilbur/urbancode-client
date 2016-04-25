from distutils.core import setup

setup(name='urbancode_client',
      version='0.1',
      description='UrbanCode Client modules for Python',
      url='http://github.com/sgwilbur/urbancode-client',
      author='Sean Wilbur',
      author_email='sgwilbur@gmail.com',
      license='MIT',
      packages=['urbancode_client', 'urbancode_client.deploy', 'urbancode_client.release']
)
