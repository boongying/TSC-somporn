import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from plot_functions import tlsStages, tlsNumpy

#Defining the stages
stageIndices = [0,0,0,1,1,1,0,0,0,1,1,1,1,0,1,0]
stageNames = ['North-South','West-East']
bar_colours = ['c','m']

tlsdf = pd.read_xml('TLSrecord.xml')
#just to change column name 'phase' to 'subStageID'
colnames = tlsdf.columns.to_series()
colnames.loc[colnames == 'phase'] = 'subStageID'
tlsdf.columns = colnames
del colnames
stages = tlsStages(tlsdf, stageIndices, stageNames, definition = 'mode')
tlsnp = tlsNumpy(tlsdf, stages)

#Plot prarameters
cyclicity = 1
'''
There are 2 variations of cyclicity plot
1) A vertical bar is stacked until the same stage is recurred (default).
2) A vertical bar is stacked until all stages are in the bar.
'''

fig, axes = plt.subplots(figsize = (10,7), ncols = 1, nrows = max(stageIndices) + 1)


greenSubStages = {}
for column in  stages:
    greenSubStages[column] = stages[column].loc[stages[column] == 'g'].index.to_list()
flattenedGreen = [i for j in list(greenSubStages.values()) for i in j]
bar_colours = pd.Series(bar_colours, index = flattenedGreen) # watch out, this may not work when a stage is green at more than 1 subStages
bar_names = pd.Series(stageNames, index = flattenedGreen) # watch out, this may not work when a stage is green at more than 1 subStages

for st_stage, ax in enumerate(axes):
    tlsnp_cut = tlsnp[tlsnp[:,1].tolist().index(flattenedGreen[st_stage]):]
    bar_loc = tlsnp_cut[0,0]
    storage = []
    cycle_temp = []
    index_temp = []
    for i in range(tlsnp_cut.shape[0]-1):
        storage.append(tlsnp_cut[i,1])
        cond1 = any([storage.count(subStageID) > 1 for subStageID in stages.index]) and cyclicity == 1 # the condition for first varition of plot
        cond2 = all([subStageID in storage for subStageID in stages.index]) and cyclicity == 2 # the condition for second varition of plot
        if cond1 or cond2:
            for k,j in enumerate(index_temp):
                ax.bar(x = bar_loc,
                    height = cycle_temp[k]/sum(cycle_temp), 
                    bottom = sum(cycle_temp[:k])/sum(cycle_temp),
                    width = sum(cycle_temp),
                    color = bar_colours[tlsnp_cut[j, 1]], 
                    align = 'edge',
                    alpha = 0.4,
                    label = bar_names[tlsnp_cut[j, 1]])
            ax.axvline(bar_loc, linewidth =1, alpha = 0.4, color = 'k')
            storage = [tlsnp_cut[i,1]]
            bar_loc = tlsnp_cut[i,0]
            cycle_temp = []
            index_temp = []

        if tlsnp_cut[i, 1] in flattenedGreen:
            cycle_temp.append(tlsnp_cut[i+1,0] - tlsnp_cut[i,0])
            index_temp.append(i)

    ax.set_xlabel('Simulation time (s)')
    ax.set_ylabel('Cycle split (-)')
    ax.xaxis.grid(True)

    ax.set_xlim(0,600)
    ax.set_ylim(0,1)
    ax.set_aspect(200, adjustable='box')

plt.sca(axes[0])
handles, labels = plt.gca().get_legend_handles_labels()
by_label = dict(zip(labels, handles))
plt.legend(by_label.values(), by_label.keys(), 
            bbox_to_anchor = (1.0,1.05), loc = 'lower right',
            borderaxespad = 0)
plt.show()