import statistics
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import RangeSlider, Button
plt.rcParams.update({'font.sans-serif':'Arial'})

def tlsStages(tlsdf: pd.DataFrame,
                   stageIndex: list,
                   stageNames: list,
                   definition: str = 'mode') -> pd.DataFrame:
    '''
    definition from the statistical mode of movement indicators
        say we have stageIndex = [0,0,0,1,1,1,0,1]
        and the state of a subStage i is 'y g g r r r g r' 
        then the states at subStage i are stage0:g (3g over 1y), stage1:r (4r)
        
    definition from the first movement indicator
        say we have sigGruppenIndex = [>0<,0,0,>1<,1,1,0,1]
        and the state of a stage i is '>y< g g >r< r r g r' 
        then the states at subStage i is stage0:y , stage1:r
    '''
    stages = pd.DataFrame(columns = stageNames,
                              index = pd.Index(pd.unique(tlsdf.iloc[:,3]),name = 'subStageID'))
    for i in stages.index:
        assert len(pd.unique(tlsdf.loc[tlsdf['subStageID'] == i,'state'])) == 1, 'movement definition conflict'
        indicators = pd.unique(tlsdf.loc[tlsdf['subStageID'] == i,'state'])[0]
        for movement in range(len(stageNames)):
            slicedIndex = [ind for ind, j in enumerate(stageIndex) if j == movement]
            movementIndicators = [indicators[ind] for ind in slicedIndex]
            if definition == 'mode':
                stageDefinition = statistics.mode(movementIndicators)
            elif definition =='first':
                stageDefinition = movementIndicators[0]
            else:
                raise ValueError('the input value for \'definition\' is invalid')
            stages.loc[i,stageNames[movement]] = stageDefinition
    return stages


def universal_widgets(axSplit, axDist, axPlan):
    
    #RangeSlider for the time axis
    axtime = plt.axes([0.3, 0, 0.3, 0.09])
    time_slider = RangeSlider(ax = axtime,
                         label = 'Plot range',
                         valmin = 0,
                         valmax = tlsdf['time'].max(),
                         valinit = (0,180),
                         valfmt = '%d s')
    
    
    # the Callable for each time there is a change of slider
    def time_update(val):
        axPlan.set_xlim(time_slider.val[0], time_slider.val[1])
        axPlan.set_aspect((time_slider.val[1]-time_slider.val[0])/60*1.5, adjustable='box')
        
        selected_time = (time_slider.val[0] < tlsnp[:,0]) & (tlsnp[:,0]  < time_slider.val[1])
        for col, barContainer in enumerate(axDist.containers, 2):
            noNaN = ~np.isnan(tlsnp[selected_time,col])
            heights = np.histogram(tlsnp[selected_time][noNaN,col], bins = dist_bins)[0]
            for i, rectangle in enumerate(barContainer.patches):
                rectangle.set_height(heights[i])

        
    # register the Callable with each slider
    time_slider.on_changed(time_update)
        
    # putting up a reset button    
    resetax = plt.axes([0.7, 0.02, 0.1, 0.06])
    button = Button(resetax, 'Reset', hovercolor='0.975')
    def reset(event):
        time_slider.reset()
        axPlan.set_ylim(-0.5,len(stageNames)-0.5)
    button.on_clicked(reset)
    return time_slider, button


def plot_signalPlan(ax: plt.Axes,
                    time_slider: RangeSlider,
                   tlsdf: pd.DataFrame,
                   stages: pd.DataFrame,
                   colours: list = ['red', 'yellow', 'green', 'forestgreen']):
    '''
    'colours' list must contain 4 pyplot colours which respectively represent the SUMO signal indicators r y g G.
    '''
    stageNames = stages.columns
    stages_plan= stages.copy()
    for i, color in enumerate('rygG'):
        stages_plan[stages==color] = colours[i]

    for i in tlsdf.index[:-1]:
        ax.barh(stageNames,
                width = tlsdf.loc[i+1,'time'] - tlsdf.loc[i,'time'], 
                left = tlsdf.loc[i,'time'],
                height = 0.5,
                color = stages_plan.loc[tlsdf.loc[i,'subStageID']])
    ax.set_xlabel('Simulation time (s)')
    ax.set_xticks(tlsdf['time'], minor = True, linewidth = 0.5)
    ax.xaxis.grid(True, which='minor')
    
    ax.set_xlim(time_slider.val[0], time_slider.val[1])
    ax.set_ylim(-0.5,len(stageNames)-0.5)
    ax.set_aspect((time_slider.val[1]-time_slider.val[0])/60*1.5, adjustable='box')

def plot_greenTimeDistribution(ax: plt.Axes,
                               time_slider: RangeSlider,
                               tlsdf: pd.DataFrame,
                               stages: pd.DataFrame,
                               num_bins: int,
                               bar_colours: list):
    '''
    The number of colours provided in 'bar_colours' has to be equal to the number of stages
    '''
    tlsdf_reduced = tlsdf.loc[:,('time','subStageID')]
    #Firstly, find which subStageIDs correspond to the green subStages of each stage. 
    greenSubStages = {}
    for column in  stages:
        greenSubStages[column] = stages[column].loc[stages[column] == 'g'].index.to_list()
        
    for column in stages:
        greenRows = (tlsdf['subStageID'] == greenSubStages[column][0])
        greenTimes = pd.concat([pd.Series(tlsdf.loc[tlsdf.index[1:],'time'].to_numpy() - tlsdf.loc[tlsdf.index[:-1],'time'].to_numpy()),
                               pd.Series([float('nan')],index = [tlsdf.index.max()])])
        tlsdf_reduced.loc[greenRows, column] = greenTimes.loc[greenRows]
        
    #plotting routine
    global tlsnp, dist_bins
    tlsnp = tlsdf_reduced.to_numpy().copy()
    
    _, dist_bins,_ = ax.hist(tlsnp[:,2:],  bins = num_bins, histtype = 'bar', color = bar_colours, label = stages.columns.to_list())
    ax.legend(prop={'size': 10})
    ax.set_xlabel('Green time (s)')
    ax.set_ylabel('Frequency')
    selected_time = (time_slider.val[0] < tlsnp[:,0]) & (tlsnp[:,0]  < time_slider.val[1])
    for col, barContainer in enumerate(axDist.containers, 2):
        noNaN = ~np.isnan(tlsnp[selected_time,col])
        heights = np.histogram(tlsnp[selected_time][noNaN,col], bins = dist_bins)[0]
        for i, rectangle in enumerate(barContainer.patches):
            rectangle.set_height(heights[i])
    


#import the tls data and rename the variable
tlsdf = pd.read_xml('TLSrecord.xml')
colnames = tlsdf.columns.to_series()
colnames.loc[colnames == 'phase'] = 'subStageID'
tlsdf.columns = colnames
del colnames

stageIndex = [0,0,0,1,1,1,0,0,0,1,1,1,1,0,1,0]
stageNames = ['North-South','West-East']
assert len(stageIndex) == len(tlsdf.loc[0,'state']), 'The grouping of movements into stages is not valid'
stages = tlsStages(tlsdf, stageIndex, stageNames)


fig = plt.figure(figsize=(12, 6))
axSplit = fig.add_subplot(2,2,1)
axDist = fig.add_subplot(2,2,2)
axPlan = fig.add_subplot(2,1,2)

'''
Notes on the widgets:
1. The widgets have to be initialised before calling the plot functions
2. The references to the widget objects have to be kept to prevent the plot from becoming non-responsive
    (keep the return variables from 'universal_widgets' function)
'''
time_slider, button = universal_widgets(axSplit, axDist, axPlan) 

axPlan.set_title('Signal Plan', fontweight ="bold")
plot_signalPlan(axPlan, time_slider, tlsdf, stages)

axDist.set_title('Green Duration Distribution', fontweight = 'bold')
plot_greenTimeDistribution(axDist, time_slider, tlsdf, stages, num_bins = 10, bar_colours = ['m', 'c'])

axSplit.set_title('Green Split', fontweight = 'bold')

plt.show()