#!/usr/bin/python

import sys

#from sp_type import Characteristic
import sp_type
import sp_glob

#verbose=False

#center of input layer : 1.47 4.58 7.94 11.55
# input layers         : 0 - 2.94 - 6.22 - 9.66 - 13.44
# input thickness      : 2.94 3.28 3.44 3.78

#def FindIndex (a,MyOutputLonMin,MyOutputLonMax):
#   import numpy
#   mapCondition = ((MyOutputLonMin<=a) * (a<=MyOutputLonMax))
#   e= numpy.extract(mapCondition,numpy.arange(a.size))
#   MyOutputLonIndex=[e.min(),e.max()]
#   if sp_glob.verbose : print 'Inner : ',a[MyOutputLonIndex[0]]
#   #print mm[m.index(True)]
#   if sp_glob.verbose : print 'Outer : ',a[MyOutputLonIndex[1]]
#   return MyOutputLonIndex



def ReadFile(MyInputFile,MyInputVariable,MyOutputLon=None,MyOutputLat=None,af64MyOutputLayer=None,RemoveInput=False) :  
   import netCDF4
   import numpy
   import os

   print >>sys.stderr, 'dbdbdbdb',MyInputFile
   MyDataset=netCDF4.Dataset(MyInputFile)
   print >>sys.stderr, 'WARNING 13 : now able to read only Med MFC file format, an important inprovement would be the ability to read bounds'
   MyDatasetVariable=MyDataset.variables[MyInputVariable]

   StandardName=getattr(MyDatasetVariable,'standard_name')
   #mv=getattr(MyDatasetVariable,'missing_value')
   #print 'mv',mv

   for tV in MyDatasetVariable.dimensions :
      #print MyDataset.variables[tV].standard_name
      if MyDataset.variables[tV].standard_name == 'latitude' :
         MyDatasetLat=MyDataset.variables[tV]
      if MyDataset.variables[tV].standard_name == 'longitude' :
         MyDatasetLon=MyDataset.variables[tV]
      if MyDataset.variables[tV].standard_name == 'depth' :
         MyDatasetDepth=MyDataset.variables[tV]
      if MyDataset.variables[tV].standard_name == 'time' :
         MyDatasetTime=MyDataset.variables[tV]
         #print MyDatasetTime.ncattrs()
         if 'bounds' in MyDatasetTime.ncattrs() : # MyDataset.variables[tV].bounds != '' :
            MyDatasetTimeBnds=MyDataset.variables[MyDataset.variables[tV].bounds]
         else :
            MyDatasetTimeBnds=None

   #print 'XYZ',MyDatasetLon,MyDatasetLat,MyOutputLon
   #if MyOutputLon != 'all' :
   if MyOutputLon is not None :
      MyOutputLonIndex=sp_type.FindIndex(MyDatasetLon[:],MyOutputLon[0],MyOutputLon[1])
      MyDatasetLon=MyDatasetLon[MyOutputLonIndex[0]:MyOutputLonIndex[1]]
   else :
      MyOutputLonIndex=(0,MyDatasetLon.size)
   if sp_glob.verbose : print >>sys.stderr, 'Lon Index :',MyOutputLonIndex
   #if MyOutputLat != 'all' :
   if MyOutputLat is not None :
      MyOutputLatIndex=sp_type.FindIndex(MyDatasetLat[:],MyOutputLat[0],MyOutputLat[1])
      MyDatasetLat=MyDatasetLat[MyOutputLatIndex[0]:MyOutputLatIndex[1]]
   else :
      MyOutputLatIndex=(0,MyDatasetLat.size)
   if sp_glob.verbose : print >>sys.stderr, 'Lat Index :',MyOutputLatIndex

   #print 'XYZ',MyDatasetLon,MyDatasetLat
   #build layer
   print >>sys.stderr, "WARNING 4 : not able to read depth boundaries"
   MyDatasetDepthLayer=numpy.insert(MyDatasetDepth[:],0,0)
   for i in range(MyDatasetDepth[:].size) :
      MyDatasetDepthLayer[i+1]=MyDatasetDepth[i]*2-MyDatasetDepthLayer[i] #prev
   if af64MyOutputLayer is not None :
      #MyDatasetDepthLayer=numpy.insert(MyDatasetDepth[:],0,0)
      #for i in range(MyDatasetDepth[:].size) :
      #   MyDatasetDepthLayer[i+1]=MyDatasetDepth[i]*2-MyDatasetDepthLayer[i] #prev
   #print "mmm",MyDatasetDepthLayer.size,MyDatasetDepthLayer

      MyInputDepthIndex=sp_type.FindIndex(MyDatasetDepthLayer,af64MyOutputLayer.min(),af64MyOutputLayer.max())
      if sp_glob.verbose : print >>sys.stderr, 'Depth Index :',MyInputDepthIndex
      #MyInputDepthIndex[1]=MyInputDepthIndex[1]+1
      #if MyInputDepthIndex[0]>0 : MyInputDepthIndex[0]=MyInputDepthIndex[0]-1
      MyDatasetDepthLayer=MyDatasetDepthLayer[MyInputDepthIndex[0]:MyInputDepthIndex[1]+1]
   else :
      MyInputDepthIndex=(0,MyDatasetDepth.size)
   #   MyDatasetDepthLayer=numpy.insert(MyDatasetDepth[:],0,0)
   #if sp_glob.verbose : print MyDatasetDepthLayer
   #MyDatasetVariable=MyDatasetVariable[:,MyInputDepthIndex[0]:MyInputDepthIndex[1],MyOutputLatIndex[0]:MyOutputLatIndex[1],MyOutputLonIndex[0]:MyOutputLonIndex[1]].copy()
   MyDatasetVariable=numpy.ma.asarray(MyDatasetVariable[:,MyInputDepthIndex[0]:MyInputDepthIndex[1],MyOutputLatIndex[0]:MyOutputLatIndex[1],MyOutputLonIndex[0]:MyOutputLonIndex[1]].copy())
   #print 'YYY1',type(MyDatasetVariable)
   #print 'm',MyDatasetVariable.mask[0,0,:,0]
   #LandMask=(MyDatasetVariable == mv)
   #print MyDatasetVariable[0,0,:,0]
   #print LandMask[0,0,:,0]
#Land=(tmpTemp == mv)
#tmpZTemp=numpy.where(Land, numpy.zeros_like(tmpTemp), tmpTemp)
##print tmpZTemp[0,0,:,0]
##Land=numpy.where(tmpTemp == mv, True , False)
##tmpZTemp=numpy.where(Land,numpy.zeros_like(tmpTemp),tmpTemp)

   #print 'XYZ',MyDatasetLon,MyDatasetLat
   LonCells=numpy.zeros((MyDatasetLon.size+1))
   DeltaLon=(MyDatasetLon[1]-MyDatasetLon[0])/2
   LonCells[0]=MyDatasetLon[0]-DeltaLon
   LonCells[1:]=MyDatasetLon[:]+DeltaLon

   LatCells=numpy.zeros((MyDatasetLat.size+1))
   DeltaLat=(MyDatasetLat[1]-MyDatasetLat[0])/2
   LatCells[0]=MyDatasetLat[0]-DeltaLat
   LatCells[1:]=MyDatasetLat[:]+DeltaLat

   import datetime
### READ MONTHLY FILE : START
#   #TimeCells=numpy.zeros((MyDatasetTime.size+1),dtype=numpy.int64)
#   #convert to datetime to elaborate
#   dtTmp=netCDF4.num2date(MyDatasetTime[:],units=MyDatasetTime.units,calendar=MyDatasetTime.calendar)
#   #for i in range(dtTmp.size) :
#      #print 'dtTmp[i]',dtTmp[i]
#      #dtTmp[i]=dtTmp[i]-datetime.timedelta(hours=12)
#      #print 'dtTmp[i]',dtTmp[i]
#   dtTmp[:]=dtTmp[:]-datetime.timedelta(hours=12)
#   dtLast=dtTmp[dtTmp.size-1]+datetime.timedelta(hours=12)
#   RifMonth=dtLast.month
#   while RifMonth==dtLast.month : dtLast=dtLast+datetime.timedelta(days=1)
#   dtLast=dtLast-datetime.timedelta(hours=12)
#   if sp_glob.verbose : print dtTmp,'Last',dtLast
#   #dtTmp2=netCDF4.date2num(dtTmp,units='seconds since 1900-01-01 00:00:00',calendar='standard')
#   #print dtTmp,dtTmp.size,dtTmp[0],TimeCells[0]
#   #TimeCells[0]=dtTmp2[0]
#   #print 'dtTmp[0]',dtTmp[0],dtTmp2[0]
#   #TimeCells[1:]=dtTmp2[:]
#   TimeCells=numpy.zeros((MyDatasetTime.size+1),dtype=numpy.int64)
#   TimeCells[:TimeCells.size-1]=netCDF4.date2num(dtTmp,units='hours since 1900-01-01 00:00:00',calendar='standard')
#   TimeCells[TimeCells.size-1]=netCDF4.date2num(dtLast,units='hours since 1900-01-01 00:00:00',calendar='standard')
### READ MONTHLY FILE : END
### READ DAILY FILE : START
   if MyDatasetTimeBnds is None :
      dtTmp=netCDF4.num2date(MyDatasetTime[:],units=MyDatasetTime.units,calendar=MyDatasetTime.calendar)
      dtStart=dtTmp-datetime.timedelta(hours=12)
      dtLast=dtTmp[dtTmp.size-1]+datetime.timedelta(hours=12)
      TimeCells=numpy.zeros((MyDatasetTime.size+1),dtype=numpy.int64)
      TimeCells[:TimeCells.size-1]=netCDF4.date2num(dtStart,units='hours since 1900-01-01 00:00:00',calendar='standard')
      TimeCells[TimeCells.size-1]=netCDF4.date2num(dtLast,units='hours since 1900-01-01 00:00:00',calendar='standard')
   else :
      dtTmp_bnds=netCDF4.num2date(MyDatasetTimeBnds[:,:],units=MyDatasetTime.units,calendar=MyDatasetTime.calendar)
      TimeCells=numpy.zeros((MyDatasetTime.size+1),dtype=numpy.int64)
      TimeCells[:TimeCells.size-1]=netCDF4.date2num(dtTmp_bnds[:,0],units='hours since 1900-01-01 00:00:00',calendar='standard')
      TimeCells[-1]=netCDF4.date2num(dtTmp_bnds[-1,1],units='hours since 1900-01-01 00:00:00',calendar='standard')
### READ DAILY FILE : END

   MyDataset.close()
   if RemoveInput : os.remove(MyInputFile)

   #print 'YYY',type(MyDatasetVariable),MyDatasetDepthLayer.size,MyDatasetVariable.shape
   return sp_type.Characteristic(StandardName,MyInputVariable,MyDatasetDepthLayer,LonCells,LatCells,TimeCells,ConcatenatioOfSpatialMaps=MyDatasetVariable)    



def WriteFile (cOut,OutFileName) :   #Out,DepthLayer) :
   import netCDF4
   import math
   import numpy
   import time
   Out=cOut.COSM
   DepthLayer=cOut.DepthLayers
   #print netCDF4.default_fillvals
   #OutDataset = netCDF4.Dataset('testout_nc4.nc', 'w') 
   print >>sys.stderr, 'WARNING 14 : to fix the target format and the criteria to handle the time'
   OutDataset = netCDF4.Dataset(OutFileName, 'w')
   #OutDataset = netCDF4.Dataset('testout_nc4c.nc', 'w', format='NETCDF4_CLASSIC')
   #OutDataset = netCDF4.Dataset('testout_nc3c.nc', 'w', format='NETCDF3_CLASSIC')  #ok checker http://puma.nerc.ac.uk/cgi-bin/cf-checker.pl
   #OutDataset = netCDF4.Dataset('testout_nc3x.nc', 'w', format='NETCDF3_64BIT')    #ok checker http://puma.nerc.ac.uk/cgi-bin/cf-checker.pl

   OutDataset.history = 'Created ' + time.ctime(time.time())
   OutDataset.Conventions = "CF-1.6"

   #print Out.shape
   OutDataset.createDimension('time',None)
   OutDataset.createDimension('depth',Out.shape[1])
   OutDataset.createDimension('lat',Out.shape[2])
   OutDataset.createDimension('lon',Out.shape[3])
   OutDataset.createDimension('nv',2)

   #print OutDataset.dimensions

#WARNING
#adottando i4 per tempo, e rappresentanto ore, posso coprire circa 4000 anni
#infati 
#pow(2,4*8)/2   = 2147483648
#4000*365*24*60 = 2102400000

   OutDataset.createVariable('time','i4',('time')) #,fill_value=None)   #WARNING : i8 mandatory to store seconds sice...but require nc4
   OutDataset.createVariable('lon','f4',('lon'),zlib=True,complevel=9)
   OutDataset.createVariable('lat','f4',('lat'),zlib=True,complevel=9)
   OutDataset.createVariable('depth','f4',('depth'),zlib=True,complevel=9)
   OutDataset.createVariable('depth_bnds','f4',('depth','nv'),zlib=True,complevel=9)
   OutDataset.createVariable('lon_bnds','f4',('lon','nv'),zlib=True,complevel=9)
   OutDataset.createVariable('lat_bnds','f4',('lat','nv'),zlib=True,complevel=9)
   OutDataset.createVariable('time_bnds','i4',('time','nv'))
   OutDataset.createVariable(cOut.VariableName,'f4',('time','depth','lat','lon'),zlib=True,complevel=9,least_significant_digit=2,fill_value=Out.fill_value)

   tmpOutTemp=OutDataset.variables[cOut.VariableName]
   #tmpOutTemp.coordinates="time depth lat lon"
   tmpOutTemp.standard_name=cOut.StandardName
   tmpOutTemp.valid_min=numpy.float32(math.floor(Out.min()))
   tmpOutTemp.valid_max=numpy.float32(math.ceil(Out.max()))
   tmpOutTemp.missing_value=Out.fill_value
   if cOut.StandardName == 'sea_water_potential_temperature' :
      tmpOutTemp.units="degC"
   tmpOutTemp[:,:,:,:]=Out

#   OutDataset.createVariable('depth','f4',('depth'),zlib=True,complevel=9)
   tmpOutD=OutDataset.variables['depth']
   tmpOutD.units='m'
   tmpOutD.positive='down'
   tmpOutD.long_name='depth'
   tmpOutD.axis='Z'
   tmpOutD.standard_name='depth'
   tmpOutD.bounds='depth_bnds'
   tmpOutD.valid_min=numpy.float32(DepthLayer.min())
   tmpOutD.valid_max=numpy.float32(DepthLayer.max())
   #print DepthLayer,tmpOutD.size,DepthLayer[:Out.shape[1]].size,DepthLayer[1:].size
   tmpOutD[:]=(DepthLayer[:Out.shape[1]]+DepthLayer[1:])/2

#   OutDataset.createVariable('depth_bnds','f4',('depth','nv'),zlib=True,complevel=9)
   tmpOutDB=OutDataset.variables['depth_bnds']
#   tmpOutDB.units='m'
#   tmpOutDB.positive='down'
#   tmpOutDB.long_name='boundaries of cells in depth '
#   tmpOutDB.axis='Z'
#   tmpOutDB.standard_name='depth_lower_limit'
#   tmpOutDB.valid_min=numpy.float32(DepthLayer.min())
#   tmpOutDB.valid_max=numpy.float32(DepthLayer.max())
   tmpOutDB[:,0]=DepthLayer[:Out.shape[1]]
   tmpOutDB[:,1]=DepthLayer[1:]


#   OutDataset.createVariable('depth_lower_limit','f4',('depth'),zlib=True,complevel=9)
#   tmpOutDL=OutDataset.variables['depth_lower_limit']
#   tmpOutDL.units='m'
#   tmpOutDL.positive='down'
#   tmpOutDL.long_name='depth layer lower limit'
#   tmpOutDL.axis='Z'
#   tmpOutDL.standard_name='depth_lower_limit'
#   tmpOutDL.valid_min=numpy.float32(DepthLayer.min())
#   tmpOutDL.valid_max=numpy.float32(DepthLayer.max())
#   tmpOutDL[:]=DepthLayer[:Out.shape[1]]

#   OutDataset.createVariable('depth_top_limit','f4',('depth'),zlib=True,complevel=9)
   #print OutDataset.variables
#   tmpOutDT=OutDataset.variables['depth_top_limit']
#   tmpOutDT.units='m'
#   tmpOutDT.positive='down'
#   tmpOutDT.long_name='depth layer top limit'
#   tmpOutDT.axis='Z'
#   tmpOutDT.standard_name='depth_top_limit'
#   tmpOutDT.valid_min=numpy.float32(DepthLayer.min())
#   tmpOutDT.valid_max=numpy.float32(DepthLayer.max())
#   tmpOutDT[:]=DepthLayer[1:]


   #OutDataset.createVariable('lon','f4',('lon'),zlib=True,complevel=9)
   tmpOutLo=OutDataset.variables['lon']
   tmpOutLo.units='degrees_east'
   tmpOutLo.long_name='longitude'
   tmpOutLo.axis='X'
   tmpOutLo.standard_name='longitude'
   tmpOutLo.bounds='lon_bnds'
   tmpOutLo.valid_min=numpy.float32(cOut.LonCells.min())
   tmpOutLo.valid_max=numpy.float32(cOut.LonCells.max())
   #print 'XXX',cOut.LonCells,cOut.LonCells.size
   tmpOutLo[:]=(cOut.LonCells[:Out.shape[3]]+cOut.LonCells[1:])/2

   #OutDataset.createVariable('lat','f4',('lat'),zlib=True,complevel=9)

   #OutDataset.createVariable('lon_bnds','f4',('lon','nv'),zlib=True,complevel=9)
   tmpOutLoB=OutDataset.variables['lon_bnds']
   tmpOutLoB[:,0]=cOut.LonCells[:Out.shape[3]]
   tmpOutLoB[:,1]=cOut.LonCells[1:]

   #OutDataset.createVariable('lat','f4',('lat'),zlib=True,complevel=9)
   tmpOutLa=OutDataset.variables['lat']
   tmpOutLa.units='degrees_north'
   tmpOutLa.long_name='latitude'
   tmpOutLa.axis='Y'
   tmpOutLa.standard_name='latitude'
   tmpOutLa.bounds='lat_bnds'
   tmpOutLa.valid_min=numpy.float32(cOut.LatCells.min())
   tmpOutLa.valid_max=numpy.float32(cOut.LatCells.max())
   tmpOutLa[:]=(cOut.LatCells[:Out.shape[2]]+cOut.LatCells[1:])/2

   #OutDataset.createVariable('lat_bnds','f4',('lat','nv'),zlib=True,complevel=9)
   tmpOutLaB=OutDataset.variables['lat_bnds']
   tmpOutLaB[:,0]=cOut.LatCells[:Out.shape[2]]
   tmpOutLaB[:,1]=cOut.LatCells[1:]

   tmpOutT=OutDataset.variables['time']
   tmpOutT.units='hours since 1900-01-01 00:00:00'
   tmpOutT.calendar='standard'
   tmpOutT.long_name='time'
   tmpOutT.standard_name='time'
   tmpOutT.axis='T'
   tmpOutT.bounds='time_bnds'
   tmpOutT[:]=cOut.TimeCells[:cOut.TimeCells.size-1] #+12

   tmpOutTB=OutDataset.variables['time_bnds']
   #tmpOutTB.units='seconds since 1900-01-01 00:00:00'
   #tmpOutTB.calendar='standard'
   #tmpOutTB.standard_name='time'
   tmpOutTB[:,0]=cOut.TimeCells[:cOut.TimeCells.size-1]
   tmpOutTB[:,1]=cOut.TimeCells[1:]

   #print cOut.TimeCells[:]

   OutDataset.close()



