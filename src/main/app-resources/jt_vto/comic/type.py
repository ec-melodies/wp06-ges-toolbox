#!/usr/bin/python
import numpy
import sys

from . import glob as sp_glob

#http://stackoverflow.com/questions/2566412/find-nearest-value-in-numpy-array
def find_nearest(array,value):
    idx = (numpy.abs(array-value)).argmin()
    #return array[idx]
    return idx

def FindIndex (a,Min,Max):
   #mapCondition = ((Min<=a) * (a<=Max))
   #e= numpy.extract(mapCondition,numpy.arange(a.size))
   #MyOutputLonIndex=[e.min(),e.max()]
   #if sp_glob.verbose : print 'Inner : ',a[MyOutputLonIndex[0]]
   #print mm[m.index(True)]
   #if sp_glob.verbose : print 'Outer : ',a[MyOutputLonIndex[1]]
   #return MyOutputLonIndex
   iMin=find_nearest(a,Min)
   if iMin > 0 : iMin-=1
   iMax=find_nearest(a,Max)
   if iMax < a.size : iMax+=1
   #print Min,Max,a
   #print iMin,iMax,a[iMin],a[iMax],a[iMin+1],a[iMax-1]
   return [iMin,iMax]


class Characteristic :
   def __init__(self,StandardName,VariableName,DepthLayers,LonCells,LatCells,TimeCells,ConcatenatioOfSpatialMaps=None,MaskedAs=None) :
      self.StandardName=StandardName
      self.VariableName=VariableName
#      if MaskedAs is not None :
#         #self.COSM=numpy.ma.zeros([ TimeCells.size-1 , DepthLayers.size-1 , LatCells.size-1 , LonCells.size-1 ])
#         #self.COSM=numpy.ma.masked_all([ TimeCells.size-1 , DepthLayers.size-1 , LatCells.size-1 , LonCells.size-1 ])
#         #self.COSM=numpy.ma.empty_like(MaskedAs)
#         #numpy.ma.masked_where(MaskedAs.getmask(),self.COSM)
#         #self.COSM=numpy.ma.array(shape=[ TimeCells.size-1 , DepthLayers.size-1 , LatCells.size-1 , LonCells.size-1 ],mask=MaskedAs.getmask())
#         #print 'XXX',type(MaskedAs),MaskedAs.COSM.shape
#        
#         #print 'MMM', self.COSM.mask,MaskedAs.COSM.shape,self.COSM[0,1,1,4:20] 
#         self.COSM=numpy.ma.empty_like(MaskedAs.COSM)
#         self.COSM[:]=0
#         #self.COSM=numpy.ma.zeros_like(MaskedAs.COSM) #non esiste
#         print 'WARNING 12 : characteristic initialization does not fix the mask'
#         self.TimeCells=None
#
#         #print 'MMM', self.COSM.mask,MaskedAs.COSM.shape,self.COSM[0,1,1,4:20]
#         #print self.COSM.shape
      if ConcatenatioOfSpatialMaps is not None :
         self.COSM=ConcatenatioOfSpatialMaps
         #self.TimeCells=TimeCells
      else :
         self.COSM=numpy.ma.zeros( ( (TimeCells.size-1), (DepthLayers.size-1), (LatCells.size-1), (LonCells.size-1) ) )
         #self.TimeCells=None
      self.DepthLayers=DepthLayers
      self.LonCells=LonCells
      self.LatCells=LatCells
      self.TimeCells=TimeCells
      # to haldle the averange in time
      self.tCounter=None
      self.tCounterTotal=None     # in case the object is a value with weight, this is the total
      #self.tLastValidityTime=None
      #self.tCOSM=None
      if self.TimeCells.ndim==1 :
         self.ClimatologicalField=False
      elif self.TimeCells.ndim==2 :
         self.ClimatologicalField=True
      else :
         self.ClimatologicalField=True  #ERROR
      self.AncillaryAttr=dict()

   def set_weight(self,TimeRange) :
      if TimeRange.shape[0] == 0 : # here is fast average without weight
         self.tCounter=1
      else :
         import netCDF4
         td=TimeRange[1]-TimeRange[0]   #hours in range
         self.tCounterTotal=(td.seconds + td.days * 24 * 3600)/3600
         #print 'sw',self.tCounterTotal,type(TimeRange[0])
         #self.tCounter=1
         TimeRangeMin=numpy.int64(numpy.rint(netCDF4.date2num(TimeRange[0],units='hours since 1900-01-01 00:00:00',calendar='standard')))
         TimeRangeMax=numpy.int64(numpy.rint(netCDF4.date2num(TimeRange[1],units='hours since 1900-01-01 00:00:00',calendar='standard')))
         #print self.TimeCells,TimeRangeMin,TimeRangeMax
         if self.TimeCells[1] < TimeRangeMin or self.TimeCells[0] > TimeRangeMax : # no intersec
            self.tCounter=0
            self.COSM=numpy.ma.zeros( ( (TimeCells.size-1), (DepthLayers.size-1), (LatCells.size-1), (LonCells.size-1) ) ) # to be checked
         else :
            if self.TimeCells[0] < TimeRangeMin : self.TimeCells[0] = TimeRangeMin
            if self.TimeCells[1] > TimeRangeMax : self.TimeCells[1] = TimeRangeMax
            self.tCounter=self.TimeCells[1]-self.TimeCells[0]
            #print numpy.ma.mean(self.COSM)
            self.COSM=self.COSM*self.tCounter/self.tCounterTotal
            #print numpy.ma.mean(self.COSM)
         self.TimeCells[0]=TimeRangeMin
         self.TimeCells[1]=TimeRangeMax
         #print 'sw',self.TimeCells,self.tCounter,self.tCounterTotal

   def SetAttributes(self,dAttr) :
      for item in dAttr :
         self.AncillaryAttr[item]=dAttr[item]

   def setAsClimatologicalField(self) :
      appo=self.TimeCells
      #print type(self.TimeCells)
      self.TimeCells=numpy.zeros((1,appo.size))
      self.TimeCells[0]=appo
      #print self.TimeCells
      self.ClimatologicalField=True

#   def masked_as(In,OutLayer=None,OutLonLat=None) :
#      #print 'XXX',In.DepthLayers.size,In.COSM.shape
#      print "WARNING 8 : to clarify this function definition"
#      tmpMask=In
#      if OutLayer is None :
#         tmpOutLayer = In.DepthLayers
#         #tmpMask=In
#      else :
#         tmpOutLayer = OutLayer
#         tmpMask=None
#      if OutLonLat is not None :
#         tmpOutLon=numpy.array([ In.LonCells[0] , In.LonCells[In.LonCells.size-1] ])
#         tmpOutLat=numpy.array([ In.LatCells[0] , In.LatCells[In.LatCells.size-1] ])
#         #print 'XXX ma',tmpOutLon
#         tmpMask=None
#      else :
#         tmpOutLon=In.LonCells
#         tmpOutLat=In.LatCells
#      app=Characteristic(In.StandardName,In.VariableName,tmpOutLayer,tmpOutLon,tmpOutLat,In.TimeCells,MaskedAs=tmpMask)
#      #print 'XXX ma1',app.COSM.shape,app.LonCells
#      return app

#   def copy( In ) :
#      return Characteristic(In.StandardName,In.VariableName,In.DepthLayers,In.LonCells,In.LatCells,In.TimeCells,ConcatenatioOfSpatialMaps=In.COSM)

   def IsAdiacent(self,Test) :
      #print stc,ttc
      if self.ClimatologicalField :
         import netCDF4
         import datetime
         #print self.TimeCells,Test.TimeCells
         stc=netCDF4.num2date(self.TimeCells,units='hours since 1900-01-01 00:00:00',calendar='standard')
         ttc=netCDF4.num2date(Test.TimeCells,units='hours since 1900-01-01 00:00:00',calendar='standard')
         print >>sys.stderr, 'WARNING 11 : leap year for climatology...'
         #print 'stc',stc
         #print 'ttc',ttc
         #if (stc[0].year == ttc[0].year and stc[1].year == ttc[1].year ) : 
            #stc[1].year=ttc[0].year

         if stc[-1][1].month == 2 and stc[-1][1].day == 29 : il_day=28
         else : il_day=stc[-1][1].day
         nstc=datetime.datetime(ttc[0][0].year,stc[-1][1].month,il_day,stc[-1][1].hour,stc[-1][1].minute)
         #print nstc,stc[0][0].year,ttc[-1][1].month,ttc[-1][1].day

         if ttc[-1][1].month == 2 and ttc[-1][1].day == 29 : il_day=28
         else : il_day=ttc[-1][1].day
         nttc=datetime.datetime(stc[0][0].year,ttc[-1][1].month,il_day,ttc[-1][1].hour,ttc[-1][1].minute)

         #print 'nstc',nstc
         #print 'nttc',nttc
#         if stc[0][0].year <= ttc[0][0].year and ( nstc==ttc[0][0] or nttc==stc[0][0] ) :
         if ( nstc==ttc[0][0] and stc[0][0].year <= ttc[0][0].year ) or ( nttc==stc[0][0] and ttc[0][0].year <= stc[0][0].year ) :
         #if self.TimeCells[0]+Test.TimeCells[1]-self.TimeCells[0]==Test.TimeCells[0] :
            #print 'vero',stc[0][0].year,ttc[0][0].year
            return True
      else :
         if self.TimeCells[-1] == Test.TimeCells[0] or self.TimeCells[0] == Test.TimeCells[1] :
            return True
      return False 

   def mask_out_of(self,LonLatList) :
      #print LonLatList.tolist()
      #print self.COSM.mask
      MaskFalse=numpy.ma.make_mask_none(self.COSM.shape)
      NewMask=numpy.ma.getmask(self.COSM)
      #print NewMask
      for LonLatBox in LonLatList :
         #print LonLatBox.tolist()#,self.LonCells
         LonRange=LonLatBox[0]
         LatRange=LonLatBox[1]
         IndexLonRange=FindIndex(self.LonCells,LonRange[0],LonRange[1])
         IndexLatRange=FindIndex(self.LatCells,LatRange[0],LatRange[1])
         #print IndexLonRange,self.LonCells[IndexLonRange[0]],self.LonCells[IndexLonRange[1]]
         #print IndexLatRange,self.LatCells[IndexLatRange[0]],self.LatCells[IndexLatRange[1]]
         MaskFalse[:,:,IndexLatRange[0]:IndexLatRange[1],IndexLonRange[0]:IndexLonRange[1]]=True
      #print "premask:",self.COSM.count(),MaskFalse.any()
      self.COSM=numpy.ma.masked_where(~MaskFalse,self.COSM)
      #self.COSM.harden_mask()
      #print "postmask:",self.COSM.count()

   def operator_s( self, OutDepth=None, OutLonLat=None ) :
      #print 'XXX os1',In.COSM.shape
      OpeV=(OutDepth is not None)
      OpeO=(OutLonLat is not None)
      print >>sys.stderr, 'WARNING 16 : possible further improvement changing the computation flow'
      if OpeV :
         self.COSM=ProcessorS(self.COSM,self.DepthLayers,OutDepth)
         self.DepthLayers=OutDepth
      if OpeO :
         self.COSM=numpy.ma.mean(self.COSM,axis=2)
         self.COSM=numpy.ma.mean(self.COSM,axis=2)[:,:,numpy.newaxis,numpy.newaxis]
         self.LonCells=numpy.array([ self.LonCells[0] , self.LonCells[self.LonCells.size-1] ])
         self.LatCells=numpy.array([ self.LatCells[0] , self.LatCells[self.LatCells.size-1] ])

   def operator_tAdd(self, In , TimeAverage=False) :
      #self.COSM+=In.COSM
      #self.tCounter+=1
      #print "WARNING 7 : can't handle average over time in some cases"
      #self.tLastValidityTime=In.TimeCells
      #print type(self.DepthLayers),type(In.DepthLayers)
      #print 'XXX tAdd',self.COSM.shape,In.COSM.shape
      #print self.COSM.mask
      #print 'XXX',self.COSM.shape,In.COSM.shape,self.DepthLayers.size,In.DepthLayers.size

      if numpy.array_equal(self.DepthLayers,In.DepthLayers) : 
         app=In.COSM
      else :
         app=ProcessorS(In.COSM,In.DepthLayers,self.DepthLayers)

      if self.COSM.shape[2] == 1 : 
         print >>sys.stderr, "WARNING 2 : weak test on orizontal consistency"
         app=numpy.ma.mean(app,axis=2)
         app=numpy.ma.mean(app,axis=2)[:,:,numpy.newaxis,numpy.newaxis]
         #print 'XXX',app.shape

      if TimeAverage :
         print >>sys.stderr, "WARNING 7 : can't handle average over time in some cases : i.e. gap, different weights, ..."
         if self.tCounterTotal is None : # here is fast average without weight
            self.tCounter+=1
            #if self.tLastValidityTime is None : self.tLastValidityTime=In.TimeCells
            if self.ClimatologicalField :
               if self.TimeCells[0][1] < In.TimeCells[0][1] : self.TimeCells[0][1]=In.TimeCells[0][1]
               if self.TimeCells[0][0] > In.TimeCells[0][0] : self.TimeCells[0][0]=In.TimeCells[0][0]
            else :
               if self.TimeCells[1] < In.TimeCells[1] : self.TimeCells[1]=In.TimeCells[1]
               if self.TimeCells[0] > In.TimeCells[0] : self.TimeCells[0]=In.TimeCells[0]
            #print 'TUU',self.tLastValidityTime
            self.COSM+=app
         else :  # here is with weight
            if not (In.TimeCells[1] < self.TimeCells[0] or In.TimeCells[0] > self.TimeCells[1] ) : # no intersec
               MyTimeCellsMin=In.TimeCells[0]
               MyTimeCellsMax=In.TimeCells[1]
               if MyTimeCellsMin < self.TimeCells[0] : MyTimeCellsMin = self.TimeCells[0]
               if MyTimeCellsMax > self.TimeCells[1] : MyTimeCellsMax = self.TimeCells[1]
               MytCounter=MyTimeCellsMax-MyTimeCellsMin
               #print numpy.ma.mean(self.COSM),numpy.ma.mean(app)
               self.COSM+=app*MytCounter/self.tCounterTotal
               self.tCounter+=MytCounter
               #print numpy.ma.mean(self.COSM)
      else :
         #print 'ABC',self.COSM.shape,app.shape
         #print 'ABCtc',self.TimeCells,type(self.TimeCells),self.TimeCells.shape
         #print 'WARNING 10 : not checking the time continuity in concatenation'
#         print 'TCO :',self.tCounter
#         if self.tCounter == 0 :
#            self.tCounter=1
#            self.TimeCells=In.TimeCells
#            self.COSM=app 
#            #print 'AVF1',type(self.COSM),self.COSM.count()
#         else :
            #print 'AVF2',type(app),app.count()

         if self.ClimatologicalField :
            import netCDF4
            import datetime
            #print self.TimeCells,Test.TimeCells
            stc=netCDF4.num2date(self.TimeCells,units='hours since 1900-01-01 00:00:00',calendar='standard')
            ttc=netCDF4.num2date(In.TimeCells,units='hours since 1900-01-01 00:00:00',calendar='standard')
            #nstc=datetime.datetime(ttc[0].year,stc[1].month,stc[1].day,stc[1].hour,stc[1].minute)
            #nttc=datetime.datetime(stc[0].year,ttc[1].month,ttc[1].day,ttc[1].hour,ttc[1].minute)
            if stc[-1][1].month == 2 and stc[-1][1].day == 29 : il_day=28
            else : il_day=stc[-1][1].day
            nstc=datetime.datetime(ttc[0][0].year,stc[-1][1].month,il_day,stc[-1][1].hour,stc[-1][1].minute)
            if ttc[-1][1].month == 2 and ttc[-1][1].day == 29 : il_day=28
            else : il_day=ttc[-1][1].day
            nttc=datetime.datetime(stc[0][0].year,ttc[-1][1].month,il_day,ttc[-1][1].hour,ttc[-1][1].minute)
            if nstc==ttc[0][0] and stc[0][0].year <= ttc[0][0].year :
               self.TimeCells=numpy.concatenate((self.TimeCells,In.TimeCells),axis=0)
               self.COSM=numpy.ma.concatenate((self.COSM,app),axis=0)
            elif nttc==stc[0][0] and ttc[0][0].year <= stc[0][0].year :
               self.TimeCells=numpy.concatenate((In.TimeCells,self.TimeCells),axis=0)
               self.COSM=numpy.ma.concatenate((app,self.COSM),axis=0)
            else : print >>sys.stderr, 'ERROR 3 : not possible to concatenate'
            #print self.TimeCells

         #if self.ClimatologicalField :
         #   if self.TimeCells[0]+In.TimeCells[1]-self.TimeCells[0]==In.TimeCells[0] :
         #      self.TimeCells=numpy.concatenate((self.TimeCells,[In.TimeCells[1]]),axis=0)
         #      self.COSM=numpy.ma.concatenate((self.COSM,app),axis=0) 
         else : 
            if self.TimeCells[-1] == In.TimeCells[0] :
               self.TimeCells=numpy.concatenate((self.TimeCells,[In.TimeCells[1]]),axis=0)
               #print 'SHA :',self.COSM.shape,app.shape
               self.COSM=numpy.ma.concatenate((self.COSM,app),axis=0)
            elif self.TimeCells[0] == In.TimeCells[1] :
               self.TimeCells=numpy.concatenate(([In.TimeCells[0]],self.TimeCells),axis=0)
               self.COSM=numpy.ma.concatenate((app,self.COSM),axis=0)
               #print 'AVF3',type(self.COSM),self.COSM.count()
            else :
               print >>sys.stderr, 'ERROR 2 : not possible to concatenate'
      #print 'AVF',type(self.COSM),self.COSM.count()
      #print self.tLastValidityTime

   def operator_tClose(self) :
      if self.tCounterTotal is None : # here is fast average without weight
         self.COSM/=self.tCounter
      #print 'XXX',self.tCounter
      #self.TimeCells=self.tLastValidityTime
      #self.tCounter=1
      #print self.TimeCells
      self.tCounter=None
      self.tCounterTotal=None




def FindLowerTop(LayerIn,LayerOutLower,LayerOutTop) :
   i=0
   while True :
      if LayerIn[i] <= LayerOutLower and LayerOutLower < LayerIn[i+1] :
         break
      i=i+1
   Lower=i
   while True :
      if LayerIn[i] < LayerOutTop and LayerOutTop <= LayerIn[i+1] :
         break
      i=i+1
   Top=i
   return (Lower,Top)

def FindWeight(Lower,Top,LayerIn,LayerOutLower,LayerOutTop) :
   import numpy
   internalType=numpy.float64
   Weight=numpy.empty([Top-Lower+1], dtype=internalType)
   #print "lolt",LayerOutLower,LayerOutTop
   #print "top",Top,"lower",Lower
   #print LayerIn
   if Lower != Top :
      Weight[0]=LayerIn[1]-LayerOutLower
      Weight[Top-Lower]=LayerOutTop-LayerIn[Top-Lower]
   else :
      Weight[0]=LayerOutTop-LayerOutLower
   for i in range(1,Top-Lower) :
      #print Top-Lower,i,LayerIn[i+1],LayerIn[i],Weight.size
      #Weight[i-Lower]=LayerIn[i+1]-LayerIn[i]
      Weight[i]=LayerIn[i+1]-LayerIn[i]
   return Weight



def ProcessorS( FieldIn , LayerIn , LayerOut ) :
   import numpy
   #global verbose
   print >>sys.stderr, "BUG 1 : not considering partial step yet"
   internalType=numpy.float64 #FieldIn.dtype
   #internalType=FieldIn.dtype
   if sp_glob.verbose : 
      print >>sys.stderr, '\nProcessorS'
      print >>sys.stderr, 'FieldIn' #,FieldIn
      print >>sys.stderr, 'LayerIn',LayerIn.size,LayerIn
      print >>sys.stderr, 'LayerOut',LayerOut
   nLayer=len(LayerOut)-1    # number of layers in output
   #print FieldIn.shape[0]
   tmpOut=numpy.zeros( (FieldIn.shape[0],nLayer,FieldIn.shape[2], FieldIn.shape[3]), dtype=internalType )
   print >>sys.stderr, 'WARNING 9 : not clear whether nedded the following FieldIn[FieldIn.mask]=0'
   #FieldIn[FieldIn.mask]=0
   #print FieldIn.fill_value   WARNING : forse e' meglio duplicare invece di modificare l'input....

   for iLayer in range(nLayer) :
      if sp_glob.verbose : print >>sys.stderr, 'processing layer' , iLayer #, LayerOut[iLayer],LayerOut[iLayer+1],LayerIn

      (Lower,Top)=FindLowerTop(LayerIn,LayerOut[iLayer],LayerOut[iLayer+1])
      if sp_glob.verbose : print 'Lower',Lower,'Top',Top

      Weight=FindWeight(Lower,Top,LayerIn[Lower:Top+1],LayerOut[iLayer],LayerOut[iLayer+1])
      if sp_glob.verbose : print >>sys.stderr, 'Weight size',Weight.size,'Weight ', Weight

#      W3D=numpy.ma.empty_like(FieldIn[:,Lower:Top+1,:,:])
#      W3D=numpy.ma.masked_where(FieldIn[:,Lower:Top+1,:,:].mask,W3D)
#      W3D.harden_mask()

      #W3D=numpy.ones_like(tmpOut[:,0,:,:])*Weight[0]
      W3D=numpy.ma.empty_like(FieldIn[:,Lower:Top+1,:,:])
      W3D=numpy.ma.masked_where(FieldIn[:,Lower:Top+1,:,:].mask,W3D)
      W3D=W3D.copy()
      #W3D.harden_mask()   #causa errori nel broadcasting
      #print 'W3D',type(W3D),W3D.shape,W3D.count(),FieldIn[:,Lower:Top+1,:,:].count()
      for i in range(W3D.shape[1]) :
         W3D[:,i,:,:]=Weight[i]
      #for i in range(Lower+1,Top+1) :
      #   W3D=numpy.concatenate( (W3D,numpy.ones_like(tmpOut[:,0,:,:])*Weight[i-Lower]) )
      #print 'W3D',type(W3D),W3D.shape,W3D.count(),FieldIn[:,Lower:Top+1,:,:].count(),W3D.min(),W3D.max() #,W3D
      W3D=numpy.ma.masked_where(FieldIn[:,Lower:Top+1,:,:].mask,W3D)

      Sum=numpy.sum(W3D,axis=1) 
      #print 'SUM',type(Sum),Sum.shape,Sum.min(),Sum.max(),W3D[:,0,:,:].shape
      for i in range(W3D.shape[1]) :
         W3D[:,i,:,:]/=Sum[:,:,:]
      #print W3D[:,i,:,:].shape, Sum[:,:,:].shape
      #print 'W3D2',type(W3D),W3D.shape,W3D.count(),FieldIn[:,Lower:Top+1,:,:].count(),W3D.min(),W3D.max() #,W3D

      if sp_glob.verbose : print >>sys.stderr, "Weight total", numpy.sum(Weight),'=',LayerOut[iLayer+1]-LayerOut[iLayer]
      Weight/=(LayerOut[iLayer+1]-LayerOut[iLayer])
      if sp_glob.verbose : print >>sys.stderr, "Weight normalized", Weight
#MODALITA' CALCOLO 2
#      WWW=numpy.ones_like(tmpOut[:,0,:,:])*Weight[0]
      #print WWW
#      for i in range(Lower+1,Top+1) :
#         WWW=numpy.concatenate( (WWW,numpy.ones_like(tmpOut[:,0,:,:])*Weight[i-Lower]) )
         #WWW.insert(
      #print 'XYT',type(WWW),WWW.shape,type(FieldIn),FieldIn[:,Lower:Top+1,:,:].min(),FieldIn[:,Lower:Top+1,:,:].max()
      #print FieldIn[:,Lower:Top+1,:,:].shape
#      tmpOut[:,iLayer,:,:]=numpy.sum(FieldIn[:,Lower:Top+1,:,:]*WWW,axis=1)
      tmpOut[:,iLayer,:,:]=numpy.sum(FieldIn[:,Lower:Top+1,:,:]*W3D,axis=1)
      if sp_glob.verbose : print >>sys.stderr, 'ABC1 min,max', tmpOut[:,iLayer,:,:].min(),tmpOut[:,iLayer,:,:].max()
      #Rif sp_glob.verbose : print "tmpOut FieldIn[0,i,88,0] Weight[i-Lower]/tot",repr(tmpOut[0,iLayer,88,0]),FieldIn[0,Lower:Top+1,88,0],Weight[:]
      #Rif sp_glob.verbose : print "tmpOut FieldIn[0,i,0,0] Weight[i-Lower]/tot",repr(tmpOut[0,iLayer,0,0]),FieldIn[0,Lower:Top+1,0,0],Weight[:]
#END 2
      #Rif sp_glob.verbose : print 'tmpOut[0,iLayer,88,0]',repr(tmpOut[0,iLayer,88,0])
      #Rif sp_glob.verbose : print 'tmpOut[0,iLayer,0,0]',repr(tmpOut[0,iLayer,0,0])

   #tmpOut=numpy.ma.masked_equal(tmpOut,0)
   tmpOut=numpy.ma.array(tmpOut,mask=(tmpOut==0))
   if sp_glob.verbose : print >>sys.stderr, 'ABC2 min,max', tmpOut[:,:,:,:].min(),tmpOut[:,:,:,:].max()
   return tmpOut



