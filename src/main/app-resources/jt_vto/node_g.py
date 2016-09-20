#!/opt/anaconda/bin/python

import sys
import os
import mr
mymr=mr.mr()

# import the ciop functtons (e.g. copy, log)
#sys.path.append('/usr/lib/ciop/python/')    #classic python, not anaconda
try :
   import cioppy            #as ciop #classic python, not anaconda
   ciop = cioppy.Cioppy()   # anaconda
except : pass

lib=dict()

def GiveOutFile(myGroup,GroupRange,lib,Dump=False,key=None) :
      out_file_name=myGroup+"-mapcomic"+str(GroupRange)+".txt"
      out_file = open(out_file_name,"w")
      print >>sys.stderr, out_file_name
      for InputPathFileName in lib[myGroup] :
         out_file.write(InputPathFileName+"\n")
      out_file.close()
      if Dump :
         print >>sys.stderr, "Dump "+os.getcwd()+'/'+out_file_name
      else :
         print >>sys.stderr, "Publishing "+os.getcwd()+'/'+out_file_name
         try :
            print >>sys.stderr, "Publishing output by ciop "+os.getcwd()+'/'+out_file_name
            ciop.publish(os.environ['TMPDIR']+'/'+out_file_name)
         except : print >>sys.stderr, "Issue to plublish by ciop "+os.getcwd()+'/'+out_file_name
         #print os.getcwd()+'/'+out_file_name
         print >>sys.stderr, "Publishing output by mr module"
         if key is None : mymr.PushRecord(os.getcwd()+'/'+out_file_name)
         else : 
            mymr.PushRecord(os.getcwd()+'/'+out_file_name,(key,))
         sys.stdout.flush()

def UpdateList(InputPathFileName,myGroup,lib,GroupRange,oKey) :
   if myGroup in lib.keys() :
      list_files=lib[myGroup]
      list_files.append(InputPathFileName)
   else :
      list_files=list()
      list_files.append(InputPathFileName)
      lib[myGroup]=list_files

   #to close and publish soon
   DoIt=False
   if GroupRange==6 :
      from calendar import monthrange
      #print len(lib[myGroup]),monthrange(int(myGroup[0:4]),int(myGroup[4:6]))[1] , monthrange(int(myGroup[0:4]),int(myGroup[4:6]))[1]+1
      if len(lib[myGroup]) == monthrange(int(myGroup[0:4]),int(myGroup[4:6]))[1]+1 : DoIt=True
   elif GroupRange==4 : #here is GroupRange=4
      #nyyyy=365
      #if isleap(int(myGroup[0:4])) : nyyyy=366
      if len(lib[myGroup]) == 12 : DoIt=True
   if DoIt :
      GiveOutFile(myGroup,GroupRange,lib,key=oKey)
      del lib[myGroup]


def main():
   #from calendar import monthrange,isleap
   try : 
      os.chdir(os.environ['TMPDIR'])
      print >>sys.stderr, "Change dir to", os.environ['TMPDIR'] 
   except : print >>sys.stderr, "Issue to change dir, working in current dir"

   print >>sys.stderr, "node_g.py"

   #opt['InFile']=ciop.getparam('InFile')   #MANDATORY
   try : 
      iKey=ciop.getparam('iKey')
      print >>sys.stderr, "Read iKey"
      GroupRange=int(ciop.getparam('GroupRange'))
      print >>sys.stderr, "Read GroupRange"
      oKey=ciop.getparam('oKey')
      print >>sys.stderr, "Read oKey"
      if oKey == 'None' : oKey=None
   except : 
      iKey=sys.argv[1]
      GroupRange=int(sys.argv[2]) # default 6
#      GroupTag=sys.argv[3]
      oKey=sys.argv[3]

   if iKey=='None' or iKey=='none' : iKey=None

   print >>sys.stderr, "iKey: ",iKey
   print >>sys.stderr, "GroupRange (6->year_month,4->year,2->month,66->year_month without completeness check):"+str(GroupRange)
#   print >>sys.stderr, "GroupTag: ",GroupTag
   print >>sys.stderr, "oKey: ",oKey

   #InputPathFileName=GetLine(iKey)
   InputPathFileName=mymr.PullValue(iKey)
   while InputPathFileName :
      myGroup6=None
      import re
      InputFileName=os.path.basename(InputPathFileName)      
      if GroupRange==2 :
         myGroup=InputFileName[4:6] 
      elif GroupRange==66 :
         myGroup=InputFileName[0:6]
      else :
         myGroup=InputFileName[0:GroupRange]
         if GroupRange==6 and InputFileName[GroupRange:GroupRange+2]=='01' : 
            import datetime
            a=datetime.datetime(int(InputFileName[0:4]),int(InputFileName[4:6]),1)
            b=a-datetime.timedelta(1)
            myGroup6=b.strftime("%Y%m")  #to catch the previous calendar month when yyyymm01

      print >>sys.stderr, "Input ",InputPathFileName
      UpdateList(InputPathFileName,myGroup,lib,GroupRange,oKey)
      print >>sys.stderr, myGroup,InputFileName
      if GroupRange==6 and myGroup6 is not None : 
         UpdateList(InputPathFileName,myGroup6,lib,GroupRange,oKey)
         print >>sys.stderr, myGroup6,InputFileName

      InputPathFileName=mymr.PullValue(iKey)

   #final closure and publication
   for myGroup in lib.keys() :
      if GroupRange==2 or GroupRange==66 :
         GiveOutFile(myGroup,GroupRange,lib,key=oKey)
      else :
         GiveOutFile(myGroup,GroupRange,lib,Dump=True)


if __name__ == "__main__":
   #import sp_bm
   from comic import bmmng as sp_bm
   sp_bm.bm_setup()
   main()
   sp_bm.bm_update(sp_bm.BM_WRAP)
   sp_bm.bm_close()
   try :
      pathname=os.environ['TMPDIR']+'/bm.txt_'+os.environ['mapred_task_id']
      os.rename('bm.txt',pathname)
      ciop.publish(pathname)
   except : print >>sys.stderr, "Issue to publish by ciop benchmarking info"

