#!/bin/bash -e

while [ 1 ]; do
  echo 'Running astro phot...'
  ./run_astro_phot.py
  echo 'Running reductions...'
  ./run_reductions.py
  sleep 1
done
