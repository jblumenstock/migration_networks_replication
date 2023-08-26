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
width = 3.487
height = width / 1.618

plt.style.use('seaborn-paper')

def plot_box(result, v):
    fig, ax = plt.subplots()
    fig.subplots_adjust(left=.16, bottom=.20, right=.97, top=.97)
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    plt.grid(axis='y',zorder=5)
    fig.set_size_inches(width, height)
    medianprops = dict(color='k')

    plt.boxplot(result, 0, 'k.', medianprops=medianprops)
    if v == 'pi_i_home':
        plt.xlabel(r'$\pi^{I,H}$')
    elif v == 'pi_i_dest':
        plt.xlabel(r'$\pi^{I,D}$')
    elif v == 'pi_c_dest':
        plt.xlabel(r'$\pi^{C,D}$')
    elif v == 'lambda':
        plt.xlabel(r'$\lambda$')
    elif v == 'alpha_home':
        plt.xlabel(r'$\alpha^{H}$')
    elif v == 'alpha_dest':
        plt.xlabel(r'$\alpha^{D}$')
    elif v == 'q':
        plt.xlabel(r'$q$')
    elif v == 'tau':
        plt.xlabel(r'$\tau$')

    plt.xticks(range(1, len(vs[v]) + 1), [str(x) for x in vs[v]])
    plt.ylabel('Accuracy')
    plt.savefig('figure/' + version + '_' + v + '_boxplot.png', dpi=300)


vs = {'pi_i_home': pi_i_home,
      'pi_i_dest': pi_i_dest,
      'pi_c_dest': pi_c_dest,
      'alpha_home': alpha_home,
      'alpha_dest': alpha_dest,
      'lambda': lambda_home,
      'tau': tao,
      }

v_idx = {'pi_i_home': pi_i_home_idx,
         'pi_i_dest': pi_i_dest_idx,
         'pi_c_dest': pi_c_dest_idx,
         'alpha_home': alpha_home_idx,
         'alpha_dest': alpha_dest_idx,
         'lambda': lambda_home_idx,
         'tau': tao_idx,
         }

# boxplot
for v in vs:
    result_2 = []
    for i, lambda_this in enumerate(vs[v]):
        idx = v_idx[v][i]
        result_this = result[idx,]
        r = np.true_divide((result_this[:,5] + result_this[:,4]),
                           (result_this[:,5] + result_this[:,4] + 
                            result_this[:,2] + result_this[:,1]))
        result_2.append(list(r[r >= accuracy_top2]))
    plot_box(result_2, v)
