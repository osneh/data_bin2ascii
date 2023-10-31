#!/usr/bin/env python3
'''
Author :        Edouard BECHETOILE, Henso ABREU
Description:    Script to dump binary data produced by PICMIC0/SAMPIC to an ASCII file 
                "version 4"
'''
import pandas as pd
import numpy as np
import sys
import os
import argparse
import re
import struct
from datetime import date,time
import picmic_modules as prepro
import csv
from termcolor import colored

headers = ["nbPixels","timeStamp1","timeStamp2","listPixels"]
CDW = os.getcwd()   # Actual directory
ascii_files = './data_ascii'

##########################################
def dumpData(list1, list2, list3, list4) :
    myList = []
    myList.append(list1)
    myList.append(list2)
    myList.append(list3)
    myList.append(list4)
    return myList

#########################################
#def checkDirExists():

##########################################
def main():
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file" , action='store_true',help="provide the binary input file produced by PICMIC0/SAMPIC")
    parser.add_argument("PARAMS", nargs='+')
    parser.add_argument("-o", "--outDir", help="provide the output folder to save the processed ASCII data")
    args, unknown = parser.parse_known_args()
    if not sys.stdin.isatty():
        args.PARAMS.extend(sys.stdin.read().splitlines())
     
    # loading the tailed file
    for f in args.PARAMS :
        
        # variable defintions
        dump =1
        nbPixel=0
        mat=[]
        numPixelsList = []
        allPixelsList = []
        timeStampList = []
        timeStampList2 = []
        cnt=0
        
        testList = []
        
        inFileName = f.split('/')[-1]
        outFileName = inFileName.replace(".","_")

        file = open(f,"rb")
    
        ## Reading information from the file comments
        head=file.readline(); ## line1
        infoFromComments  = str(head).split("==")[2].split("=")[1:]
        runInfo = [i.split(' ')[1] for i in infoFromComments]
    
        head=file.readline(); ## line2
        freq = int(str(head).split("==")[-2].split(' ')[4])

        ## lines 3 
        head=file.readline() # 3 #=== DATA STRUCTURE PER FRAME===
        newVarValues = [int(i.split(' ')[1]) for i in str(head).split(':')[2:] ]
        newVarNames = [ j.split(' ')[-1].strip() for j in str(head).split(':')[1:]]
        dictNewVars = dict(zip(newVarNames,newVarValues))

        head=file.readline() # line 4 # === NB_OF_PIXELS_IN_FRAMES (2 bytes) RAW_TIMESTAMP (in fe_clock_periods) (5 Bytes), PIXEL_COLUMN (1 byte), PIXEL ROW ( 1 byte) ==
        head=file.readline() # line 5 #
        head=file.readline() # line 6 #
    
        while dump:
            dump =int.from_bytes(file.read(2), 'little') 
            timeStamp= file.read(2*4)
            #cnt+=1

            while cnt<dump:
            #while cnt<100:
                cnt+=1
                nbPixel= int.from_bytes(file.read(2),'little')
                timeStamp2= file.read(2*4)
                
                if nbPixel >0:
                    RCs= file.read(2*nbPixel)
                    mat = [[int.from_bytes(RCs[2*i+1:2*i+2],'little'),int.from_bytes(RCs[2*i:2*i+1],'little')] for i in range(nbPixel)] 
                    
                    ch = [ prepro.getPisteId(idx[1],idx[0]) for idx in mat]
                    
                    numPixelsList.append(nbPixel)
                
                    timeStampList.append(struct.unpack('<d',timeStamp)[0])
                    timeStampList2.append(struct.unpack('<d',timeStamp2)[0])
                    allPixelsList.append(ch)
                    
                
                else:
                    break
            break

        allData = dumpData(numPixelsList,timeStampList,timeStampList2,allPixelsList)
        myDict = dict(zip(headers,allData))

        df2Csv = pd.DataFrame.from_dict(myDict)
        df2Csv['UnixTime'] = runInfo[0]
        dateformat = runInfo[1].split('.')
        timeformat = runInfo[2].split('.')
        df2Csv['dateTime'] = pd.Timestamp(int(dateformat[0]),int(dateformat[1]),int(dateformat[2]), int(timeformat[0][:-1]), int(timeformat[1][:-1]),  int(timeformat[2][:-1]),int(timeformat[3][:-2]) )
        df2Csv['Freq'] = freq
    
        # loop to add new variable information
        for key, value in dictNewVars.items():
            df2Csv[key] = value

        df2Csv.to_csv(outFileName+'.csv', index=False)
    
        file.close()
        print(colored('---- FILE : ' +f+ '  already processed -----','red'))
    
        if (df2Csv.empty==False):
        
            this_dict = pd.value_counts(np.hstack(df2Csv.listPixels)).to_dict()
            for k, v in this_dict.items() :
                this_dict[k]= "{0:.2f}".format(v/cnt)
                
            this_dict.update({'VRefN':"{0:03}".format(df2Csv.VrefN[0])})
            this_dict = dict(sorted(this_dict.items(),reverse=True)) 
        
            # sCurve save data
            l1 = ''
            l2 = ''
        
            for idx, k in enumerate(this_dict.keys()) :
                if (idx != len(this_dict.keys() ) -1) :
                    l1 +=k+','        
                    l2+=str(this_dict[k])+','
                else :
                    l1+=k+'\n'
                    l2+=str(this_dict[k])+'\n'
                
        
            l2write = []
            l2write.append(l1)
            l2write.append(l2)
        
            with open(outFileName+'_VRefN'+str("{0:03}".format(df2Csv.VrefN[0]))+'.txt','w') as w:
                for line in l2write :
                    w.write(line)
        
            print(20*'-')
            
    prepro.dataframe_concat()
        
    exit()
    
##########################################    
if __name__ == "__main__":
    main()
