import pandas as pd
import random
from datetime import datetime
from dateutil.relativedelta import relativedelta

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


start_date = datetime.strptime('2006 7', '%Y %m')
end_date = datetime.strptime('2008 6', '%Y %m')
loop_num = relativedelta(end_date, start_date).months + 12 * relativedelta(end_date, start_date).years + 1

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

    user_result = pd.DataFrame(columns=['user'])
    user_result['user'] = users_loc_base['user']
    users_with_conn = conn_filtered_bidir['user_1'].append(conn_filtered_bidir['user_2'])
    users_with_conn_uniq = users_with_conn.unique()
    user_result_raw = user_result[user_result.user.isin(users_with_conn_uniq)]
    user_result_raw['month'] = data_date
    print(i)
    print(user_result_raw.shape)
    if i == 0:
        user_result_final = user_result_raw
    else:
        user_result_final = pd.concat([user_result_final, user_result_raw])

for i in range(loop_num):
    date_ = start_date + relativedelta(months=i)
    data_date = date_.strftime('%Y%m')[2:]
    migration_file_name = data_date + '_migration_1month.txt'
    users = pd.read_csv('data/' + migration_file_name)
    _user = user_result_final[user_result_final['month'] == int(data_date)]
    _user = _user.merge(users[['id','type','dest']], left_on='user', right_on='id', how='inner')
    if i == 0:
        r_1month = _user 
    else:
        r_1month = pd.concat([r_1month, _user])

print(len(r_1month['user'].unique()))
print(len(r_1month[r_1month['type'].isin([1, 2, 5])]['user'].unique()))


for i in range(loop_num):
    date_ = start_date + relativedelta(months=i)
    data_date = date_.strftime('%Y%m')[2:]
    migration_file_name = data_date + '_migration.txt'
    users = pd.read_csv('data/' + migration_file_name)
    _user = user_result_final[user_result_final['month'] == int(data_date)]
    _user = _user.merge(users[['id','type','dest']], left_on='user', right_on='id', how='inner')
    if i == 0:
        r_2month = _user 
    else:
        r_2month = pd.concat([r_2month, _user])

print(len(r_2month['user'].unique()))
print(len(r_2month[r_2month['type'].isin([1, 2, 5])]['user'].unique()))


for i in range(loop_num):
    date_ = start_date + relativedelta(months=i)
    data_date = date_.strftime('%Y%m')[2:]
    migration_file_name = data_date + '_migration_3month.txt'
    users = pd.read_csv('data/' + migration_file_name)
    _user = user_result_final[user_result_final['month'] == int(data_date)]
    _user = _user.merge(users[['id','type','dest']], left_on='user', right_on='id', how='inner')
    if i == 0:
        r_3month = _user 
    else:
        r_3month = pd.concat([r_3month, _user])

print(len(r_3month['user'].unique()))
print(len(r_3month[r_3month['type'].isin([1, 2, 5])]['user'].unique()))


for i in range(loop_num):
    date_ = start_date + relativedelta(months=i)
    data_date = date_.strftime('%Y%m')[2:]
    migration_file_name = data_date + '_migration_6month.txt'
    users = pd.read_csv('data/' + migration_file_name)
    _user = user_result_final[user_result_final['month'] == int(data_date)]
    _user = _user.merge(users[['id','type','dest']], left_on='user', right_on='id', how='inner')
    if i == 0:
        r_6month = _user 
    else:
        r_6month = pd.concat([r_6month, _user])

print(len(r_6month['user'].unique()))
print(len(r_6month[r_6month['type'].isin([1, 2, 5])]['user'].unique()))
