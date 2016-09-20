. wfgen/wflib.sh

cDir=$PWD/`dirname $0`     #to link jt_vto and wfgen, must be in same dir with this file
cUP=$PWD/up                #file with authentication info in case of ftp access
NodeName=wf

mkdir $NodeName
cd $NodeName
exec 2> err.txt
echo $NodeName" start "`date` > log.txt
ln -fs $cDir/../jt_vto jt_vto
ln -fs $cDir/../wfgen wfgen
gather $cUP | $cDir/node_vg.sh | $cDir/node_mtmg.sh | passer buffer.txt | $cDir/node_mty.sh 
cat buffer.txt | $cDir/node_mtc.sh 
grep outcome_m buffer.txt 

echo $NodeName" end "`date` >> log.txt
