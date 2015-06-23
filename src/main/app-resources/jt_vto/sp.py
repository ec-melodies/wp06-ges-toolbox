#!/opt/anaconda/bin/python

import sys
import os

import sp_glob
import sp_type
from sp_ionc import ReadFile, WriteFile
import sp_bm
import mr

sp_glob.verbose=False

#center of input layer : 1.47 4.58 7.94 11.55
# input layers         : 0 - 2.94 - 6.22 - 9.66 - 13.44
# input thickness      : 2.94 3.28 3.44 3.78


class sp :
   def __init__(self,InputVariableName,OutFileName,LonLat=None,OutputLayer=None,bm=False,SpeedUp=False,OutLonLat=None,TimeAverage=False,RemoveInput=False) :

      self.OutApp=None

      #par to read data
      self.InputVariableName=InputVariableName
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
      self.TimeAverage=TimeAverage

      #behaviour flags
      self.bm=bm
      self.SpeedUp=SpeedUp
      #self.sList=sList
      self.CatList=list()
      self.RemoveInput=RemoveInput

   def once(self,InputFileName,OutFileNameIsPostfix=False) :
      print >>sys.stderr, 'WARNING 5 : possible improvement if data to read is reduced to the min size'
      #print self.LonMinMax,self.LatMinMax

      InApp=ReadFile(InputFileName,self.InputVariableName,self.LonMinMax,self.LatMinMax,self.OutputLayer,self.RemoveInput)
      #print InApp.COSM.size
      if self.bm : sp_bm.bm_update(sp_bm.BM_READ,InApp.COSM)

      self.OutApp=InApp
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
      WriteFile(self.OutApp,OutFileName)
      if self.bm : sp_bm.bm_update(sp_bm.BM_WRITE,self.OutApp.COSM)

      self.OutApp=None
      return OutFileName

   def loop_go(self,InputFileName) :
      print >>sys.stderr, 'WARNING 6 : possible improvement if data to read is reduced'
      #print self.LonMinMax,self.LatMinMax

      InApp=ReadFile(InputFileName,self.InputVariableName,self.LonMinMax,self.LatMinMax,self.OutputLayer,self.RemoveInput)
      if self.bm : sp_bm.bm_update(sp_bm.BM_READ,InApp.COSM)

      # TIMESERIES WITH OR WITHOUT LAYERS
      if self.OutApp is None :
         self.OutApp=InApp
         if self.LonLat is not None : self.OutApp.mask_out_of(self.LonLat)
         if not ( self.SpeedUp and (self.OutputLayer is not None or self.OutLonLat is not None ) ) :
            self.OutApp.operator_s(self.OutputLayer,self.OutLonLat)
      else :
         if self.TimeAverage :
            self.OutApp.operator_tAdd(InApp,self.TimeAverage)
         else :
            if self.LonLat is not None : InApp.mask_out_of(self.LonLat)
            #if self.OutApp.TimeCells[-1] == InApp.TimeCells[0] or self.OutApp.TimeCells[0] == InApp.TimeCells[1] :
            if self.OutApp.IsAdiacent(InApp) :
               self.OutApp.operator_tAdd(InApp,self.TimeAverage)
            else :
               self.CatList.append(InApp)
               print >>sys.stderr, 'WARNING 15 : not able to handle this case now : concatenation postponed'
      
#      print 'TGH :',self.OutApp.TimeCells,InApp.TimeCells
#      if self.TimeAverage : 
#         self.OutApp.operator_tAdd(InApp,self.TimeAverage)
#      else :
#         #print 'TGH :',self.OutApp.TimeCells,InApp.TimeCells
#         if self.OutApp.TimeCells is None :
#            self.OutApp.operator_tAdd(InApp,self.TimeAverage)
#         elif self.OutApp.TimeCells[-1] == InApp.TimeCells[0] or self.OutApp.TimeCells[0] == InApp.TimeCells[1] :
#            self.OutApp.operator_tAdd(InApp,self.TimeAverage)
#         else :
#            print 'WARNING 15 : not able to handle this case now : concatenation postponed'
#            self.CatList.append(InApp)
      if self.bm : sp_bm.bm_update(sp_bm.BM_COMPUTE)


   def loop_close(self) :
      if self.TimeAverage : 
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
                  self.OutApp.operator_tAdd(InApp,self.TimeAverage)
               else :
                  self.CatList.append(InApp)
      if len(self.CatList) != 0 : print 'ERROR 1 : wrong input'
      print >>sys.stderr, 'WARNING 1: something to improve...'  # in ch ordine tclose e operator_s
      if self.SpeedUp and (self.OutputLayer is not None or self.OutLonLat is not None ) :
         self.OutApp.operator_s(self.OutputLayer,self.OutLonLat)
      #print 'XXX lc',self.OutApp.COSM.shape
      if self.bm : sp_bm.bm_update(sp_bm.BM_COMPUTE)
      import os
      WriteFile(self.OutApp,self.OutFileName)
      if self.bm : sp_bm.bm_update(sp_bm.BM_WRITE,self.OutApp.COSM)
      self.OutApp=None
      return os.getcwd()+'/'+self.OutFileName





#############   COMMAND LINE FRONT END   

def ParseRange ( opt ) :
   import numpy
   import json
   #return numpy.array(map(float,opt.replace(" ","").replace("[","").replace("]","").split(",")))
   return numpy.array(json.loads(opt))

#http://stackoverflow.com/questions/301134/dynamic-module-import-in-python

#http://stackoverflow.com/questions/8525765/load-parameters-from-a-file-in-python
class Params(object):
   def __init__(self, input_file_name):
      with open(input_file_name, 'r') as input_file:
         for line in input_file:
            #print line
            row = line.split("#")[0].split("=")
            label = row[0].replace(" ","").replace("\r","").replace("\n","")
            if label != "" :
               data = row[1].replace(" ","").replace("\r","").replace("\n","")  # rest of row is data list
               self.__dict__[label] = data #values if len(values) > 1 else values[0]

def GetLine(opt_bm,keyPattern=None,stream=sys.stdin) :
   import sys
   import re
   if stream is sys.stdin :
      if opt_bm : sp_bm.bm_update(sp_bm.BM_INIT)
      a=mymr.PullValue(keyPattern)
      if opt_bm : sp_bm.bm_update(sp_bm.BM_IDLE)
      return a
   else :
      if opt_bm : sp_bm.bm_update(sp_bm.BM_INIT)
      a=stream.readline()
      if opt_bm : sp_bm.bm_update(sp_bm.BM_IDLE)
      a=a.replace("\r","").replace("\n","").replace(" ","").replace("\t","")
      if a != '' : return a
      else : return False
# whether read from file, non need of keyPattern
#      while a != '' :
#         good=False
#         if keyPattern is None : good=True
#         elif re.search(keyPattern,a) is not None : good=True
#         if good : return a
#         if opt_bm : sp_bm.bm_update(sp_bm.BM_INIT)
#         a=stream.readline()         #.replace("\r","").replace("\n","").replace(" ","").replace("\t","")
#         if opt_bm : sp_bm.bm_update(sp_bm.BM_IDLE)
#         a=a.replace("\r","").replace("\n","").replace(" ","").replace("\t","")
#      return False


class tag_op :

   def __init__(self) :
      import optparse

      parser = optparse.OptionParser()
      parser.add_option("--ifile",   dest="MyInputFile",     default="none",   metavar="InFile",    help="read data from file InFile (netcdf format) ; if InFile='list' then read data from the list of files which names are passed in standard input") 
      parser.add_option("--ifield",  dest="MyInputVariable", metavar="Var",    help="working variable to be read from input file/s")
      parser.add_option("--ilonlat", dest="LonLat",          default=None,     metavar="LonLat",    help="optional - spatial working domain - default : the whole in input")
      parser.add_option("--ikey",    dest="iKey",            default=None,     metavar="iKey",      help="optional - input selection mapreduce key/s")
      parser.add_option("--iClean",  dest="iClean",          default=False,    action="store_true", help="flag to remove the input file after reading")
      parser.add_option("--ofile",   dest="MyOutFile",       default="out.nc", metavar="OutFile",   help="optional - file name for output or postfix in case of multiple output files - default 'out.nc'")
      parser.add_option("--oat",     dest="oat",             default=None,     action="store_true", help="flag to activate the computation of average value over time")
      parser.add_option("--oav",     dest="oav",             default=None,     metavar="OutLayer" , help="flag to activate the computation of average value over spatial depth layers given here as parameter") 
      parser.add_option("--oao",     dest="oao",             default=None,     action="store_true", help="flag to activate the computation of average value over the spatial lon lat plane")
      parser.add_option("--otc",     dest="otc",             default=None,     action="store_true", help="flag to concatenate output along the time dimension into one single output file")
      parser.add_option("--okey",    dest="oKey",            default=None,     metavar="oKey",      help="optional - output mapreduce key")
      parser.add_option("-v",        dest="verbose",         default=False,    action="store_true", help="legacy - be verbose")
      parser.add_option("-p",        dest="MyParameterFile", default='none',   metavar="ParFile",   help="legacy - alternative parameter file to provide var , lout, lon, lat")
      parser.add_option("--bm",      dest="bm",              default=False,    action="store_true", help="print and save benchmarking information")
      parser.add_option("-s",        dest="SpeedUp",         default=False,    action="store_true", help="might use more memory and improve the execution speed")
      (options, args) = parser.parse_args()
      #print options
      #print args

      if options.MyParameterFile != 'none' :
         #print options.MyParameterFile
         #exec "import %s" % options.MyParameterFile
         params = Params(options.MyParameterFile)
         #print options.MyInputFile
         if options.MyInputFile == 'none' : 
            #print options.MyInputFile
            options.MyInputFile=params.MyInputFile
         options.MyInputVariable=params.MyInputVariable
         options.MyOutputLayer=params.MyOutputLayer
         if ~ hasattr(params,"MyOutputLon") : params.MyOutputLon=None
         options.MyOutputLon=params.MyOutputLon
         if ~ hasattr(params,"MyOutputLat") : params.MyOutputLat=None
         options.MyOutputLat=params.MyOutputLat

      if options.oav is not None :
         self.OutLayer=ParseRange(options.oav) 
      else :
         self.OutLayer=None

      if options.LonLat is not None :
         #import numpy
         #import json
         #self.LonLat=numpy.array(json.loads(options.LonLat))
         self.LonLat=ParseRange(options.LonLat)
      else :
         self.LonLat=None

      if options.oao is not None :
         self.oao=True
      else :
         self.oao=None

      if options.otc is not None :
         self.otc=True
      else :
         self.otc=None

      self.InFile=options.MyInputFile
      self.iKey=options.iKey
      self.Variables=options.MyInputVariable
      self.iClean=options.iClean
      self.OutFile=options.MyOutFile
      self.bm=options.bm
      self.s=options.SpeedUp
      self.v=options.verbose
      self.oat=options.oat
      self.oKey=options.oKey


def EchoInputFile(text) :
   print >>sys.stderr, 'Input File  :',text

import mr
mymr=mr.mr()

def EchoOutputFile(text,key=None) :
   #print text
   #sys.stdout.flush
   if key is None : mymr.PushRecord(text)
   else : mymr.PushRecord(text,(key,))
   print >>sys.stderr, 'Output File :',text

def NoneOrList(ar) :
   if ar is None : return None
   return ar.tolist()


def Many2OneBlock (opt_bm,my_sp,InitFileName,keyPattern,type=None,outputKey=None) :
   import sys
   if type == "stream" :
      stream=open(InitFileName)
      InputFileName=GetLine(opt_bm,keyPattern,stream)
   else :
      InputFileName=InitFileName
      stream=sys.stdin
   one=False
   while InputFileName :
      one=True
      EchoInputFile(InputFileName)
      my_sp.loop_go(InputFileName)
      InputFileName=GetLine(opt_bm,keyPattern,stream)
   if one :
      output_name=my_sp.loop_close()
      EchoOutputFile(output_name,outputKey)


def main():
   import re
   #import time   #test to use time.sleep
   sp_bm.bm_setup()
   print >>sys.stderr, "sp.py"

   opt=tag_op()

   if opt.v :
      sp_glob.verbose=True
   
   VSpaceAverage=(opt.OutLayer is not None) 
   TimeAverage=(opt.oat is not None)
   OSpaceAverage=(opt.oao is not None) 
   One2One=(opt.InFile != 'list')
   Many2One=(opt.InFile == 'list') and ( TimeAverage or opt.otc is not None )
   Many2Many=(opt.InFile == 'list') and not TimeAverage and opt.otc is None

   print >>sys.stderr, "\nInput"
   print >>sys.stderr, " Input File/s    : ", opt.InFile
   print >>sys.stderr, " Selection Key   : ", opt.iKey
   print >>sys.stderr, "\nWorking Domain"
   print >>sys.stderr, " Variable/s      : ", opt.Variables
   print >>sys.stderr, " Time Range      :  None"
   print >>sys.stderr, " Depth Range     :  None"
   print >>sys.stderr, " Lon x Lat Range : ", NoneOrList(opt.LonLat)    #.tolist()
   print >>sys.stderr, "\nComputation"
   print >>sys.stderr, " Grid - Time      : ", opt.oat
   print >>sys.stderr, " Grid - Layer     : ", NoneOrList(opt.OutLayer)  #.tolist()
   print >>sys.stderr, " Grid - Lon x Lat : ", opt.oao
   print >>sys.stderr, "\nOutput"
   if Many2Many : 
      print >>sys.stderr, " File             : [InputFile]+", opt.OutFile
   else :
      print >>sys.stderr, " File             : ", opt.OutFile
   print >>sys.stderr, " Output Key       : ", opt.oKey
   print >>sys.stderr, "\nBehaviour--------"
   print >>sys.stderr, "\nWhich Operation"
   print >>sys.stderr, " average over vertical space  :",VSpaceAverage
   print >>sys.stderr, " average over orizontal space :",OSpaceAverage
   print >>sys.stderr, " average over time            :",TimeAverage
   print >>sys.stderr, "\nWhich I/O Flow Schema"
   print >>sys.stderr, " many to many :",Many2Many
   print >>sys.stderr, " many to one  :",Many2One
   print >>sys.stderr, " one to one   :",One2One
   print >>sys.stderr, "\n"
   print >>sys.stderr, "\nExecution-------"

   if opt.iKey is not None :
      keyPattern=re.compile(opt.iKey)
   else :
      keyPattern=None

   if opt.bm : sp_bm.bm_update(sp_bm.BM_INIT)

   #my_sp=sp(opt.Variables,opt.OutFile,opt.LonLat,opt.OutLayer,opt.bm,opt.s, OutLonLat=opt.oao , TimeAverage=TimeAverage , RemoveInput=opt.iClean )

   # many files to one file
   if Many2One : 
      #one=False
      InputFileName=GetLine(opt.bm,keyPattern)
      if InputFileName :
         if InputFileName[-4:]==".txt" :
            while InputFileName :
               #one=True
               print >>sys.stderr, "Processing group..."+InputFileName 
               EchoInputFile(InputFileName)
               my_sp=sp(opt.Variables,os.path.basename(InputFileName)+opt.OutFile,opt.LonLat,opt.OutLayer,opt.bm,opt.s, OutLonLat=opt.oao , TimeAverage=TimeAverage , RemoveInput=opt.iClean )
               Many2OneBlock(opt.bm,my_sp,InputFileName,None,type="stream",outputKey=opt.oKey)
               InputFileName=GetLine(opt.bm,keyPattern)
            #if one :
            #OutputFileName=my_sp.loop_close()
            #EchoOutputFile(OutputFileName)
         else : #in this case must be InputFileName[-3:]==".nc"
            print >>sys.stderr, "Processing simple..."
            my_sp=sp(opt.Variables,opt.OutFile,opt.LonLat,opt.OutLayer,opt.bm,opt.s, OutLonLat=opt.oao , TimeAverage=TimeAverage , RemoveInput=opt.iClean )
            Many2OneBlock(opt.bm,my_sp,InputFileName,keyPattern,outputKey=opt.oKey)
   # many files to many files
   elif Many2Many : 
      my_sp=sp(opt.Variables,opt.OutFile,opt.LonLat,opt.OutLayer,opt.bm,opt.s, OutLonLat=opt.oao , TimeAverage=TimeAverage , RemoveInput=opt.iClean )
      InputFileName=GetLine(opt.bm,keyPattern)
      while InputFileName :
         EchoInputFile(InputFileName)
         OutputFileName=my_sp.once(InputFileName,OutFileNameIsPostfix=True)
         EchoOutputFile(OutputFileName,opt.oKey)
         #time.sleep(1)
         InputFileName=GetLine(opt.bm,keyPattern)

   # one file to one file
   elif One2One : 
      my_sp=sp(opt.Variables,opt.OutFile,opt.LonLat,opt.OutLayer,opt.bm,opt.s, OutLonLat=opt.oao , TimeAverage=TimeAverage , RemoveInput=opt.iClean )
      InputFileName=opt.InFile
      EchoInputFile(InputFileName)
      OutputFileName=my_sp.once(InputFileName)
      EchoOutputFile(OutputFileName)

   #nothing
   else :
      print >>sys.stderr, "Nothing to do"

   #if sp_glob.verbose : print 'Out[0,0,88,0]=',my_sp.COSM[0,0,88,0], type(my_sp.COSM[0,0,88,0]), repr(my_sp.COSM[0,0,88,0]),my_sp.COSM[:,:,88,0]

   if opt.bm : sp_bm.bm_close()



if __name__ == "__main__":
   main()

