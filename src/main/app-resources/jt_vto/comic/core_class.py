#!/opt/anaconda/bin/python

import sys

from ionc import ReadFile, WriteFile
from . import processor
from . import bmmng as sp_bm

class sp :
   def __init__(self,OutputFieldName,OutFileName,LonLat=None,OutputLayer=None,bm=False,SpeedUp=False,OutLonLat=None,TimeRange=None,ClimatologicalAverage=False,RemoveInput=False,AttrFile=None,AttrStr=None) :

      self.OutApp=None

      #par to read data
      self.OutputFieldName=OutputFieldName
      self.LonLat=LonLat 
      #self.Lat=Lat
      self.LonMinMax=None
      self.LatMinMax=None
      if self.LonLat is not None :
         self.LonMinMax=[0,0]
         self.LatMinMax=[0,0]
         self.LonMinMax[0]=self.LonLat[0][0][0]
         self.LonMinMax[1]=self.LonLat[0][0][1]
         self.LatMinMax[0]=self.LonLat[0][1][0]
         self.LatMinMax[1]=self.LonLat[0][1][1]
         for Region in self.LonLat :
            LonRange=Region[0]
            LatRange=Region[1]
            if self.LonMinMax[0]>LonRange[0] : self.LonMinMax[0]=LonRange[0]
            if self.LonMinMax[1]<LonRange[1] : self.LonMinMax[1]=LonRange[1]
            if self.LatMinMax[0]>LatRange[0] : self.LatMinMax[0]=LatRange[0]
            if self.LatMinMax[1]<LatRange[1] : self.LatMinMax[1]=LatRange[1]

      #par to elaborate and output data
      self.OutputLayer=OutputLayer
      self.OutFileName=OutFileName
      self.OutLonLat=OutLonLat
      self.TimeRange=TimeRange
      self.ClimatologicalAverage=ClimatologicalAverage

      #behaviour flags
      self.bm=bm
      self.SpeedUp=SpeedUp
      #self.sList=sList
      self.CatList=list()
      self.RemoveInput=RemoveInput
      self.FieldComputation=False  # False -> field in input ; True -> field to be computed
      self.ListInApp=None          # buffer for input fields
      self.listPIFN=None           # actual list of input fields
      if AttrFile is not None :
         import json
         self.dAttrOut=json.load(open(AttrFile,'r'))
      elif AttrStr is not None :
         import json
         self.dAttrOut=json.loads(AttrStr)
      else : self.dAttrOut=dict()

   def once(self,InputFileName,OutFileNameIsPostfix=False) :
      print >>sys.stderr, 'WARNING 5 : possible improvement if data to read is reduced to the min size'
      #print self.LonMinMax,self.LatMinMax

      InApp=ReadFile(InputFileName,self.OutputFieldName,self.LonMinMax,self.LatMinMax,self.OutputLayer,self.RemoveInput)
      #print InApp.COSM.size
      if self.bm : sp_bm.bm_update(sp_bm.BM_READ,InApp.COSM)

      self.OutApp=InApp
      if self.OutputFieldName in self.dAttrOut : self.OutApp.SetAttributes(self.dAttrOut[self.OutputFieldName])
      if self.LonLat is not None : self.OutApp.mask_out_of(self.LonLat)
      if self.OutputLayer is not None or self.OutLonLat is not None :
         self.OutApp.operator_s(self.OutputLayer,self.OutLonLat)
      #else :
      #   self.OutApp=sp_type.Characteristic.copy(InApp)
      if self.bm : sp_bm.bm_update(sp_bm.BM_COMPUTE)

      if OutFileNameIsPostfix :
         import os
         OutFileName=os.getcwd()+'/'+os.path.basename(InputFileName)+self.OutFileName
      else :
         OutFileName=self.OutFileName
      if 'global' in self.dAttrOut : WriteFile(self.OutApp,OutFileName,self.dAttrOut['global'])
      else : WriteFile(self.OutApp,OutFileName)
      if self.bm : sp_bm.bm_update(sp_bm.BM_WRITE,self.OutApp.COSM)

      self.OutApp=None
      return OutFileName

   def loop_go(self,InputFileName) :
      print >>sys.stderr, 'WARNING 6 : possible improvement if data to read is reduced'
      #print self.LonMinMax,self.LatMinMax

      if not self.FieldComputation :
         try : 
            InApp=ReadFile(InputFileName,self.OutputFieldName,self.LonMinMax,self.LatMinMax,self.OutputLayer,self.RemoveInput)
            if self.bm : sp_bm.bm_update(sp_bm.BM_READ,InApp.COSM)
         except Exception as e :       #NameError as e :
            #print e,type(e),e.args[0],type(e.args[0])
            if type(e) is NameError and e.args[0] == 'NoInputField' :
               self.FieldComputation=True
               self.ListInApp=dict()
               self.listPIFN=list(processor.dict[self.OutputFieldName][0])
            else : raise
         else :
            # TIMESERIES WITH OR WITHOUT LAYERS
            if self.OutApp is None :
               self.OutApp=InApp
               if self.LonLat is not None : self.OutApp.mask_out_of(self.LonLat)
               if not ( self.SpeedUp and (self.OutputLayer is not None or self.OutLonLat is not None ) ) :
                  self.OutApp.operator_s(self.OutputLayer,self.OutLonLat)
               if self.TimeRange is not None : self.OutApp.set_weight(self.TimeRange)
               if self.ClimatologicalAverage : self.OutApp.setAsClimatologicalField()
               #print 'aaaaaaaaaaaaa',self.OutApp.ClimatologicalField
            else :
               if self.TimeRange is not None :
                  if self.ClimatologicalAverage : InApp.setAsClimatologicalField()
                  self.OutApp.operator_tAdd(InApp,TimeAverage=True)
                  #print 'cccc'
               else :
                  if self.LonLat is not None : InApp.mask_out_of(self.LonLat)
                  #if self.OutApp.TimeCells[-1] == InApp.TimeCells[0] or self.OutApp.TimeCells[0] == InApp.TimeCells[1] :
                  if self.OutApp.IsAdiacent(InApp) :
                     self.OutApp.operator_tAdd(InApp)
                  else :
                     self.CatList.append(InApp)
                     print >>sys.stderr, 'WARNING 15 : not able to handle this case now : concatenation postponed'
            if self.bm : sp_bm.bm_update(sp_bm.BM_COMPUTE)
      if self.FieldComputation :
         #print "attempt to process ",processor.dict[self.OutputFieldName]
         #if self.ListInApp is None : self.ListInApp=dict()
         #self.listPIFN=list(processor.dict[self.OutputFieldName][0])   #list of pending field name
         for onePIFN in self.listPIFN :
            try :
               self.ListInApp[onePIFN]=ReadFile(InputFileName,onePIFN,self.LonMinMax,self.LatMinMax,self.OutputLayer,self.RemoveInput)
               if self.bm : sp_bm.bm_update(sp_bm.BM_READ,self.ListInApp[onePIFN].COSM)
               self.listPIFN.remove(onePIFN)
            except Exception as e :
               if type(e) is NameError and e.args[0] == 'NoInputField' : continue
               else : raise
            if self.LonLat is not None : self.ListInApp[onePIFN].mask_out_of(self.LonLat)
            if self.OutputLayer is not None or self.OutLonLat is not None :
               self.ListInApp[onePIFN].operator_s(self.OutputLayer,self.OutLonLat)
            if self.bm : sp_bm.bm_update(sp_bm.BM_COMPUTE)



   def loop_close(self) :
      if self.FieldComputation :     #in this case, it is the computation of a new field
         #print 'leeeeennn ',len(self.listPIFN),self.listPIFN,self.ListInApp
         if len(self.listPIFN) != 0 : raise NameError('WrongInput')
         func=processor.dict[self.OutputFieldName][1]
         self.OutApp=func(self.ListInApp)
      else :
         if self.TimeRange is not None :     #ture = TimeRange is a time range or an empty time range ; false = TimeRange is None
            self.OutApp.operator_tClose()
         else :
            maxi=len(self.CatList)
            while len(self.CatList) != 0 and maxi != 0 :
               maxi=maxi-1
               for i in range(len(self.CatList)) :
                  InApp=self.CatList.pop(0)
            #for InApp in self.CatList :
               #if self.OutApp.TimeCells[-1] == InApp.TimeCells[0] or self.OutApp.TimeCells[0] == InApp.TimeCells[1] : 
                  if self.OutApp.IsAdiacent(InApp) :
                     self.OutApp.operator_tAdd(InApp)
                  else :
                     self.CatList.append(InApp)
         if len(self.CatList) != 0 : print 'ERROR 1 : wrong input ', len(self.CatList)
         print >>sys.stderr, 'WARNING 1: something to improve...'  # in ch ordine tclose e operator_s
         if self.SpeedUp and (self.OutputLayer is not None or self.OutLonLat is not None ) :
            self.OutApp.operator_s(self.OutputLayer,self.OutLonLat)
      #print 'XXX lc',self.OutApp.COSM.shape
         if self.OutputFieldName in self.dAttrOut : self.OutApp.SetAttributes(self.dAttrOut[self.OutputFieldName])

      if self.bm : sp_bm.bm_update(sp_bm.BM_COMPUTE)
      import os
      if 'global' in self.dAttrOut : WriteFile(self.OutApp,self.OutFileName,self.dAttrOut['global'])
      else : WriteFile(self.OutApp,self.OutFileName)
      if self.bm : sp_bm.bm_update(sp_bm.BM_WRITE,self.OutApp.COSM)
      self.OutApp=None
      return os.getcwd()+'/'+self.OutFileName

