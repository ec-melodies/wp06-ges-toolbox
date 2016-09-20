. wfgen/wflib.sh

cDir=$PWD
NodeName=node_mtc

map_ct() {
   mkdir map_ct
   cd map_ct
   exec 2> err.txt
   echo "map_ct start "`date` > log.txt
   $cDir/jt_vto/runc.py --ifile list --ifield=votemper --ikey=list_cmonth --oac --ofile=.out.nc --okey=outcome_cmmap -s --bm 
   echo "map_ct end "`date` >> log.txt
   }

reduce_ct() {
   mkdir reduce_ct
   cd reduce_ct
   exec 2> err.txt
   echo "reduce_ct start "`date` > log.txt
   $cDir/jt_vto/runc.py --ifile list --ifield=votemper --ikey=outcome_cmmap --oac --ofile=out_m_12.nc --okey=outcome_cymap --bm
   echo "reduce_ct end "`date` >> log.txt
   }

reduce_oa() {
   mkdir reduce_oa
   cd reduce_oa
   exec 2> err.txt
   echo "reduce_oa start "`date` > log.txt
   $cDir/jt_vto/runc.py --ifile list --ifield=votemper --ikey=outcome_cmmap --oao --otc --ofile=out_ts_12.nc --okey=outcome_cmts --bm
   echo "reduce_oa end "`date` >> log.txt
   }

mkdir $NodeName
cd $NodeName
exec 2> err.txt

echo $NodeName" start "`date` > log.txt 

map_ct | passer buffer.txt | reduce_ct 
cat buffer.txt | reduce_oa 
cat buffer.txt 

echo $NodeName" end "`date` >> log.txt


