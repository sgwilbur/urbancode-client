## Python client for interacting UrbanCode Web APIs

The primary client provides a Pythonic interface to UrbanCode for simplifying setup, administration, and testing of UrbanCode tools. The goal is to provide some working examples of API access to various pieces of functionality and I will refactor reusable bits as I can to make a more usable "client" for future use.

Let me know if you have specific APIs or scenarios that you want to see in action and I can try and make that happen :)

### Setup

These examples are built and tested with Python2 but I have tried not to do any thing or use any pip modules that will break in Python3. Install the requirements for these helpers are identified in the requirements.txt file:

    pip install -r requirements.txt

#### Running examples

Since everything here is adhoc and not using proper modules, to run the examples you need to cd to the `examples` directory as the imports are relatively pathed for now. So as an example I just create a new folder to work in, clone the repo, setup my virtualenv, install the required modules, and run an example.

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

Then actually running the script you pass in the required parameters:

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
