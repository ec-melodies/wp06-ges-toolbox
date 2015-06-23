#!/opt/anaconda/bin/python

import sys
import os
import mr
mymr=mr.mr()

# import the ciop functtons (e.g. copy, log)
#sys.path.append('/usr/lib/ciop/python/')    #classic python, not anaconda
import cioppy            #as ciop #classic python, not anaconda
ciop = cioppy.Cioppy()   # anaconda

#def GetLine(keyPattern=None) :
#   import sys
#   import re
#   a=sys.stdin.readline().replace("\r","").replace("\n","").replace(" ","").replace("\t","")
#   while a != '' :
#      #print "checking ",a[-3:]+'f'
#      good=False
#
#      if keyPattern is None : good=True
#      elif re.search(keyPattern,a) is not None : good=True
#
#      if good : return a
#      print >>sys.stderr, "Dump ",a
#      a=sys.stdin.readline().replace("\r","").replace("\n","").replace(" ","").replace("\t","")
#
#   return False



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
         try :
            print >>sys.stderr, "Publishing output by ciop", out_file_name
            ciop.publish(os.environ['TMPDIR']+'/'+out_file_name)
         except : print >>sys.stderr, "Issue to plublish by ciop"
         #print os.getcwd()+'/'+out_file_name
         if key is None : mymr.PushRecord(os.getcwd()+'/'+out_file_name)
         else : mymr.PushRecord(os.getcwd()+'/'+out_file_name,(key,))
         sys.stdout.flush()


def main():
   from calendar import monthrange,isleap
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
      GroupRange=int(sys.argv[2]) #6
      oKey=sys.argv[3]
   print >>sys.stderr, "iKey: ",iKey
   print >>sys.stderr, "GroupRange (6-> month,4->year):"+str(GroupRange)
   print >>sys.stderr, "oKey: ",oKey

   #InputPathFileName=GetLine(iKey)
   InputPathFileName=mymr.PullValue(iKey)
   while InputPathFileName :
      InputFileName=os.path.basename(InputPathFileName)      
      myGroup=InputFileName[0:GroupRange]
      if myGroup in lib.keys() :
         list_files=lib[myGroup]
         list_files.append(InputPathFileName)
      else :
         list_files=list()
         list_files.append(InputPathFileName)
         lib[myGroup]=list_files
      print >>sys.stderr, "Input ",InputPathFileName
      print >>sys.stderr, myGroup,InputFileName
      DoIt=False
      if GroupRange==6 :
         if len(lib[myGroup]) == monthrange(int(myGroup[0:4]),int(myGroup[4:6]))[1] : DoIt=True
      else : #here is GroupRange=4
         #nyyyy=365
         #if isleap(int(myGroup[0:4])) : nyyyy=366
         if len(lib[myGroup]) == 12 : DoIt=True
      if DoIt : 
         GiveOutFile(myGroup,GroupRange,lib,key=oKey)
         del lib[myGroup]
      #InputPathFileName=GetLine(iKey)
      InputPathFileName=mymr.PullValue(iKey)

   for myGroup in lib.keys() :
      GiveOutFile(myGroup,GroupRange,lib,Dump=True)
      #out_file_name=myGroup+"-mapcomic"+str(GroupRange)+".txt"
      #out_file = open(out_file_name,"w")
      #print >>sys.stderr, out_file_name
      #for InputPathFileName in lib[myGroup] :
      #   out_file.write(InputPathFileName+"\n")
      #out_file.close()
      #try : 
      #   print >>sys.stderr, "Publishing by ciop", out_file_name
      #   ciop.publish(os.environ['TMPDIR']+'/'+out_file_name)
      #except : print >>sys.stderr, "Issue to plublish by ciop"
      #print os.getcwd()+'/'+out_file_name

if __name__ == "__main__":
   import sp_bm
   sp_bm.bm_setup()
   main()
   sp_bm.bm_update(sp_bm.BM_WRAP)
   sp_bm.bm_close()
   try :
      pathname=os.environ['TMPDIR']+'/bm.txt_'+os.environ['mapred_task_id']
      os.rename('bm.txt',pathname)
      ciop.publish(pathname)
   except : print >>sys.stderr, "Issue to publish by ciop benchmarking info"

