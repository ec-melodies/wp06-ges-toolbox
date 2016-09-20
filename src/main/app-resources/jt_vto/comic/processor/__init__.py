import glob
#print 'path ',__path__
filelist=glob.glob( __path__[0] + '/plugin_*.py')     #['plugin_a']
#print 'filelist ', filelist

__all__=list()
for pathfile in filelist :
   filename=pathfile.split('/')[-1]
   __all__.append(filename.split('.')[0])

#print 'all ',__all__

import imp

dict=dict()

for modulename in __all__ :
   pa=imp.find_module(modulename,__path__)
   #pb=modulename.split('_')[1]
   pm=imp.load_module(__name__+'.'+modulename,pa[0],pa[1],pa[2])
   dict[pm.lout]=(pm.lin,pm.processor)
   #ld[pb]=imp.load_module(__name__+'.'+pb,pa[0],pa[1],pa[2]).processor

del pm,pa,modulename,pathfile,filelist,imp,glob,filename

#from . import *
#print 'myout ',__name__,' ', dir()
