#!/bin/bash -e

while [ 1 ]; do
  echo 'Running astrometry...'
  ./run_astrometry.py
  echo 'Running photometry...'
  ./run_photometry.py
  echo 'Running reductions...'
  ./run_reductions.py
  sleep 1
done
