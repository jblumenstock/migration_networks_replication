import pandas as pd
import numpy as np
import matplotlib as mpl
mpl.rcParams['axes.unicode_minus'] = False
mpl.use('Agg')
import matplotlib.pyplot as plt

df = pd.read_csv('data/dest_home_d_s_l.csv')
df_d10 = df[df.d_dest == 10]

migrant = df_d10[df_d10.if_move == 1]
remain = df_d10[df_d10.if_move == 0]

h1, b = np.histogram(migrant.l_dest, bins=np.arange(0, 501, 25))
h1 = h1 / float(sum(h1))
h2, b = np.histogram(remain.l_dest, bins=np.arange(0, 501, 25))
h2 = h2 / float(sum(h2))

fig, ax = plt.subplots()
fig.subplots_adjust(left=.1, bottom=.1, right=.98, top=.97)
plt.bar(b[:-1]+12.5, h1, width=25, color='b', alpha=.5, label='migrant')
plt.bar(b[:-1]+12.5, h2, width=25, color='g', alpha=.5, label='non-migrant')
plt.legend()
plt.xlabel('Unique friends of friends in destination')
plt.ylabel('Proportion')
plt.savefig('figure/infor_10.png', dpi=300)