#!/opt/anaconda/bin/python
import cProfile
import spciop
import os

pathname=os.environ['TMPDIR']+'/profileout_'+os.environ['mapred_task_id']
cProfile.run('spciop.main()',pathname)
#import sys
# import the ciop functtons (e.g. copy, log)
#sys.path.append('/usr/lib/ciop/python/')    #classic python, not anaconda
import cioppy            #as ciop #classic python, not anaconda
ciop = cioppy.Cioppy()   # anaconda
ciop.publish(pathname)
