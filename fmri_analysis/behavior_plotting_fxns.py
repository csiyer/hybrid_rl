# helper plotting functions for behavior.ipynb

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from scipy.stats import linregress
import matplotlib.pyplot as plt
import seaborn as sns

def overall_plot(data, x_var, y_var, grouping_var, mean=True, **kwargs):
    # e.g., plot each subject (grouping_var) their average reward (y_var) per run (x_var)
    group_data = data.groupby([x_var,grouping_var]).mean()[y_var].reset_index() 

    plt.figure(figsize=(4,4))
    for group in group_data[grouping_var].unique():
        subset = group_data[group_data[grouping_var] == group]
        plt.plot(subset[x_var], subset[y_var], label=group, alpha=0.5)
    if mean:
        mean_data = group_data.groupby(x_var)[y_var].mean().reset_index()
        plt.plot(mean_data[x_var], mean_data[y_var], label='mean', color='black', linewidth=3)
    if 'chance' in kwargs:
        plt.hlines(y=kwargs['chance'], xmin=min(group_data[x_var]), xmax=max(group_data[x_var]), 
                   color='gray', linestyle='--', label='Chance')
    
    title = kwargs['title'] if 'title' in kwargs else f'{y_var} vs {x_var} by {grouping_var}'
    plt.title(title)
    xlabel = kwargs['xlabel'] if 'xlabel' in kwargs else x_var
    plt.xlabel(xlabel)
    ylabel = kwargs['ylabel'] if 'ylabel' in kwargs else f"{y_var} (average)"
    plt.ylabel(ylabel)
    if 'ylim' in kwargs: plt.ylim(kwargs['ylim'])
    if 'yticks' in kwargs: plt.yticks(kwargs['yticks'])
    # if 'yticklabels' in kwargs: plt.yticklabels(kwargs['yticklabels'])
    if 'xlim' in kwargs: plt.xlim(kwargs['xlim'])
    if 'xticks' in kwargs: plt.xticks(kwargs['xticks'])
    # if 'xticklabels' in kwargs: plt.xticklabels(kwargs['xticklabels'])
    if 'legend' in kwargs: plt.legend(title=grouping_var)
    plt.show()


def overall_boxplot(data, grouping_var, y_var, **kwargs):
    group_data = data.groupby(grouping_var)[y_var].mean().reset_index()
    n = len(group_data)
    x_jitter = np.ones(n) + (np.random.rand(n)-0.5)/20

    plt.figure(figsize=(4,4))
    plt.scatter(x_jitter, group_data[y_var], alpha=0.4)
    plt.boxplot(group_data[y_var])
    plt.xticks([])
    if 'chance' in kwargs:
        xmin,xmax = (kwargs['xlim']) if 'xlim' in kwargs else (0.8,1.2)
        plt.hlines(y=kwargs['chance'], xmin=xmin, xmax=xmax, 
                   color='gray', linestyle='--', label='Chance')
    title = kwargs['title'] if 'title' in kwargs else f'{y_var} by {grouping_var}'
    plt.title(title)
    xlabel = kwargs['xlabel'] if 'xlabel' in kwargs else grouping_var
    plt.xlabel(xlabel)
    ylabel = kwargs['ylabel'] if 'ylabel' in kwargs else y_var
    plt.ylabel(ylabel)
    if 'ylim' in kwargs: plt.ylim(kwargs['ylim'])
    if 'yticks' in kwargs: plt.yticks(kwargs['yticks'])
    # if 'yticklabels' in kwargs: plt.yticklabels(kwargs['yticklabels'])
    if 'xlim' in kwargs: plt.xlim(kwargs['xlim'])
    if 'xticks' in kwargs: plt.xticks(kwargs['xticks'])
    # if 'xticklabels' in kwargs: plt.xticklabels(kwargs['xticklabels'])
    if 'legend' in kwargs: plt.legend(title=grouping_var)
    plt.show()


def simple_plot(data, x_var, y_var, sem=True, **kwargs):
    data=data.copy()
    if 'bins' in kwargs:
        if 'bins' not in kwargs:
            kwargs['bins'] = sorted(data[x_var][data[x_var].notna()].unique())
        bins = kwargs['bins']
        bin_centers = bins[:-1] + np.diff(bins) / 2 
        data[x_var] = pd.cut(data[x_var], bins, labels=bin_centers)

    group_data = data.groupby(x_var)[y_var].agg(['count','mean','sem'])
    if 'y2' in kwargs:
        y2 = kwargs['y2']
        if '_lik' in y2:
            data[y2] = np.exp(data[y2])
        group_data2 = data.groupby(x_var)[y2].mean()

    plt.figure(figsize=(6, 4))
    # plot the data
    plt.plot(group_data['mean'], linestyle='-', linewidth=3, zorder=3)
    # add sem
    plt.fill_between(group_data['mean'].keys(), 
                     (group_data['mean'] + group_data['sem']), 
                     (group_data['mean'] - group_data['sem']),
                     color='gray', alpha=0.5)
    if 'y2' in kwargs: 
        plt.plot(group_data2, linestyle='--', label=kwargs['y2_label'], zorder=2)
    if 'chance' in kwargs:
        xmin,xmax = (min(group_data['mean'].keys()), max(group_data['mean'].keys())) if min(group_data['mean'].keys()) > 1 else (0,1)
        plt.hlines(y=kwargs['chance'], xmin=xmin, xmax=xmax, 
                   color='gray', linestyle='--', label='Chance', zorder=1)
        
    title = kwargs['title'] if 'title' in kwargs else f'{y_var} by {x_var}'
    plt.title(title)
    xlabel = kwargs['xlabel'] if 'xlabel' in kwargs else x_var
    plt.xlabel(xlabel)
    ylabel = kwargs['ylabel'] if 'ylabel' in kwargs else y_var
    plt.ylabel(ylabel)
    if 'ylim' in kwargs: plt.ylim(kwargs['ylim'])
    if 'yticks' in kwargs: plt.yticks(kwargs['yticks'])
    # if 'yticklabels' in kwargs: plt.yticklabels(kwargs['yticklabels'])
    if 'xlim' in kwargs: plt.xlim(kwargs['xlim'])
    if 'xticks' in kwargs: plt.xticks(kwargs['xticks'])
    # if 'xticklabels' in kwargs: plt.xticklabels(kwargs['xticklabels'])
    if 'legend' in kwargs: plt.legend()
    plt.grid(True)
    plt.show()


def simple_plot_pair(data, x_var, y_var, **kwargs):
    group_data = data.groupby(x_var)[y_var].agg(['count','mean','sem'])
    plt.figure(figsize=(4, 4))
    # plot the data
    plt.errorbar(x= group_data['mean'].keys(), y = group_data['mean'].values,
             yerr= group_data['sem'].values, marker='o', capsize=4, capthick=2)
    if 'chance' in kwargs:
        xmin,xmax = (min(group_data['mean'].keys()), max(group_data['mean'].keys())) if min(group_data['mean'].keys()) > 1 else (0,1)
        plt.hlines(y=kwargs['chance'], xmin=xmin, xmax=xmax, 
                   color='gray', linestyle='--', label='Chance', zorder=1)
    title = kwargs['title'] if 'title' in kwargs else f'{y_var} by {x_var}'
    plt.title(title)
    xlabel = kwargs['xlabel'] if 'xlabel' in kwargs else x_var
    plt.xlabel(xlabel)
    ylabel = kwargs['ylabel'] if 'ylabel' in kwargs else y_var
    plt.ylabel(ylabel)
    if 'ylim' in kwargs: plt.ylim(kwargs['ylim'])
    if 'yticks' in kwargs: plt.yticks(kwargs['yticks'])
    # if 'yticklabels' in kwargs: plt.yticklabels(kwargs['yticklabels'])
    if 'xlim' in kwargs: plt.xlim(kwargs['xlim'])
    if 'xticks' in kwargs: plt.xticks(kwargs['xticks'])
    # if 'xticklabels' in kwargs: plt.xticklabels(kwargs['xticklabels'])
    if 'legend' in kwargs: plt.legend()
    plt.grid(True)
    plt.show()



def logistic(x, L, x0, k):
    return L / (1 + np.exp(-k * (x - x0)))

def fit_logistic(x,y):
    popt, _ = curve_fit(logistic, x, y, p0=[1, np.mean(x), 1], maxfev=10000)
    x_fit = np.linspace(min(x), max(x), 100)
    y_fit = logistic(x_fit, *popt)
    return x_fit, y_fit

def plot_separate_subjects(data, x_cols, y_cols, x_texts, y_texts, logistic_fit, title=''):
    data = data.copy()
    fig,axs = plt.subplots(1,3, figsize=(12,4))
    fig.suptitle(title)

    for ax,x_col,y_col,x_text,y_text in zip(axs,x_cols,y_cols,x_texts,y_texts):
        # bin if necessary
        if len(data[x_col].unique()) > 20:
            xmin, xmax  = (min(data[x_col]), max(data[x_col]))
            bins = np.linspace(xmin,xmax,11)
            bin_centers = bins[:-1] + np.diff(bins) / 2 
            data[x_col] = pd.cut(data[x_col], bins, labels=bin_centers).astype(float)

        group_data = data.groupby(["Sub", x_col])[y_col].mean().reset_index()
        # plot subject data
        for sub in group_data["Sub"].unique():
            sub_data = group_data[group_data["Sub"] == sub]
            x = sub_data[x_col].values
            y = sub_data[y_col].values
            x = x[~np.isnan(y)]
            y = y[~np.isnan(y)]
            if logistic_fit:
                x_fit, y_fit = fit_logistic(x,y)
                ax.plot(x_fit, y_fit, alpha=0.5)
            else:
                ax.plot(x, y, alpha=0.5)
        # plot mean
        mean_data = data.groupby(x_col)[y_col].mean().reset_index()
        if logistic_fit:
            x_mean_fit, y_mean_fit = fit_logistic(x = mean_data[x_col].values, y = mean_data[y_col].values)
            ax.plot(x_mean_fit, y_mean_fit, color='black', linewidth=3)
        else:
            ax.plot(mean_data[x_col].values, mean_data[y_col].values, color='black', linewidth=3)

        ax.set_xlabel(x_text, fontsize=12)
        ax.set_ylabel(y_text, fontsize=12)
        ax.set_title(title, fontsize=14)
        ax.set_ylim((0,1.1))

    plt.tight_layout()
    plt.show()


def plot_lingering_modes(data, oldnew_vs_newnew=False, **kwargs):
    # first, assign a trial as having previous object memory or not (old trial and optimal choice)
    data = data.copy()
    data["prec_obj_memory"] = data.apply(
        lambda row: (
            1 if row["OldT"] == 1 and row["OptObj"] == 1 else # used episodic memory
            -1 if row["OldT"] == 1 and row["OptObj"] == 0 else # did not use episodic memory
            0 # new/new trial
        ),
        axis=1
    )
    data["prec_obj_memory"] = data["prec_obj_memory"].shift(1) # shift to the last trial

    if oldnew_vs_newnew: # compare old/new trials whose preceding trial is old/new successful vs new/new
        data = data[(data.OldT==1) & (data.prec_obj_memory.isin([0,1]) )] 
        labels = ['preceding_newnew', 'prec_optimal_memory']
    else:
        # compare old/new trials whose preceding trial is old/new successful vs old/new unsuccessful
        data = data[(data.OldT==1) & (data.prec_obj_memory.isin([-1,1]) )] 
        labels = ['preceding_error_memory', 'prec_optimal_memory']
    
    f, axs = plt.subplots(1, 4, figsize=(12, 3), sharey=False)
    if 'title' in kwargs: f.suptitle(kwargs['title'])

    for i,(x_col, y_col, x_label, y_label, title) in enumerate(zip(
        ####  try deck version also with OldDeckPP vs OldObjC
        ['ObjPP', 'PP'], ['OldObjC', 'StayResp'], 
        ['Value of old object','Previous deck reward'], ['Likelihood of chooosing old card','Likelihood of staying with deck'],
        ['Object Use','Deck Use']
    )):
        group_data = data.groupby(['prec_obj_memory', x_col])[y_col].agg(['count','mean','sem']).reset_index()
        
        for j,(key, group) in enumerate(group_data.groupby('prec_obj_memory')):
            color = ['blue', 'green'][j]
            axs[i*2].plot(group[x_col], group['mean'], color=color, label=labels[j])
            axs[i*2].fill_between(group[x_col], 
                                  (group['mean'] + group['sem']), (group['mean'] - group['sem']),
                                  color='gray', alpha=0.5)
            
            slope, _, _, _, _ = linregress([0,0.2,0.4,0.6,0.8,1.0], group['mean'])
            # slope = (group['mean'].iloc[-1] - group['mean'].iloc[0])
            axs[i*2+1].bar(x=1-j, height=slope, color=color, label=labels[j])

        axs[i*2].set_ylim(0.2,0.8)
        axs[i*2].set_title(title)
        axs[i*2].set_xlabel(x_label)
        axs[i*2].set_ylabel(y_label)
        axs[i*2].legend()

        axs[i*2+1].set_ylim(0,0.4)
        axs[i*2+1].set_title(title)
        axs[i*2+1].set_xticks([0,1])
        axs[i*2+1].set_xticklabels(['mem', 'no mem'])
        axs[i*2+1].set_xlabel('Preceding trial memory')
        axs[i*2+1].set_ylabel('Slope of linear fit')

    plt.tight_layout()
    plt.show()


def plot_lingering_modes_iti(data, from_choice_or_fb = 'choice', oldnew_vs_newnew=False, **kwargs):
    #### SAME STUFF AS ABOVE
    # first, assign a trial as having previous object memory or not (old trial and optimal choice)
    data = data.copy()
    data["prec_obj_memory"] = data.apply(
        lambda row: (
            1 if row["OldT"] == 1 and row["OptObj"] == 1 else # used episodic memory
            -1 if row["OldT"] == 1 and row["OptObj"] == 0 else # did not use episodic memory
            0 # new/new trial
        ),
        axis=1
    )
    data["prec_obj_memory"] = data["prec_obj_memory"].shift(1) # shift to the last trial

    if oldnew_vs_newnew: # compare old/new trials whose preceding trial is old/new successful vs new/new
        data = data[(data.OldT==1) & (data.prec_obj_memory.isin([0,1]) )] 
        labels = ['preceding_newnew', 'prec_optimal_memory']
    else:
        # compare old/new trials whose preceding trial is old/new successful vs old/new unsuccessful
        data = data[(data.OldT==1) & (data.prec_obj_memory.isin([-1,1]) )] # this implicitly limits to only consecutive old/new trials 
        labels = ['preceding_error_memory', 'prec_optimal_memory']

    ## NOW NEW STUFF
    if from_choice_or_fb=='choice':
        iti_helper_col = 'iti_fromchoice'
    elif from_choice_or_fb=='fb':
        iti_helper_col = 'iti_fromfb'
    data = data[~pd.isna(data[iti_helper_col])]
    data['iti_round'] = data[iti_helper_col].round(0) # round for easy binning
    
    f, axs = plt.subplots(1, 2, figsize=(12, 3), sharey=False)
    if 'title' in kwargs: f.suptitle(kwargs['title'])

    for i,(x_col, y_col, title) in enumerate(zip(['ObjPP', 'PP'], 
                                                 ['OldObjC', 'StayResp'], 
                                                 ['Object Use','Deck Use'])):
        # first panel: object use, second panel deck use
        group_data = data.groupby(['iti_round', 'prec_obj_memory', x_col])[y_col].mean().reset_index()
        def compute_slope(group):
            X = group[x_col].values
            y = group[y_col].values
            if len(X) > 1: 
                return linregress(X, y).slope
            return None
        slopes_df = group_data.groupby(['iti_round', 'prec_obj_memory']).apply(compute_slope, include_groups=False).reset_index(name='slope')
        slopes_mem = slopes_df[slopes_df['prec_obj_memory'] == 1]
        slopes_nomem = slopes_df[slopes_df['prec_obj_memory'] != 1]

        axs[i].scatter(slopes_nomem['iti_round'], slopes_nomem['slope'], color='blue', label=labels[0], alpha=0.7)
        axs[i].scatter(slopes_mem['iti_round'], slopes_mem['slope'], color='green', label=labels[1], alpha=0.7)
        axs[i].plot(slopes_nomem['iti_round'], slopes_nomem['slope'], color='blue', alpha=0.5)
        axs[i].plot(slopes_mem['iti_round'], slopes_mem['slope'], color='green' , alpha=0.5)
        

        axs[i].set_xlabel(f'ITI (from {from_choice_or_fb})')
        axs[i].set_ylabel(f'Slope of linear fit \n(x={x_col}, y={y_col})')
        axs[i].set_title(title)
        axs[i].legend()

    plt.tight_layout()
    plt.show()


def add_isi_to_data(data, save=True):
    # add ITI to data, assess mode effect by bin grouping
    import os, scipy.io
    beh_path = '/Volumes/shohamy-locker/shohamy_from_labshare/rgerraty/hybrid_mri/behavior'
    if not os.path.isdir(beh_path):
        print('Behavioral files not found')
        return 
    
    data['iti_fromfb'] = np.zeros(len(data))
    data['iti_fromchoice'] = np.zeros(len(data))
    for sub in data.Sub.unique():
        for run in data.Run.unique():

            pfile = scipy.io.loadmat(beh_path + f'/{sub:02d}_output/Performance_5.mat')
            start_of_choice = pfile['Performance']['time'][0,0]['startChoice'][0,0][0] # startTrial is start of choice period, startChoice is the response time
            start_of_isi = pfile['Performance']['time'][0,0]['startISI'][0,0][0]
            run_mask = pfile['Performance']['cond'][0,0]['Run'][0,0][0] == run
            
            # fix one weird thing
            if sub == 13:
                resp = pfile['Performance']['choose'][0, 0]['resp'][0,0][0]
                start_of_choice = start_of_choice[resp != 0]
                start_of_isi = start_of_isi[resp != 0]
                run_mask = run_mask[resp != 0]

            start_of_choice = start_of_choice[run_mask]
            start_of_isi = start_of_isi[run_mask]

            # difference between onset of choice and onset of previous choice
            data.loc[(data.Sub==sub)&(data.Run==run), 'iti_fromchoice'] = np.hstack([[np.nan], np.diff(start_of_choice)]) 
        
            # difference between onset of choice and offset of previous fb (start of true ITI) 
            data.loc[(data.Sub==sub)&(data.Run==run), 'iti_fromfb'] = np.hstack([[np.nan], start_of_choice[1:]-start_of_isi[:-1]])

    if save:
        data.to_csv('data/hybrid_data.csv',index=False)

    return data