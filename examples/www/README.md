## Example web Pipeline view

Using [Flask](http://flask.pocoo.org/) to host a simple web application, utilizing some of the nicer features for a rapid iterative framework for testing and creating views of the data. Namely the use of Jinga Templates and the simple caching mechanism to store copies of the larger requests from UCR to avoid rendering taking quite so long.

The current implementation all values are hardcoded and requires that you have access to the `www.py` file to set the server/user/pass to connect to UCR.

### Install pre-requisites

This is a basic Python setup based n 2.7 and uses standard modules available via pip to get up and running.

   git clone
   cd uc-clients/examples/www
   pip install < requirements.txt

See the uc-clients/README.md for and example of running this in a Python Virtual Environment, or where you do not want to make system wide changes.

### Starting the server

The server is wrapped with a simple CLI parser to allow for passing parameters in on startup.

    cd uc-clients/examples/www
    ./www.py [--host 127.0.0.1] [--port 5000] [--debug]
