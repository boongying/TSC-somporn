import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from plot_functions import tlsStages, tlsNumpy
import itertools

#DO note that g and G makes tons of differences and leading to bugs

#Defining the stages
stageIndices = [2,2,3,0,0,1,2,2,3,0,0,1]
stageNames = ['WE_ls','WE_r','NS_ls','NS_r']
longStageNames = ['West-East: Left & Through','West-East: Right','North-South: Left & Through','North-South: Right']
# bar_colours = ['salmon','olive','lime','plum']
bar_colours = ['c','y','m','k']

study = 'D2.0'
exp = '2'
run = '0'
eps = 999

tlsdf = pd.read_xml('./data/{}_e{}_r{}_tlsrecord_eps{}.xml'.format(study,exp,run,eps))

#change all the subStageID of the fixed time program
newids = [1, 2, 3, 4, 0, 5, 6, 7, 8, 0]
oldtls = tlsdf.copy()
for oldID, newID in enumerate(newids):
    tlsdf.loc[(tlsdf['programID'] == 'Fixed') & (oldtls['phase'] == oldID), 'phase'] = newID
del oldtls, newids


#just to change column name 'phase' to 'subStageID'
colnames = tlsdf.columns.to_series()
colnames.loc[colnames == 'phase'] = 'subStageID'
tlsdf.columns = colnames
del colnames

#adding last row
last_row = tlsdf.loc[(tlsdf['subStageID'] == 0),:].iloc[0].to_frame().T
last_row['time'] = 3750.0
tlsdf = pd.concat([tlsdf,last_row], ignore_index = True, axis = 0)

stages = tlsStages(tlsdf, stageIndices, stageNames, definition = 'mode')
tlsnp = tlsNumpy(tlsdf, stages)

#plot for state history
s_rl = pd.read_csv('./data/{}_e{}_r{}_test{}_hist.csv'.format(study,exp,run,eps))
s_rl[stageNames[0]] = s_rl[['Queue_W_l','Queue_W_s','Queue_E_l','Queue_E_s']].sum(axis = 1)
s_rl[stageNames[1]] = s_rl[['Queue_W_r','Queue_E_r']].sum(axis = 1)
s_rl[stageNames[2]] = s_rl[['Queue_N_l','Queue_N_s','Queue_S_l','Queue_S_s']].sum(axis = 1)
s_rl[stageNames[3]] = s_rl[['Queue_N_r','Queue_S_r']].sum(axis = 1)

#evaluation data
eval_e3 = pd.read_csv('./data/{}_e{}_r{}_eps{}_eval.csv'.format(study,exp,run,eps))
eval_e3 = pd.concat([eval_e3.iloc[0:1], eval_e3], ignore_index = True)
eval_e3.iloc[0,0] = 0
eval_e3.drop('meanTimeLoss',axis = 1, inplace = True)

#total log data
total_df = pd.read_csv('./data/{}_e{}_r{}_eps{}_total.csv'.format(study,exp,run,eps))



#%% plot for evaluation matrices
fig, axes = plt.subplots(figsize = (12,8), ncols = 2, nrows = 2, sharex = True)


e3_labels = ['$[veh]$','$[-]$','$[s]$']
e3_titles = ['Intersection throughput','Average halts per vehicle','Average travel time']
for i, ax in enumerate(list(itertools.chain.from_iterable(axes[:2]))):

    if i == 3:
        ax.step(s_rl['time'],s_rl['reward'], label = "Reward",linewidth = 0.9, color = 'gray')
        ax.set_ylabel('$[veh]$')
        ax.set_title('RL Reward')
        ax.set_ylim(-35,0)
        ax.grid('on')
    else:
        ax.step(x = eval_e3['to_time'], y = eval_e3.iloc[:,i+1],
                linewidth = 1.2, where='pre')
        ax.set_ylabel(e3_labels[i])
        ax.set_title(e3_titles[i])
        ax.set_xlim(eval_e3['to_time'].min(), eval_e3['to_time'].max())
        ax.set_xticks(np.arange(150,eval_e3['to_time'].max()+150, 600))
        ax.grid('on')

fig.suptitle('Exp. {}, episode {}'.format(exp, eps))
plt.tight_layout()
plt.savefig("summary_exp{}_ep{}.svg".format(exp, eps), format = 'svg')
plt.close('all')
#%% plot for state history
fig, axes = plt.subplots(figsize = (15,10), ncols = 1, nrows = 3, sharex = True)
plotGrouping = [['WE_ls','WE_r'],['NS_ls','NS_r']]


axes[0].step(s_rl['time'],s_rl['reward'], label = "Reward",linewidth = 0.9, color = 'gray')
axes[0].set_ylabel('$[veh]$')
axes[0].set_title('RL Reward')
axes[0].set_ylim(-35,0)
axes[0].grid('on')

counter = 0
for i, sublist in enumerate(plotGrouping, start = 1):
    for stagename in sublist:
        axes[i].step(s_rl['time'],s_rl[stagename], linewidth = 0.9,
                       color = bar_colours[counter], where='post', label = longStageNames[counter])
        axes[i].set_ylabel('$[veh]$')
        axes[i].set_ylim(-1,20)
        axes[i].set_yticks(np.arange(0,24,4))
        axes[i].xaxis.grid(True)
        axes[i].set_title('Sum of lane-queue by stage')
        axes[i].legend(loc = 'upper left')
        counter += 1

axes[-1].set_xlim(eval_e3['to_time'].min(), eval_e3['to_time'].max())
axes[-1].set_xticks(np.arange(150,eval_e3['to_time'].max()+150, 150))
axes[-1].set_xlabel('Simulation time (s)')

fig.suptitle('Exp. {}, episode {}'.format(exp, eps))
plt.tight_layout()
plt.savefig("history_exp{}_ep{}.svg".format(exp, eps), format = 'svg')
plt.close('all')

#%% Plot for cyclicity 
#Plot prarameters
cyclicity = 1
'''
There are 2 variations of cyclicity plot
1) A vertical bar is stacked until the same stage is recurred (default).
2) A vertical bar is stacked until all stages are in the bar.
'''
fig, ax = plt.subplots(figsize = (20,8))

greenSubStages = {}
for column in  stages:
    greenSubStages[column] = stages[column].loc[stages[column] == 'G'].index.to_list()
flattenedGreen = [i for j in list(greenSubStages.values()) for i in j]
pdbar_colours = pd.Series(bar_colours, index = flattenedGreen) # watch out, this may not work when a stage is green at more than 1 subStages
bar_names = pd.Series(longStageNames, index = flattenedGreen) # watch out, this may not work when a stage is green at more than 1 subStages


bar_loc =  tlsnp[0,0]
storage = []
cycle_temp = []
index_temp = []
for i in range(tlsnp.shape[0]):
    storage.append(tlsnp[i,1])
    cond1 = any([storage.count(subStageID[0]) > 1 for subStageID in greenSubStages.values()]) and cyclicity == 1 # the condition for first varition of plot
    cond2 = all([subStageID[0] in storage for subStageID in greenSubStages.values()]) and cyclicity == 2 # the condition for second varition of plot
    terminal = (i == tlsnp.shape[0]-1)
    if cond1 or cond2 or terminal:
        for k,j in enumerate(index_temp):
            ax.bar(x = bar_loc,
                height = cycle_temp[k]/sum(cycle_temp), 
                bottom = sum(cycle_temp[:k])/sum(cycle_temp),
                width = sum(cycle_temp),
                color = pdbar_colours[tlsnp[j, 1]], 
                align = 'edge',
                alpha = 0.7,
                label = bar_names[tlsnp[j, 1]])
        ax.axvline(bar_loc, linewidth =1, alpha = 0.4, color = 'k')
        storage = [tlsnp[i,1]]
        bar_loc = tlsnp[i,0]
        cycle_temp = []
        index_temp = []

    if tlsnp[i, 1] in flattenedGreen:
        cycle_temp.append(tlsnp[i+1,0] - tlsnp[i,0])
        index_temp.append(i)

ax.set_xlabel('Simulation time $[s]$')
ax.set_ylabel('Cycle split $[-]$')
ax.set_xticks(np.arange(0,3900, 150))
ax.xaxis.grid(True)

ax.set_xlim(0,3750)
ax.set_ylim(0,1)
ax.set_aspect(500, adjustable='box')

plt.sca(ax)
handles, labels = plt.gca().get_legend_handles_labels()
by_label = dict(zip(labels, handles))
plt.legend(by_label.values(), by_label.keys(), 
            bbox_to_anchor = (1.0,1.05), loc = 'lower right',
            borderaxespad = 0)

plt.tight_layout()
plt.savefig("cyclicity_exp{}_ep{}.svg".format(exp, eps), format = 'svg')
plt.close('all')


#%% Plot for in-depth inspection
fig, ax = plt.subplots(figsize = (20,8))

ax.step(x = total_df['simTime'], y= total_df['e2_W_0/JamLengthVehicle'],
        label = 'Queue', where = 'pre')
ax.step(x = total_df['simTime'], y= total_df['e2_W_0/LastStepVehicleNumber'],
        label = 'Occupancy', where = 'pre')
ax.legend()

plt.tight_layout()
plt.savefig("data_diff_exp{}_ep{}.svg".format(exp, eps), format = 'svg')
plt.close('all')
