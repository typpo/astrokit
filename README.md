# astrokit

AstroKit provides web-based tools for asteroid characterization.  It's
supported by a NASA research grant and Deep Space Industries.

Users (scientists, amateur astronomers) will upload sky imagery.

## Installation

1. Install virtualenv (`sudo apt-get install python-virtualenv` on Debian/Ubuntu).

2. Create a virtualenv in the astrokit dierctory: `virtualenv venv`.

3. Enter the environment (you'll have to do this each time you want to run astrokit in a new terminal): `source venv/bin/activate`

4. Run it:  `./manage.py runserver`.

5. Postgres is optional but used in production:

    sudo apt-get install postgresql postgresql-server-dev-9.4
