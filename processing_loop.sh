#!/bin/bash -e

while [ 1 ]; do
  echo 'Running astrometry...'
  ./run_astrometry.py
  echo 'Running photometry...'
  ./run_photometry.py
  echo 'Running lightcurve reductions...'
  ./run_lightcurve_reductions.py
  echo 'Running image reductions...'
  ./run_image_reductions.py
  sleep 1
done
