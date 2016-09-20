#!/opt/anaconda/bin/python

#import sp_bm
import comic
from comic import bmmng as sp_bm
import sp

#############   CIOP FRONT END   

#import site
import os

# import the ciop functtons (e.g. copy, log)
#sys.path.append('/usr/lib/ciop/python/')    #classic python, not anaconda
import cioppy            #as ciop #classic python, not anaconda
ciop = cioppy.Cioppy()   # anaconda

def CheckNone(text) :
   if ( text == 'None' ) or ( text == '' ) :
      return None
   return text

def CheckNoneOrRange(text,Time=False) :
   if ( text == 'None' ) or ( text == '' ) :
      return None
   return sp.ParseRange(text,Time)

def GetInput(InputFileName) :
   ciop.log('INFO', 'input: ' + InputFileName)
   #print 'Input File Name :',InputFileName
   res = ciop.copy(InputFileName, os.environ['TMPDIR'])
   # LocalInputFileName = os.path.basename(res[0].rstrip('\n')) #classic python, not anaconda
   LocalInputFileName = os.path.basename(res) # anaconda
   if opt['bm'] : sp_bm.bm_update(sp_bm.BM_WRAP)
   return LocalInputFileName

def PutOutput(output_name, RemoveOutput=False, par_metalink=False) :
   #ciop.publish(os.environ['TMPDIR']+'/'+output_name )
   ciop.publish(output_name )
   #if par_metalink : ciop.publish(os.environ['TMPDIR']+'/'+output_name , metalink=par_metalink)
   if par_metalink : ciop.publish(output_name , metalink=par_metalink)
   if RemoveOutput : os.remove(output_name)
   if opt['bm'] : sp_bm.bm_update(sp_bm.BM_WRAP)

def Many2OneBlock (sp_bm,my_sp,InitFileName,keyPattern,type=None) :
   import sys
   if type == "stream" :
      #print "type="+type+", Processing stream..."
      stream=open(InitFileName) 
      InputFileName=sp.GetLine(sp_bm,keyPattern,stream)
      #print "InputFileName="+InputFileName
   else : 
      #print "type="+type+", Processing single..."
      InputFileName=InitFileName
      stream=sys.stdin
   one=False    #in this version, at least one always exists
   while InputFileName :
      one=True
      LocalInputFileName = GetInput(InputFileName)
      sp.EchoInputFile(LocalInputFileName)
      my_sp.loop_go(LocalInputFileName)
      #os.remove(LocalInputFileName)
      InputFileName=sp.GetLine(sp_bm,keyPattern,stream)
   if one :
      output_name=my_sp.loop_close()
      PutOutput(output_name, par_metalink=True)
      sp.EchoOutputFile(output_name)


opt=dict()

def main():
   import re

   sp_bm.bm_setup()

   os.chdir(os.environ['TMPDIR'])

   print "spciop.py"
   print "available processors :",comic.processor.dict

   #opt=dict()
   opt['InFile']=ciop.getparam('InFile')   #MANDATORY
   try : opt['iKey']=CheckNone(ciop.getparam('iKey'))
   except : opt['iKey']=None
   opt['Var']=CheckNone(ciop.getparam('Var'))    #MANDATORY
   try : opt['LonLat']=CheckNoneOrRange(ciop.getparam('LonLat'))
   except : opt['LonLat']=None
   print "WARNING 16 : also in case of wrong format for input parameters the value will be None and computation continues"
   try : opt['iClean']=ciop.getparam('iClean')
   except : opt['iClean']=False
   opt['OutFile']=CheckNone(ciop.getparam('OutFile'))   #MANDATORY
   try : opt['OutTRange']=CheckNoneOrRange(ciop.getparam('oat'),Time=True)
   except : opt['OutTRange']=None
   try : opt['OutLayer']=CheckNoneOrRange(ciop.getparam('OutLayer'))
   except : opt['OutLayer']=None
   try : opt['oao']=(ciop.getparam('oao')=='True')     
   except : opt['oao']=False
   if not opt['oao'] : opt['oao']=None
   try : opt['otc']=(ciop.getparam('otc')=='True')
   except : opt['otc']=False
   try : opt['oac']=(ciop.getparam('oac')=='True')
   except : opt['oac']=False
   if not opt['oac'] : opt['oac']=None
   try : opt['OutField']=CheckNone(ciop.getparam('OutField'))
   except : opt['OutField']=None
   try : opt['bm']=(ciop.getparam('bm')=='True')
   except : opt['bm']=False
   try : opt['s']=(ciop.getparam('s')=='True')
   except : opt['s']=False
   try : opt['AttrStr']=CheckNone(ciop.getparam('AttrStr'))
   except : opt['AttrStr']=None
   try : opt['OutField']=CheckNone(ciop.getparam('OutField'))
   except : opt['OutField']=None
   opt['v']=False

   if opt['OutField'] is not None :
      print "WARNING : forcing the input variable"
      opt['Var']=comic.processor.dict[opt['OutField']][0]
      print "WARNING : forcing the operation flags to ensure the correct behaviour"
      #opt.OutTRange=None
      #opt['OutLayer']=None
      opt['oao']=None

   VSpaceAverage=(opt['OutLayer'] is not None) 
   TimeAverage=(opt['OutTRange'] is not None or opt['oac'] is not None) 
   if TimeAverage and opt['OutTRange'] is None : opt['OutTRange']=sp.ParseRange('[]')
   OSpaceAverage=(opt['oao'] is not None) 
   FieldComputation=(opt['OutField'] is not None)

   One2One=(opt['InFile'] != 'list')
   Many2One=(opt['InFile'] == 'list') and ( TimeAverage or opt['otc'] or FieldComputation )
   Many2Many=(opt['InFile'] == 'list') and not ( TimeAverage or opt['otc'] or FieldComputation ) 

   print "\nInput"
   print " Input File/s    : ", opt['InFile']
   print " Selection Key   : ", opt['iKey']
   print " Attribute Str   : ", opt['AttrStr']
   print "\nWorking Domain"
   print " Variable/s      : ", opt['Var']
   print " Time Range      :  None"
   print " Depth Range     :  None"
   print " Lon x Lat Range : ", sp.NoneOrList(opt['LonLat'])
   print "\nComputation"
   print " Grid - Time      : ", sp.NoneOrList(opt['OutTRange'])
   print " Grid - Climatological Time      : ", opt['oac']
   print " Grid - Layer     : ", sp.NoneOrList(opt['OutLayer'])
   print " Grid - Lon x Lat : ", opt['oao']
   print " Field            : ", opt['OutField']
   print "\nOutput"
   if Many2Many :
      print " File             : [InputFile]+",opt['OutFile']
   else :
      print " File             : ",opt['OutFile'] 
   print "\nBehaviour--------"
   print "\nWhich Operation : "
   print " average over vertical space  :",VSpaceAverage
   print " average over orizontal space :",OSpaceAverage
   print " average over time            :",TimeAverage
   print " compute new field            :",FieldComputation
   print "\nWhich I/O Flow Schema : "
   print " many to many :",Many2Many
   print " many to one  :",Many2One
   print " one to one   :",One2One
   print "\n"
   print "\nExecution-------"

   if opt['iKey'] is not None :
      keyPattern=re.compile(opt['iKey'])
   else :
      keyPattern=None

   if opt['bm'] : sp_bm.bm_update(sp_bm.BM_INIT)

   #my_sp=sp.sp(opt['Var'],opt['OutFile'],opt['LonLat'],opt['OutLayer'],opt['bm'],opt['s'],OutLonLat=opt['oao'], TimeAverage=TimeAverage , RemoveInput=opt['iClean'])

   if Many2One :
      flagOutTRange=0
      #one=False
      InputFileName=sp.GetLine(opt['bm'],keyPattern)
      if InputFileName :
         if InputFileName[-4:]==".txt" :
            if opt['OutTRange'] is not None and len(opt['OutTRange'])==1 :
               if opt['OutTRange'][0]=='i6' : flagOutTRange=6
            while InputFileName :
               LocalInputFileName = GetInput(InputFileName)
               print "Processing group..."+LocalInputFileName
               sp.EchoInputFile(LocalInputFileName)
               if flagOutTRange==6 :
                  import numpy
                  import datetime
                  from calendar import monthrange
                  first=datetime.datetime(int(LocalInputFileName[0:4]),int(LocalInputFileName[4:6]),1)
                  last=datetime.datetime(int(LocalInputFileName[0:4]),int(LocalInputFileName[4:6]), monthrange(int(LocalInputFileName[0:4]),int(LocalInputFileName[4:6]))[1]  )
                  first1m=last+datetime.timedelta(1)
                  opt['OutTRange']=numpy.array([ first , first1m ])
                  print " Grid - Time REDEF: ", sp.NoneOrList(opt['OutTRange'])
               if FieldComputation :
                  my_sp=comic.pilot(opt['OutField'],LocalInputFileName+opt['OutFile'],opt['LonLat'],opt['OutLayer'],opt['bm'],opt['s'],OutLonLat=opt['oao'], TimeRange=opt['OutTRange'], ClimatologicalAverage=opt['oac'], RemoveInput=opt['iClean'], AttrStr=opt['AttrStr'])
               else :
                  my_sp=comic.pilot(opt['Var'],LocalInputFileName+opt['OutFile'],opt['LonLat'],opt['OutLayer'],opt['bm'],opt['s'],OutLonLat=opt['oao'], TimeRange=opt['OutTRange'], ClimatologicalAverage=opt['oac'], RemoveInput=opt['iClean'], AttrStr=opt['AttrStr'])
               Many2OneBlock(opt['bm'],my_sp,LocalInputFileName,None,type="stream") 
               InputFileName=sp.GetLine(opt['bm'],keyPattern)
         else : #in this case must be InputFileName[-3:]==".nc"
            print "Processing simple..."
            if FieldComputation :
               my_sp=comic.pilot(opt['OutField'],opt['OutFile'],opt['LonLat'],opt['OutLayer'],opt['bm'],opt['s'],OutLonLat=opt['oao'], TimeRange=opt['OutTRange'], ClimatologicalAverage=opt['oac'], RemoveInput=opt['iClean'], AttrStr=opt['AttrStr'])
            else :
               my_sp=comic.pilot(opt['Var'],opt['OutFile'],opt['LonLat'],opt['OutLayer'],opt['bm'],opt['s'],OutLonLat=opt['oao'], TimeRange=opt['OutTRange'], ClimatologicalAverage=opt['oac'], RemoveInput=opt['iClean'], AttrStr=opt['AttrStr'])
            Many2OneBlock(opt['bm'],my_sp,InputFileName,keyPattern)
   elif Many2Many :
      my_sp=comic.pilot(opt['Var'],opt['OutFile'],opt['LonLat'],opt['OutLayer'],opt['bm'],opt['s'],OutLonLat=opt['oao'], TimeRange=opt['OutTRange'], RemoveInput=opt['iClean'], AttrStr=opt['AttrStr'])
      InputFileName=sp.GetLine(opt['bm'],keyPattern)
      while InputFileName :
         LocalInputFileName = GetInput(InputFileName)
         sp.EchoInputFile(LocalInputFileName)
         output_name=my_sp.once(LocalInputFileName,OutFileNameIsPostfix=True)
         #os.remove(LocalInputFileName)
         PutOutput(output_name,RemoveOutput=opt['iClean'])
         sp.EchoOutputFile(output_name)
         InputFileName=sp.GetLine(opt['bm'],keyPattern)

   #elif One2One :
   #   InputFileName=opt['InFile']
   #   # line contains a reference to a catalogue entry
   #   ciop.log('INFO', 'input: ' + InputFileName)
   #   print 'Input File Name :',InputFileName
   #   #my_sp.once(InputFileName)

   else :
      print "Nothing to do"

   if opt['bm'] : 
      pathname=os.environ['TMPDIR']+'/bm.txt_'+os.environ['mapred_task_id']
      sp_bm.bm_close(pathname)
      ciop.publish(pathname)


if __name__ == "__main__":
   main()

