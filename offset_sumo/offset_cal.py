import pandas as pd
import matplotlib.pyplot as plt

#%% Input

tls1df = pd.read_xml('./offset_sumo/J1tlsrecord.xml')
tls3df = pd.read_xml('./offset_sumo/J3tlsrecord.xml')

cyclic_offset = 30 #sec which is the travel time at progressive speed

coor_tls1Index = (2,3) #(start stage index, end stage index)
coor_tls3Index = (2,3) #(start stage index, end stage index)

#%% Calculation
green1 = pd.DataFrame()
green1['start'] = tls1df.loc[tls1df['phase'] == coor_tls1Index[0],
                             'time'].reset_index(drop=True)
green1['end'] = tls1df.loc[tls1df['phase'] == coor_tls1Index[1],
                           'time'].reset_index(drop=True)

green3 = pd.DataFrame()
green3['start'] = tls3df.loc[tls3df['phase'] == coor_tls3Index[0],
                             'time'].reset_index(drop=True)
green3['end'] = tls3df.loc[tls3df['phase'] == coor_tls3Index[1],
                           'time'].reset_index(drop=True)

str_order = ['1st','2nd','3rd','4th','5th']
            
def offset_time(i, row, order, reference_int, offset_int):
    if len(offset_int.loc[row['start'] < offset_int['start'],'start']) >= order:
        reference_int.loc[i,str_order[order-1]+'_offset'] = offset_int.loc[row['start'] < offset_int['start'],'start'].iloc[order-1] \
            - row['start']

def usable_time(i, row, order, reference_int, offset_int):
    if len(offset_int.loc[row['start'] < offset_int['start'],'start']) >= order:
        usable_checkend = offset_int.loc[row['start'] < offset_int['start'],'end'].iloc[order-1] - row['start'] - cyclic_offset
        usable_checkstart = offset_int.loc[row['start'] < offset_int['start'],'start'].iloc[order-1] - row['start'] - cyclic_offset
        if usable_checkend > 0 and usable_checkstart < 0: 
            reference_int.loc[i,str_order[order-1]+'_usable'] = usable_checkend
        elif usable_checkend > 0 and usable_checkstart > 0:
            reference_int.loc[i,str_order[order-1]+'_usable'] = offset_int.loc[row['start'] < offset_int['start'],'end'].iloc[order-1]\
                        - offset_int.loc[row['start'] < offset_int['start'],'start'].iloc[order-1]
        else: 
            reference_int.loc[i,str_order[order-1]+'_usable'] = 0

            
#tls1 as the reference
def main(reference_int, offset_int, orders):
    reference_int = reference_int.copy()
    offset_int = offset_int.copy()
    for i, row in reference_int.iterrows():
        #concurrent green-onset
        reference_int.loc[i,'concur'] = any((row['start'] >= offset_int['start']) 
                                        & (row['start'] < offset_int['end']).to_list())
        #usable time of concurrent green-onset
        if reference_int.loc[i,'concur']:
            usable_concur = row['start'] - offset_int.loc[row['start'] < offset_int['end'],'end'].iloc[0] - cyclic_offset
            if usable_concur > 0:
                reference_int.loc[i,'concur_usable'] = usable_concur
            else:
                reference_int.loc[i,'concur_usable'] = 0
        else:
            reference_int.loc[i,'concur_usable'] = 0
        
        for k in range(1,orders+1):
            offset_time(i, row, k, reference_int, offset_int)
            usable_time(i, row, k, reference_int, offset_int)
    return reference_int

#%% Example
tls1_result = main(reference_int=green1, offset_int=green3, orders=3)
tls3_result = main(reference_int=green3, offset_int=green1, orders=3)
