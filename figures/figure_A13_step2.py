import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns


census_dest = pd.read_csv('census_destination_simple.csv')
census_dest = census_dest.rename(columns={'total': 'total_census', 'proportion': 'prop_census'})

cdr_origin = pd.read_csv('cdr_move_from_district_proportion.csv')
dist_dict = dict(zip(cdr_origin['home'], cdr_origin['district']))

cdr_dest_6month = pd.read_csv('cdr_move_to_district_proportion_6month.csv')
cdr_dest_6month = cdr_dest_6month.rename(columns={'num': 'total_cdr'})
cdr_dest_6month = cdr_dest_6month[cdr_dest_6month.dest.isin(dist_dict)]
cdr_dest_6month['district'] = cdr_dest_6month.apply(lambda x: dist_dict[x['dest']], axis=1)

compare_dest_6month = census_dest.merge(cdr_dest_6month, on='district', how='inner')
compare_dest_6month = compare_dest_6month.sort_values(by='total_census', ascending=False)


cdr_dest_12month = pd.read_csv('cdr_move_to_district_proportion_12month.csv')
cdr_dest_12month = cdr_dest_12month.rename(columns={'num': 'total_cdr'})
cdr_dest_12month = cdr_dest_12month[cdr_dest_12month.dest.isin(dist_dict)]
cdr_dest_12month['district'] = cdr_dest_12month.apply(lambda x: dist_dict[x['dest']], axis=1)

compare_dest_12month = census_dest.merge(cdr_dest_12month, on='district', how='inner')
compare_dest_12month = compare_dest_12month.sort_values(by='total_census', ascending=False)


sns.set()

COLOR = 'k'
mpl.rcParams['axes.labelcolor'] = COLOR
mpl.rcParams['xtick.color'] = COLOR
mpl.rcParams['ytick.color'] = COLOR
width = 3.487 *3
height = 3.487

fig, ax = plt.subplots()
ax.set_facecolor('#E5E5E5')

fig.subplots_adjust(left=.18, bottom=.22, right=.97, top=.97)

fig.set_size_inches(width, height)
plt.bar(np.arange(len(compare_dest_6month))-.25, compare_dest_6month['total_cdr'], width=.35, label='CDR', color='#E24A33', edgecolor='#E24A33')
plt.ylabel('Number of migrants from CDR', color='#E24A33')
ax.tick_params(axis='y', labelcolor='#E24A33')
plt.xlim(-0.7, len(compare_dest_6month)-.3)
plt.ylim(0, 10000)
plt.xticks(np.arange(len(compare_dest_6month)), compare_dest_6month.district, rotation=90)

ax2 = ax.twinx()
ax2.grid(False)

plt.bar(np.arange(len(compare_dest_6month))+.25, compare_dest_6month['total_census'], width=.35, label='Census', color='steelblue', edgecolor='steelblue')
ax2.set_ylabel('Number of migrants from census', color='steelblue')
ax2.tick_params(axis='y', labelcolor='steelblue')
plt.ylim(0, 223500)
plt.savefig('figure/migration_number_validation_destination_ordered_by_census_6month.png', dpi=300, bbox_inches="tight")


sns.set()

COLOR = 'k'
mpl.rcParams['axes.labelcolor'] = COLOR
mpl.rcParams['xtick.color'] = COLOR
mpl.rcParams['ytick.color'] = COLOR
width = 3.487 *3
height =3.487

fig, ax = plt.subplots()
ax.set_facecolor('#E5E5E5')

fig.subplots_adjust(left=.18, bottom=.22, right=.97, top=.97)

fig.set_size_inches(width, height)
plt.bar(np.arange(len(compare_dest_12month))-.25, compare_dest_12month['total_cdr'], width=.35, label='CDR', color='#E24A33', edgecolor='#E24A33')
plt.ylabel('Number of migrants from CDR', color='#E24A33')
ax.tick_params(axis='y', labelcolor='#E24A33')
plt.xlim(-0.7, len(compare_dest_12month)-.3)
plt.ylim(0, 10000)
plt.xticks(np.arange(len(compare_dest_12month)), compare_dest_12month.district, rotation=90)

ax2 = ax.twinx()
ax2.grid(False)

plt.bar(np.arange(len(compare_dest_12month))+.25, compare_dest_12month['total_census'], width=.35, label='Census', color='steelblue', edgecolor='steelblue')
ax2.set_ylabel('Number of migrants from census', color='steelblue')
ax2.tick_params(axis='y', labelcolor='steelblue')
plt.ylim(0, 223500)
plt.savefig('figure/migration_number_validation_destination_ordered_by_census_12month.png', dpi=300, bbox_inches="tight")




