import pandas as pd
import numpy as np
import time
import matplotlib as mpl
from datetime import datetime
from dateutil.relativedelta import relativedelta
mpl.rcParams['axes.unicode_minus'] = False
mpl.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import gridspec


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
    network_file_2 = 'data/' + t_str + '_user_result.csv'
    users_this = pd.read_csv(network_file_2, sep=',')
    users_this['date'] = [t_str] * len(users_this)
    networks[t_str] = users_this
    print(x)

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
        print(t)

    users = users.replace('None', np.nan)
    users = users.fillna(0)
    del users['type']

    samples = migrant.copy()
    samples = samples.append(remain)

    samples['home_real'] = samples['home']
    samples['dest_real'] = samples['dest']

    user_select = users.merge(samples, left_on='user', right_on='id', how='inner')

    for v in ['s_', 'l_', 'd_']:
        user_select[v + 'dest_real'] = user_select.apply(lambda x: x[v + str(x['dest_real'])], axis=1)
        user_select[v + 'home_real'] = user_select.apply(lambda x: x[v + str(x['home_real'])], axis=1)
    
    user_select = user_select[user_select['d_dest_real'] > 1]
    user_select = user_select[user_select['d_home_real'] > 1]
    user_migrant = user_select[user_select['user'].isin(migrant['id'])][['user',
                                                                         'date',
                                                                         'type', 
                                                                         's_home_real',
                                                                         's_dest_real',
                                                                         'l_home_real',
                                                                         'l_dest_real'
                                                                         ]]
    if i == 0:
        user_migrant_all = user_migrant
    else:
        user_migrant_all.append(user_migrant)
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


migrant_d = user_migrant_all[user_migrant_all.type.isin([1,2,5])]
migrant_d = migrant_d.groupby('date').agg({'s_home_real': ['mean', 'std'],
                                           's_dest_real': ['mean', 'std'],
                                           'l_home_real': ['mean', 'std'],
                                           'l_dest_real': ['mean', 'std']
                                           })


fig, ax = plt.subplots()
fig.subplots_adjust(left=.1, bottom=.1, right=.97, top=.97)
plt.plot(range(len(migrant_d)), migrant_d['s_home_real']['mean'], label="Contacts in home district")
plt.plot(range(len(migrant_d)), migrant_d['s_dest_real']['mean'], label='Contacts in destination district')
plt.xlabel('Month')
plt.ylabel('Percent of supported friends in location')
plt.xlim(0, len(migrant_d) - 1)
plt.ylim(0, 0.6)
plt.xticks(range(len(migrant_d)), xticks)
leg = plt.legend(loc=2, fancybox=False)
leg.get_frame().set_edgecolor('k')
plt.axvline(x=12, c='k', ls='--')
plt.savefig('figure/support_change.png', dpi=300)


fig, ax = plt.subplots()
fig.subplots_adjust(left=.1, bottom=.1, right=.97, top=.97)
plt.plot(range(len(migrant_d)), migrant_d['l_home_real']['mean'], label="Contacts in home district")
plt.plot(range(len(migrant_d)), migrant_d['l_dest_real']['mean'], label='Contacts in destination district')
plt.xlabel('Month')
plt.ylabel('Number of friends of friends in location')
plt.xlim(0, len(migrant_d) - 1)
plt.ylim(0, 400)
plt.xticks(range(len(migrant_d)), xticks)
leg = plt.legend(loc=2, fancybox=False)
leg.get_frame().set_edgecolor('k')
plt.axvline(x=12, c='k', ls='--')
plt.savefig('figure/information_change.png', dpi=300)
