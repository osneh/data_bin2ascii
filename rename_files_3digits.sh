#!/bin/bash
num=`expr match "$1" '[^0-9]*\([0-9]\+\).*'`
paddednum=`printf "%03d" $num`
##echo ${1/$num/$paddednum}
mv -i -- $i ${1/$num/$paddednum}
