# astrokit

AstroKit (http://www.astrokit.org/) provides web-based tools for asteroid
characterization.  It's supported by [NASA](http://nspires.nasaprs.com/external/).

Users (scientists, amateur astronomers) will upload sky imagery and receive
astrometry, photometry, and light curve results derived from their images.

## Installation

Install virtualenv (`sudo apt-get install python-virtualenv` on Debian/Ubuntu).  Also install redis (`sudo apt-get install redis-server`).

Create a virtualenv in the astrokit directory: `virtualenv venv`.

Enter the environment (you'll have to do this each time you want to run astrokit in a new terminal): `source venv/bin/activate`

Install matplotlib system dependencies: `sudo apt-get install libfreetype6-dev libxft-dev`

Install scipy system dependencies: `sudo apt-get install libblas-dev liblapack-dev libatlas-base-dev gfortran libspatialindex-dev`

Install numpy and scipy first (scikit bug): `pip install numpy scipy`

Install pip dependencies: `pip install -r requirements.txt`

Install node modules: `npm install sass/`

Compile sass files using gulp: `cd sass && gulp build`

[NOT NEEDED ANYMORE]  ~~Setup the astrometry analyzer: `./astrometry/setup/setup.sh`.  This will take some time.~~

Run the server:  `./manage.py runserver`.

Postgres is optional but used in production:

    sudo apt-get install postgresql postgresql-server-dev-9.4

## Post setup

In your virtual environment...

`python manage.py createsuperuser`
`python manage.py migrate`

## IRAF setup

Download IRAF: http://iraf.noao.edu/

Read the README: ftp://iraf.noao.edu/iraf/v216/README

`sudo apt-get install csh`

Put these statically linked binaries in your path:

ftp://iraf.noao.edu/pub/fitz/xgterm.STATIC
ftp://iraf.noao.edu/pub/fitz/ximtool.STATIC

## Other

pip install numpy scipy scikit-image photuils
sudo apt-get install libblas-dev liblapack-dev libatlas-base-dev gfortran g++


