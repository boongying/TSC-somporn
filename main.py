#Usage example
import pandas as pd
import matplotlib.pyplot as plt
from plot_functions import clusterPlot_TLS
tlsdf = pd.read_xml('./data/exp6_tlsrecord_episode31.xml')
stageIndices = [2,2,3,0,0,1,2,2,3,0,0,1]
stageNames = ['WE_ls','WE_r','NS_ls','NS_r']

time_slider, button, radio1, radio2 = clusterPlot_TLS(tlsdf, stageIndices, stageNames, bar_colours = ['c','y','m','k'])

plt.show()