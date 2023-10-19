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
#from struct import *

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
        #print(args.PARAMS)
       
    ##print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
    ##print("---- PARAMS", args.PARAMS)
    ##print("---DIM(PARA)" ,len(args.PARAMS))
    ##print("#### ARGS ",args)
    ##print("++++ FILE ",args.file)
    ##print("@@@@ UNKNOWN",unknown)
    ##print("!!!! OUTDIR",args.outDir)


    #CWD = os.getcwd()
    #print('CWD',CWD)
    #print(os.scandir(CWD))
    
    #print(args.PARAMS)
    
    #return 
     
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
        
        inFileName = f.split('/')[-1]
        outFileName = inFileName.replace(".","_")
    
        #file = open(inFileName,"rb")
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
            cnt=0

            while cnt<dump:
                cnt+=1
                nbPixel= int.from_bytes(file.read(2),'little')
                timeStamp2= file.read(2*4)
                #for ii in range(nbPixel):
                if nbPixel >0:
            
                    
                    RCs= file.read(2*nbPixel)
                    mat = [[int.from_bytes(RCs[2*i+1:2*i+2],'little'),int.from_bytes(RCs[2*i:2*i+1],'little')] for i in range(nbPixel)] 
                    numPixelsList.append(nbPixel)
                
                    timeStampList.append(struct.unpack('<d',timeStamp)[0])
                    timeStampList2.append(struct.unpack('<d',timeStamp2)[0])
                    allPixelsList.append(mat)
                
                else:
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
        print('---- FILE : ' +f+ '  already processed')
    
    exit()
    
##########################################    
if __name__ == "__main__":
    main()
