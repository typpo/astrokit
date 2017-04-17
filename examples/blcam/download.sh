#!/bin/bash -e

for i in {1..9}; do
  wget "http://www.phys.vt.edu/~jhs/SIP/images/blcam/blcam_0${i}.fit"
done

for i in {10..21}; do
  wget "http://www.phys.vt.edu/~jhs/SIP/images/blcam/blcam_${i}.fit"
done
