#!/usr/bin/env python3
'''
Author :        Henso ABREU
Description:    Script to merge outputfile produced by the PICMIC v356 
USAGE :
python /group/picmic/software/data_bin2ascii_pushPull/merger.py sampic_run*.txt
'''
import pandas as pd
import numpy as np
import argparse
import sys
import picmic_modules as prepro

##########################################
def main():
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file" , action='store_true',help="provide the binary input file produced by PICMIC0")
    parser.add_argument("PARAMS", nargs='+')
    ##parser.add_argument("-o", "--outDir", help="provide the output folder to save the processed ASCII data")
    args, unknown = parser.parse_known_args()
    if not sys.stdin.isatty():
        args.PARAMS.extend(sys.stdin.read().splitlines())
    
    # loading the tailed file
    listOfFiles = [f for f in args.PARAMS ]
    #mylist = listOfFiles.copy()
    
    inFileName = listOfFiles[0].split('/')[0]
    #outFileName = inFileName.replace(".","_")
    outFileName = inFileName
    
    ##print(inFileName)
    ##print('--------------')
    ##print(outFileName)
    ##print('----------------')
    
    nameScurve = outFileName.replace(outFileName.split('_')[-2],"VRefN-SCAN")
    prepro.dataframe_concat_standalone(listOfFiles, var='VRefN',name=nameScurve)
    print(' Done : ' +nameScurve+' <<<======'  )
    
    exit()

##########################################    
if __name__ == "__main__":
    main()
