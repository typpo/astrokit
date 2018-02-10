#!/bin/bash -e
# Script for running docker astrometry.net server, used to solve astrometry.

sudo apt-get install git-core
curl -sSL https://get.docker.com/ | sh
sudo usermod -aG docker ${USER}

git clone -b astrokit_modifications https://github.com/typpo/nova-docker.git
cd nova-docker

cd /INDEXES/ && for i in 4100 4200; do \
     wget -r -l1 --no-parent -nc -nd -A ".fits" http://data.astrometry.net/$i/; \
done
cd ..

wget http://data.astrometry.net/hip.fits
wget http://data.astrometry.net/tycho2.kd
wget http://data.astrometry.net/hd.fits

docker build -t astrometryserver .
docker run -d -p 80:80 --mount type=bind,source=$PWD/INDEXES,target=/INDEXES astrometryserver
