import pandas as pd
import numpy as np
import matplotlib as mpl
mpl.rcParams['axes.unicode_minus'] = False
mpl.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import gridspec


plt.style.use('seaborn-paper')

params = {
    'xtick.direction' : 'out',
    'ytick.direction' : 'out',
    'axes.labelsize': 8,
    'font.size': 8,
    'legend.fontsize': 8,
    'xtick.labelsize': 8,
    'ytick.labelsize': 8,
    'text.usetex': False,
    'grid.color': '#c7c8ca',
    'grid.linestyle': '-',
    'grid.linewidth': 0.5,
}
mpl.rcParams.update(params)

mpl.rcParams['font.family'] = 'serif'
mpl.rcParams['font.serif'] = ['Times']
width = 3.49
height = 2.87


def plot_inset(slope, confs, variable, home_or_dest, file_name, degree_dest, degree_home):
    conf_low, conf_high = confs
    fig, ax = plt.subplots()
    if variable == 'information':
        fig.subplots_adjust(left=.16, bottom=.15, right=.97, top=.97)
    else:
        fig.subplots_adjust(left=.20, bottom=.15, right=.97, top=.97)
    fig.set_size_inches(width, height)
    # migration figure
    gs = gridspec.GridSpec(2, 1, height_ratios=[3, 1])
    ax1 = plt.subplot(gs[0])
    ax1.yaxis.set_ticks_position('left')
    ax1.xaxis.set_ticks_position('bottom')
    ax1.spines['right'].set_visible(False)
    ax1.spines['top'].set_visible(False)

    slope_min = np.nanmin(slope)
    slope_max = np.nanmax(slope)
    y_min = slope_min - (slope_max - slope_min) * 0.1
    y_max = slope_max + (slope_max - slope_min) * 0.1
    if variable == 'support':
        plt.ylabel(r'$\beta_k$ (common support effect)')
        if home_or_dest == 'dest':
            plt.ylim([-2000, 3000])
        else:
            plt.ylim([-2000, 2000])
    elif variable == 'cluster':
        plt.ylabel(r'$\beta_k$ (clustering effect)')
        if home_or_dest == 'dest':
            plt.ylim(-4100, 13000)
        else:
            plt.ylim(-8000, 5110)
    elif variable == 'information':
        plt.ylabel(r'$\beta_k$ (friends of friends effect)')
        if home_or_dest == 'dest':
            plt.ylim([-6, 6.3])
        else:
            plt.ylim([-7, 35])
    elif variable == 'cluster':
        plt.ylabel(r'$\beta_k$ (clustering effect)')
    elif variable == 'degree':
        plt.ylabel(r'$\beta_k$ (degree centrality effect)')
    scatter_min_v = {
        'information': 1,
        'support': 2,
        'cluster': 2
    }
    scatter_min = scatter_min_v[variable]
    if home_or_dest == 'home':
        plt.scatter(range(scatter_min, 23), slope, color='k', s=7)
        
        plt.errorbar(range(scatter_min, 23), slope, yerr=[slope-conf_low, conf_high-slope], capsize=2, capthick=1, linewidth=1, ecolor='k', linestyle='None')
        plt.axhline(y=0, c='k', linewidth=0.5, ls='dashed')
        plt.xlim([0, 23])
    else:
        plt.scatter(range(scatter_min, 23), slope, color='k', s=7)
        print(len(slope))
        print(len(conf_low))
        print(slope-conf_low)
        plt.errorbar(range(scatter_min, 23), slope, yerr=[slope-conf_low, conf_high-slope],capsize=2, capthick=1, linewidth=1,ecolor='k', linestyle='None')
        plt.axhline(y=0, c='k', linewidth=0.5, ls='dashed')
        plt.xlim([0, 23])
    plt.grid(axis='y',zorder=1)

    plt.tick_params(axis='both', which='both', bottom='on', top='off', labelbottom='off', right='off', left='on', labelleft='on')
    ax2 = plt.subplot(gs[1])
    ax2.yaxis.set_ticks_position('left')
    ax2.xaxis.set_ticks_position('bottom')
    ax2.spines['right'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
    if home_or_dest == 'dest':
        plt.bar(np.arange(scatter_min , 22.5, 1),
                          degree_dest['num'][scatter_min:], width=1,edgecolor='black',
                          color='gray', zorder=2)
        plt.xlim([0, 23])
        plt.xlabel('Network size (degree centrality) at destination')
    else:
        plt.bar(np.arange(scatter_min , 22.5, 1),
                          degree_home['num'][scatter_min:], width=1,edgecolor='black',
                          color='gray', zorder=2)
        plt.xlim(0, 23)
        plt.xlabel('Network size (degree centrality) at home')
    if home_or_dest == 'dest':
        if variable == 'information':
            plt.yticks([0, .4e7, .8e7, 1.2e7, 1.6e7])
        else:
            plt.yticks([0, 1.0e6, 2.0e6, 3.0e6, 4.0e6, 5.0e6])
    else:
        plt.yticks([0, .5e5, 1.0e5, 1.5e5, 2.0e5])

    plt.ylabel('Count')
    plt.grid(axis='y',zorder=1)
    plt.tick_params(axis='both', which='both', bottom='on', top='off', labelbottom='on', right='off', left='on', labelleft='on')
    plt.savefig(file_name, dpi=300)


for variable in ['support', 'information', 'cluster']:
    for home_or_dest in ['dest', 'home']:
        degree_dest = pd.read_csv('data/inset_degree_distribution_dest.csv')
        degree_home = pd.read_csv('data/inset_degree_distribution_home.csv')
        slope = np.asarray(pd.read_csv('data/inset_' + variable + '_coef_' + home_or_dest + '.csv')['x'])
        se_low = np.asarray(pd.read_csv('data/inset_' + variable + '_se_' + home_or_dest + '_left.csv')['x'])
        se_high = np.asarray(pd.read_csv('data/inset_' + variable + '_se_' + home_or_dest + '_right.csv')['x'])
        file_name = 'figure/' + variable + '_' + home_or_dest + '_' + 'inset.png'
        plot_inset(slope, [se_low, se_high], variable, home_or_dest, file_name, degree_dest, degree_home)
