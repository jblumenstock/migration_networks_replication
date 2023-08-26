import pandas as pd
import numpy as np
import random
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
import matplotlib as mpl
mpl.rcParams['axes.unicode_minus'] = False
mpl.use('Agg')
import matplotlib.pyplot as plt
from pandarallel import pandarallel

random.seed(0)

pandarallel.initialize(nb_workers=10)


def get_user_order(user_1, user_2):
    if user_1 > user_2:
        return [user_2, user_1]
    elif user_1 == user_2:
        return ['None', 'None']
    else:
        return [user_1, user_2]


def get_network(network_date):
    conn_base = pd.read_csv('data/' + network_date + '_call.txt', delimiter='|', header=None)
    conn_base = conn_base.rename(columns={0: 'user_1', 1: 'user_2'})
    print(conn_base.shape)
    conn_order = conn_base.parallel_apply(lambda x: get_user_order(x['user_1'], x['user_2']), axis=1, result_type='expand')
    conn_order = conn_order.rename(columns={0: 'user_1', 1: 'user_2'})
    conn_order = conn_order[conn_order.user_1 != 'None']
    conn_num = conn_order.groupby(['user_1', 'user_2']).size().reset_index(name='conn_num')

    d1 = conn_num.groupby('user_1').size().reset_index(name='degree')
    d1 = d1.rename(columns={'user_1': 'user'})
    d2 = conn_num.groupby('user_2').size().reset_index(name='degree')
    d2 = d2.rename(columns={'user_2': 'user'})
    degree_df = pd.concat([d1, d2])
    degree_user = degree_df.groupby('user').degree.sum().reset_index()
    degree_sort = sorted(degree_user.degree.tolist())
    degree_95 = degree_sort[int(len(degree_sort) * 0.95)]
    user_not_outlier = degree_user[degree_user.degree < degree_95]['user'].tolist()
    conn_filtered = conn_num[(conn_num.user_1.isin(user_not_outlier)) & (conn_num.user_2.isin(user_not_outlier))]
    print(conn_filtered.shape)
    print('remove outliers done')

    users_with_modal_tower_base = pd.read_csv('data/' + network_date + '_modal_district.txt', delimiter='\t', header=None)
    users_with_modal_tower_base = users_with_modal_tower_base.rename(columns={0: 'user', 1: 'home'})
    users_loc_base = users_with_modal_tower_base
    users_loc_base['user'] = users_loc_base.parallel_apply(lambda x: x['user'].split('_')[0], axis=1)

    conn_filtered = conn_filtered.merge(users_loc_base, left_on='user_1', right_on='user', how='inner')
    conn_filtered = conn_filtered.rename(columns={'home': 'user_1_home'})
    conn_filtered = conn_filtered.merge(users_loc_base, left_on='user_2', right_on='user', how='inner')
    conn_filtered = conn_filtered.rename(columns={'home': 'user_2_home'})
    conn_filtered_bidir = conn_filtered.copy()

    tmp = conn_filtered.copy()
    tmp = tmp.rename(columns={'user_1': 'u2', 'user_2': 'u1',
                'user_1_home': 'u2_home', 'user_2_home': 'u1_home'})
    tmp = tmp.rename(columns={'u2': 'user_2', 'u1': 'user_1',
                'u2_home': 'user_2_home', 'u1_home': 'user_1_home'})
    conn_filtered_bidir = conn_filtered_bidir.append(tmp)
    del tmp
    conn_filtered_bidir = conn_filtered_bidir[['user_1', 'user_2', 'conn_num', 'user_1_home', 'user_2_home']]
    print('conn_filtered_bidir is done')

    user_result = pd.DataFrame(columns=['user', 'home'])
    user_result['user'] = users_loc_base['user']
    user_result['home'] = users_loc_base['home']
    users_with_conn = conn_filtered_bidir['user_1'].append(conn_filtered_bidir['user_2'])
    users_with_conn_uniq = users_with_conn.unique()
    user_result_final = user_result[user_result.user.isin(users_with_conn_uniq)]

    return conn_filtered_bidir, user_result_final


def get_varaibles(date, fixed_network, result_df):
    this_network, _ = get_network(date)
    migration = pd.read_csv('data/0801_migration.txt', sep=',')[['id', 'type', 'home', 'dest']]
    dist = list(set(migration['home']) | set(migration['dest']))

    for _i in dist:
        edge = fixed_network[fixed_network.user_2_home == _i]
        fixed_network_still_exist = edge[edge.user_2.isin(this_network.user_1.unique())]
        degree_i = fixed_network_still_exist.groupby('user_1').size().reset_index(name='degree')
        degree_i = degree_i.rename(columns={'user_1': 'user'})
        edge_copy = this_network[this_network.user_2_home == _i].copy()
        edge_copy = edge_copy.rename(columns={'user_1': 'user_2', 'user_2': 'user_3'})
        three_node = edge[['user_1', 'user_2']].merge(edge_copy[['user_2', 'user_3']], on='user_2', how='inner')
        three_node = three_node[three_node.user_1 != three_node.user_3]
        new_edge = three_node[['user_1', 'user_3']].drop_duplicates()

        information_edge = pd.merge(new_edge, edge, left_on=['user_1', 'user_3'], right_on=['user_1', 'user_2'], how='left', indicator=True)
        information_edge = information_edge[information_edge['_merge'] == "left_only"]
        information_edge.drop('_merge', axis=1, inplace=True)
        information_edge = information_edge[['user_1', 'user_3']].drop_duplicates()
        information_i = information_edge.groupby('user_1').size().reset_index(name='l_' + str(_i))
        information_i = information_i.rename(columns={'user_1': 'user'})
        
        supported_edge = edge[['user_1', 'user_2']].merge(new_edge, left_on=['user_1', 'user_2'], right_on=['user_1', 'user_3'], how='inner')
        supported_edge = supported_edge[['user_1', 'user_2']].drop_duplicates()
        support_i = supported_edge.groupby('user_1').size().reset_index(name='support_n')
        support_i = support_i.rename(columns={'user_1': 'user'})
        support_i = support_i.merge(degree_i, on='user', how='right')
        support_i = support_i.fillna(0)
        support_i['support'] = support_i['support_n'] / degree_i['degree']
        # drop column support_n
        support_i = support_i.drop(columns=['support_n'])
        support_i = support_i.rename(columns={'support': 's_' + str(_i), 'degree': 'd_' + str(_i)})
        
        user_result_this = result_df[['user']].copy()
        user_result_this = user_result_this[['user']].merge(information_i, on='user', how='left')
        user_result_this = user_result_this.merge(support_i, on='user', how='left')
        result_df = result_df.merge(user_result_this, on='user', how='inner')
        print(_i)

    result_df = result_df.fillna(0)
    return result_df

start_date = datetime.strptime('2007 2', '%Y %m')
start_date_str = start_date.strftime('%Y%m')[2:]
end_date = datetime.strptime('2007 7', '%Y %m')
end_date_str = end_date.strftime('%Y%m')[2:]
loop_num = relativedelta(end_date, start_date).months + 12 * relativedelta(end_date, start_date).years + 1

migration_home = []
migration_dest = []
migration_other = []
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

    network_date = start_date + relativedelta(months=i-12)
    network_date = network_date.strftime('%Y%m')[2:]
    fixed_network, result_df = get_network(network_date)

    for x in range(19):
        t = study_date + relativedelta(months=(x - 12))
        t_str = t.strftime('%Y%m')[2:]
        v = get_varaibles(t_str, fixed_network, result_df)
        v['date'] = x
        if x == 0:
            users = v
        else:
            users = users.append(v)
        print(t)

    users = users.replace('None', np.nan)
    users = users.fillna(0)
    print('user result read')
    print(users.shape)

    samples = migrant.copy()
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
                                                                         'd_home_real',
                                                                         'd_dest_real',
                                                                         's_home_real',
                                                                         's_dest_real',
                                                                         'l_home_real',
                                                                         'l_dest_real'
                                                                         ]]
    if i == 0:
        user_migrant_all = user_migrant
    else:
        user_migrant_all = pd.concat([user_migrant_all, user_migrant])
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
                                           'l_dest_real': ['mean', 'std'],
                                           'd_home_real': ['mean', 'std'],
                                           'd_dest_real': ['mean', 'std'],
                                           })

fig, ax = plt.subplots()
fig.subplots_adjust(left=.1, bottom=.1, right=.97, top=.97)

plt.plot(range(len(migrant_d)), migrant_d['s_home_real']['mean'], label="Contacts in home district")
plt.plot(range(len(migrant_d)), migrant_d['s_dest_real']['mean'], label='Contacts in destination district')
plt.xlabel('Month')
plt.ylabel('Percent of supported friends in location')
plt.xlim(0, len(migrant_d) - 1)
plt.ylim(0, 0.5)
plt.xticks(range(len(migrant_d)), xticks)
leg = plt.legend(loc=2, fancybox=False)
leg.get_frame().set_edgecolor('k')
plt.axvline(x=12, c='k', ls='--')
plt.savefig('figure/figure_A9_support_change_shift_share.png', dpi=300)


fig, ax = plt.subplots()
fig.subplots_adjust(left=.1, bottom=.1, right=.97, top=.97)

plt.plot(range(len(migrant_d)), migrant_d['l_home_real']['mean'], label="Contacts in home district")
plt.plot(range(len(migrant_d)), migrant_d['l_dest_real']['mean'], label='Contacts in destination district')
plt.xlabel('Month')
plt.ylabel('Number of friends of friends in location')
plt.xlim(0, len(migrant_d) - 1)
plt.ylim(0, 300)
plt.xticks(range(len(migrant_d)), xticks)
leg = plt.legend(loc=2, fancybox=False)
leg.get_frame().set_edgecolor('k')
plt.axvline(x=12, c='k', ls='--')
plt.savefig('figure/figure_A8_information_change_shift_share.png', dpi=300)
