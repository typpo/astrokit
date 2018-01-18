# astrokit

AstroKit (http://www.astrokit.org/) provides web-based tools for asteroid
characterization.  It's supported by [NASA](http://nspires.nasaprs.com/external/).

Users (scientists, amateur astronomers) will upload sky imagery and receive
astrometry, photometry, and light curve results derived from their images.

# Installation

## Python dependencies

Install virtualenv (`sudo apt-get install python-virtualenv` on Debian/Ubuntu). 

Create a virtualenv in the astrokit directory: `virtualenv venv`.

Enter the environment (you'll have to do this each time you want to run astrokit in a new terminal): `source venv/bin/activate`

Install python dependencies:  `pip install -r requirements.txt`

## Other system dependencies

Install matplotlib: `sudo apt-get install libfreetype6-dev libxft-dev`

Install scipy: `sudo apt-get install libblas-dev liblapack-dev libatlas-base-dev gfortran libspatialindex-dev`

Install node modules: `npm install webassets/`

Compile sass files using gulp: `cd webassets && gulp build`

Postgres is optional but used in production:

    sudo apt-get install postgresql postgresql-server-dev-9.4
    
## Optional: IRAF setup

Download IRAF: http://iraf.noao.edu/ (README: ftp://iraf.noao.edu/iraf/v216/README)

`sudo apt-get install csh`

Put these statically linked binaries in your path:

ftp://iraf.noao.edu/pub/fitz/xgterm.STATIC
ftp://iraf.noao.edu/pub/fitz/ximtool.STATIC
    
# Before you run the server

Run migrations:  `./manage.py migrate`

And create an admin user:  `./manage.py createsuperuser`

Install frontend dependencies (only needed once, or when package.json changes):
```
cd webassets
yarn install
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
