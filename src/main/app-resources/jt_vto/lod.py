import sys
import comic
import netCDF4

# cd /home/melodies-wp6/ncpi/scratch/lod
# ls *nc | python jt_vto/lod.py ls 1> a
# cat a
#sea_water_salinity
#2013-07-12
#daily_mean_map
#-6.03125 30.15625 - 36.28125 45.96875
#19870101_dm-INGV--PSAL-MFSs4b3-MED-b20130712_re-fv04.00.nc
#sea_water_potential_temperature
#2013-07-12
#daily_mean_map
#-6.03125 30.15625 - 36.28125 45.96875

def PrintMetaRecord(myin,myinm) :
   print myin
   #print myinm.StandardName
   #print myinm.created
   #print myinm.celltype
   #print myinm.LonCells[0],myinm.LatCells[0],'-',myinm.LonCells[-1],myinm.LatCells[-1]
   t_start=netCDF4.num2date(myinm.TimeCells[0],units='hours since 1900-01-01 00:00:00',calendar='standard')
   t_end=netCDF4.num2date(myinm.TimeCells[1],units='hours since 1900-01-01 00:00:00',calendar='standard')
   print t_start,'-',t_end

def ReadMeta(myin) :
   myinm=None
   try : myinm=comic.ionc.ReadFile(myin,'vosaline',NoData=True)
   except: pass
   try : myinm=comic.ionc.ReadFile(myin,'votemper',NoData=True)
   except: pass
   return myinm


myin=sys.stdin.readline().replace("\r","").replace("\n","").replace(" ","").replace("\t","")
myinm=ReadMeta(myin)
PrintMetaRecord(myin,myinm)

TagVariable=myinm.StandardName
TagType=myinm.celltype
TagProdDate=myinm.created
TagGeoCover=(myinm.LonCells[0],myinm.LatCells[0],myinm.LonCells[-1],myinm.LatCells[-1])
TagTime=[myinm.TimeCells[0],myinm.TimeCells[1]]

myin=sys.stdin.readline().replace("\r","").replace("\n","").replace(" ","").replace("\t","")

while myin :

   print
   myinm=ReadMeta(myin)
   if myinm is not None :
      if TagVariable==myinm.StandardName and TagType==myinm.celltype and TagProdDate==myinm.created and TagGeoCover==(myinm.LonCells[0],myinm.LatCells[0],myinm.LonCells[-1],myinm.LatCells[-1]) :
         PrintMetaRecord(myin,myinm) 
         if TagTime[0]>myinm.TimeCells[0] : TagTime[0]=myinm.TimeCells[0]
         if TagTime[1]<myinm.TimeCells[1] : TagTime[1]=myinm.TimeCells[1]

   myin=sys.stdin.readline().replace("\r","").replace("\n","").replace(" ","").replace("\t","")

print TagVariable
print TagType
print TagProdDate
print TagGeoCover[0],TagGeoCover[1],TagGeoCover[2],TagGeoCover[3]
t_start=netCDF4.num2date(TagTime[0],units='hours since 1900-01-01 00:00:00',calendar='standard')
t_end=netCDF4.num2date(TagTime[1],units='hours since 1900-01-01 00:00:00',calendar='standard')
print t_start,'-',t_end

