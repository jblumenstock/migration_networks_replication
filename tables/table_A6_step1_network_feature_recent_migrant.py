import pandas as pd
import numpy as np
import sys
import random
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
random.seed(0)

from pandarallel import pandarallel
pandarallel.initialize(nb_workers=10)


def get_user_order(user_1, user_2):
    if user_1 > user_2:
        return [user_2, user_1]
    elif user_1 == user_2:
        return ['None', 'None']
    else:
        return [user_1, user_2]


start_date = datetime.strptime('2006 7', '%Y %m')
end_date = datetime.strptime('2008 6', '%Y %m')
loop_num = relativedelta(end_date, start_date).months + 12 * relativedelta(end_date, start_date).years + 1

users_dict = {}
for i in range(loop_num):
    date_ = start_date + relativedelta(months=i)
    data_date = date_.strftime('%Y%m')[2:]
    migration_file = 'data/' + data_date + '_migration.txt'
    users = pd.read_csv(migration_file, sep=',')[['id', 'type', 'home', 'dest']]
    users = users[users['type'].isin([1,2,3,4,5])]
    users_dict[data_date] = users

all_users = pd.concat(list(users_dict.values()))
all_users_df = all_users.drop(columns=['type'])
all_users_df = all_users_df.drop_duplicates()

migration_file = 'data/0801_migration.txt'
migration = pd.read_csv(migration_file, sep=',')[['id', 'type', 'home', 'dest']]
dist = list(set(migration['home']) | set(migration['dest']))

for i in range(loop_num):
    date_ = start_date + relativedelta(months=i)
    data_date = date_.strftime('%Y%m')[2:]
    network_date = start_date + relativedelta(months=i - 1)
    network_date = network_date.strftime('%Y%m')[2:]

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
    user_result_raw = user_result[user_result.user.isin(users_with_conn_uniq)]
    user_result_final = user_result_raw

    user_pre_list = []
    for k in users_dict:
        if k <= data_date:
            user_pre_list.append(users_dict[k])
    user_pre_df = pd.concat(user_pre_list)
    user_pre_df = user_pre_df.drop(columns=['type'])
    user_pre_df = user_pre_df.drop_duplicates()


    ego_friends = conn_filtered_bidir.groupby('user_1')['user_2'].apply(list).reset_index(name='friends')
    for _i in dist:
        edge = conn_filtered_bidir[conn_filtered_bidir.user_2_home == _i]
        _all_users = all_users_df[all_users_df.dest == _i]
        _all_users['co_mig'] = 1
        edge_recent_friend = edge.merge(_all_users, left_on=['user_2', 'user_1_home'], right_on=['id', 'home'], how='left')
        edge_recent_friend = edge_recent_friend[~np.isnan(edge_recent_friend.co_mig)]
        edge_recent_friend = edge_recent_friend[['user_1', 'user_2']].drop_duplicates()
        ego_result_1 = edge_recent_friend.groupby('user_1').size().reset_index(name='co_mig_friend' + str(_i))
        
        _user_pre = user_pre_df[user_pre_df.dest == _i]
        _user_pre['recent_mig'] = 1
        edge_recent_friend = edge.merge(_user_pre, left_on=['user_2', 'user_1_home'], right_on=['id', 'home'], how='left')
        edge_recent_friend = edge_recent_friend[~np.isnan(edge_recent_friend.recent_mig)]
        edge_recent_friend = edge_recent_friend[['user_1', 'user_2']].drop_duplicates()
        ego_result_2 = edge_recent_friend.groupby('user_1').size().reset_index(name='recent_mig_friend' + str(_i))
        
        ego_result = ego_result_1.merge(ego_result_2, on='user_1', how='outer')
        ego_result = ego_result.rename(columns={'user_1': 'user'})

        user_result_final = user_result_final.merge(ego_result, on='user', how='left')
        user_result_final = user_result_final.fillna(0)
        print(_i)

    user_result_final.to_csv('data/' + data_date + '_user_result_recent_migrant.csv', index=None)
    print(data_date + ' done')
