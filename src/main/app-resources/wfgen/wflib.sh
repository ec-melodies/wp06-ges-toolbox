#!/bin/bash

passer() {
   while read record ; do
      echo $record >> $1
      echo $record
      done
   }


gather() {
   mkdir gather 
   cd gather

   exec 2> err.txt

   echo "gather start "`date` > log.txt

   while read filename; do
      #echo $filename
      prot=`echo $filename| cut -c 1-3`
      if [ "$prot" = "s3:" ]; then
         s3cmd get $filename >> log.txt
      elif [ "$prot" = "ftp" ]; then
         echo "ftp download $filename" >> log.txt
         ncftpget -f $1 $filename >> log.txt
      else :
         prot="loc"
         fi
      num_c=`basename $filename | wc -c`
      num_c_3=`expr $num_c - 3`
      #echo $num_c $num_c_3
      este=`basename $filename| cut -c $num_c_3-`
      if [ "$este" = ".gz" ]; then
         num_c_3c=`expr $num_c_3 - 1`
         outfile=$PWD/`basename $filename| cut -c -$num_c_3c`
         if [ "$prot" = "loc" ]; then
            gzip -c -d $filename > $outfile
         else :
            gzip -d `basename $filename` 
            fi
         echo $outfile
      else :
         if [ "$prot" = "loc" ]; then
            ln -sf $filename `basename $filename`
            fi
         echo $PWD/`basename $filename`
         fi

      numfile=`ls -1 | wc -l`
      while [ $numfile -gt 31 ]; do
         echo $numfile >> err.txt
         sleep 10
         numfile=`ls -1 | wc -l`
         done

      done

   echo "gather end "`date` >> log.txt
   }
