#Usage example
import pandas as pd
import matplotlib.pyplot as plt
from plot_functions import clusterPlot_TLS
tlsdf = pd.read_xml('./data/tlsrecord5_dt3.xml')
stageIndices = [0,0,0,1,1,1,0,0,0,1,1,1,1,0,1,0]
stageNames = ['North-South','West-East']

time_slider, button, radio1, radio2 = clusterPlot_TLS(tlsdf, stageIndices, stageNames, bar_colours = ['c','m'])

plt.show()