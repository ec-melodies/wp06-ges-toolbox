#!/bin/bash

#. wfgen/wflib.sh

cDir=$PWD
NodeName=node_vg

map_v() {
   mkdir map_v
   cd map_v
   exec 2> err.txt
   echo "map_v start "`date` > log.txt
   $cDir/jt_vto/runc.py --ifile list --ifield=votemper --oav='[0,10,50,100,500,1000,2000]' --okey=none --bm --iClean
   echo "map_v end "`date` >> log.txt
   }

reduce_gm() {
   mkdir reduce_gm
   cd reduce_gm
   exec 2> err.txt
   echo "reduce_gm start "`date` > log.txt
   $cDir/jt_vto/node_g.py none 6 list_month
   echo "reduce_gm end "`date` >> log.txt
   }



mkdir $NodeName
cd $NodeName
exec 2> err.txt
echo $NodeName" start "`date` > log.txt
map_v | reduce_gm
echo $NodeName" end "`date` >> log.txt
