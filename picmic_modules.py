import pandas as pd
from os import listdir

def getPisteId(m_row,m_col):
    
    tempdf = pd.read_csv("listWays.csv")
    #print("Row-->",m_row,"Col-->",m_col)
    name =  tempdf['Name'][    (tempdf['Column']==m_col) &  (tempdf['Row']==m_row) ].to_list()  
    #print(name)
    #print('len name = ', name)
    #id = tempdf.Name.iloc[name].at(0)
    id = "R"+str(m_row)+"-C"+str(m_col)
    #print("id=",id)
    
    if ( len(name)>0 ) :
        id = name[0].strip()
    del tempdf
    return id


def cleanPandaPicmic(mypd, xAxis='VBN_adj') : 
    my_df = mypd.copy()
    my_df = my_df.dropna(axis=1)
    dim_data = len(my_df.columns)
    mylist = []
    mylist.append(xAxis)

    for i in range(1,dim_data) :
        ##my_pixel = 'R'+str(int(my_df.iloc[0].at[i]))+'-C'+str(int(my_df.iloc[1].at[i]))
        my_pixel = getPisteId(int(my_df.iloc[0].at[i]),int(my_df.iloc[1].at[i]))
        ##print('-------',my_pixel,i)
        temp = 'VBN_adj' if i == 0 else my_pixel
        mylist.append(temp)
        ##print(my_pixel,i,temp)

    ##print(mylist)  
    my_dict = {idx : mylist[idx] for idx in range(0,dim_data)}
    ##print(my_dict)
    
    my_df.rename(columns = my_dict, inplace=True) # rename columns 0 and 1
    #my_df = my_df.astype({0:'float',1:'float'})
    my_df = my_df.tail(-2) # to delete the two first rows
    #my_df = my_df.astype({'VBN_adj':'float','Eff_trig_'+my_way:'float'})
    my_df[xAxis] = my_df[xAxis].astype(int)
    return my_df

def dataframe_concat(var='VRefN',name='concat_scurves.csv'):
    
    mylist = [ x for x in listdir() if x.endswith(".txt") ]    
    dflist = [pd.read_csv(f) for f in mylist]
    
    pd_concat = pd.concat(dflist)
    pd_concat = pd_concat.fillna(0)
    
    zero = [0 for i in range(len(pd_concat.columns))]
    zero[0] = pd_concat[var].min()-1
    
    pd_concat.loc[-1] = zero
    pd_concat = pd_concat.sort_values(by=[var])
    pd_concat.to_csv(name,index=False)