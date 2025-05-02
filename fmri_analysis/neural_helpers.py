"""Helper functions for neural_patterns.ipynb"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.spatial.distance import cdist

bids_dir = '/Volumes/shohamy-locker/chris/hybrid_mri_bids'
nibs_dir = f'{bids_dir}/derivatives/nibetaseries'


sub_conversion = pd.read_csv('./data/n31_subject_list.txt')
beh = pd.read_csv('./data/hybrid_data.csv')

def get_beh_data(sub_num):
    """behavioral data"""
    bids_sub_num = f'sub-hybrid{sub_num:02d}'
    orig_sub_id = sub_conversion.original[sub_conversion.bids == bids_sub_num].iloc[0]
    orig_sub_num = int(orig_sub_id[-2:])
    return beh[(beh.Sub==orig_sub_num) & (~pd.isna(beh.RT))].reset_index()

def get_roi_patterns(sub_num, trial_type, roi):
    """Retrieve pre-extracted and normalized hippocampal patterns for a sub/trial type (choice/fb)
        We will concatenate all avaialble runs"""
    sub_id = f'sub-hybrid{sub_num:02d}'
    run_patterns = []
    for run in range(1,6):
        if sub_num==12 and run==4: continue
        path = os.path.join(nibs_dir, sub_id, 'func', 'rois', f'{sub_id}_task-main_run-{run}_space-MNI152NLin2009cAsym_desc-{trial_type}_betaseries_{roi}_norm.npy')
        run_patterns.append(np.load(path))
    return np.hstack(run_patterns).T # timepoints x voxels

def get_all_roi_patterns(roi):
    all_patterns = {}
    for sub_num in range(1,32):
        all_patterns[sub_num] = {
            'choice': get_roi_patterns(sub_num, 'choice', roi),
            'fb': get_roi_patterns(sub_num, 'fb', roi),
        }
    return all_patterns

def get_corr_matrix(all_patterns, sub_num, trial_type):
    # correlate trials of type tt1 with trials of type tt2
    if trial_type == 'choice' or trial_type == 'fb':
        hipp_patterns = all_patterns[sub_num][trial_type]
        return np.corrcoef(hipp_patterns)
    else: # correlate retrieval choice w encoding feedback
        n_trials = all_patterns[sub_num]['choice'].shape[0]
        hipp_patterns_choice = all_patterns[sub_num]['choice']
        hipp_patterns_fb = all_patterns[sub_num]['fb']
        return np.corrcoef(hipp_patterns_choice, hipp_patterns_fb)[:n_trials, n_trials:]

def get_dist_matrix(all_patterns, sub_num, trial_type):
    if trial_type in ['choice', 'fb']:
        patterns = all_patterns[sub_num][trial_type]
        return cdist(patterns, patterns, metric='euclidean')
    else:
        patterns_choice = all_patterns[sub_num]['choice']
        patterns_fb = all_patterns[sub_num]['fb']
        return cdist(patterns_choice, patterns_fb, metric='euclidean') # mat[i,j] gives distance from CHOICE[i] to FB[j]


################# PLOTTING

def simple_violin(x1, x2, **kwargs):
    plt.figure(figsize=(6, 4))
    if 'title' in kwargs:
        plt.title(kwargs['title'])
    plt.scatter(np.zeros_like(x1), x1, color="blue", label=kwargs['x1_label'], alpha=0.7)
    plt.scatter(np.ones_like(x2), x2, color="orange", label=kwargs['x2_label'], alpha=0.7)
    sns.violinplot([x1,x2], palette=['blue','orange'], inner=None, linewidth=1, alpha = 0.5)
    plt.xticks([0, 1], [kwargs['x1_label'], kwargs['x2_label'] ] )
    if 'xlabel' in kwargs: plt.xlabel(kwargs['xlabel'])
    if 'ylabel' in kwargs: plt.ylabel(kwargs['ylabel'])
    if 'xlim' in kwargs: plt.xlim(kwargs['xlim'])
    if 'ylim' in kwargs: plt.ylim(kwargs['ylim'])
    if 'yticks' in kwargs: plt.yticks(kwargs['yticks'])
    # if 'yticklabels' in kwargs: plt.yticklabels(kwargs['yticklabels'])
    if 'legend' in kwargs: plt.legend()
    # plt.grid(True)
    plt.show()


def simple_bar(x1, x2, **kwargs):
    plt.figure(figsize=(6, 4))
    if 'title' in kwargs:
        plt.title(kwargs['title'])
    # sns.violinplot([x1,x2], palette=['blue','orange'], inner=None, linewidth=1, alpha = 0.5)
    plt.bar([0, 1], [np.mean(x1), np.mean(x2)], color=['blue', 'orange'], alpha=0.6)
    for i in range(len(x1)):
        plt.plot([0, 1], [x1[i], x2[i]], color='gray', alpha=0.5)
    plt.scatter(np.zeros_like(x1), x1, color="blue", label=kwargs['x1_label'], alpha=0.7, edgecolor="black")
    plt.scatter(np.ones_like(x2), x2, color="orange", label=kwargs['x2_label'], alpha=0.7, edgecolor="black")
    plt.xticks([0, 1], [kwargs['x1_label'], kwargs['x2_label'] ] )
    if 'xlabel' in kwargs: plt.xlabel(kwargs['xlabel'])
    if 'ylabel' in kwargs: plt.ylabel(kwargs['ylabel'])
    if 'xlim' in kwargs: plt.xlim(kwargs['xlim'])
    if 'ylim' in kwargs: plt.ylim(kwargs['ylim'])
    if 'yticks' in kwargs: plt.yticks(kwargs['yticks'])
    # if 'yticklabels' in kwargs: plt.yticklabels(kwargs['yticklabels'])
    if 'legend' in kwargs: plt.legend()
    # plt.grid(True)
    plt.show()


def double_bar(x_arr,labels_arr,**kwargs):
    fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharey=True, sharex=True)
    if 'title' in kwargs:
        fig.suptitle(kwargs['title'])
    for i,ax in enumerate(axes):
        x1,x2 = x_arr[i*2], x_arr[i*2+1]
        label1, label2 = labels_arr[i*2], labels_arr[i*2+1]
        if 'ax_titles' in kwargs:
            ax.set_title(kwargs['ax_titles'][i])
        ax.bar([0, 1], [np.mean(x1), np.mean(x2)], color=['blue', 'orange'], alpha=0.5)
        for j in range(len(x1)):
            ax.plot([0, 1], [x1[j], x2[j]], color='gray', alpha=0.5)
        ax.scatter(np.zeros_like(x1), x1, color="blue", label=label1, alpha=0.7, edgecolor="black")
        ax.scatter(np.ones_like(x2), x2, color="orange", label=label2, alpha=0.7, edgecolor="black")
        ax.set_xticks([0, 1])
        ax.set_xticklabels([label1, label2])
        if 'xlabel' in kwargs: ax.set_xlabel(kwargs['xlabel'])
        if 'xlim' in kwargs: ax.set_xlim(kwargs['xlim'])
        # if 'ylabel' in kwargs: ax.set_ylabel(kwargs['ylabel'])
        if 'ylim' in kwargs: ax.set_ylim(kwargs['ylim'])
        if 'yticks' in kwargs: ax.set_yticks(kwargs['yticks'])
        # if 'legend' in kwargs and kwargs['legend']: ax.legend()
    if 'ylabel' in kwargs: plt.ylabel(kwargs['ylabel'])
    # if 'yticklabels' in kwargs: plt.yticklabels(kwargs['yticklabels'])
    if 'legend' in kwargs: plt.legend()
    plt.tight_layout()
    plt.show()


def simple_plot(arr,x=None,xlabel='',ylabel='',title=''):
    if not x:
        x = np.arange(len(arr))
    means = [np.mean(a) for a in arr]
    std = [np.std(a) for a in arr]
    plt.figure(figsize=(8, 5))
    plt.plot(x, means, color='b', linewidth=0.5)
    plt.errorbar(x, means, yerr=std, fmt='o', capsize=5, color='b')
    plt.xticks(x, labels=np.array(x).astype(str))
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.show()


def plot_enc_kernel(kernel_array1, kernel_array2=None, label1='', label2='',
                    xlabel="Distance from encoding trial (choice)",
                    ylabel="Pattern similarity to retrieval choice",
                    title=""):
    # for each timepoint relative to encoding trial, plot across-subject mean pattern similarity
    n_subs = len(kernel_array1)
    arr1_means = np.mean(kernel_array1, axis=0)
    arr1_errors = np.std(kernel_array1, axis=0) / np.sqrt(n_subs)  # Standard Error of the Mean (SEM)
    x = np.arange(len(arr1_means)) - len(arr1_means) // 2
    plt.figure(figsize=(8, 5))
    plt.plot(x, arr1_means, color='b', linewidth=0.5)
    plt.errorbar(x, arr1_means, yerr=arr1_errors, fmt='o', capsize=5, label=label1, color='b')
    if kernel_array2:
        arr2_means = np.mean(kernel_array2, axis=0)
        arr2_errors = np.std(kernel_array2, axis=0) / np.sqrt(n_subs)  # Standard Error of the Mean (SEM)
        plt.plot(x, arr2_means, color='orange', linewidth=0.5)
        plt.errorbar(x, arr2_means, yerr=arr2_errors, fmt='o', capsize=5, label=label2, color='orange')
        plt.legend()
    plt.xticks(x, labels=x.astype(str))
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.show()

def plot_ers_delay(delay_dict, title, xlabel):
    # for each timepoint relative to encoding trial, plot across-subject mean pattern similarity
    keys = sorted(delay_dict.keys())
    means = [np.mean(delay_dict[k]) for k in keys]
    errors = [np.std(delay_dict[k])/np.sqrt(31) for k in keys]
    x = [int(k) for k in keys]
    plt.figure(figsize=(8, 5))
    plt.plot(x, means, color='b', linewidth=0.5)
    plt.errorbar(x, means, yerr=errors, fmt='o', capsize=5, label='Enc-ret pairs', color='b')
    # plt.plot(x, arr2_means, color='orange', linewidth=0.5)
    # plt.errorbar(x, arr2_means, yerr=arr2_errors, fmt='o', capsize=5, label=label2, color='orange')
    plt.xticks(x, labels=keys)
    plt.xlabel(xlabel)
    plt.ylabel("Pattern similarity")
    plt.title(title)
    # plt.legend()
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.show()

def plot_revt_ps(dict1, dict2=None, title='', xlabel=''):
    # for each timepoint relative to encoding trial, plot across-subject mean pattern similarity
    keys = sorted(dict1.keys())
    x = [int(k) for k in keys]
    means1 = [np.mean(dict1[k]) for k in keys]
    errors1 = [np.std(dict1[k])/np.sqrt(31) for k in keys]

    plt.figure(figsize=(8, 5))
    plt.plot(x, means1, color='b', linewidth=0.5, label='optimal memory')
    plt.errorbar(x, means1, yerr=errors1, fmt='o', capsize=5, color='b')

    if dict2:
        means2 = [np.mean(dict2[k]) for k in keys]
        errors2 = [np.std(dict2[k])/np.sqrt(31) for k in keys]
        plt.plot(x, means2, color='orange', linewidth=0.5,  label='nonoptimal memory')
        plt.errorbar(x, means2, yerr=errors2, fmt='o', capsize=5, color='orange')
    
    plt.xticks(x, labels=keys)
    plt.xlabel(xlabel)
    plt.ylabel("Pattern similarity")
    plt.title(title)
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.show()


def heatmap_grid(mats, title=''):
    fig, axes = plt.subplots(nrows=6, ncols=6, figsize=(15, 15))
    axes = axes.flatten()  # Flatten to iterate easily
    for i,mat in enumerate(mats):
        ax = axes[i]
        sns.heatmap(mat, cmap="coolwarm", center=0, ax=ax, cbar=False)
        # ax.set_title(f"sub {i+1}")
        ax.set_xticks([])  # Remove x-ticks for clarity
        ax.set_yticks([])  # Remove y-ticks for clarity
    for ax in axes[len(mats):]:
        ax.axis("off")
    plt.suptitle(title, fontsize=16)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.show()


