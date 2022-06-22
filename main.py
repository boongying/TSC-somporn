import pandas as pd
import matplotlib.pyplot as plt
from plot_functions import clusterPlot_TLS
#import the tls data and rename the variable
tlsdf = pd.read_xml('TLSrecord.xml')
stageIndices = [0,0,0,1,1,1,0,0,0,1,1,1,1,0,1,0]
stageNames = ['North-South','West-East']

time_slider, button, radio1, radio2 = clusterPlot_TLS(tlsdf, stageIndices, stageNames)

plt.show()