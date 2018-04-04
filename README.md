# astrokit

[![Join the chat at https://gitter.im/astrokit/Lobby](https://badges.gitter.im/astrokit/Lobby.svg)](https://gitter.im/astrokit/Lobby?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

AstroKit (http://www.astrokit.org/) provides web-based tools for asteroid
characterization.  It's supported by [NASA](http://nspires.nasaprs.com/external/).

Users (scientists, amateur astronomers) will upload sky imagery and receive
astrometry, photometry, and light curve results derived from their images.

# Installation

## System dependencies: Linux

Some dependencies must be installed at the system level.  These packages are available on most Debian/Ubuntu distributions:

```
sudo apt-get install build-essential python-dev python-virtualenv libfreetype6-dev libxft-dev libblas-dev liblapack-dev libatlas-base-dev gfortran libspatialindex-dev sextractor psfex
```

PIL dependencies:

```
sudo apt-get install libtiff5-dev libjpeg-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python-tk
```

Postgres is optional but may be used in production:

```
sudo apt-get install postgresql postgresql-server-dev-9.4
```

## Node dependencies

Install a stable version of node.  See [NodeSource](https://nodejs.org/en/download/package-manager/#debian-and-ubuntu-based-linux-distributions) for latest install steps.  Currently, Node 8.x is the stable LTS distribution:

```
curl -sL https://deb.nodesource.com/setup_8.x | sudo -E bash -
sudo apt-get install -y nodejs
```

`yarn` installation is optional but recommended.  See [yarnpkg.org](https://yarnpkg.com/lang/en/docs/install/) for latest install steps.  Currently you may install like so:

```
curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -
echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list
sudo apt-get update && sudo apt-get install yarn
```

Next, `cd webassets/` and `yarn install` (or `npm install`)

Compile sass files with `gulp build`, or use the `yarn run build` (`npm run build`) alias.  If you are actively developing the web assets, use `yarn run watch` to recompile on-the-fly.  **Changes to web assets will not be reflected by the web server unless you rebuild**.

## Python dependencies

You installed virtualenv (python-virtualenv) above.  Now, create a virtualenv in the astrokit directory:

```
virtualenv venv
```

Enter the environment (you'll have to do this each time you want to run astrokit in a new terminal):

```
source venv/bin/activate
```

Install python dependencies:

```
pip install -r requirements.txt
```

# Before you run the server

```
# Run migrations
./manage.py migrate

# Create an admin user
./manage.py createsuperuser

# Create ImageFilter default objects
./manage.py loaddata image_filter
```
Build frontend dependencies (necessary whenever you change something in webassets/): `yarn run build`

# Run the server

`./manage.py runserver` and visit http://localhost:8000

# Use some examples

Go to `examples/blcam` and run `./download.sh` to download some example fits.

# Contributing

If you are looking to help to with a code contribution our project uses Python (Django), Javascript, HTML/CSS. If you don't feel ready to make a code contribution yet, feel free to reach out and we can discuss how to get involved!

If you are interested in making a code contribution, have a look at the issues tab to find an existing task or create your own issue that you'd like to work on.  Fork this repository and make your code changes.  When you're done (or if you want to check in on the direction of your change), create a pull request on Github against this project.

In the description of the pull request, explain the changes that you made, any issues you think exist with the pull request you made, and any questions you have for the maintainer. It's OK if your pull request is not perfect (no pull request is), the reviewer will be able to help you fix any problems and improve it!

# License (MIT)

Copyright (C) 2016 by Ian Webster (http://www.ianww.com)

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
