import pandas as pd
import numpy as np
import time
import matplotlib as mpl
from datetime import datetime
from dateutil.relativedelta import relativedelta
mpl.rcParams['axes.unicode_minus'] = False
mpl.use('Agg')
import matplotlib.pyplot as plt


start_date = datetime.strptime('2007 2', '%Y %m')
start_date_str = start_date.strftime('%Y%m')[2:]
end_date = datetime.strptime('2007 7', '%Y %m')
end_date_str = end_date.strftime('%Y%m')[2:]
loop_num = relativedelta(end_date, start_date).months + 12 * relativedelta(end_date, start_date).years + 1

# read network
networks = {}
for x in range(24):
    t = datetime.strptime('2006 2', '%Y %m') + relativedelta(months=x)
    t_str = t.strftime('%Y%m')[2:]
    network_file = 'data/' + t_str + '_user_result.csv'
    users_this = pd.read_csv(network_file, sep=',')
    users_this['date'] = t_str
    networks[t_str] = users_this

migration_home = []
migration_dest = []
migration_other = []
remain_home = []
remain_other = []
for i in range(loop_num):
    t0 = time.time()
    study_date = start_date + relativedelta(months=i)
    study_date_str = study_date.strftime('%Y%m')[2:]

    migration_file = 'data/' + study_date_str + '_migration.txt'
    migration = pd.read_csv(migration_file, sep=',')[['id', 'type', 'home', 'dest']]

    migrant_raw = migration[migration['type'].isin([1, 2, 5])]
    remain_raw = migration[migration['type'].isin([3, 4])]

    N = migrant_raw.shape[0]
    np.random.seed(123)
    migrant = migrant_raw.copy()
    remain = remain_raw.sample(N)

    for x in range(19):
        t = study_date + relativedelta(months=(x - 12))
        t_str = t.strftime('%Y%m')[2:]
        if x == 0:
            users = networks[t_str]
            users['date'] = x
        else:
            n_ = networks[t_str]
            n_['date'] = x
            users = users.append(n_)

    users = users.replace('None', np.nan)
    users = users.fillna(0)
    del users['type']
    print('user result read')
    print(users.shape)

    samples = migrant.copy()
    samples = samples.append(remain)

    samples['home_real'] = samples['home']
    samples['dest_real'] = samples['dest']

    user_select = users.merge(samples, left_on='user', right_on='id', how='inner')

    for v in ['d_percent_', 'd_', 'conn_weight_']:
        user_select[v + 'dest_real'] = user_select.apply(lambda x: x[v + str(x['dest_real'])], axis=1)
        user_select[v + 'home_real'] = user_select.apply(lambda x: x[v + str(x['home_real'])], axis=1)
        user_select[v + 'kigali'] = user_select.apply(lambda x: x[v + '11'], axis=1)

    user_select['conn_weight_all'] = user_select["conn_weight_11"] + user_select["conn_weight_54"] + user_select["conn_weight_45"] + user_select["conn_weight_57"] + user_select["conn_weight_36"] + user_select["conn_weight_56"] + user_select["conn_weight_43"] + user_select["conn_weight_26"] + user_select["conn_weight_53"] + user_select["conn_weight_31"] + user_select["conn_weight_55"] + user_select["conn_weight_33"] + user_select["conn_weight_24"] + user_select["conn_weight_22"] + user_select["conn_weight_27"] + user_select["conn_weight_51"] + user_select["conn_weight_28"] + user_select["conn_weight_52"] + user_select["conn_weight_41"] + user_select["conn_weight_44"] + user_select["conn_weight_35"] + user_select["conn_weight_21"] + user_select["conn_weight_34"] + user_select["conn_weight_37"] + user_select["conn_weight_25"]

    user_migrant = user_select[user_select['user'].isin(migrant['id'])][['user',
                                                                         'date',
                                                                         'type', 
                                                                         'd_percent_home_real',
                                                                         'd_percent_dest_real', 
                                                                         'd_home_real',
                                                                         'd_dest_real',
                                                                         'd_all',
                                                                         'conn_weight_home_real',
                                                                         'conn_weight_dest_real',
                                                                         'conn_weight_all'
                                                                         ]]
    user_remain = user_select[user_select['user'].isin(remain['id'])][['user',
                                                                         'date',
                                                                         'type', 
                                                                         'd_percent_home_real',
                                                                         'd_percent_dest_real', 
                                                                         'd_home_real',
                                                                         'd_dest_real',
                                                                         'd_all',
                                                                         'conn_weight_home_real',
                                                                         'conn_weight_dest_real',
                                                                         'conn_weight_all'
                                                                         ]]
    if i == 0:
        user_migrant_all = user_migrant
        user_remain_all = user_remain
    else:
        user_migrant_all.append(user_migrant)
        user_remain_all.append(user_remain)
    t1 = time.time()
    print(i)
    print(t1 - t0)


xticks = []
for i in range(19):
    if i - 12 < 0:
        t2 = 't' + str(i - 12)
    elif i - 12 == 0:
        t2 = 't'
    else:
        t2 = 't+' + str(i - 12)
    xticks.append(t2)


# all types of migrants'
migrant_d = user_migrant_all[user_migrant_all.type.isin([1,2,5])]
migrant_d = migrant_d.groupby('date').agg({'d_percent_home_real': ['mean', 'std'],
                                           'd_percent_dest_real': ['mean', 'std'],
                                           'd_home_real': ['mean', 'std'],
                                           'd_dest_real': ['mean', 'std'],
                                           'd_all': ['mean', 'std'],
                                           'conn_weight_home_real': ['mean', 'std'],
                                           'conn_weight_dest_real': ['mean', 'std'],
                                           'conn_weight_all': ['mean', 'std']})
migrant_d['d_percent_other'] = 1 - migrant_d['d_percent_home_real']['mean'] - \
    migrant_d['d_percent_dest_real']['mean']
migrant_d['d_other'] = migrant_d['d_all']['mean'] - migrant_d['d_home_real']['mean'] - \
    migrant_d['d_dest_real']['mean']
migrant_d['conn_weight_other'] = migrant_d['conn_weight_all']['mean'] - migrant_d['conn_weight_home_real']['mean'] - \
    migrant_d['conn_weight_dest_real']['mean']

remain_d = user_remain_all.groupby('date').agg({'d_percent_home_real': ['mean', 'std'],
                                                'd_percent_dest_real': ['mean', 'std'],
                                                'd_home_real': ['mean', 'std'],
                                                'd_dest_real': ['mean', 'std'],
                                                'd_all': ['mean', 'std'],
                                                'conn_weight_home_real': ['mean', 'std'],
                                                'conn_weight_dest_real': ['mean', 'std'],
                                                'conn_weight_all': ['mean', 'std']})
remain_d['d_percent_other'] = 1 - remain_d['d_percent_home_real']['mean']
remain_d['d_other'] = remain_d['d_all']['mean'] - remain_d['d_home_real']['mean']
remain_d['conn_weight_other'] = remain_d['conn_weight_all']['mean'] - remain_d['conn_weight_home_real']['mean']


# Figure 4: Changes in network structure over time
# (a) migrants
fig, ax = plt.subplots()
fig.subplots_adjust(left=.1, bottom=.1, right=.97, top=.97)
plt.plot(range(len(migrant_d)), migrant_d['d_percent_home_real']['mean'], label="Contacts in home district")
plt.plot(range(len(migrant_d)), migrant_d['d_percent_dest_real']['mean'], label="Contacts in destination district")
plt.plot(range(len(migrant_d)), migrant_d['d_percent_other'], label="Contacts in other districts")
plt.ylim(ymin=0)
plt.xlabel('Month')
plt.ylabel('Percent of contacts in location')
plt.xlim(0, len(migrant_d) - 1)
plt.xticks(range(len(migrant_d)), xticks)
leg = plt.legend(loc=4, fancybox=False, framealpha=1)
leg.get_frame().set_edgecolor('k')
plt.axvline(x=12, c='k', ls='--')
plt.savefig('degree_percentage_change_migrant.png', dpi=300)


# (b) non-migrants
green_color = '#339e34'
fig, ax = plt.subplots()
fig.subplots_adjust(left=.1, bottom=.1, right=.97, top=.97)
plt.plot(range(len(remain_d)), remain_d['d_percent_home_real']['mean'], label='Contacts in home district')
plt.plot(range(len(remain_d)), remain_d['d_percent_other'], c=green_color, label='Contacts in other districts')
leg = plt.legend(loc=2, fancybox=False)
leg.get_frame().set_edgecolor('k')
plt.xlabel('Month')
plt.ylabel('Percent of contacts in location')
plt.xlim(0, len(migrant_d) - 1)
plt.xticks(range(len(migrant_d)), xticks)
plt.axvline(x=12, c='k', ls='--')
plt.ylim(0.2, 0.9)
plt.savefig('degree_percentage_change_non-migrant.png', dpi=300)


# Figure A2: Changes in number of contacts over time
# (a) migrants
fig, ax = plt.subplots()
fig.subplots_adjust(left=.1, bottom=.1, right=.97, top=.97)
plt.plot(range(len(migrant_d)), migrant_d['d_home_real']['mean'], label="Contacts in home district")
plt.plot(range(len(migrant_d)), migrant_d['d_dest_real']['mean'], label='Contacts in destination district')
plt.plot(range(len(migrant_d)), migrant_d['d_other'], label="Contacts in other districts")
plt.xlabel('Month')
plt.ylabel('Number of contacts in location')
plt.xlim(0, len(migrant_d) - 1)
plt.xticks(range(len(migrant_d)), xticks)
leg = plt.legend(loc=2, fancybox=False)
leg.get_frame().set_edgecolor('k')
plt.axvline(x=12, c='k', ls='--')
plt.savefig('degree_change_migrant.png', dpi=300)

# (b) non-migrants
fig, ax = plt.subplots()
fig.subplots_adjust(left=.1, bottom=.1, right=.97, top=.97)
plt.plot(range(len(remain_d)), remain_d['d_home_real']['mean'], label='Contacts in home district')
plt.plot(range(len(remain_d)), remain_d['d_other'], c=green_color, label='Contacts in other districts')
leg = plt.legend(loc=2, fancybox=False)
leg.get_frame().set_edgecolor('k')
plt.xlabel('Month')
plt.ylabel('Number of contacts in location')
plt.xlim(0, len(migrant_d) - 1)
plt.xticks(range(len(migrant_d)), xticks)
plt.axvline(x=12, c='k', ls='--')
plt.savefig('degree_change_non-migrant.png', dpi=300)


# Figure A3: Changes in number of calls over time
# (a) migrants
fig, ax = plt.subplots()
fig.subplots_adjust(left=.1, bottom=.1, right=.97, top=.97)
plt.plot(range(len(migrant_d)), migrant_d['conn_weight_home_real']['mean'], label="Calls to home district")
plt.plot(range(len(migrant_d)), migrant_d['conn_weight_dest_real']['mean'], label='Calls to destination district')
plt.plot(range(len(migrant_d)), migrant_d['conn_weight_other'], label="Calls to other districts")
leg = plt.legend(loc=2, fancybox=False)
leg.get_frame().set_edgecolor('k')
plt.xlabel('Month')
plt.ylabel('Number of calls to location')
plt.xlim(0, len(migrant_d) - 1)
plt.xticks(range(len(migrant_d)), xticks)
plt.axvline(x=12, c='k', ls='--')
plt.savefig('call_change_migrant.png', dpi=300)

# (b) non-migrants
fig, ax = plt.subplots()
fig.subplots_adjust(left=.1, bottom=.1, right=.97, top=.97)
plt.plot(range(len(remain_d)), remain_d['conn_weight_home_real']['mean'], label='Calls to home district')
plt.plot(range(len(remain_d)), remain_d['conn_weight_other'], c=green_color, label='Calls to other districts')
leg = plt.legend(loc=2, fancybox=False)
leg.get_frame().set_edgecolor('k')
plt.xlabel('Month')
plt.ylabel('Number of calls to location')
plt.xlim(0, len(migrant_d) - 1)
plt.xticks(range(len(migrant_d)), xticks)
plt.axvline(x=12, c='k', ls='--')
plt.savefig('call_change_non-migrant.png', dpi=300)
