#Usage example
import pandas as pd
import matplotlib.pyplot as plt
from plot_functions import clusterPlot_TLS
tlsdf = pd.read_xml('./data/exp6_tlsrecord_episode31.xml')
stageIndices = [2,2,3,0,0,1,2,2,3,0,0,1]
stageNames = ['WE_ls','WE_r','NS_ls','NS_r']

newids = [1, 2, 3, 4, 0, 5, 6, 7, 8, 0]
oldtls = tlsdf.copy()
for oldID, newID in enumerate(newids):
    tlsdf.loc[(tlsdf['programID'] == 'Fixed') & (oldtls['phase'] == oldID), 'phase'] = newID
del oldtls, newids

time_slider, button, radio1, radio2 = clusterPlot_TLS(tlsdf, stageIndices, stageNames, 3750.0, bar_colours = ['c','y','m','k'])

plt.show()