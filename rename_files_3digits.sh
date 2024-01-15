#!/bin/bash
##home=$(pwd)
num=`expr match "$1" '[^0-9]*\([0-9]\+\).*'`
paddednum=`printf "%03d" $num`
mv --i -- $i ${1/$num/$paddednum}
