#!/bin/sh

# TDA performance test used to determine optimal number of threads (-n ?)
# to use when running on a given number of VMs in Saucelabs or other Selenium Grid

date
for i in {1..12}; do
  echo "-n $i"
  RUN_ID=util_test_n_$i BATCH_SIZE=10 REPEATABLE_RANDOM=1 py.test -s -n $i desktop_web
done
date

