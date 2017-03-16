## Python client for interacting UrbanCode Web APIs

The primary client provides a Pythonic interface to UrbanCode for simplifying setup, administration, and testing of UrbanCode tools. The goal is to provide some working examples of API access to various pieces of functionality and I will refactor reusable bits as I can to make a more usable "client" for future use.

Let me know if you have specific APIs or scenarios that you want to see in action and I can try and make that happen :)

### Setup

These examples are built and tested with Python2 but I have tried not to do any thing or use any pip modules that will break in Python3. Install the requirements for these helpers are identified in the requirements.txt file:

    pip install -r requirements.txt

#### In Docker

    docker build -t uc-cli .

### Running examples

Since everything here is now a simple module, so until I get in published to the public pypi repos it is still an download and install process, so not ideal but getting there.

To run the examples you can view them in the `examples` directory. So as an example I just create a new folder to work in, clone the repo, setup my virtualenv, install the required modules, and run an example.

    sgwilbur@gura:~/workspaces$ mkdir uc-testing
    sgwilbur@gura:~/workspaces$ cd uc-testing/
    sgwilbur@gura:~/workspaces/uc-testing$ git clone https://github.com/sgwilbur/urbancode-clients
    Cloning into 'urbancode-clients'...
    remote: Counting objects: 142, done.
    remote: Total 142 (delta 0), reused 0 (delta 0), pack-reused 142
    Receiving objects: 100% (142/142), 64.63 KiB | 0 bytes/s, done.
    Resolving deltas: 100% (57/57), done.
    Checking connectivity... done.

[optional] Setup a testing Python virtual env ( See http://docs.python-guide.org/en/latest/dev/virtualenvs/ )

    sgwilbur@gura:~/workspaces/uc-testing$ virtualenv -p python2 urbancode-clients-virtualenv
    Running virtualenv with interpreter /usr/local/bin/python2
    New python executable in urbancode-clients-virtualenv/bin/python2.7
    Also creating executable in urbancode-clients-virtualenv/bin/python
    Installing setuptools, pip...done.
    sgwilbur@gura:~/workspaces/uc-testing$ . ./urbancode-clients-virtualenv/bin/activate

Install the dependencies:

    (urbancode-clients-virtualenv)sgwilbur@gura:~/workspaces/uc-testing$ cd urbancode-clients
    (urbancode-clients-virtualenv)sgwilbur@gura:~/workspaces/uc-testing/urbancode-clients$ pip install -r requirements.txt
    You are using pip version 6.0.8, however version 7.1.2 is available.
    You should consider upgrading via the 'pip install --upgrade pip' command.
    Collecting datadiff==1.1.6 (from -r requirements.txt (line 1))
    Using cached datadiff-1.1.6.zip
    Collecting requests==2.7.0 (from -r requirements.txt (line 2))
    Using cached requests-2.7.0-py2.py3-none-any.whl
    Installing collected packages: requests, datadiff

    Running setup.py install for datadiff
    Successfully installed datadiff-1.1.6 requests-2.7.0

And install the module.

    python setup.py install
    (urbancode-clients-virtualenv)sgwilbur@gura:~/workspaces/uc-testing/urbancode-clients$ python setup.py install
    running install
    running build
    running build_py
    creating build/lib/urbancode_client
    copying urbancode_client/__init__.py -> build/lib/urbancode_client
    copying urbancode_client/common.py -> build/lib/urbancode_client
    copying urbancode_client/resource.py -> build/lib/urbancode_client
    copying urbancode_client/utils.py -> build/lib/urbancode_client
    creating build/lib/urbancode_client/deploy
    copying urbancode_client/deploy/__init__.py -> build/lib/urbancode_client/deploy
    copying urbancode_client/deploy/environment.py -> build/lib/urbancode_client/deploy
    copying urbancode_client/deploy/ucdclient.py -> build/lib/urbancode_client/deploy
    creating build/lib/urbancode_client/release
    copying urbancode_client/release/__init__.py -> build/lib/urbancode_client/release
    copying urbancode_client/release/ucrclient.py -> build/lib/urbancode_client/release
    running install_lib
    creating /Users/sgwilbur/workspaces/python-virtualenvs/urbancode-clients-virtualenv/lib/python2.7/site-packages/urbancode_client
    copying build/lib/urbancode_client/__init__.py -> /Users/sgwilbur/workspaces/python-virtualenvs/urbancode-clients-virtualenv/lib/python2.7/site-packages/urbancode_client
    copying build/lib/urbancode_client/common.py -> /Users/sgwilbur/workspaces/python-virtualenvs/urbancode-clients-virtualenv/lib/python2.7/site-packages/urbancode_client
    creating /Users/sgwilbur/workspaces/python-virtualenvs/urbancode-clients-virtualenv/lib/python2.7/site-packages/urbancode_client/deploy
    copying build/lib/urbancode_client/deploy/__init__.py -> /Users/sgwilbur/workspaces/python-virtualenvs/urbancode-clients-virtualenv/lib/python2.7/site-packages/urbancode_client/deploy
    copying build/lib/urbancode_client/deploy/environment.py -> /Users/sgwilbur/workspaces/python-virtualenvs/urbancode-clients-virtualenv/lib/python2.7/site-packages/urbancode_client/depl
    oy
    copying build/lib/urbancode_client/deploy/ucdclient.py -> /Users/sgwilbur/workspaces/python-virtualenvs/urbancode-clients-virtualenv/lib/python2.7/site-packages/urbancode_client/deploy
    creating /Users/sgwilbur/workspaces/python-virtualenvs/urbancode-clients-virtualenv/lib/python2.7/site-packages/urbancode_client/release
    copying build/lib/urbancode_client/release/__init__.py -> /Users/sgwilbur/workspaces/python-virtualenvs/urbancode-clients-virtualenv/lib/python2.7/site-packages/urbancode_client/releas
    e
    copying build/lib/urbancode_client/release/ucrclient.py -> /Users/sgwilbur/workspaces/python-virtualenvs/urbancode-clients-virtualenv/lib/python2.7/site-packages/urbancode_client/relea
    se
    copying build/lib/urbancode_client/resource.py -> /Users/sgwilbur/workspaces/python-virtualenvs/urbancode-clients-virtualenv/lib/python2.7/site-packages/urbancode_client
    copying build/lib/urbancode_client/resource.py -> /Users/sgwilbur/workspaces/python-virtualenvs/urbancode-clients-virtualenv/lib/python2.7/site-packages/urbancode_client
    copying build/lib/urbancode_client/utils.py -> /Users/sgwilbur/workspaces/python-virtualenvs/urbancode-clients-virtualenv/lib/python2.7/site-packages/urbancode_client
    byte-compiling /Users/sgwilbur/workspaces/python-virtualenvs/urbancode-clients-virtualenv/lib/python2.7/site-packages/urbancode_client/__init__.py to __init__.pyc
    byte-compiling /Users/sgwilbur/workspaces/python-virtualenvs/urbancode-clients-virtualenv/lib/python2.7/site-packages/urbancode_client/common.py to common.pyc
    byte-compiling /Users/sgwilbur/workspaces/python-virtualenvs/urbancode-clients-virtualenv/lib/python2.7/site-packages/urbancode_client/deploy/__init__.py to __init__.pyc
    byte-compiling /Users/sgwilbur/workspaces/python-virtualenvs/urbancode-clients-virtualenv/lib/python2.7/site-packages/urbancode_client/deploy/environment.py to environment.pyc
    byte-compiling /Users/sgwilbur/workspaces/python-virtualenvs/urbancode-clients-virtualenv/lib/python2.7/site-packages/urbancode_client/deploy/ucdclient.py to ucdclient.pyc
    byte-compiling /Users/sgwilbur/workspaces/python-virtualenvs/urbancode-clients-virtualenv/lib/python2.7/site-packages/urbancode_client/release/__init__.py to __init__.pyc
    byte-compiling /Users/sgwilbur/workspaces/python-virtualenvs/urbancode-clients-virtualenv/lib/python2.7/site-packages/urbancode_client/release/ucrclient.py to ucrclient.pyc
    byte-compiling /Users/sgwilbur/workspaces/python-virtualenvs/urbancode-clients-virtualenv/lib/python2.7/site-packages/urbancode_client/resource.py to resource.pyc
    byte-compiling /Users/sgwilbur/workspaces/python-virtualenvs/urbancode-clients-virtualenv/lib/python2.7/site-packages/urbancode_client/utils.py to utils.pyc
    running install_egg_info
    Writing /Users/sgwilbur/workspaces/python-virtualenvs/urbancode-clients-virtualenv/lib/python2.7/site-packages/urbancode_client-0.1-py2.7.egg-info

Now you are ready to run the examples, I created a template after creating a handful of these so they conform to a standard pattern to some extent. For example calling a specific example with no parameters should output a usage statement.

    (urbancode-clients-virtualenv)sgwilbur@gura:~/workspaces/uc-testing/urbancode-clients/examples$ ./ucd-compare_roles.py
    Missing required arguments
    ucd-compare_roles
    [-h|--help] - Optional, show usage
    [-v|--verbose] - Optional, turn on debugging
    -s|--server http[s]://server[:port] - Set server url
    [-u|--user username (do not supply when using a token) ]
    --password [password|token] - Supply password or token to connect with
    "<Role Name>" "<Role Name>" - 2 Roles to compare, quotes only required when Role Name contains spaces

Then run the example of choice:

    (urbancode-clients-virtualenv)sgwilbur@gura:~/workspaces/uc-testing/urbancode-clients/examples$ ./ucd-compare_roles.py --server https://ucdandr:9443 --user admin --password admin Developer Observer
    Defined Roles: Administrator, Developer, Observer
    Comparing Developer and Observer
    Only in Developer (14)
        Action: View processes in this team.
        Action: Execute processes.
        Action: Manage resources.
        Action: Execute processes on environments.
        Action: View environments in this team.
        Action: View components in this team.
        Action: View cloud connections in this team.
        Action: View resources in this team.
        Action: View agent pools in this team.
        Action: View applications in this team.
        Action: View agents in this team.
        Action: View the processes tab.
        Action: View component templates in this team.
        Action: View resource templates in this team.
    Only n Observer (1)
        Action: Edit basic settings for components.

Or you can also run in Docker (after building the image above in the Setup section):

    docker run -it uc-cli ucd-compare_roles.py <args>
