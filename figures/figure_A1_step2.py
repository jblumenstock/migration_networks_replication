import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns


census_dest = pd.read_csv('census_destination_simple.csv')
census_origin = pd.read_csv('census_origin.csv')
census_dest = census_dest.rename(columns={'total': 'total_census', 'proportion': 'prop_census'})
census_origin = census_origin.rename(columns={'total': 'total_census', 'prop': 'prop_census'})

cdr_origin = pd.read_csv('cdr_move_from_district_proportion_2month.csv')
cdr_dest = pd.read_csv('cdr_move_to_district_proportion_2month.csv')
cdr_origin = cdr_origin.rename(columns={'num': 'total_cdr', 'prop': 'prop_cdr'})
cdr_dest = cdr_dest.rename(columns={'num': 'total_cdr', 'prop': 'prop_cdr'})

compare_dest = census_dest.merge(cdr_dest, on='district', how='inner')
compare_origin = census_origin.merge(cdr_origin, on='district', how='inner')

compare_dest = compare_dest.sort_values(by='total_cdr', ascending=False)
compare_origin = compare_origin.sort_values(by='total_cdr', ascending=False)

sns.set()

mpl.rcParams['axes.labelcolor'] = 'k'
mpl.rcParams['xtick.color'] = 'k'
mpl.rcParams['ytick.color'] = 'k'

width = 3.487 *3
height = 3.487

fig, ax = plt.subplots()
ax.set_facecolor('#E5E5E5')
fig.subplots_adjust(left=.18, bottom=.22, right=.97, top=.97)
fig.set_size_inches(width, height)
plt.bar(np.arange(len(compare_dest))-.25, compare_dest['total_cdr'], width=.35, label='CDR', color='#E24A33', edgecolor='#E24A33')
plt.ylabel('Number of migrants from CDR', color='#E24A33')
ax.tick_params(axis='y', labelcolor='#E24A33')
plt.xlim(-0.7, len(compare_dest)-.3)
plt.ylim(0, 80000)
plt.xticks(np.arange(len(compare_dest)), compare_dest.district, rotation=90)

ax2 = ax.twinx() 
ax2.grid(False)
plt.bar(np.arange(len(compare_dest))+.25, compare_dest['total_census'], width=.35, label='Census', color='steelblue', edgecolor='steelblue')
ax2.set_ylabel('Number of migrants from census', color='steelblue') 
ax2.tick_params(axis='y', labelcolor='steelblue')
plt.ylim(0, 223500)
plt.savefig('figure/migration_number_validation_destination_ordered_by_cdr.png', dpi=300, bbox_inches="tight")


mpl.rcParams['axes.labelcolor'] = 'k'
mpl.rcParams['xtick.color'] = 'k'
mpl.rcParams['ytick.color'] = 'k'
width = 3.487 *3
height = 3.487

fig, ax = plt.subplots()
ax.set_facecolor('#E5E5E5')

fig.subplots_adjust(left=.18, bottom=.22, right=.97, top=.97)
fig.set_size_inches(width, height)
plt.bar(np.arange(len(compare_origin))-.25, compare_origin['total_cdr'], width=.35, label='CDR', color='#E24A33', edgecolor='#E24A33')
plt.ylabel('Number of migrants from CDR', color='#E24A33')
ax.tick_params(axis='y', labelcolor='#E24A33')
plt.xlim(-0.7, len(compare_origin)-.3)
plt.ylim(0, 80000)
plt.xticks(np.arange(len(compare_origin)), compare_origin.district, rotation=90)

ax2 = ax.twinx()
ax2.grid(False)
plt.bar(np.arange(len(compare_origin))+.25, compare_origin['total_census'], width=.35, label='Census', color='steelblue', edgecolor='steelblue')
ax2.set_ylabel('Number of migrants from census', color='steelblue')
ax2.tick_params(axis='y', labelcolor='steelblue')
plt.ylim(0, 223500)
plt.savefig('figure/migration_number_validation_origin_ordered_by_cdr.png', dpi=300, bbox_inches="tight")