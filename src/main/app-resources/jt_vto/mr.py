import sys

def AppendRecordIn(text) :
   f = open('mrin.txt', 'a')
   f.write(text)
   f.close()

def AppendRecordOut(text) :
   f = open('mrout.txt', 'a')
   f.write(text)
   f.close()

class mr :

   def __init__(self) :
      pass

   def PushRecord(self,value,key=None) :
      if key is None : 
         print value
         AppendRecordOut(value+"\n")
         #print >>sys.stderr, 'Output record :',value
      else : 
         for iKey in key : 
            print iKey+","+value
            AppendRecordOut(iKey+","+value+"\n")
            #print >>sys.stderr, 'Output record :',iKey+","+value+"\n"
      sys.stdout.flush

   def ClosePushRecordMap(self) : pass
   def ClosePushRecordReuce(self) : pass

   def PullRecord(self,reKeySelector=None) : 
      import sys
      import re
      a=sys.stdin.readline()
      a=a.replace("\r","").replace("\n","").replace(" ","").replace("\t","")
      #AppendRecordIn(a+"\n")
      if reKeySelector is None :
         AppendRecordIn(a+"\n")
         return a
      else : 
         while a != '' :
            #good=False
            if re.search(reKeySelector,a.split(",")[0]) is not None : #good=True
               AppendRecordIn(a+"\n")
               return a
            #if good : return a
            else : 
               AppendRecordIn("dump,"+a+"\n")
               a=sys.stdin.readline()
               a=a.replace("\r","").replace("\n","").replace(" ","").replace("\t","")
               #AppendRecordIn(a+"\n")
         return False

   def PullValue(self,reKeySelector=None) :
      a=self.PullRecord(reKeySelector)
      if a == False : return False
      index_comma=a.find(',')
      return a[index_comma+1:]
