import seaborn as sns


params = {
    "pgf.texsystem": "pdflatex",
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
    'legend.fancybox': False
}
mpl.rcParams.update(params)
mpl.rcParams['font.family'] = 'serif'
mpl.rcParams['font.serif'] = ['Times']
plt.rc('text', usetex=True)
plt.rc('axes', axisbelow=True)
plt.style.use('seaborn-paper')
width = 3.487
height = width


def get_utility(p):
    pi_home_i_this, pi_dest_i_this, pi_home_c_this, pi_dest_c_this, \
        alpha_home_this, alpha_dest_this, \
        lambda_home_this, rho_this, t_this, diffusion_p_this = p

    all_ = all_add_feature.copy()
    # home
    all_['slink_home_multiply'] = alpha_home_this * all_['slink_home']
    all_['uc_home'] = all_['d_home'] + all_['slink_home_multiply']
    all_['uc_home_multiply'] = pi_home_c_this * all_['uc_home']
    all_['ui_home'] = all_['ui_home_'+str(lambda_home_this)] / (0.016 ** 2)
    all_['ui_home_multiply'] = pi_home_i_this * all_['ui_home']
    all_['u_home'] = all_['uc_home_multiply'] + all_['ui_home_multiply']
    # dest
    all_['slink_dest_multiply'] = alpha_dest_this * all_['slink_dest']
    all_['uc_dest'] = all_['d_dest'] + all_['slink_dest_multiply']
    all_['uc_dest_multiply'] = pi_dest_c_this * all_['uc_dest']
    all_['ui_dest'] = all_['ui_dest_'+str(lambda_home_this)] / (0.016 ** 2)
    all_['ui_dest_multiply'] = pi_dest_i_this * all_['ui_dest']
    all_['u_dest'] = all_['uc_dest_multiply'] + all_['ui_dest_multiply']

    all_['u_home_multiply'] = rho_this * all_['u_home']
    all_['u_diff'] = all_['u_dest'] - all_['u_home_multiply']
    all_['move_result'] =\
        all_.apply(lambda x: move_or_not(x['u_diff'], 0), axis=1)

    remain = all_[all_['if_migrant'] == 0]
    migrant = all_[all_['if_migrant'] == 1]
    wrong_num_remain = remain[remain['move_result'] == 1].shape[0]
    right_num_remain = remain[remain['move_result'] == 0].shape[0]

    wrong_num_migrant = migrant[migrant['move_result'] == 0].shape[0]
    right_num_migrant = migrant[migrant['move_result'] == 1].shape[0]
    wrong_total = wrong_num_remain + wrong_num_migrant
    right_total = right_num_remain + right_num_migrant

    return [[wrong_total, wrong_num_remain, wrong_num_migrant,
            right_total, right_num_remain, right_num_migrant],
            remain, migrant, all_]

def get_coop_u_bin(x):
    bins = np.arange(0, 451, 10)
    for i in range(len(bins)-1):
        left = bins[i]
        right = bins[i+1]
        if x >= left and x < right:
            return i


# optimal parameters
para_test = [5.0, 20.0, 1.0, 1.0, 1.0, 5.0, 0.5, 1.0, 3.0, 0.016]
acc, remain, migrant, all_ = get_utility(para_test)

combine1 = remain.copy()
combine1['if_migrant'] = 'migrant'
combine2 = migrant.copy()
combine2['if_migrant'] = 'non-migrant'
combine3 = combine1.append(combine2)
combine3['coop_bin'] = combine3.apply(lambda x: get_coop_u_bin(x['uc_dest_multiply']), axis=1)

fig, ax = plt.subplots()
fig.subplots_adjust(left=.16, bottom=.14, right=.97, top=.97)
ax.yaxis.set_ticks_position('left')
ax.xaxis.set_ticks_position('bottom')
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
plt.grid(axis='y',zorder=1)
fig.set_size_inches(width, height)

medianprops = dict(color='k')
result_test = []
for i in range(17):
    result_test.append(combine3[combine3.coop_bin == i]['ui_dest_multiply'])
x_loc = np.arange(.5, 17, 1)
plt.boxplot(result_test, 0, '', medianprops=medianprops, positions=x_loc)
xlabel_loc = np.arange(18)
x_real = [i*10 for i in xlabel_loc]
plt.plot(xlabel_loc, x_real, linestyle='--', c='gray')
plt.xticks(xlabel_loc, x_real)
plt.yticks(x_real, x_real)
plt.xlim(0,16)
plt.ylim(0,160)
plt.xlabel('Total utility from cooperation capital (in destination)')
plt.ylabel('Total utility from information capital (in destination)')
plt.savefig('infor_coop_dest_combined_boxplot.png', dpi=300)
