import statistics
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import RangeSlider, Button, RadioButtons
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

def tlsNumpy(tlsdf: pd.DataFrame,
             stages: pd.DataFrame):

    tlsdf_reduced = tlsdf.loc[:,('time','subStageID')]
    #find which subStageIDs correspond to the green subStages of each stage. 
    greenSubStages = {}
    for column in  stages:
        greenSubStages[column] = stages[column].loc[stages[column] == 'g'].index.to_list()
        greenRows = (tlsdf['subStageID'] == greenSubStages[column][0])
        greenTimes = pd.concat([pd.Series(tlsdf.loc[tlsdf.index[1:],'time'].to_numpy() - tlsdf.loc[tlsdf.index[:-1],'time'].to_numpy()),
                               pd.Series([float('nan')],index = [tlsdf.index.max()])])
        tlsdf_reduced.loc[greenRows, column] = greenTimes.loc[greenRows]
    #last column for yellow and red time
    amberRedRows = ~greenRows
    amberRedTimes = pd.concat([pd.Series(tlsdf.loc[tlsdf.index[1:],'time'].to_numpy() - tlsdf.loc[tlsdf.index[:-1],'time'].to_numpy()),
                        pd.Series([float('nan')],index = [tlsdf.index.max()])])
    tlsdf_reduced.loc[greenRows, 'AmberRed'] = greenTimes.loc[greenRows]
    return tlsdf_reduced.to_numpy().copy()
    

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
            heights = np.histogram(tlsnp[selected_time][noNaN,col], bins = dist_bins, density = density)[0]
            for i, rectangle in enumerate(barContainer.patches):
                rectangle.set_height(heights[i])
                
        all_green = np.nan_to_num(tlsnp[selected_time,2:]).sum(axis=0)
        all_green_cumsum = np.append(0,np.cumsum(all_green))
        green_percent = all_green/all_green.sum()
        for i, barContainer in enumerate(axSplit.containers):
            barContainer.patches[0].set_x(all_green_cumsum[i])
            barContainer.patches[0].set_width(all_green[i])
            texts[i].set_text('{:.2f}'.format(green_percent[i]))
            texts[i].set_x(all_green_cumsum[i] + 0.45*all_green[i])
        axSplit.set_xticks(all_green_cumsum)
        axSplit.set_xlim(0, all_green_cumsum[-1])
        axSplit.set_aspect((all_green_cumsum[-1])/60*2, adjustable='box')

    # register the Callable with each slider
    time_slider.on_changed(time_update)
    
    # RadioButtons for more plot options
    radio1 = RadioButtons(plt.axes([0.77, 0.37, 0.2, 0.1]), ['Frequency','Probability density'])
    def histfunc(label):
        global density
        if label =='Frequency':
            axDist.set_ylabel('Frequency')
            density = False
            axDist.set_ylim(dist_ylim)
        elif label == 'Probability mass':
            axDist.set_ylabel('Probability mass')
            density = True
            axDist.set_ylim(0,0.5)

        selected_time = (time_slider.val[0] < tlsnp[:,0]) & (tlsnp[:,0]  < time_slider.val[1])
        for col, barContainer in enumerate(axDist.containers, 2):
            noNaN = ~np.isnan(tlsnp[selected_time,col])
            heights = np.histogram(tlsnp[selected_time][noNaN,col], bins = dist_bins, density = density)[0]
            for i, rectangle in enumerate(barContainer.patches):
                rectangle.set_height(heights[i])
        
        
                
        
                
    radio1.on_clicked(histfunc)
    
    radio2 = RadioButtons(plt.axes([0.1, 0.37, 0.2, 0.1]), ['Green','Green + Yellow + Red'])
    def splitfunc(label):
        if label == 'Green':
            pass
        elif label == 'Green + Yellow & Red':
            pass
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
                               tlsnp: np.ndarray,
                               stages: pd.DataFrame,
                               num_bins: int,
                               bar_colours: list):
    '''
    The number of colours provided in 'bar_colours' has to be equal to the number of stages
    '''
    global dist_bins, density, dist_ylim
    density = False
    _, dist_bins,_ = ax.hist(tlsnp[:,2:],  bins = num_bins, histtype = 'bar',
                             density = density, color = bar_colours, label = stages.columns.to_list())
    dist_ylim = ax.get_ylim()
    ax.legend(prop={'size': 10})
    ax.set_xlabel('Green time (s)')
    ax.set_ylabel('Frequency')
    selected_time = (time_slider.val[0] < tlsnp[:,0]) & (tlsnp[:,0]  < time_slider.val[1])
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
    global texts

    stageNames = stages.columns.to_list()
    all_green = np.nan_to_num(tlsnp[:,2:]).sum(axis=0)
    all_green_cumsum = np.append(0,np.cumsum(all_green))
    green_percent = all_green/all_green.sum()
    for i in range(len(all_green)):
        axSplit.barh(['Green Split'],
                        width = all_green[i],
                        left = all_green_cumsum[i],
                        height = 3,
                        color = bar_colours[i],
                        label = stageNames[i])
    texts = [ax.text(all_green_cumsum[i] + 0.45*all_green[i],-0.25,'{:.2f}'.format(green_percent[i]), color = 'white') for i in range(len(all_green))]\
        + [ax.text(all_green_cumsum[-1]) + 0.45*]
    ax.set_xlabel('Time (s)')
    ax.legend(loc = 'lower left', bbox_to_anchor=(0, 1.04), borderaxespad=0, prop={'size': 10})


    selected_time = (time_slider.val[0] < tlsnp[:,0]) & (tlsnp[:,0]  < time_slider.val[1])
    all_green = np.nan_to_num(tlsnp[selected_time,2:]).sum(axis=0)
    all_green_cumsum = np.append(0,np.cumsum(all_green))
    green_percent = all_green/all_green.sum()
    for i, barContainer in enumerate(ax.containers):
        barContainer.patches[0].set_x(all_green_cumsum[i])
        barContainer.patches[0].set_width(all_green[i])
        texts[i].set_text('{:.2f}'.format(green_percent[i]))
        texts[i].set_x(all_green_cumsum[i] + 0.45*all_green[i])
    ax.set_xticks(all_green_cumsum)
    ax.set_xlim(0, all_green_cumsum[-1])
    ax.set_aspect((all_green_cumsum[-1])/60*2, adjustable='box')

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
tlsnp = tlsNumpy(tlsdf, stages)


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
time_slider, button, radio1 = universal_widgets(axSplit, axDist, axPlan) 

axPlan.set_title('Signal Plan', fontweight ="bold")
plot_signalPlan(axPlan, time_slider, tlsdf, stages)

axDist.set_title('Green Duration Distribution', fontweight = 'bold')
plot_greenTimeDistribution(axDist, time_slider, tlsnp, stages, num_bins = 10, bar_colours = ['m', 'c'])

axSplit.set_title('Green Split', fontweight = 'bold')
plot_greenTimeSplit(axSplit, time_slider, tlsnp, stages, bar_colours = ['m', 'c'])

plt.show()