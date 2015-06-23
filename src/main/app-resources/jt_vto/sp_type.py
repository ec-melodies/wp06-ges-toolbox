#!/usr/bin/python
import numpy
import sys

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
      self.tCounter=1
      #self.tLastValidityTime=None
      #self.tCOSM=None

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

   def operator_tAdd(self, In , TimeAverage=True) :
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
         self.tCounter+=1
         #if self.tLastValidityTime is None : self.tLastValidityTime=In.TimeCells
         if self.TimeCells[1] < In.TimeCells[1] : self.TimeCells[1]=In.TimeCells[1]
         if self.TimeCells[0] > In.TimeCells[0] : self.TimeCells[0]=In.TimeCells[0]
         #print 'TUU',self.tLastValidityTime
         self.COSM+=app
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
      self.COSM/=self.tCounter
      #print 'XXX',self.tCounter
      #self.TimeCells=self.tLastValidityTime
      self.tCounter=1
      #print self.TimeCells




import sp_glob 

#verbose=False

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



