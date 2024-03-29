'''
MIT License

Copyright (c) 2022 Somporn Sahachaisaree

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

This software is intended to be freely shared among Oguchi Lab members for research purposes
'''

import statistics
import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.widgets import RangeSlider, Button, RadioButtons
plt.rcParams.update({'font.sans-serif':'Arial'})


def tlsStages(tlsdf: pd.DataFrame,
                stageIndices: list,
                stageNames: list,
                definition: str = 'mode') -> pd.DataFrame:
    '''
    There are two ways for definition of subStage definition
    1) definition from the statistical mode of movement indicators
        say we have stageIndices = [0,0,0,1,1,1,0,1]
        and the state of a subStage i is 'y g g r r r g r' 
        then the states at subStage i are stage0:g (3g over 1y), stage1:r (4r)
        
    2) definition from the first movement indicator
        say we have sigGruppenIndex = [>0<,0,0,>1<,1,1,0,1]
        and the state of subStage i is '>y< g g >r< r r g r' 
        then the states at subStage i is stage0:y , stage1:r
    '''
    stages = pd.DataFrame(columns = stageNames,
                              index = pd.Index(pd.unique(tlsdf.iloc[:,3]),name = 'subStageID'))
    for i in stages.index:
        assert len(pd.unique(tlsdf.loc[tlsdf['subStageID'] == i,'state'])) == 1, 'movement definition conflict'
        indicators = pd.unique(tlsdf.loc[tlsdf['subStageID'] == i,'state'])[0]
        for movement in range(len(stageNames)):
            slicedIndex = [ind for ind, j in enumerate(stageIndices) if j == movement]
            movementIndicators = [indicators[ind] for ind in slicedIndex]
            if definition == 'mode':
                stageDefinition = statistics.mode(movementIndicators)
            elif definition =='first':
                stageDefinition = movementIndicators[0]
            else:
                raise ValueError('the input value for \'definition\' is invalid')
            stages.loc[i,stageNames[movement]] = stageDefinition
    return stages

def tlsNumpy(tlsdf: pd.DataFrame,
             stages: pd.DataFrame):
    tlsdf_reduced = tlsdf.loc[:,('time','subStageID')]
    #find which subStageIDs correspond to the green subStages of each stage. 
    greenSubStages = {}
    amberRedRows = pd.Series([False for _ in range(tlsdf.shape[0])])
    for column in  stages:
        greenSubStages[column] = stages[column].loc[stages[column] == 'g'].index.to_list()
        greenRows = (tlsdf['subStageID'] == greenSubStages[column][0])
        greenTimes = pd.concat([pd.Series(tlsdf.loc[tlsdf.index[1:],'time'].to_numpy() - tlsdf.loc[tlsdf.index[:-1],'time'].to_numpy()),
                               pd.Series([float('nan')],index = [tlsdf.index.max()])])
        tlsdf_reduced.loc[greenRows, column] = greenTimes.loc[greenRows]
        amberRedRows = amberRedRows | greenRows
    #last column for yellow and red time
    amberRedRows = ~amberRedRows
    amberRedTimes = pd.concat([pd.Series(tlsdf.loc[tlsdf.index[1:],'time'].to_numpy() - tlsdf.loc[tlsdf.index[:-1],'time'].to_numpy()),
                        pd.Series([float('nan')],index = [tlsdf.index.max()])])
    tlsdf_reduced.loc[amberRedRows, 'AmberRed'] = amberRedTimes.loc[amberRedRows]
    return tlsdf_reduced.to_numpy(dtype=np.float32).copy()
    

def universal_widgets(tlsnp, axSplit, axDist, axCyclic, axPlan):
    #RangeSlider for the time axis
    axtime = plt.axes([0.3, 0, 0.3, 0.09])
    time_slider = RangeSlider(ax = axtime,
                         label = 'Plot range',
                         valmin = 0,
                         valmax = tlsnp[:,0].max(),
                         valinit = (0,180),
                         valfmt = '%d s')
    
    # the Callable for each time there is a change of slider
    def time_update(val):
        axCyclic.set_xlim(time_slider.val[0]-3, time_slider.val[1]+3)
        axCyclic.set_aspect((time_slider.val[1]-time_slider.val[0])/720, adjustable='box')
        axPlan.set_xlim(time_slider.val[0], time_slider.val[1])
        axPlan.set_aspect((time_slider.val[1]-time_slider.val[0])/60*1.5, adjustable='box')
        
        selected_time = (time_slider.val[0] < tlsnp[:,0]) & (tlsnp[:,0]  < time_slider.val[1])
        for col, barContainer in enumerate(axDist.containers, 2):
            noNaN = ~np.isnan(tlsnp[selected_time,col])
            heights = np.histogram(tlsnp[selected_time][noNaN,col], bins = dist_bins, density = density)[0]
            for i, rectangle in enumerate(barContainer.patches):
                rectangle.set_height(heights[i])
                
        selected_time = (time_slider.val[0] < tlsnp[:,0]) & (tlsnp[:,0]  < time_slider.val[1])
        all_signal = np.nan_to_num(tlsnp[selected_time,2:onlyGreen]).sum(axis=0)
        all_signal_cumsum = np.append(0,np.cumsum(all_signal))
        green_percent = all_signal/all_signal.sum()
        for i, barContainer in enumerate(axSplit.containers[:onlyGreen]):
            barContainer.patches[0].set_x(all_signal_cumsum[i])
            barContainer.patches[0].set_width(all_signal[i])
            texts[i].set_text('{:.2f}'.format(green_percent[i]))
            texts[i].set_x(all_signal_cumsum[i] + 0.45*all_signal[i])
        axSplit.set_xticks(all_signal_cumsum)
        axSplit.set_xlim(0, all_signal_cumsum[-1])
        axSplit.set_aspect((all_signal_cumsum[-1])/60*2, adjustable='box')

    # register the Callable with each slider
    time_slider.on_changed(time_update)
    
    # RadioButtons for more plot options
    radio1 = RadioButtons(plt.axes([0.72, 0.58, 0.18, 0.07]), ['Frequency','Probability density'])
    def histfunc(label):
        global density
        if label =='Frequency':
            axDist.set_ylabel('Frequency')
            density = False
            axDist.set_ylim(dist_ylim)
        elif label == 'Probability density':
            axDist.set_ylabel('Probability density')
            density = True
            axDist.set_ylim(0,0.3)

        selected_time = (time_slider.val[0] < tlsnp[:,0]) & (tlsnp[:,0]  < time_slider.val[1])
        for col, barContainer in enumerate(axDist.containers, 2):
            noNaN = ~np.isnan(tlsnp[selected_time,col])
            heights = np.histogram(tlsnp[selected_time][noNaN,col], bins = dist_bins, density = density)[0]
            for i, rectangle in enumerate(barContainer.patches):
                rectangle.set_height(heights[i])
    
    radio1.on_clicked(histfunc)
    
    radio2 = RadioButtons(plt.axes([0.3, 0.63, 0.18, 0.07]), ['Green + Yellow & red','Green'])
    def splitfunc(label):
        global onlyGreen
        if label == 'Green + Yellow & red':
            onlyGreen = 0
            texts[-1].set_alpha(1.0)
        elif label == 'Green':
            onlyGreen = -1
            texts[-1].set_alpha(0)
            axSplit.containers[-1].patches[0].set_width(0)
        selected_time = (time_slider.val[0] < tlsnp[:,0]) & (tlsnp[:,0]  < time_slider.val[1])
        all_signal = np.nan_to_num(tlsnp[selected_time,2:onlyGreen]).sum(axis=0)
        all_signal_cumsum = np.append(0,np.cumsum(all_signal))
        green_percent = all_signal/all_signal.sum()
        for i, barContainer in enumerate(axSplit.containers[:onlyGreen]):
            barContainer.patches[0].set_x(all_signal_cumsum[i])
            barContainer.patches[0].set_width(all_signal[i])
            texts[i].set_text('{:.2f}'.format(green_percent[i]))
            texts[i].set_x(all_signal_cumsum[i] + 0.45*all_signal[i])
        axSplit.set_xticks(all_signal_cumsum)
        axSplit.set_xlim(0, all_signal_cumsum[-1])
        axSplit.set_aspect((all_signal_cumsum[-1])/60*2, adjustable='box')
        
    radio2.on_clicked(splitfunc)
           
    # putting up a reset button for the time slider
    resetax = plt.axes([0.7, 0.02, 0.1, 0.06])
    button = Button(resetax, 'Reset', hovercolor='0.975')
    def reset(event):
        time_slider.reset()
        # axPlan.set_ylim(-0.5,len(stageNames)-0.5)
    button.on_clicked(reset)
    return time_slider, button, radio1, radio2


def plot_signalPlan(ax: plt.Axes,
                    time_slider: RangeSlider,
                    tlsnp: np.ndarray,
                    stages: pd.DataFrame,
                    colours: list = ['red', 'yellow', 'green', 'forestgreen']):
    '''
    'colours' list must contain 4 pyplot colours which respectively represent the SUMO signal indicators r y g G.
    '''
    stageNames = stages.columns
    stages_plan= stages.copy()
    for i, color in enumerate('rygG'):
        stages_plan[stages==color] = colours[i]

    for i in range(tlsnp.shape[0]-1):
        ax.barh(stageNames,
                width = tlsnp[i+1,0] - tlsnp[i,0], 
                left = tlsnp[i,0],
                height = 0.5,
                color = stages_plan.loc[tlsnp[i,1]])
    ax.set_xlabel('Simulation time (s)')
    ax.set_xticks(tlsnp[:,0], minor = True, linewidth = 0.5)
    ax.xaxis.grid(True, which='minor')
    
    ax.set_xlim(time_slider.val[0], time_slider.val[1])
    ax.set_ylim(-0.5,len(stageNames)-0.5)
    ax.set_aspect((time_slider.val[1]-time_slider.val[0])/60*1.5, adjustable='box')

def plot_greenTimeDistribution(ax: plt.Axes,
                               time_slider: RangeSlider,
                               tlsnp: np.ndarray,
                               stages: pd.DataFrame,
                               num_bins: int,
                               bar_colours: list):
    '''
    The number of colours provided in 'bar_colours' has to be equal to the number of stages
    '''
    global dist_bins, density, dist_ylim
    density = False
    _, dist_bins,_ = ax.hist(tlsnp[:,2:-1],  bins = num_bins, histtype = 'bar',
                             density = density, color = bar_colours, label = stages.columns.to_list())
    dist_ylim = ax.get_ylim()
    ax.legend(prop={'size': 10})
    ax.set_xlabel('Green time (s)')
    ax.set_xticks(dist_bins)
    ax.set_ylabel('Frequency')
    selected_time = (time_slider.val[0] < tlsnp[:,0]) & (tlsnp[:,0]  < time_slider.val[1])
    print(tlsnp.dtype)
    for col, barContainer in enumerate(ax.containers, 2):
        noNaN = ~np.isnan(tlsnp[selected_time,col])
        heights = np.histogram(tlsnp[selected_time][noNaN,col], bins = dist_bins, density = density)[0]
        for i, rectangle in enumerate(barContainer.patches):
            rectangle.set_height(heights[i])
    
def plot_greenTimeSplit(ax: plt.Axes, 
                        time_slider: RangeSlider,
                        tlsnp: np.ndarray,
                        stages: pd.DataFrame,
                        bar_colours: list):
    '''
    The number of colours provided in 'bar_colours' has to be equal to the number of stages
    '''
    global texts, onlyGreen
    onlyGreen = None # None or -1
    bar_colours.append('grey')
    stageNames = stages.columns.to_list()
    stageNames.append('Yellow & red')
    all_signal = np.nan_to_num(tlsnp[:,2:]).sum(axis=0)
    all_signal_cumsum = np.append(0,np.cumsum(all_signal))
    signal_percent = all_signal/all_signal.sum()
    for i in range(len(all_signal)):
        ax.barh(['Green Split'],
                        width = all_signal[i],
                        left = all_signal_cumsum[i],
                        height = 3,
                        color = bar_colours[i],
                        label = stageNames[i])
    texts = [ax.text(all_signal_cumsum[i] + 0.45*all_signal[i],-0.25,'{:.2f}'.format(signal_percent[i]), color = 'white') for i in range(len(all_signal))]
    ax.set_xlabel('Time (s)')
    ax.legend(loc = 'lower left', bbox_to_anchor=(0, 1.04), borderaxespad=0, prop={'size': 10})


    selected_time = (time_slider.val[0] < tlsnp[:,0]) & (tlsnp[:,0]  < time_slider.val[1])
    all_signal = np.nan_to_num(tlsnp[selected_time,2:onlyGreen]).sum(axis=0)
    all_signal_cumsum = np.append(0,np.cumsum(all_signal))
    green_percent = all_signal/all_signal.sum()
    for i, barContainer in enumerate(ax.containers[:onlyGreen]):
        barContainer.patches[0].set_x(all_signal_cumsum[i])
        barContainer.patches[0].set_width(all_signal[i])
        texts[i].set_text('{:.2f}'.format(green_percent[i]))
        texts[i].set_x(all_signal_cumsum[i] + 0.45*all_signal[i])
    ax.set_xticks(all_signal_cumsum)
    ax.set_xlim(0, all_signal_cumsum[-1])
    ax.set_aspect((all_signal_cumsum[-1])/60*2, adjustable='box')

def plot_cyclicity(ax: plt.Axes, 
                        time_slider: RangeSlider,
                        tlsnp: np.ndarray,
                        stages: pd.DataFrame,
                        cyclicity: int,
                        bar_colours: list):
    '''
    There are 2 variations of cyclicity plot
    1) A vertical bar is stacked until the same stage is recurred (default).
    2) A vertical bar is stacked until all stages are in the bar.
    '''
    bar_loc = 0
    last_top = 0 
    storage = []
    greenSubStages = {}
    for column in  stages:
        greenSubStages[column] = stages[column].loc[stages[column] == 'G'].index.to_list()
    flattenedGreen = [i for j in list(greenSubStages.values()) for i in j]
    bar_colours = pd.Series(bar_colours, index = flattenedGreen) # watch out, this may not work when a stage is green at more than 1 subStages
    for i in range(tlsnp.shape[0]):
        storage.append(tlsnp[i,1])
        cond1 = any([storage.count(subStageID[0]) > 1 for subStageID in greenSubStages.values()]) and cyclicity == 1 # the condition for first varition of plot
        cond2 = all([subStageID[0] in storage for subStageID in greenSubStages.values()]) and cyclicity == 2 # the condition for second varition of plot
        terminal = (i == tlsnp.shape[0]-1)
        if cond1 or cond2 or terminal:
            storage = [tlsnp[i,1]]
            bar_loc = tlsnp[i,0]
            last_top = 0 
            
        if tlsnp[i, 1] in flattenedGreen:
            ax.bar(x = bar_loc,
                    height = tlsnp[i+1,0] - tlsnp[i,0], 
                    bottom = last_top,
                    width = 5,
                    color = bar_colours[tlsnp[i, 1]])
            last_top = tlsnp[i+1,0] - tlsnp[i,0] + last_top

    ax.set_xlabel('Simulation time (s)')
    ax.set_ylabel('Quasi-cyclic green time (s)')
    ax.xaxis.grid(True)
    
    ax.set_xlim(time_slider.val[0]-3, time_slider.val[1]+3)
    ax.set_aspect((time_slider.val[1]-time_slider.val[0])/720, adjustable='box')
    


def clusterPlot_TLS(tlsdf, stageIndices, stageNames, end_time, **kwargs):
    assert len(stageIndices) == len(tlsdf.loc[0,'state']), 'The grouping of movements into stages is not valid'
    
    #Handling the keyword arugments which are optional arguments
    bar_colours = kwargs.get('bar_colours', [mini_dict['color'] for mini_dict in mpl.rcParams["axes.prop_cycle"][:len(stageNames)]])
    num_bins = kwargs.get('num_bins', 10)
    cyclicity_type = kwargs.get('cyclicity_type', 1)
    stage_type = kwargs.get('stage_type', 'mode')
    
    #just to change column name 'phase' to 'subStageID'
    colnames = tlsdf.columns.to_series()
    colnames.loc[colnames == 'phase'] = 'subStageID'
    tlsdf.columns = colnames
    del colnames
    
    #adding last row
    last_row = tlsdf.loc[(tlsdf['subStageID'] == 0),:].iloc[0].to_frame().T
    last_row['time'] = end_time
    tlsdf = pd.concat([tlsdf,last_row], ignore_index = True, axis = 0)
    
    #basic meta-data for the following subroutines
    stages = tlsStages(tlsdf, stageIndices, stageNames, stage_type)
    tlsnp = tlsNumpy(tlsdf, stages)

    fig = plt.figure(figsize=(12, 8))
    gs = gridspec.GridSpec(9, 2)
    axSplit = fig.add_subplot(gs[0:2,0])
    axDist = fig.add_subplot(gs[0:2,1])
    axCyclic = fig.add_subplot(gs[3:6,:])
    axPlan = fig.add_subplot(gs[6:9,:])

    '''
    Notes on the widgets:
    1. The widgets have to be initialised before calling the plot functions
    2. The references to the widget objects have to be kept to prevent the plot from becoming non-responsive
        (keep the return variables from 'universal_widgets' function)
    '''
    time_slider, button, radio1, radio2 = universal_widgets(tlsnp, axSplit, axDist, axCyclic, axPlan) 

    axPlan.set_title('Signal Plan', fontweight ="bold")
    plot_signalPlan(axPlan, time_slider, tlsnp, stages)

    axDist.set_title('Green Duration Distribution', fontweight = 'bold')
    plot_greenTimeDistribution(axDist, time_slider, tlsnp, stages, num_bins, bar_colours)

    axCyclic.set_title('Cyclicity plot using the {} definition'.format('first' if cyclicity_type == 1 else 'second'), fontweight ='bold')
    plot_cyclicity(axCyclic, time_slider, tlsnp, stages, cyclicity_type, bar_colours)

    axSplit.set_title('Green Split', fontweight = 'bold')
    plot_greenTimeSplit(axSplit, time_slider, tlsnp, stages, bar_colours)
    
    return time_slider, button, radio1, radio2