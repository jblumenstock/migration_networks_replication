import pandas as pd
import numpy as np
from statsmodels.stats.proportion import proportion_confint
import matplotlib as mpl
from datetime import datetime
from dateutil.relativedelta import relativedelta
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
plt.rc('text', usetex=True)
plt.rc('axes', axisbelow=True)

width = 3.49
height = 2.87


def bin_num_bound(data, bins, variable):
    zero_num = data.count(0)
    max_data = max(bins)
    max_num = data.count(max_data)
    data = [x for x in data if (x != 0) and (x != max_data) and (not np.isnan(x))]
    counts, bins = np.histogram(data, bins)
    counts = np.append(counts, zero_num)
    counts = np.append(counts, max_num)
    return counts


def bin_num(range_min, range_max, bin_size, data, variable, home_or_dest):
    if variable == 'd':
        if home_or_dest == 'home':
            bins = np.arange(0.5, 74.6, bin_size)
        else:
            bins = np.arange(0.5, 22.6, bin_size)
    else:
        bins = np.arange(range_min, range_max, bin_size)
    counts_moveto = bin_num_bound(data[0], bins, variable)
    counts_total = bin_num_bound(data[1], bins, variable)
    return counts_moveto, counts_total


def plot_migration(input):
    range_min, range_max, bin_size, y, two, xlabel, ylabel, title, file_name, fix_degree_slope, variable, home_or_dest = input
    bins = np.arange(range_min, range_max, bin_size)
    bin_centers = (bins[:-1] + bins[1:]) / 2.0

    fig, ax = plt.subplots()
    fig.subplots_adjust(left=.16, bottom=.15, right=.97, top=.97)
    fig.set_size_inches(width, height)
    # migration figure
    gs = gridspec.GridSpec(2, 1, height_ratios=[3, 1])
    ax1 = plt.subplot(gs[0])
    ax1.yaxis.set_ticks_position('left')
    ax1.xaxis.set_ticks_position('bottom')
    ax1.spines['right'].set_visible(False)
    ax1.spines['top'].set_visible(False)

    lower_error = []
    upper_error = []
    moveto_result = two[0]
    all_result = two[1]
    for i in xrange(len(two[0])):
        l, u = proportion_confint(moveto_result[i], all_result[i], alpha=0.05, method='wilson')
        lower_error.append(y[i] - l)
        upper_error.append(u - y[i])
    if variable in ['cluster', 'support']:
        x = [0, 1]
    else:
        x = [0, range_max - 1]
    if variable == 'degree':
        plt.scatter(bins[1:], y[:-2], color='k', s=7)
        plt.errorbar(bins[1:], y[:-2], yerr=[lower_error[:-2], upper_error[:-2]], capsize=2, capthick=1, linewidth=1, ecolor='k', linestyle='None')
    else:
        plt.scatter(bin_centers, y[:-2], color='k', s=7)
        plt.errorbar(bin_centers, y[:-2], yerr=[lower_error[:-2], upper_error[:-2]], capsize=2, capthick=1, linewidth=1, ecolor='k', linestyle='None')
    plt.grid(axis='y',zorder=1)
    if variable == 'cluster':
        if home_or_dest == 'home':
            plt.ylim([0, 0.202])
        else:
            plt.ylim([0, 0.062])
    elif variable == 'support':
        if home_or_dest == 'home':
            plt.ylim([0, 0.062])
        else:
            plt.ylim([0, 0.142])
    elif variable == 'information':
        if home_or_dest == 'dest':
            plt.ylim([0, 0.142])
        else:
            plt.ylim([0, 0.162])
    if variable == 'degree':
        if home_or_dest == 'home':
            plt.xlim([0, 75])
            plt.ylim(0, .162)
        else:
            plt.xlim([0, 23])
            plt.ylim(0, .0922)
    else:
        plt.xlim([0, bins[-1]])
    plt.ylim(ymin=0)
    plt.ylabel('Migration rate')
    plt.tick_params(axis='both', which='both', bottom='on', top='off', labelbottom='off', right='off', left='on', labelleft='on')

    # all user distribution figure
    ax2 = plt.subplot(gs[1])
    ax2.yaxis.set_ticks_position('left')
    ax2.xaxis.set_ticks_position('bottom')
    ax2.spines['right'].set_visible(False)
    ax2.spines['top'].set_visible(False)

    if variable == 'degree':
        plt.bar(bin_centers+bin_size/2., all_result[:-2], bin_size, edgecolor='black', color='gray')
    else:
        plt.bar(bins[:-1]+bin_size/2., all_result[:-2], bin_size, edgecolor='black', color='gray')
    plt.ylabel('Count')
    plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
    if variable == 'degree':
        if home_or_dest == 'home':
            plt.xlim([0, 75])
            xlabel = 'Network size (degree centrality) at home'
        else:
            plt.xlim([0, 23])
            xlabel = 'Network size (degree centrality) at destination'
            plt.yticks([0, .4e7, .8e7, 1.2e7, 1.6e7])
    else:
        plt.xlim([0, bins[-1]])
        if variable == 'information':
            if home_or_dest == 'home':
                xlabel = 'Unique friends of friends at home'
                plt.yticks([0, 3e4, 6e4, 9e4])
            else:
                xlabel = 'Unique friends of friends at destination'
                plt.yticks([0, 2e6, 4e6, 6e6, 8e6])
        elif variable == 'support':
            if home_or_dest == 'home':
                xlabel = 'Fraction of home contacts with common support'
                plt.yticks([0, 2e5, 4e5, 6e5])
            else:
                xlabel = 'Fraction of destination contacts with common support'
                plt.yticks([0, 2e5, 4e5, 6e5, 8e5])
        elif variable == 'cluster':
            if home_or_dest == 'home':
                xlabel = 'Clustering at home'
            else:
                xlabel = 'Clustering at destination'
                plt.yticks([0, 2e5, 4e5, 6e5, 8e5])

    plt.xlabel(xlabel)
    plt.grid(axis='y',zorder=1)
    plt.tick_params(axis='both', which='both', bottom='on', top='off', labelbottom='on', right='off', left='on', labelleft='on')
    plt.savefig(file_name, dpi=300)
    print(file_name)


def get_bin_count(users_moveto, users, d_this, variable, range_min, range_max, bin_size):
    if d_this == 'home':  # this is for calculating the home variables
        moveto = users_moveto[variable + '_home'].values.tolist()
        total = users[variable + '_home'].values.tolist()
    else:
        moveto = users_moveto[variable + '_' + str(d_this)].values.tolist()
        total = users[variable + '_' + str(d_this)].values.tolist()
    moveto_y_dest, total_y_dest = bin_num(range_min, range_max, bin_size, [moveto, total], variable, d_this)
    return moveto_y_dest, total_y_dest


def get_combine_result(input_data, range_min, range_max, bin_size, xlabel, ylabel, title, file_name, variable, home_or_dest):
    moveto_y_all = input_data[0]
    total_y_all = input_data[1]
    fix_degree_slope = input_data[2]

    moveto_y_all = np.array(moveto_y_all)
    total_y_all = np.array(total_y_all)

    if home_or_dest == 'dest':
        two = [moveto_y_all.sum(axis=0), total_y_all.sum(axis=0)]
    else:
        two = [moveto_y_all, total_y_all]

    migration_y_all_avg = np.true_divide(two[0], two[1])
    plot_migration([range_min, range_max, bin_size, migration_y_all_avg, two, xlabel, ylabel, title, file_name, fix_degree_slope, variable, home_or_dest])


def to_dest(users, districts_analyze, range_min, range_max, bin_size, xlabel, ylabel, title, file_name, variable, home_or_dest):
    moveto_y_all_dest, total_y_all_dest = [], []
    input_data = []

    v = variable_dict[variable]
    regression_all = pd.DataFrame(columns=['user', 'if_move', 'v', 'd', 'date', 'home', 'dest'])
    for d_this in districts_analyze:
        users_this = users[users['home'] != d_this]
        users_moveto = users_this[users_this.dest == d_this]
        users_remain = users_this[users_this.dest != d_this]
        moveto_y_dest, total_y_dest = get_bin_count(users_moveto, users_this, d_this, v, range_min, range_max, bin_size)
        moveto_y_all_dest.append(moveto_y_dest)
        total_y_all_dest.append(total_y_dest)

    beta, low_conf, high_conf = [], [], []
    input_data.append(moveto_y_all_dest)
    input_data.append(total_y_all_dest)
    input_data.append([beta, low_conf, high_conf])

    get_combine_result(input_data, range_min, range_max, bin_size, xlabel, ylabel, title, file_name, variable, home_or_dest)


def from_home(users, range_min, range_max, bin_size, xlabel, ylabel, title, file_name, variable, home_or_dest):
    regression_all = pd.DataFrame(columns=['user', 'if_move', 'v', 'd', 'date', 'home', 'dest'])
    users_move = users[users.type.isin([1, 2, 5])]
    users_remain = users[~(users.type.isin([1, 2, 5]))]

    v = variable_dict[variable]
    moveto_y_home, total_y_home = get_bin_count(users_move, users, 'home', v, range_min, range_max, bin_size)

    beta, low_conf, high_conf = [], [], []
    input_data = []
    input_data.append(moveto_y_home)
    input_data.append(total_y_home)
    input_data.append([beta, low_conf, high_conf])
    get_combine_result(input_data, range_min, range_max, bin_size, xlabel, ylabel, title, file_name, variable, home_or_dest)


if __name__ == '__main__':
    start_date = datetime.strptime('2006 7', '%Y %m')
    end_date = datetime.strptime('2008 6', '%Y %m')
    start_date_str = start_date.strftime('%Y%m')[2:]
    end_date_str = end_date.strftime('%Y%m')[2:]
    loop_num = relativedelta(end_date, start_date).months + 12 * relativedelta(end_date, start_date).years + 1

    date = start_date.strftime('%Y%m') + '-' + end_date.strftime('%Y%m')

    for i in xrange(loop_num):
        t2 = start_date + relativedelta(months=i)
        t2_str = t2.strftime('%Y%m')[2:]
        network_file_2 = 'data/' + t2_str + '_user_result.csv'
        users_2 = pd.read_csv(network_file_2, sep=',')
        users_2['date'] = [t2_str] * len(users_2)
        if i == 0:
            users = users_2
        else:
            users = users.append(users_2)

    users = users.replace('None', np.nan)

    migration_file = 'data/' + end_date_str + '_migration.txt'
    migration = pd.read_csv(migration_file, sep=',')[['id', 'type', 'home', 'dest']]
    dist = list(set(migration['home']) | set(migration['dest']))

    types = users[['user', 'type']].groupby('type').count()
    types_value = types['user'].values.tolist()

    users = users[users.type != 6]

    for v in ['d', 'l']:
        for i in dist:
            users[v + '_' + str(i)] = users[v + '_' + str(i)].fillna(value=0)

    variables = []
    variable_dict = {'degree': 'd', 'support': 's', 'cluster': 'c', 'information': 'l',}
    variables.append(['Degree', 0, 75, 1])
    variables.append(['Information', 0, 1001, 10])
    variables.append(['Support', 0, 1.01, 0.04])
    variables.append(['Cluster', 0, 1.01, 0.04])

    for v_all in variables:
        v, v_min, v_max, v_step = v_all
        v_lower = v.lower()
        v_max_dest = v_max
        v_max_home = v_max
        if v == 'Degree':
            v_max_dest = 23
            
        to_dest(users, dist, v_min, v_max_dest, v_step, v,
                'Migration rate', 'Migration rate vs ' + v_lower + ' at destination',
                'figure/migration_rate_' + v_lower.replace(' ','_') + '_dest.png', v_lower, 'dest')

        from_home(users, v_min, v_max_home, v_step, v,
                    'Migration rate', 'Migration rate vs ' + v_lower + ' at home',
                    'figure/migration_rate_' + v_lower.replace(' ','_') + '_home.png', v_lower, 'home')
